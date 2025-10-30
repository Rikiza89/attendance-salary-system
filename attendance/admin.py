from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'clock_in_time', 'clock_out_time', 'working_hours', 'overtime_hours', 'leave_type']
    list_filter = ['date', 'leave_type', 'source', 'late_flag']
    search_fields = ['employee__name', 'employee__employee_no']
    date_hierarchy = 'date'