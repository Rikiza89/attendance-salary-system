from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', '在職'),
        ('inactive', '退職'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    employee_no = models.CharField('社員番号', max_length=20, unique=True)
    name = models.CharField('氏名', max_length=100)
    department = models.CharField('部署', max_length=100)
    position = models.CharField('役職', max_length=100)
    hire_date = models.DateField('入社日')
    email = models.EmailField('メールアドレス', blank=True, null=True)
    base_salary = models.DecimalField('基本給', max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField('時給', max_digits=8, decimal_places=2, blank=True, null=True)
    is_manager = models.BooleanField('管理者', default=False)
    is_admin = models.BooleanField('システム管理者', default=False)
    nfc_id = models.CharField('NFC ID', max_length=50, blank=True, null=True, unique=True)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='active')
    annual_leave_days = models.IntegerField('年休日数', default=10)
    remaining_leave_days = models.DecimalField('残年休日数', max_digits=4, decimal_places=1, default=10)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        verbose_name = '社員'
        verbose_name_plural = '社員'
        ordering = ['employee_no']
    
    def __str__(self):
        return f"{self.employee_no} - {self.name}"