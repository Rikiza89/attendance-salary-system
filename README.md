# 勤怠・給与管理システム

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Django製の包括的な勤怠・給与管理システム。日本の税制に完全対応し、NFC打刻機能も搭載。

## 📋 主な機能

### 勤怠管理
- ✅ 手動またはNFCリーダーによる出退勤打刻
- 📅 月次勤怠カレンダー表示
- ⏰ 自動残業時間計算
- 🏷️ 遅刻フラグ自動判定
- 📊 Excel/CSVエクスポート

### 年休管理
- 📝 年休申請・承認ワークフロー
- 👨‍💼 管理者による承認/却下機能
- 📈 残年休日数自動管理
- 🔔 申請ステータス通知

### 給与管理
- 💰 月次給与自動計算
- 🧾 日本の税制完全対応
  - 健康保険料
  - 厚生年金保険料
  - 雇用保険料
  - 所得税
  - 住民税
- 📄 給与明細書PDF/Excel出力
- ⚙️ 年度別税率設定機能

### ダッシュボード
- 📊 社員用ダッシュボード（今日の勤怠、月次統計）
- 🎛️ 管理者用ダッシュボード（部署別出勤率、残業ランキング）
- 📈 リアルタイム統計表示

## 🚀 クイックスタート

### 必要要件

- Python 3.11以上（３.１１．９はテスト済）
- PostgreSQL 14以上（sqlite3のみテスト済）
- NFCリーダー（NFC PaSoRi RC-S380テスト済）

### インストール

1. **リポジトリをクローン**
```bash
git clone https://github.com/Rikiza89/attendance-salary-system.git
cd attendance-salary-system
```

2. **仮想環境作成**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **依存パッケージインストール**
```bash
pip install -r requirements.txt
```

4. **環境変数設定**
```bash
cp .env.example .env
# .envファイルを編集してDB接続情報を設定
```

5. **データベース作成**
```sql
CREATE DATABASE attendance_salary;
CREATE USER attendance_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_salary TO attendance_user;
```

6. **マイグレーション実行**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **スーパーユーザー作成**
```bash
python manage.py createsuperuser
```

8. **サンプルデータ投入（オプション）**
```bash
python manage.py seed_data
```

9. **開発サーバー起動**
```bash
python manage.py runserver

#またはホストを設定し（例：123.123.123.123 - port:12345）
#この場合は自分が設定したホストもsettings.pyに追加　⇒ ALLOWED_HOSTS = ['localhost', '127.0.0.1','123.123.123.123']
python manage.py runserver 123.123.123.123：12345
```

アクセス: `http://localhost:8000` または `http://123.123.123.123：12345`

## 📱 使い方

### ログイン
- 社員番号とパスワードでログイン
- サンプルユーザー（seed_data実行時）：
  - 社員番号: `EMP001` / パスワード: `pass001` （管理者）
  - 社員番号: `EMP002` / パスワード: `pass002`
  - 社員番号: `EMP003` / パスワード: `pass003`

### 出退勤打刻
1. ダッシュボードから「出勤打刻」ボタンをクリック
2. 退勤時は「退勤打刻」ボタンをクリック
3. NFC有効時はカードをタッチするだけで自動打刻

### 年休申請
1. メニューから「年休申請」を選択
2. 期間と理由を入力して申請
3. 管理者が承認/却下を実施

### 給与計算
```bash
# 前月分の給与を自動計算
python manage.py generate_payroll

# 特定月を指定
python manage.py generate_payroll --month=2025-01
```

### 月次処理（Cron設定例）
```bash
# 毎月1日午前0時に実行
0 0 1 * * /path/to/venv/bin/python /path/to/manage.py generate_payroll
```

## 🔧 NFC設定（オプション）

### Linux
```bash
# libusb-1.0インストール
sudo apt-get install libusb-1.0-0-dev

# udevルール設定
sudo sh -c 'echo SUBSYSTEM==\"usb\", ACTION==\"add\", ATTRS{idVendor}==\"054c\", ATTRS{idProduct}==\"06c3\", MODE=\"0666\" > /etc/udev/rules.d/99-pasori.rules'
sudo udevadm control --reload-rules

# ユーザー権限設定
sudo usermod -a -G dialout $USER
```

### macOS
追加設定不要。nfcpyが自動的にデバイスを検出します。

### NFC有効化
`.env`ファイルに追加：
```
NFC_ENABLED=True
```

### NFCテスト
このメソッドを使用して従業員NFCリーダー用のUIDを取得・登録。

```bash
python manage.py shell
>>> from core.nfc_reader import test_nfc_reader
>>> test_nfc_reader()
```

## ⚙️ 税金設定

管理画面（`/admin/`）から年度別の税率を設定可能：

- 健康保険料率（デフォルト: 9.96%）
- 厚生年金保険料率（デフォルト: 18.3%）
- 雇用保険料率（デフォルト: 0.6%）
- 所得税率（デフォルト: 7.14%）
- 住民税率（デフォルト: 10%）

## 📁 プロジェクト構成

```
attendance_salary/
├── core/               # 共通機能（NFC、ユーティリティ）
├── employees/          # 社員管理
├── attendance/         # 勤怠管理
├── leave/              # 年休管理
├── payroll/            # 給与管理
├── templates/          # HTMLテンプレート
├── static/             # 静的ファイル
└── manage.py
```

## 🛠️ 技術スタック

- **バックエンド**: Django 5.0
- **データベース**: PostgreSQL
- **フロントエンド**: Bootstrap 5 + Bootstrap Icons
- **NFC**: nfcpy
- **Excel出力**: openpyxl
- **データ処理**: pandas

## 📊 データベースモデル

### Employee（社員）
社員マスタ情報、基本給、時給、NFC ID

### Attendance（勤怠）
日次出退勤記録、勤務時間、残業時間

### LeaveRequest（年休申請）
年休申請、承認ステータス、承認者

### Payroll（給与）
月次給与、支給額、控除額、税金

### TaxConfig（税金設定）
年度別税率設定

## 🔒 セキュリティ

- CSRF保護有効
- パスワードハッシュ化
- 認証必須ページ保護
- ロールベースアクセス制御（社員/管理者）

## 🐛 トラブルシューティング

### NFC読み取りエラー
```bash
# デバイス権限確認
ls -l /dev/bus/usb/

# ユーザーをdialoutグループに追加
sudo usermod -a -G dialout $USER
```

### PostgreSQL接続エラー
- `pg_hba.conf`の認証方法を確認
- `settings.py`のDATABASES設定を確認
- PostgreSQLサービスが起動しているか確認

### 静的ファイルが表示されない
```bash
python manage.py collectstatic
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 👥 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📞 サポート

問題が発生した場合は、[Issues](https://github.com/Rikiza89/attendance-salary-system/issues)を開いてください。

## 🎯 今後の予定

- [ ] メール通知機能
- [ ] モバイルアプリ対応
- [ ] レポート機能強化
- [ ] API提供
- [ ] 多言語対応

---

**開発者**: Rikiza89  
**バージョン**: 1.0.0  

**最終更新**: 2025年10月

