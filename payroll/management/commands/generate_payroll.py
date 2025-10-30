from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.conf import settings
from employees.models import Employee
from attendance.models import Attendance
from payroll.models import Payroll
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = '月次給与計算を実行'
    
    def add_arguments(self, parser):
        parser.add_argument('--month', type=str, help='対象月 (YYYY-MM形式)')
    
    def handle(self, *args, **options):
        target_month = options.get('month')
        
        if not target_month:
            from dateutil.relativedelta import relativedelta
            last_month = datetime.now().date() - relativedelta(months=1)
            target_month = last_month.strftime('%Y-%m')
        
        year, month = map(int, target_month.split('-'))
        
        self.stdout.write(f'給与計算開始: {target_month}')
        
        active_employees = Employee.objects.filter(status='active')
        
        for employee in active_employees:
            attendances = Attendance.objects.filter(
                employee=employee,
                date__year=year,
                date__month=month
            )
            
            stats = attendances.aggregate(total_overtime=Sum('overtime_hours'))
            overtime_hours = stats['total_overtime'] or Decimal('0')
            
            base_salary = employee.base_salary
            hourly_rate = employee.hourly_rate or (base_salary / Decimal('160'))
            overtime_pay = overtime_hours * hourly_rate * Decimal(str(settings.OVERTIME_MULTIPLIER))
            
            payroll, created = Payroll.objects.update_or_create(
                employee=employee,
                month=target_month,
                defaults={
                    'base_salary': base_salary,
                    'overtime_pay': overtime_pay,
                    'bonus': Decimal('0'),
                    'status': 'calculated'
                }
            )
            
            # 控除額計算
            payroll.calculate_deductions()
            payroll.save()
            
            action = '作成' if created else '更新'
            self.stdout.write(
                self.style.SUCCESS(f'{employee.name}の給与を{action}: ¥{payroll.total_salary:,.0f}')
            )
        
        self.stdout.write(self.style.SUCCESS(f'給与計算完了: {target_month}'))