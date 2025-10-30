from django.test import TestCase
from django.contrib.auth.models import User
from employees.models import Employee
from .models import Attendance
from datetime import date, time

class AttendanceTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test001', password='testpass')
        self.employee = Employee.objects.create(
            user=user,
            employee_no='test001',
            name='テスト太郎',
            department='開発部',
            position='一般',
            hire_date=date(2024, 1, 1),
            base_salary=300000
        )
    
    def test_working_hours_calculation(self):
        """勤務時間計算テスト"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            clock_in_time=time(9, 0),
            clock_out_time=time(18, 0)
        )
        # 9:00-18:00 = 9時間 - 休憩1時間 = 8時間
        self.assertEqual(float(attendance.working_hours), 8.0)
        self.assertEqual(float(attendance.overtime_hours), 0.0)
    
    def test_overtime_calculation(self):
        """残業時間計算テスト"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            clock_in_time=time(9, 0),
            clock_out_time=time(21, 0)
        )
        # 9:00-21:00 = 12時間 - 休憩1時間 = 11時間
        # 残業 = 11 - 8 = 3時間
        self.assertEqual(float(attendance.working_hours), 11.0)
        self.assertEqual(float(attendance.overtime_hours), 3.0)
    
    def test_late_flag(self):
        """遅刻フラグテスト"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            clock_in_time=time(9, 30),
            clock_out_time=time(18, 30)
        )
        self.assertTrue(attendance.late_flag)