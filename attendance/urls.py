from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.attendance_calendar, name='attendance_calendar'),
    path('clock/', views.clock_in_out_manual, name='clock_in_out_manual'),
    path('nfc/', views.nfc_attendance, name='nfc_attendance'),
    path('edit/<int:pk>/', views.attendance_edit, name='attendance_edit'),  # <int:pk>追加
    path('export/', views.export_attendance_excel, name='export_attendance'),
]