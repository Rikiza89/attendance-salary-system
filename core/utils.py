from django.utils import timezone

def get_current_month_str():
    """現在月をYYYY-MM形式で返す"""
    return timezone.now().strftime('%Y-%m')

def calculate_business_days(start_date, end_date):
    """営業日数計算（土日を除く）"""
    from datetime import timedelta
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 月-金
            days += 1
        current += timedelta(days=1)
    return days