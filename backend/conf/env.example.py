import os

from application.settings import BASE_DIR

# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
# 数据库 ENGINE ，默认演示使用 sqlite3 数据库，正式环境建议使用 mysql 数据库
# # 数据库密码
DATABASE_ENGINE = "psqlextra.backend"
# # # 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 5432
# 数据库用户名
DATABASE_USER = "postgres"
# 数据库密码
DATABASE_PASSWORD = "Aa123456."
# 数据库名
DATABASE_NAME = "packaging_coding"

# 表前缀
TABLE_PREFIX = "dvadmin_"
# ================================================= #
# ******** redis配置，无redis 可不进行配置  ******** #
# ================================================= #
REDIS_PASSWORD = ''
REDIS_HOST = '127.0.0.1'
REDIS_DB = 21
CELERY_BROKER_DB = 22
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6380'
# ================================================= #
# ****************** 功能 启停  ******************* #
# ================================================= #
DEBUG = True
# 启动登录详细概略获取(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = False
# 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
LOGIN_NO_CAPTCHA_AUTH = False
# 是否启动API日志记录
API_LOG_ENABLE = locals().get("API_LOG_ENABLE", True)
# API 日志记录的请求方式
API_LOG_METHODS = locals().get("API_LOG_METHODS", ["POST", "UPDATE", "DELETE", "PUT"])
# API_LOG_METHODS = 'ALL' # ['POST', 'DELETE']
# ================================================= #
# ************** ClickHouseDb 配置  ************** #
# ================================================= #
CLICK_HOUSE_DB_URL = 'http://127.0.0.1:8123'
CLICK_HOUSE_DB_USERNAME = ''
CLICK_HOUSE_DB_PASSWORD = ''
CLICK_HOUSE_DB_PREFIX = 'packaging_coding_test'
CLICK_HOUSE_CLUSTER_NAME = 'default'

# ================================================= #
# ****************** 其他 配置  ******************* #
# ================================================= #
ENVIRONMENT = "local"  # 环境，test 测试环境;prod线上环境;local本地环境
ALLOWED_HOSTS = ["*"]
# 系统配置存放位置：redis/memory(默认)
DISPATCH_DB_TYPE = 'redis'

# 加密秘钥KEY
ENCRYPTION_KEY_ID = [
    'test0000',
    'test0001',
    'test0002',
    'test0003',
    'test0004',
    'test0005',
    'test0006',
    'test0007',
    'test0008',
    'test0009',
]
