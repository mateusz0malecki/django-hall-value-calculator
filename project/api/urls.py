from django.urls import path, include
from rest_framework import routers
from .views import RegisterView, LoginView, MaterialsPricesViewSet, MaterialsAmountViewSet, HallViewSet, UserViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'halls', HallViewSet, basename='halls')
router.register(r'prices', MaterialsPricesViewSet, basename='prices')
router.register(r'amounts', MaterialsAmountViewSet, basename='amounts')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]
