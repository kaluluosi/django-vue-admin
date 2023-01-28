from rest_framework import routers

from carton_manage.basics_manage.views.device_manage import DeviceManageViewSet
from carton_manage.basics_manage.views.factory_info import FactoryInfoViewSet
from carton_manage.basics_manage.views.production_line import ProductionLineViewSet

url = routers.SimpleRouter()
url.register(r'factory_info', FactoryInfoViewSet)
url.register(r'device_manage', DeviceManageViewSet)
url.register(r'production_line', ProductionLineViewSet)

urlpatterns = [
]
urlpatterns += url.urls