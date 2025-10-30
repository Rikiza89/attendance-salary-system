from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.leave_request_create, name='leave_request_create'),
    path('list/', views.leave_request_list, name='leave_request_list'),
    path('approve/<int:pk>/', views.leave_request_approve, name='leave_request_approve'),  # <int:pk>追加
]