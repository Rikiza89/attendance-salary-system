from django.conf import settings
from employees.models import Employee
from attendance.models import Attendance
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)

def check_nfc_available():
    """NFCデバイスが利用可能かチェック"""
    if not settings.NFC_ENABLED:
        return False
    
    try:
        import nfc
        clf = nfc.ContactlessFrontend('usb')
        clf.close()
        return True
    except Exception as e:
        logger.debug(f"NFC not available: {e}")
        return False

def nfc_auto_clock(timeout=5):
    """NFC自動打刻（タイムアウト付き）"""
    try:
        import nfc
        import time
        
        clf = nfc.ContactlessFrontend('usb')
        
        result = {'success': False, 'message': 'カードを検出できませんでした'}
        start_time = time.time()
        
        def on_connect(tag):
            uid = tag.identifier.hex()
            logger.info(f"Card detected: {uid}")
            
            try:
                employee = Employee.objects.get(nfc_id=uid, status='active')
            except Employee.DoesNotExist:
                result['success'] = False
                result['message'] = f"登録されていないカードです: {uid}"
                return False
            
            today = timezone.now().date()
            now_time = timezone.now().time()
            
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={'source': 'nfc'}
            )
            
            if not attendance.clock_in_time:
                attendance.clock_in_time = now_time
                attendance.save()
                result['success'] = True
                result['message'] = f"{employee.name}さん、おはようございます"
                result['employee'] = employee.name
                result['action'] = 'clock_in'
                result['time'] = now_time.strftime('%H:%M')
            elif not attendance.clock_out_time:
                attendance.clock_out_time = now_time
                attendance.save()
                result['success'] = True
                result['message'] = f"{employee.name}さん、お疲れ様でした"
                result['employee'] = employee.name
                result['action'] = 'clock_out'
                result['time'] = now_time.strftime('%H:%M')
            else:
                result['success'] = False
                result['message'] = f"{employee.name}さん、本日の打刻は完了しています"
                result['employee'] = employee.name
                result['action'] = 'completed'
            
            return False
        
        # タイムアウト付きで待機
        clf.connect(rdwr={
            'on-connect': on_connect,
        }, terminate=lambda: time.time() - start_time > timeout)
        
        clf.close()
        return result
        
    except ImportError:
        return {'success': False, 'message': 'nfcpyがインストールされていません'}
    except Exception as e:
        logger.error(f"NFC error: {e}")
        return {'success': False, 'message': f'NFCエラー: {str(e)}'}

def test_nfc_reader():
    """NFC接続テスト"""
    try:
        import nfc
        clf = nfc.ContactlessFrontend('usb')
        print("✓ PaSoRi検出成功")
        
        def on_connect(tag):
            print(f"カード検出: {tag}")
            print(f"UID: {tag.identifier.hex()}")
            return True
        
        print("カードをタッチしてください...")
        clf.connect(rdwr={'on-connect': on_connect, 'iterations': 1})
        clf.close()
        
    except Exception as e:
        print(f"✗ エラー: {e}")