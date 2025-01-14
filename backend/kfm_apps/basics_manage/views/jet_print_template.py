import django_filters
from django_restql.fields import DynamicSerializerMethodField
from rest_framework import serializers

from basics_manage.models import JetPrintTemplate, JetPrintTemplateAttribute, CodePackageTemplate
from carton_manage.production_manage.models import ProductionWork
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomValidationError
from dvadmin.utils.viewset import CustomModelViewSet


class JPTCodePackageTemplateSerializer(CustomModelSerializer):
    """
    码包模板-序列化器
    """
    class Meta:
            model = CodePackageTemplate
            fields = ['id','name']
            read_only_fields = ["id"]

class JPTAttributeFiledSerializer(CustomModelSerializer):

    class Meta:
        model = JetPrintTemplateAttribute
        fields = '__all__'
        extra_kwargs = {'jet_print_template': {'required': False,'allow_null':True}}

class JetPrintTemplateSerializer(CustomModelSerializer):
    """
    喷码模板-序列化器
    """
    code_package_template_name = serializers.CharField(read_only=True,source="code_package_template.name")
    attr_fields = serializers.SerializerMethodField()

    def get_attr_fields(self, instance):
        fields = JPTAttributeFiledSerializer(instance.jetprinttemplateattribute_set.all(),many=True)
        return fields.data

    class Meta:
            model = JetPrintTemplate
            fields = "__all__"
            read_only_fields = ["id"]


class JetPrintTemplateCreateUpdateSerializer(CustomModelSerializer):
    """
    喷码模板管理 创建/更新时的列化器
    """
    class Meta:
        model = JetPrintTemplate
        fields = '__all__'
    def create(self, validated_data):
        instance = JetPrintTemplate.objects.create(**validated_data)
        init_data = self.initial_data
        attr_fields = init_data.get("attr_fields",[])
        serializer = JPTAttributeFiledSerializer(data=attr_fields,many=True,request=self.request)
        serializer.is_valid(raise_exception=True)
        serializer.save(jet_print_template=instance)
        return instance

    def update(self, instance, validated_data):
        _ProductionWork = ProductionWork.objects.filter(jet_print_template=instance.id).exists()
        if _ProductionWork:
            raise CustomValidationError("喷码模板已被生产工单使用,无法修改")
        init_data = self.initial_data
        attr_fields = init_data.get("attr_fields", [])
        need_update_id = []
        for item in attr_fields:
            id = item.get("id", None)
            queryset = JetPrintTemplateAttribute.objects.filter(id=id).first()
            if queryset:
                serializer = JPTAttributeFiledSerializer(instance=queryset,data=item, many=False, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                need_update_id.append(id)
            else:
                serializer = JPTAttributeFiledSerializer(data=item, many=False, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save(jet_print_template=instance)
                need_update_id.append(serializer.instance.id)
        JetPrintTemplateAttribute.objects.filter(jet_print_template=instance.id).exclude(id__in=need_update_id).delete()
        return super().update(instance, validated_data)

class JetPrintTemplateFilter(django_filters.FilterSet):
    id = django_filters.AllValuesMultipleFilter(field_name="id",lookup_expr='in')
    code_package_template_name = django_filters.CharFilter(field_name="code_package_template__name",lookup_expr='icontains')
    code_package_template_id = django_filters.NumberFilter(field_name="code_package_template__id",lookup_expr='exact')
    class Meta:
        model = JetPrintTemplate
        fields = "__all__"

class JetPrintTemplateViewSet(CustomModelViewSet):
    """
    喷码模板管理接口:
    """
    queryset = JetPrintTemplate.objects.all()
    serializer_class = JetPrintTemplateSerializer
    create_serializer_class = JetPrintTemplateCreateUpdateSerializer
    update_serializer_class = JetPrintTemplateCreateUpdateSerializer
    filter_class = JetPrintTemplateFilter
    search_fields = ['no', 'name']
