from rest_framework import serializers

from carton_manage.verify_manage.models import VerifyCodeRecord
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class VerifyCodeRecordSerializer(CustomModelSerializer):
    """
   校验码记录-序列化器
    """
    class Meta:
        model = VerifyCodeRecord
        fields = "__all__"
        read_only_fields = ["id"]


class VerifyCodeRecordCreateUpdateSerializer(CustomModelSerializer):
    """
   校验码记录管理 创建/更新时的列化器
    """

    class Meta:
        model = VerifyCodeRecord
        fields = '__all__'


class VerifyCodeRecordViewSet(CustomModelViewSet):
    """
   校验码记录管理接口:
    """
    queryset = VerifyCodeRecord.objects.all()
    serializer_class = VerifyCodeRecordSerializer
    create_serializer_class = VerifyCodeRecordCreateUpdateSerializer
    update_serializer_class = VerifyCodeRecordCreateUpdateSerializer
