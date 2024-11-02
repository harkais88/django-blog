from django.urls import path
from . import views

urlpatterns = [
    path('account/login', views.login, name="login"),
    path('account/login/otp/<str:username>',views.otp,name="otp"),
    path('account/login/password/change/request',views.password_change_request,name='password_change_request'),
    path('account/login/password/change/verify',views.password_change_verify,name='password_change_verify'),
    path('account/login/password/change',views.password_change,name='password_change'),
    path('account/register', views.register, name="register"),
    path('account/logout', views.logout, name="logout"),
    path('check_username/',views.check_username, name="check_username"),
]
