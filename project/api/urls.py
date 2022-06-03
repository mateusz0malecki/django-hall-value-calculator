from django.urls import path, include
from rest_framework import routers
from .views import MaterialsPricesViewSet, MaterialsAmountViewSet, HallViewSet, UserViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'halls', HallViewSet, basename='halls')
router.register(r'prices', MaterialsPricesViewSet, basename='prices')
router.register(r'amounts', MaterialsAmountViewSet, basename='amounts')


urlpatterns = [
    path('', include(router.urls)),
]
