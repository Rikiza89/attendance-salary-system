from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_dashboard, name='employee_dashboard'),
    path('login/', views.employee_login, name='login'),
    path('logout/', views.employee_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/nfc-status/', views.check_nfc_status, name='nfc_status'),
    path('api/nfc-auto/', views.nfc_auto_attendance, name='nfc_auto_attendance'),
]