from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("check-if-user-isregistered/", views.user_identifier, name="user_identifier"),
    path("login/", views.TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("send-otp/", views.otp_sender, name="send-otp"),
    path("verify-otp/", views.verify_otp, name="verify-otp"),
    path("signin/", views.registerUser, name="register"),
    path("profile/", views.get_user_profile, name="get_user_profile"),
    path("garage/", views.get_user_garage, name="get_user_garage"),
    path("add-to-user-garage/", views.add_to_user_garage, name="add_to_user_garage"),
    path("remove-from-user-garage/<int:garage_id>/", views.remove_from_user_garage, name="remove_from_user_garage"),
    path("update-user-profile/", views.update_user_profile, name="update_user_profile"),
    path("update-user-address/", views.update_user_address, name="update_user_address"),
]
