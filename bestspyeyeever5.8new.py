import os
import cv2
import socket
import pyaudio
import wave
import logging
import time
import subprocess
from datetime import datetime
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs

# ============================
# إعداد السجل
# ============================
LOG_FILE = 'cyber_tool_ultimate_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ============================
# قائمة الأدوات
# ============================
TOOLS = {
    "sqlmap": "sqlmap -u {url} --batch",
    "nmap": "nmap -A {ip}",
    "nikto": "nikto -h {ip}",
    "xss": "xsser -u {url}",
    "command_injection": "python3 exploit_scripts/command_injection.py {url}",
    "akamai": "akamai-dns.py {url}",
    "intruder": "intruder_scan.py {url}",
    "acunetix": "acunetix_scan {url}",
    "nessus": "nessus_scan {ip}",
    "invicti": "invicti-cli scan -u {url}",
    "openvas": "gvm-cli scan -u {url}",
    "zap": "zap-cli -u {url} active-scan",
    "angry_ip_scanner": "angry-ip-scanner {ip}",
    "metasploit": "msfconsole -r metasploit_script.rc",
    "cobalt_strike": "cobaltstrike -connect {ip}",
    "empire": "empire-cli {ip}",
    "beef": "beef-cli {url}",
    "veil": "veil -p payload -o payload_output",
    "wannacry": "wannacry_emulation.py {ip}",
    "keylogger": "python3 keylogger_script.py {ip}",
    "adware": "adware_test.py {ip}",
    "trojan_horse": "trojan_emulator.py {ip}",
    "mitm": "ettercap -T -q -M arp:remote /{ip}// /{gateway_ip}//",
    "darkcomet": "darkcomet_server.py {ip}",
    "onvif": "onvif_device_manager.py {ip}",
    "vlc": "vlc {url}"
}

# ============================
# وظائف إضافية
# ============================

def detect_and_record_camera(target_ip):
    """التقاط فيديو وصوت من كاميرا مستهدفة"""
    try:
        print(f"Attempting to access camera at {target_ip}")
        cap = cv2.VideoCapture(0)  # محاكاة الكاميرا المحلية

        if not cap.isOpened():
            print(f"Unable to access camera at IP {target_ip}")
            return

        video_filename = f"video_{target_ip}.avi"
        audio_filename = f"audio_{target_ip}.wav"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
        audio_frames = []

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            video_out.write(frame)
            cv2.imshow(f"Video Stream - {target_ip}", frame)
            audio_frames.append(stream.read(1024))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        video_out.release()
        cv2.destroyAllWindows()

        with wave.open(audio_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))

        print(f"Video and audio saved for {target_ip}")
        logging.info(f"Saved video: {video_filename}, audio: {audio_filename}")

    except Exception as e:
        logging.error(f"Error with camera recording for {target_ip}: {e}")

def run_tool(tool_name, target, target_type="ip"):
    """
    تشغيل أداة محددة بناءً على اسمها والمعاملات.
    """
    try:
        if tool_name not in TOOLS:
            print(f"[ERROR] Tool {tool_name} is not defined.")
            return

        command = TOOLS[tool_name].format(ip=target, url=target)
        print(f"Running {tool_name} on {target}")
        logging.info(f"Running command: {command}")

        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.stdout.decode()
        error = process.stderr.decode()

        if process.returncode == 0:
            print(f"[SUCCESS] {tool_name} completed successfully.")
            logging.info(f"{tool_name} output:\n{output}")
        else:
            print(f"[ERROR] {tool_name} encountered an error.")
            logging.error(f"{tool_name} error:\n{error}")

    except Exception as e:
        logging.error(f"Exception while running {tool_name}: {e}")
        print(f"[ERROR] Exception occurred: {e}")

# ============================
# القائمة الرئيسية
# ============================

def main_menu():
    print("\nCyber Security Toolkit")
    print("=======================")
    print("1. Run a specific tool")
    print("2. Run all tools")
    print("3. Detect and record camera")
    print("4. Exit")
    choice = input("Select an option: ").strip()
    return choice

# ============================
# تشغيل البرنامج
# ============================

if __name__ == "__main__":
    while True:
        user_choice = main_menu()

        if user_choice == "1":
            print("\nAvailable tools:")
            for idx, tool in enumerate(TOOLS.keys(), start=1):
                print(f"{idx}. {tool}")
            tool_choice = int(input("Select a tool number: ").strip()) - 1

            target = input("Enter target IP/URL: ").strip()
            tool_name = list(TOOLS.keys())[tool_choice]
            run_tool(tool_name, target)

        elif user_choice == "2":
            target = input("Enter target IP/URL: ").strip()
            for tool_name in TOOLS.keys():
                run_tool(tool_name, target)

        elif user_choice == "3":
            target_ip = input("Enter camera IP: ").strip()
            detect_and_record_camera(target_ip)

        elif user_choice == "4":
            print("Exiting. Goodbye!")
            break

        else:
            print("[ERROR] Invalid choice. Please try again.")
