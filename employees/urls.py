from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_dashboard, name='employee_dashboard'),  # これを確認
    path('login/', views.employee_login, name='login'),
    path('logout/', views.employee_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]