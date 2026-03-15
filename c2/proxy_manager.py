import random
import time
import sqlite3
import threading
import os
from typing import List, Optional, Dict, Tuple
from fastapi import HTTPException, status
from models import Proxy
from utils import read_proxy_files

class ProxyManager:
    def __init__(self, proxy_dir: str, proxy_files: List[str]):
        self.proxy_dir = proxy_dir
        self.proxy_files = proxy_files
        self.proxies: List[Proxy] = []
        self.lock = threading.Lock()
        self.rotation_counter = 0
        self.last_update = 0
        self.db_path = 'proxy_manager.db'
        self._init_db()
        self._load_proxies()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS proxies
                         (ip TEXT, port INTEGER, country TEXT, protocol TEXT, 
                          anonymity TEXT, last_checked REAL, active INTEGER, 
                          fail_count INTEGER, response_time REAL, last_used REAL,
                          PRIMARY KEY (ip, port))''')
        conn.commit()
        conn.close()
    
    def _load_proxies(self):
        proxy_list = read_proxy_files(self.proxy_dir, self.proxy_files)
        
        with self.lock:
            self.proxies = []
            for proxy_str in proxy_list:
                try:
                    ip, port = proxy_str.split(':')
                    port = int(port)
                    proxy = Proxy(ip=ip, port=port, protocol="http")
                    self.proxies.append(proxy)
                except:
                    continue
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT ip, port, country, protocol, anonymity, last_checked, active, fail_count, response_time, last_used FROM proxies")
            for row in cursor.fetchall():
                proxy = Proxy(*row)
                proxy.protocol = "http"  
                self.proxies.append(proxy)
            conn.close()
    
    def get_proxy(self) -> Optional[Proxy]:
        with self.lock:
            if not self.proxies:
                return None
            
            self.rotation_counter += 1
            if self.rotation_counter >= 50:
                self.rotation_counter = 0
                random.shuffle(self.proxies)
            
            proxy = min(self.proxies, key=lambda p: p.response_time if p.response_time > 0 else float('inf'))
            proxy.last_used = time.time()
            return proxy
    
    def mark_failed(self, proxy: Proxy):
        with self.lock:
            for p in self.proxies:
                if p.ip == proxy.ip and p.port == proxy.port:
                    p.fail_count += 1
                    if p.fail_count >= 3:
                        p.active = False
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE proxies SET active=0 WHERE ip=? AND port=?", (p.ip, p.port))
                        conn.commit()
                        conn.close()
                    break
    
    def update_proxy_stats(self, proxy: Proxy, response_time: float, active: bool):
        with self.lock:
            proxy.last_checked = time.time()
            proxy.response_time = response_time
            proxy.active = active
            proxy.protocol = "http"  
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO proxies 
                             (ip, port, country, protocol, anonymity, 
                              last_checked, active, fail_count, response_time, last_used)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (proxy.ip, proxy.port, proxy.country, proxy.protocol,
                          proxy.anonymity, proxy.last_checked, proxy.active,
                          proxy.fail_count, proxy.response_time, proxy.last_used))
            conn.commit()
            conn.close()
    
    def get_stats(self) -> Dict:
        with self.lock:
            total = len(self.proxies)
            active = sum(1 for p in self.proxies if p.active)
            countries = list(set(p.country for p in self.proxies if p.active))
            
            if active > 0:
                avg_response = sum(p.response_time for p in self.proxies if p.active) / active
            else:
                avg_response = 0
            
            return {
                "total_proxies": total,
                "active_proxies": active,
                "countries": countries,
                "avg_response_time": avg_response,
                "rotation_counter": self.rotation_counter
            }