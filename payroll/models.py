from django.db import models
from employees.models import Employee
from decimal import Decimal

class TaxConfig(models.Model):
    """税金設定"""
    year = models.IntegerField('適用年度', unique=True)
    health_insurance_rate = models.DecimalField('健康保険料率', max_digits=5, decimal_places=4, default=0.0996)
    pension_insurance_rate = models.DecimalField('厚生年金保険料率', max_digits=5, decimal_places=4, default=0.183)
    employment_insurance_rate = models.DecimalField('雇用保険料率', max_digits=5, decimal_places=4, default=0.006)
    income_tax_rate = models.DecimalField('所得税率', max_digits=5, decimal_places=4, default=0.0714)
    residence_tax_rate = models.DecimalField('住民税率', max_digits=5, decimal_places=4, default=0.10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '税金設定'
        verbose_name_plural = '税金設定'
    
    def __str__(self):
        return f"{self.year}年度 税金設定"

class Payroll(models.Model):
    STATUS_CHOICES = [
        ('calculated', '計算済'),
        ('paid', '支払済'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='社員')
    month = models.CharField('対象月', max_length=7)
    base_salary = models.DecimalField('基本給', max_digits=10, decimal_places=2)
    overtime_pay = models.DecimalField('残業代', max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField('賞与', max_digits=10, decimal_places=2, default=0)
    
    # 控除項目
    health_insurance = models.DecimalField('健康保険料', max_digits=10, decimal_places=2, default=0)
    pension_insurance = models.DecimalField('厚生年金保険料', max_digits=10, decimal_places=2, default=0)
    employment_insurance = models.DecimalField('雇用保険料', max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField('所得税', max_digits=10, decimal_places=2, default=0)
    residence_tax = models.DecimalField('住民税', max_digits=10, decimal_places=2, default=0)
    other_deduction = models.DecimalField('その他控除', max_digits=10, decimal_places=2, default=0)
    
    total_deduction = models.DecimalField('控除合計', max_digits=10, decimal_places=2, default=0)
    total_salary = models.DecimalField('支給額', max_digits=10, decimal_places=2)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='calculated')
    paid_at = models.DateTimeField('支払日時', null=True, blank=True)
    remarks = models.TextField('備考', blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        verbose_name = '給与'
        verbose_name_plural = '給与'
        ordering = ['-month']
        unique_together = ['employee', 'month']
    
    def __str__(self):
        return f"{self.employee.name} - {self.month}"
    
    def calculate_deductions(self):
        """控除額を計算"""
        year = int(self.month.split('-')[0])
        try:
            tax_config = TaxConfig.objects.get(year=year)
        except TaxConfig.DoesNotExist:
            tax_config = TaxConfig.objects.create(year=year)
        
        gross_salary = self.base_salary + self.overtime_pay
        
        # 社会保険料計算
        self.health_insurance = (gross_salary * tax_config.health_insurance_rate / 2).quantize(Decimal('0.01'))
        self.pension_insurance = (gross_salary * tax_config.pension_insurance_rate / 2).quantize(Decimal('0.01'))
        self.employment_insurance = (gross_salary * tax_config.employment_insurance_rate).quantize(Decimal('0.01'))
        
        # 課税対象額
        taxable_income = gross_salary - self.health_insurance - self.pension_insurance - self.employment_insurance
        
        # 所得税（簡易計算）
        self.income_tax = (taxable_income * tax_config.income_tax_rate).quantize(Decimal('0.01'))
        
        # 住民税（前年所得ベース、ここでは簡易的に10%）
        self.residence_tax = (gross_salary * tax_config.residence_tax_rate / 12).quantize(Decimal('0.01'))
        
        # 控除合計
        self.total_deduction = (
            self.health_insurance + 
            self.pension_insurance + 
            self.employment_insurance + 
            self.income_tax + 
            self.residence_tax +
            self.other_deduction
        )
        
        # 差引支給額
        self.total_salary = self.base_salary + self.overtime_pay + self.bonus - self.total_deduction