from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'days', 'status', 'request_date']
    list_filter = ['status', 'request_date']
    search_fields = ['employee__name', 'employee__employee_no']
    readonly_fields = ['request_date', 'created_at', 'updated_at']