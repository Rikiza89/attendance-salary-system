from django.db import models
from employees.models import Employee

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '申請中'),
        ('approved', '承認済'),
        ('rejected', '却下'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='社員', related_name='leave_requests')
    request_date = models.DateField('申請日', auto_now_add=True)
    start_date = models.DateField('開始日')
    end_date = models.DateField('終了日')
    days = models.DecimalField('日数', max_digits=3, decimal_places=1)
    reason = models.TextField('理由')
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, 
                                 verbose_name='承認者', related_name='approved_leaves')
    approved_at = models.DateTimeField('承認日時', null=True, blank=True)
    rejection_reason = models.TextField('却下理由', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        verbose_name = '年休申請'
        verbose_name_plural = '年休申請'
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.start_date} ~ {self.end_date}"