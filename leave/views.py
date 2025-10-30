from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import LeaveRequest
from .forms import LeaveRequestForm, LeaveApprovalForm
from attendance.models import Attendance

@login_required
def leave_request_create(request):
    employee = request.user.employee
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            
            # 残年休チェック
            if leave_request.days > employee.remaining_leave_days:
                messages.error(request, '残年休日数が不足しています')
                return render(request, 'leave/request_form.html', {'form': form})
            
            leave_request.save()
            messages.success(request, '年休申請を送信しました')
            
            # 通知メール送信（管理者へ）
            # send_mail(...)
            
            return redirect('leave_request_list')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'leave/request_form.html', {'form': form})

@login_required
def leave_request_list(request):
    employee = request.user.employee
    
    if employee.is_manager or employee.is_admin:
        # 管理者：全申請表示
        leave_requests = LeaveRequest.objects.all()
    else:
        # 一般社員：自分の申請のみ
        leave_requests = LeaveRequest.objects.filter(employee=employee)
    
    return render(request, 'leave/request_list.html', {'leave_requests': leave_requests})

@login_required
def leave_request_approve(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    employee = request.user.employee
    
    if not (employee.is_manager or employee.is_admin):
        messages.error(request, '承認権限がありません')
        return redirect('leave_request_list')
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            
            if action == 'approve':
                leave_request.status = 'approved'
                leave_request.approver = employee
                leave_request.approved_at = timezone.now()
                
                # 残年休を減算
                leave_request.employee.remaining_leave_days -= leave_request.days
                leave_request.employee.save()
                
                # 勤怠レコードを年休として登録
                current_date = leave_request.start_date
                while current_date <= leave_request.end_date:
                    Attendance.objects.update_or_create(
                        employee=leave_request.employee,
                        date=current_date,
                        defaults={
                            'leave_type': 'annual',
                            'source': 'admin_edit',
                            'remarks': f'年休申請ID: {leave_request.id}'
                        }
                    )
                    from datetime import timedelta
                    current_date += timedelta(days=1)
                
                messages.success(request, '年休申請を承認しました')
            else:
                leave_request.status = 'rejected'
                leave_request.rejection_reason = form.cleaned_data.get('rejection_reason', '')
                messages.info(request, '年休申請を却下しました')
            
            leave_request.save()
            
            # 通知メール送信
            # send_mail(...)
            
            return redirect('leave_request_list')
    else:
        form = LeaveApprovalForm()
    
    return render(request, 'leave/approve.html', {'form': form, 'leave_request': leave_request})