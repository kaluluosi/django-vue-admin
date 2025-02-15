from django.urls import path
from rest_framework import routers

from carton_manage.ipc_api.views.back_haul_file import IpcBackHaulFileViewSet
from carton_manage.ipc_api.views.jet_print_template import JetPrintTemplateViewSet
from carton_manage.ipc_api.views.production_work import ProductionWorkViewSet
from carton_manage.ipc_api.views.code_package import CodePackageViewSet
from carton_manage.ipc_api.views.code_package_template import CodePackageTemplateViewSet

url = routers.SimpleRouter()
url.register(r'code_package_template', CodePackageTemplateViewSet)
url.register(r'production_work', ProductionWorkViewSet)
url.register(r'jet_print_template', JetPrintTemplateViewSet)



urlpatterns = [
    path('code_package/', CodePackageViewSet.as_view({'post': 'list'})),
    path(r'download_code_package_file/<str:tenant_name>/<str:day>/<str:file_name>',
         CodePackageViewSet.as_view({'post': 'download_code_package_file'})),
    # 检测端文件回传
    path(r'check/data_upload/', IpcBackHaulFileViewSet.as_view({'post': 'data_upload'})),
    # 检测端状态更新
    path(r'check/verify_status_change/', IpcBackHaulFileViewSet.as_view({'post': 'verify_status_change'})),
    # 检测端校验文件是否全部已上传
    path(r'check/check_file_upload_all/', IpcBackHaulFileViewSet.as_view({'post': 'check_file_upload_all'})),
]
urlpatterns += url.urls

