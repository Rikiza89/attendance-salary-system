import sys
import requests
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QPushButton, QLabel, QButtonGroup)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
import nfc

# Django API設定
API_BASE_URL = "http://localhost:8000"
API_CLOCK_ENDPOINT = f"{API_BASE_URL}/api/nfc-clock/"

class NFCReaderThread(QThread):
    card_detected = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, pause_after_detection=3):
        super().__init__()
        self.running = True
        self.mode = 'clock_in'
        self.pause_after_detection = pause_after_detection  # seconds
    
    def run(self):
        """無限ループでNFCカード読み取り"""
        while self.running:
            try:
                clf = nfc.ContactlessFrontend('usb')

                def on_connect(tag):
                    uid = tag.identifier.hex()
                    self.card_detected.emit(uid)
                    # Pause loop to avoid multiple detections
                    time.sleep(self.pause_after_detection)
                    return False  # 一度読み取ったら終了
                
                clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: not self.running)
                clf.close()
                
            except Exception as e:
                self.error_occurred.emit(f"NFCエラー: {str(e)}")
                time.sleep(2)
    
    def stop(self):
        self.running = False

class NFCKioskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.nfc_thread = None
        self.current_mode = 'clock_in'
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('NFC打刻端末')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # タイトル
        title = QLabel('勤怠管理システム')
        title.setFont(QFont('メイリオ', 32, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # ステータス表示
        self.status_label = QLabel('モードを選択してください')
        self.status_label.setFont(QFont('メイリオ', 20))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "padding: 30px; background-color: #f0f0f0; border-radius: 10px;"
        )
        layout.addWidget(self.status_label)
        
        # メッセージ表示
        self.message_label = QLabel('')
        self.message_label.setFont(QFont('メイリオ', 16))
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("padding: 20px; min-height: 100px;")
        layout.addWidget(self.message_label)
        
        # モード選択ボタン
        self.clock_in_btn = QPushButton('出勤モード')
        self.clock_out_btn = QPushButton('退勤モード')
        
        for btn, color, hover, checked in [
            (self.clock_in_btn, '#28a745', '#218838', '#1e7e34'),
            (self.clock_out_btn, '#dc3545', '#c82333', '#bd2130')
        ]:
            btn.setFont(QFont('メイリオ', 24, QFont.Bold))
            btn.setMinimumHeight(120)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: {hover};
                }}
                QPushButton:checked {{
                    background-color: {checked};
                    border: 5px solid black;
                }}
            """)
        
        self.clock_in_btn.clicked.connect(lambda: self.set_mode('clock_in'))
        self.clock_out_btn.clicked.connect(lambda: self.set_mode('clock_out'))
        
        # ボタングループ
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.clock_in_btn)
        self.button_group.addButton(self.clock_out_btn)
        
        layout.addWidget(self.clock_in_btn)
        layout.addWidget(self.clock_out_btn)
    
    def set_mode(self, mode):
        self.current_mode = mode
        # Stop previous thread
        if self.nfc_thread and self.nfc_thread.isRunning():
            self.nfc_thread.stop()
            self.nfc_thread.wait()
        # Start new thread
        self.nfc_thread = NFCReaderThread(pause_after_detection=3)
        self.nfc_thread.mode = mode
        self.nfc_thread.card_detected.connect(self.handle_card)
        self.nfc_thread.error_occurred.connect(self.handle_error)
        self.nfc_thread.start()
        
        mode_text = '出勤' if mode == 'clock_in' else '退勤'
        self.status_label.setText(f'{mode_text}モード: カードをタッチしてください')
        self.status_label.setStyleSheet(
            f"padding: 30px; background-color: {'#d4edda' if mode=='clock_in' else '#f8d7da'}; "
            f"border-radius: 10px; color: {'#155724' if mode=='clock_in' else '#721c24'};"
        )
        self.message_label.setText('')
    
    def handle_card(self, uid):
        self.message_label.setText(f'カード検出中...\nUID: {uid}')
        QApplication.processEvents()
        try:
            response = requests.post(
                API_CLOCK_ENDPOINT,
                json={'uid': uid, 'action': self.current_mode},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.show_success(data.get('message', '打刻完了'))
                else:
                    self.show_error(data.get('message', '打刻失敗'))
            else:
                self.show_error(f'サーバーエラー: {response.status_code}')
        except Exception as e:
            self.show_error(f'エラー: {str(e)}')
    
    def handle_error(self, error_msg):
        self.show_error(error_msg)
    
    def show_success(self, message):
        self.message_label.setText(f'✓ {message}')
        self.message_label.setStyleSheet(
            "padding: 20px; min-height: 100px; background-color: #d4edda; "
            "color: #155724; border-radius: 10px; font-weight: bold;"
        )
        QApplication.processEvents()
        time.sleep(3)
        self.message_label.setText('')
        self.message_label.setStyleSheet("padding: 20px; min-height: 100px;")
    
    def show_error(self, message):
        self.message_label.setText(f'✗ {message}')
        self.message_label.setStyleSheet(
            "padding: 20px; min-height: 100px; background-color: #f8d7da; "
            "color: #721c24; border-radius: 10px; font-weight: bold;"
        )
    
    def closeEvent(self, event):
        if self.nfc_thread:
            self.nfc_thread.stop()
            self.nfc_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NFCKioskApp()
    window.show()
    sys.exit(app.exec())
