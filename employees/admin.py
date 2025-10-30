from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_no', 'name', 'department', 'position', 'status', 'hire_date']
    list_filter = ['department', 'status', 'is_manager', 'is_admin']
    search_fields = ['employee_no', 'name', 'email']
    readonly_fields = ['created_at', 'updated_at']