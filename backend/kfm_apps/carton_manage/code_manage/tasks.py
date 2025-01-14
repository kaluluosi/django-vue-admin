import datetime
import functools
import os
import re
import shutil

import django
from django.db import connection

from application import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()
from django_tenants.utils import schema_context

from application.celery import app
from carton_manage.code_manage.models import CodePackage, CodeRepetitionRecord
from utils.currency import des_encrypt_file, zip_compress_file, get_code_package_import_txt_path, md5_file, md5_value, \
    get_code_package_import_zip_path
from dvadmin_tenants.models import HistoryTemporaryCode, HistoryCodeInfo, Client


def base_task_error():
    """
    celery 通用装饰器
    :return:
    """

    def wraps(func):
        @app.task()
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                code_package_obj = CodePackage.objects.get(id=args[0])
                code_package_obj.write_log({
                    "content": f"未知错误",
                    "remark": f"错误信息:{exc}",
                    "step": 9,
                    "type": 'error'
                })
                raise

        return wrapper

    return wraps


@base_task_error()
def code_package_import_check(code_package_id):
    """
    码包导入校验确认(单队列)
    1.校验码包状态
    2.根据规则验证码包是否合格
    3.码包本身重码验证
    4.历史重码校验
    5.数据入库到ck中
    6.对数据进行加密并删除源数据
    code_package_id: 码包ID
    """
    code_package_obj = CodePackage.objects.get(id=code_package_id)
    code_package_obj.import_log = None
    code_package_obj.import_start_datetime = datetime.datetime.now()
    code_package_obj.save()
    # 1.校验码包状态

    if code_package_obj.validate_status not in [1, 2]:
        code_package_obj.write_log({
            "content": f"码包校验状态",
            "remark": f"当前状态为:[{code_package_obj.validate_status}]{code_package_obj.get_validate_status_display()}",
            "step": 1,
            "type": 'error'
        })
        return f"校验状态错误:{code_package_obj.get_validate_status_display()}"
    code_package_obj.validate_status = 2
    code_package_obj.save()
    # code_package_obj.write_log({"content": f"码包状态", "step": 1, })
    # 2.根据规则验证码包是否合格
    source_file_path = os.path.join(get_code_package_import_txt_path(), code_package_obj.file_position)
    code_package_template_obj = code_package_obj.code_package_template
    with open(source_file_path, 'rb') as file:
        readline = file.readline().decode('utf-8')
        # 2.1.校验换行符
        if (code_package_template_obj.line_feed == 2 and not readline.endswith(
                '\r\n')) or (code_package_template_obj.line_feed == 1 and readline.endswith('\r\n')):  # 回车换行
            # 换行符校验失败
            code_package_obj.write_log({
                "content": '规则验证-换行符',
                "step": 2.1,
                "type": 'error',
            })
            return "规则验证-换行符校验失败"
        code_package_obj.write_log({"content": f"规则验证-换行符", "step": 2.1})
        # 2.2.校验整体字符长度
        if len(readline) != code_package_template_obj.char_length:
            code_package_obj.write_log({
                "content": '规则验证-整体字符长度',
                "step": 2.2,
                "type": 'error'
            })
            return "规则验证-整体字符长度校验失败"
        readline = readline.replace('\r\n', '').replace('\n', '')
        code_package_obj.write_log({"content": f"规则验证-整体字符长度", "step": 2.2})
        # 2.3.分隔符
        if code_package_template_obj.separator == '无':
            readline_list = [readline]
        else:
            readline_list = readline.split(code_package_template_obj.separator)
            if len(readline_list) <= 1:
                code_package_obj.write_log({
                    "content": '规则验证-分隔符',
                    "step": 2.3,
                    "type": 'error'
                })
                return "规则验证-分隔符校验失败"
        code_package_obj.write_log({"content": f"规则验证-分隔符", "step": 2.3})
        # 2.4.分割后的字段数
        if len(readline_list) != code_package_template_obj.fields:
            code_package_obj.write_log({
                "content": '规则验证-字段数',
                "step": 2.4,
                "type": 'error'
            })
            return "规则验证-字段数校验失败"
        code_package_obj.write_log({"content": f"规则验证-字段数", "step": 2.4})
        #
        # 根据码包模板校验字段属性
        template_attribute = code_package_template_obj.codepackagetemplateattribute_set.order_by('number').all()
        is_code_content_number = []
        for attribute in template_attribute:
            """
            2.5 根据字段属性，根据字段序号排序，校验所有的字段属性是否符合规则
            2.5.0 判断字段序号是否超出
            2.5.1 校验字段长度是否符合
            2.5.2 验证匹配字符，先校验是否开头，如果不是则校验是否是正则匹配
            """
            pass
            if attribute.number + 1 > len(readline_list):
                code_package_obj.write_log({
                    "content": '规则验证-字段属性',
                    "step": 2.50,
                    "type": 'error'
                })
                return "规则验证-字段序号超出"
            string = readline_list[attribute.number]
            if attribute.char_length != -1 and attribute.char_length != len(string):
                code_package_obj.write_log({
                    "content": '规则验证-字段属性',
                    "step": 2.51,
                    "type": 'error'
                })
                return "规则验证-字段长度不符"

            if attribute.verify_matches and not (
                    string.startswith(attribute.verify_matches) or re.fullmatch(attribute.verify_matches, string)):
                code_package_obj.write_log({
                    "content": '规则验证-字段属性',
                    "step": 2.52,
                    "type": 'error'
                })
                return "规则验证-验证匹配符不符"
            if attribute.is_code_content:
                is_code_content_number.append(attribute.number)
        code_package_obj.write_log({"content": f"规则验证-字段属性", "step": 2.5})
    code_data_list = []
    # 码数据先入临时表中
    _HistoryTemporaryCode = HistoryTemporaryCode.set_db(timeout=60 * 30)
    _HistoryTemporaryCode.create_table(table_suffix=code_package_obj.id)
    tenant_id = Client.objects.get(schema_name=connection.tenant.schema_name).id
    code_package_template_obj.codepackagetemplateattribute_set.order_by('number').all()
    with open(source_file_path) as file:
        for readline in file:
            readline = readline.replace('\r\n', '').replace('\n', '')
            if code_package_template_obj.separator == '无':
                readline_list = [readline]
            else:
                readline_list = readline.split(code_package_template_obj.separator)
            for code_content_number in is_code_content_number:

            # if code_package_template_obj.code_type in [0, 2]:  # 外码
            #     w_url = readline_list[code_package_template_obj.w_field_position]
                code_data_list.append(_HistoryTemporaryCode(
                    code=md5_value(readline_list[code_content_number]),
                    code_type='2',
                    content=readline_list[code_content_number],
                    tenant_id=f"{tenant_id}",
                    package_id=f"{code_package_obj.id}",
                    timestamp=datetime.datetime.now()
                ))
            if len(code_data_list) >= 500000:
                _HistoryTemporaryCode.bulk_insert(code_data_list)
                code_data_list = []
    if len(code_data_list) != 0:
        _HistoryTemporaryCode.bulk_insert(code_data_list)
    # 3.码包本身重码验证
    count, data = _HistoryTemporaryCode.select_duplicate()
    if count != 0:
        # 问题码入库
        error_data_list = []
        for key, val in data.items():
            for ele in range(val.get('count') - 1):
                error_data_list.append(CodeRepetitionRecord(
                    **{
                        "code_package": code_package_obj,
                        "repetition_code_package": code_package_obj,
                        "code_content": val.get('content'),
                        "code_content_md5": key,
                        "code_type": val.get('code_type'),
                        "repetition_type": 0,
                        "creator": code_package_obj.creator,
                        "modifier": code_package_obj.modifier,
                        "dept_belong_id": code_package_obj.dept_belong_id,
                    }
                ))
        CodeRepetitionRecord.objects.bulk_create(error_data_list)
        _HistoryTemporaryCode.delete()

        code_package_obj.write_log({
            "content": f'本码包查重',
            "remark": f"发现重码数{len(error_data_list)}个",
            "step": 3,
            "type": 'error'
        }, package_repetition_number=len(error_data_list))
        return
    code_package_obj.write_log({"content": '本码包查重', "step": 3})
    # 4.历史重码校验
    from_table = HistoryCodeInfo.get_base_all_model().table_name()
    _HistoryCodeInfo = HistoryCodeInfo.set_db()
    count, history_code_data = _HistoryTemporaryCode.verify_history_code_repetition(
        from_db=_HistoryCodeInfo.db.db_name, from_table=from_table)
    if count != 0:
        if count > 1000:
            code_package_obj.write_log({
                "content": '历史查重',
                "remark": '历史码数据中发现大量重复码,重复数量超过1000,请检查码包是否重复导入!',
                "step": 4,
                "type": 'error'
            }, database_repetition_number=1001)
            _HistoryTemporaryCode.delete()
            return
        duplicate_list = []
        for key, val in history_code_data.items():
            # 获取明码内容
            duplicate_list.append(CodeRepetitionRecord(
                **{
                    "code_package": code_package_obj,
                    "repetition_code_package_id": val.get('repetition_code_package'),
                    "code_content": val.get('content'),
                    "code_content_md5": key,
                    "code_type": val.get('code_type'),
                    "repetition_type": 1,
                    "creator": code_package_obj.creator,
                    "modifier": code_package_obj.modifier,
                    "dept_belong_id": code_package_obj.dept_belong_id,
                }
            ))
        CodeRepetitionRecord.objects.bulk_create(duplicate_list)
        _HistoryTemporaryCode.delete()
        code_package_obj.write_log({
            "content": f'历史查重',
            "remark": f'历史码包重复码校验失败，发现重码数{len(duplicate_list)}个',
            "step": 4,
            "type": 'error'
        }, database_repetition_number=len(duplicate_list))
        return
    code_package_obj.write_log({"content": '历史查重', "step": 4})
    # 5.数据入库到ck中
    _HistoryTemporaryCode.insert_history(from_table, insert_db=HistoryCodeInfo.db.db_name)
    _HistoryTemporaryCode.delete()
    # 6.对数据进行加密并删除源数据
    target_file_path = source_file_path.replace('.txt', '.zip')
    zip_compress_file(source_file_path, target_file_path, is_rm=True)
    des_encrypt_file(target_file_path, settings.ENCRYPTION_KEY_ID[code_package_obj.key_id])
    # 移动文件到对应zip目录
    os.rename(target_file_path, target_file_path.replace('.zip', '.zip.des'))
    to_file = os.path.join(get_code_package_import_zip_path(),
                           code_package_obj.file_position.replace('.txt', '.zip.des'))
    if not os.path.exists(os.path.join(get_code_package_import_zip_path(),
                                       *code_package_obj.file_position.split(os.sep)[:-1])):  # 文件夹不存在则创建
        os.makedirs(
            os.path.join(get_code_package_import_zip_path(), *code_package_obj.file_position.split(os.sep)[:-1]))
    shutil.move(target_file_path.replace('.zip', '.zip.des'), to_file)

    code_package_obj = CodePackage.objects.get(id=code_package_id)
    code_package_obj.file_position = code_package_obj.file_position.replace('.txt', '.zip.des')
    code_package_obj.validate_status = 4
    code_package_obj.des_file_md5 = md5_file(
        os.path.join(get_code_package_import_zip_path(), code_package_obj.file_position))
    code_package_obj.save()
    code_package_obj.write_log({"content": '全部校验', "step": 5})


if __name__ == '__main__':
    with schema_context("demo"):
        # HistoryCodeInfo.set_db().create_table()
        code_package_import_check(10)
        # print(json.loads(CodePackage.objects.get(id=2).import_log))
