from django.urls import path
from .views import RegisterView,LoginView,LogoutView,PasswordResetRequestView,PasswordResetConfirmView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("reset-password/", PasswordResetRequestView.as_view(), name="reset-password"),
    path("reset-password-confirm/<int:user_id>/<str:token>/", PasswordResetConfirmView.as_view(), name="reset-password-confirm"),
]
