from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee
from attendance.models import Attendance
from leave.models import LeaveRequest
from payroll.models import Payroll, TaxConfig
from datetime import date, time, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'シードデータを投入'

    def handle(self, *args, **options):
        # 税金設定作成
        current_year = date.today().year
        TaxConfig.objects.get_or_create(
            year=current_year,
            defaults={
                'health_insurance_rate': Decimal('0.0996'),
                'pension_insurance_rate': Decimal('0.183'),
                'employment_insurance_rate': Decimal('0.006'),
                'income_tax_rate': Decimal('0.0714'),
                'residence_tax_rate': Decimal('0.10'),
            }
        )
        self.stdout.write(f"税金設定作成: {current_year}年度")

        # ユーザーとEmployee作成
        users_data = [
            {'username': 'emp001', 'password': 'pass001', 'employee_no': 'EMP001', 'name': '田中太郎', 'department': '開発部', 'position': '課長', 'is_manager': True, 'salary': 400000},
            {'username': 'emp002', 'password': 'pass002', 'employee_no': 'EMP002', 'name': '佐藤花子', 'department': '開発部', 'position': '一般', 'is_manager': False, 'salary': 300000},
            {'username': 'emp003', 'password': 'pass003', 'employee_no': 'EMP003', 'name': '鈴木一郎', 'department': '営業部', 'position': '一般', 'is_manager': False, 'salary': 280000},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(username=user_data['username'])
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f"User created: {user.username}")
            
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_no': user_data['employee_no'],
                    'name': user_data['name'],
                    'department': user_data['department'],
                    'position': user_data['position'],
                    'hire_date': date(2023, 4, 1),
                    'base_salary': user_data['salary'],
                    'hourly_rate': Decimal(user_data['salary']) / Decimal('160'),
                    'is_manager': user_data['is_manager'],
                    'is_admin': user_data['is_manager'],
                    'nfc_id': f"NFC{user_data['employee_no']}" if user_data['employee_no'] == 'EMP001' else None,
                }
            )
            if created:
                self.stdout.write(f"Employee created: {employee.name}")

        # 勤怠データ（過去1ヶ月）
        today = date.today()
        for i in range(30):
            work_date = today - timedelta(days=i)
            for emp in Employee.objects.all():
                clock_out = time(18, 0) if i % 3 == 0 else time(20, 0)
                Attendance.objects.get_or_create(
                    employee=emp,
                    date=work_date,
                    defaults={
                        'clock_in_time': time(9, 0),
                        'clock_out_time': clock_out,
                        'source': 'manual'
                    }
                )

        self.stdout.write("勤怠データ作成完了")

        # 給与データ（過去3ヶ月分）
        for month_offset in range(3):
            target_date = today - timedelta(days=30 * month_offset)
            target_month = target_date.strftime('%Y-%m')
            
            for emp in Employee.objects.all():
                month_attendances = Attendance.objects.filter(
                    employee=emp,
                    date__year=target_date.year,
                    date__month=target_date.month
                )
                
                total_overtime = sum([float(a.overtime_hours) for a in month_attendances])
                hourly_rate = emp.hourly_rate or (emp.base_salary / Decimal('160'))
                overtime_pay = Decimal(total_overtime) * hourly_rate * Decimal('1.25')
                bonus = Decimal('50000') if month_offset == 0 else Decimal('0')
                
                payroll, created = Payroll.objects.get_or_create(
                    employee=emp,
                    month=target_month,
                    defaults={
                        'base_salary': emp.base_salary,
                        'overtime_pay': overtime_pay,
                        'bonus': bonus,
                        'status': 'paid' if month_offset > 0 else 'calculated',
                        'remarks': f'{target_month}分給与'
                    }
                )
                
                # 控除額計算
                payroll.calculate_deductions()
                payroll.save()
                
                if created:
                    self.stdout.write(f"給与作成: {emp.name} {target_month}")

        self.stdout.write("給与データ作成完了")

        # 年休申請
        emp = Employee.objects.first()
        LeaveRequest.objects.get_or_create(
            employee=emp,
            start_date=today + timedelta(days=7),
            defaults={
                'end_date': today + timedelta(days=7),
                'days': 1,
                'reason': '私用のため',
                'status': 'pending'
            }
        )

        self.stdout.write(self.style.SUCCESS('✓ シードデータ投入完了'))