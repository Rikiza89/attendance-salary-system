from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import EmployeeLoginForm
from attendance.models import Attendance
from leave.models import LeaveRequest
from payroll.models import Payroll
from django.http import HttpResponse

def employee_login(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('employee_dashboard')
    else:
        form = EmployeeLoginForm()
    return render(request, 'login.html', {'form': form})

def employee_logout(request):
    logout(request)
    return redirect('login')

@login_required
def employee_dashboard(request):
    try:
        employee = request.user.employee
    except employee.DoesNotExist:
        # Employeeレコードがない場合
        return HttpResponse('社員情報が登録されていません。管理者に連絡してください。')
    today = timezone.now().date()
    current_month = today.replace(day=1)
    
    # 今日の出退勤
    today_attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    # 今月の勤務統計
    month_stats = Attendance.objects.filter(
        employee=employee,
        date__gte=current_month,
        date__lte=today
    ).aggregate(
        total_hours=Sum('working_hours'),
        total_overtime=Sum('overtime_hours'),
        days_worked=Count('id')
    )
    
    # 最新給与
    latest_payroll = Payroll.objects.filter(
        employee=employee
    ).order_by('-month').first()
    
    # 未承認年休
    pending_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='pending'
    ).count()
    
    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'month_stats': month_stats,
        'latest_payroll': latest_payroll,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'employee/dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.employee.is_admin:
        return redirect('employee_dashboard')
    
    today = timezone.now().date()
    current_month = today.replace(day=1)
    
    # 部署別出勤率
    from employees.models import Employee
    departments = Employee.objects.filter(status='active').values('department').distinct()
    
    dept_stats = []
    for dept in departments:
        dept_name = dept['department']
        employees = Employee.objects.filter(department=dept_name, status='active')
        total_employees = employees.count()
        
        worked_today = Attendance.objects.filter(
            employee__in=employees,
            date=today
        ).count()
        
        attendance_rate = (worked_today / total_employees * 100) if total_employees > 0 else 0
        dept_stats.append({
            'department': dept_name,
            'attendance_rate': round(attendance_rate, 1)
        })
    
    # 残業時間ランキング
    overtime_ranking = Attendance.objects.filter(
        date__gte=current_month
    ).values('employee__name').annotate(
        total_overtime=Sum('overtime_hours')
    ).order_by('-total_overtime')[:10]
    
    # 未承認年休
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    
    # 給与支払いステータス
    unpaid_payrolls = Payroll.objects.filter(status='calculated').count()
    
    context = {
        'dept_stats': dept_stats,
        'overtime_ranking': overtime_ranking,
        'pending_leaves': pending_leaves,
        'unpaid_payrolls': unpaid_payrolls,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)