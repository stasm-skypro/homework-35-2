from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from users.apps import UsersConfig
from rest_framework import routers
from .views import (
    UserViewSet,
    PaymentViewSet,
    SubscriptionAPIView,
)

app_name = UsersConfig.name

routers = routers.DefaultRouter()
routers.register(r"user", UserViewSet, basename="user")
routers.register(r"payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenObtainPairView.as_view(), name="token_refresh"),
    path("subscription/", SubscriptionAPIView.as_view(), name="subscription"),
] + routers.urls
