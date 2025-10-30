from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
from calendar import monthcalendar
from .models import Attendance
from .forms import AttendanceForm
from core.nfc_reader import nfc_clock_in_out
import openpyxl

@login_required
def attendance_calendar(request):
    employee = request.user.employee
    today = timezone.now().date()
    
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    target_date = datetime(year, month, 1).date()
    
    # カレンダー生成
    cal = monthcalendar(year, month)
    
    # 月の勤怠データ取得
    attendances = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    )
    
    attendance_dict = {a.date.day: a for a in attendances}
    
    # カレンダーにデータをマッピング
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                date_obj = datetime(year, month, day).date()
                attendance = attendance_dict.get(day)
                week_data.append({
                    'day': day,
                    'date': date_obj,
                    'attendance': attendance,
                    'is_today': date_obj == today
                })
        calendar_data.append(week_data)
    
    # 前月・次月
    prev_month = target_date - timedelta(days=1)
    next_month = (target_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    context = {
        'calendar_data': calendar_data,
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'next_month': next_month,
    }
    return render(request, 'attendance/calendar.html', context)

@login_required
def clock_in_out_manual(request):
    employee = request.user.employee
    today = timezone.now().date()
    
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={'source': 'manual'}
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'clock_in' and not attendance.clock_in_time:
            attendance.clock_in_time = timezone.now().time()
            attendance.save()
        elif action == 'clock_out' and attendance.clock_in_time and not attendance.clock_out_time:
            attendance.clock_out_time = timezone.now().time()
            attendance.save()
        return redirect('employee_dashboard')
    
    return redirect('employee_dashboard')

@login_required
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    # 管理者または本人のみ編集可能
    if not (request.user.employee.is_admin or attendance.employee == request.user.employee):
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save(commit=False)
            if request.user.employee.is_admin:
                attendance.source = 'admin_edit'
            attendance.save()
            return redirect('attendance_calendar')
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'attendance/edit.html', {'form': form, 'attendance': attendance})

@login_required
def nfc_attendance(request):
    """NFC打刻エンドポイント"""
    from django.conf import settings
    if not settings.NFC_ENABLED:
        return HttpResponse("NFC機能は無効です", status=400)
    
    result = nfc_clock_in_out()
    return HttpResponse(result)

@login_required
def export_attendance_excel(request):
    """勤怠データExcelエクスポート"""
    employee = request.user.employee
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).order_by('date')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{year}年{month}月勤怠"
    
    # ヘッダー
    headers = ['日付', '出勤時刻', '退勤時刻', '勤務時間', '残業時間', '遅刻', '勤怠区分', '備考']
    ws.append(headers)
    
    # データ
    for att in attendances:
        ws.append([
            att.date.strftime('%Y-%m-%d'),
            att.clock_in_time.strftime('%H:%M') if att.clock_in_time else '',
            att.clock_out_time.strftime('%H:%M') if att.clock_out_time else '',
            float(att.working_hours),
            float(att.overtime_hours),
            '遅刻' if att.late_flag else '',
            att.get_leave_type_display(),
            att.remarks
        ])
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=attendance_{year}_{month}.xlsx'
    wb.save(response)
    return response