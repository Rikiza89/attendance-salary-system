from django.conf import settings
from employees.models import Employee
from attendance.models import Attendance
from django.utils import timezone

def nfc_clock_in_out():
    """NFC打刻処理"""
    if not settings.NFC_ENABLED:
        return "NFC機能が無効です"
    
    try:
        import nfc
        
        clf = nfc.ContactlessFrontend('usb')
        
        def on_connect(tag):
            uid = tag.identifier.hex()
            
            try:
                employee = Employee.objects.get(nfc_id=uid, status='active')
            except Employee.DoesNotExist:
                return f"登録されていないカードです: {uid}"
            
            today = timezone.now().date()
            now_time = timezone.now().time()
            
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={'source': 'nfc'}
            )
            
            if not attendance.clock_in_time:
                # 出勤打刻
                attendance.clock_in_time = now_time
                attendance.save()
                return f"{employee.name}さん、おはようございます（出勤: {now_time.strftime('%H:%M')}）"
            elif not attendance.clock_out_time:
                # 退勤打刻
                attendance.clock_out_time = now_time
                attendance.save()
                return f"{employee.name}さん、お疲れ様でした（退勤: {now_time.strftime('%H:%M')}）"
            else:
                return f"{employee.name}さん、本日の打刻は完了しています"
        
        clf.connect(rdwr={'on-connect': on_connect})
        
    except ImportError:
        return "nfcpyがインストールされていません"
    except Exception as e:
        return f"NFCエラー: {str(e)}"
    finally:
        try:
            clf.close()
        except:
            pass

def test_nfc_reader():
    """NFC接続テスト"""
    try:
        import nfc
        clf = nfc.ContactlessFrontend('usb')
        print("PaSoRi検出成功")
        
        def on_connect(tag):
            print(f"カード検出: {tag}")
            print(f"UID: {tag.identifier.hex()}")
            return True
        
        print("カードをタッチしてください...")
        clf.connect(rdwr={'on-connect': on_connect, 'iterations': 1})
        clf.close()
        
    except Exception as e:
        print(f"エラー: {e}")