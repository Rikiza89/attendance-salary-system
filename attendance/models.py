from django.db import models
from employees.models import Employee
from django.conf import settings
from datetime import datetime, timedelta

class Attendance(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('normal', '通常出勤'),
        ('annual', '年休'),
        ('special', '特休'),
        ('sick', '病欠'),
        ('absent', '欠勤'),
    ]
    
    SOURCE_CHOICES = [
        ('manual', '手動入力'),
        ('nfc', 'NFC'),
        ('admin_edit', '管理者編集'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='社員')
    date = models.DateField('日付')
    clock_in_time = models.TimeField('出勤時刻', blank=True, null=True)
    clock_out_time = models.TimeField('退勤時刻', blank=True, null=True)
    working_hours = models.DecimalField('勤務時間', max_digits=4, decimal_places=2, default=0)
    overtime_hours = models.DecimalField('残業時間', max_digits=4, decimal_places=2, default=0)
    late_flag = models.BooleanField('遅刻', default=False)
    leave_type = models.CharField('勤怠区分', max_length=20, choices=LEAVE_TYPE_CHOICES, default='normal')
    remarks = models.TextField('備考', blank=True)
    source = models.CharField('入力元', max_length=20, choices=SOURCE_CHOICES, default='manual')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        verbose_name = '勤怠'
        verbose_name_plural = '勤怠'
        ordering = ['-date', '-clock_in_time']
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.date}"
    
    def save(self, *args, **kwargs):
        if self.clock_in_time and self.clock_out_time:
            # 勤務時間計算
            clock_in = datetime.combine(self.date, self.clock_in_time)
            clock_out = datetime.combine(self.date, self.clock_out_time)
            
            if clock_out < clock_in:
                clock_out += timedelta(days=1)
            
            total_hours = (clock_out - clock_in).total_seconds() / 3600
            
            # 休憩時間控除（1時間）
            if total_hours > 6:
                total_hours -= 1
            
            self.working_hours = round(total_hours, 2)
            
            # 残業時間計算
            standard_hours = settings.STANDARD_WORK_HOURS
            if self.working_hours > standard_hours:
                self.overtime_hours = round(self.working_hours - standard_hours, 2)
            else:
                self.overtime_hours = 0
            
            # 遅刻判定
            work_start = datetime.strptime(settings.WORK_START_TIME, '%H:%M').time()
            if self.clock_in_time > work_start:
                self.late_flag = True
        
        super().save(*args, **kwargs)