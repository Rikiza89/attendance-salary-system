from django.contrib import admin
from .models import Payroll, TaxConfig

@admin.register(TaxConfig)
class TaxConfigAdmin(admin.ModelAdmin):
    list_display = ['year', 'health_insurance_rate', 'pension_insurance_rate', 'employment_insurance_rate', 'income_tax_rate', 'residence_tax_rate']
    list_editable = ['health_insurance_rate', 'pension_insurance_rate', 'employment_insurance_rate', 'income_tax_rate', 'residence_tax_rate']
    ordering = ['-year']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'base_salary', 'total_deduction', 'total_salary', 'status', 'paid_at']
    list_filter = ['status', 'month']
    search_fields = ['employee__name', 'employee__employee_no']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['recalculate_deductions']
    
    def recalculate_deductions(self, request, queryset):
        for payroll in queryset:
            payroll.calculate_deductions()
            payroll.save()
        self.message_user(request, f'{queryset.count()}件の給与を再計算しました')
    recalculate_deductions.short_description = '控除額を再計算'