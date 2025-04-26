# backup_db.py
import os
import shutil
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path
import schedule
import time

# Tải thông tin từ file .env
load_dotenv(dotenv_path=".env")

THU_MUC_NGUON = Path("./databases")
THU_MUC_BACKUP = Path("./backup")

EMAIL_GUI = os.getenv("EMAIL_GUI")
MAT_KHAU_GUI = os.getenv("MAT_KHAU_GUI")
EMAIL_NHAN = os.getenv("EMAIL_NHAN")

# Gửi thông báo qua email
def gui_email(tieu_de, noi_dung):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_GUI
    msg["To"] = EMAIL_NHAN
    msg["Subject"] = tieu_de
    msg.attach(MIMEText(noi_dung, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_GUI, MAT_KHAU_GUI)
            smtp.send_message(msg)
        print("\u2709\ufe0f Da gui email thong bao.")
    except Exception as loi:
        print("Khong the gui email:", loi)

# Thuc hien backup file database
def sao_luu_database():
    print("🔄 Dang kiem tra file de backup...")
    
    if not THU_MUC_BACKUP.exists():
        THU_MUC_BACKUP.mkdir(parents=True)

    dem = 0
    for tep in THU_MUC_NGUON.iterdir():
        if tep.suffix in [".sql", ".sqlite3"]:
            ten_moi = f"{tep.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{tep.suffix}"
            duong_dan_moi = THU_MUC_BACKUP / ten_moi
            try:
                shutil.copy2(tep, duong_dan_moi)
                dem += 1
            except Exception as loi_copy:
                gui_email("Backup that bai", f"Khong the sao luu {tep.name}: {loi_copy}")
                return

    if dem:
        gui_email("Backup thanh cong", f"Da sao luu {dem} file database vao '{THU_MUC_BACKUP.resolve()}'")
    else:
        gui_email("Khong co file database", "Khong tim thay file .sql hoac .sqlite3 trong thu muc databases.")

# Lich chay hang ngay luc 00:00
schedule.every().day.at("01:50").do(sao_luu_database)
print("\u231b He thong dang cho den 00:00 de tien hanh sao luu...")

try:
    while True:
        schedule.run_pending()
        time.sleep(60)
except KeyboardInterrupt:
    print("\u274c Da dung chuong trinh.")
