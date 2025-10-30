from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.payroll_list, name='payroll_list'),
    path('slip/<int:pk>/', views.payslip_view, name='payslip_view'),
    path('slip/<int:pk>/download/', views.payslip_download, name='payslip_download'),
]