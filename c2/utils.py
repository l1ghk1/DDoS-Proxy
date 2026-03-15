import random
import time
import os
from typing import List, Dict, Optional
from urllib.parse import urlparse

def parse_target(target: str) -> tuple:
    try:
        if target.startswith(('http://', 'https://')):
            parsed = urlparse(target)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            return target, host, port
        elif target.startswith('//'):
            full_url = 'http:' + target
            parsed = urlparse(full_url)
            host = parsed.hostname
            port = parsed.port or 80
            return full_url, host, port
        elif ':' in target:
            ip, port = target.split(':')
            port = int(port)
            return f"http://{target}", ip, port
        else:
            return f"http://{target}", target, 80
    except Exception as e:
        raise Exception(f"Invalid target format: {e}")

def validate_target(target: str) -> bool:
    try:
        parsed = urlparse(target)
        if parsed.scheme not in ['http', 'https']:
            return False
        if not parsed.hostname:
            return False
        return True
    except:
        return False

def read_proxy_files(proxy_dir: str, proxy_files: List[str]) -> List[str]:
    proxies = []
    for filename in proxy_files:
        filepath = os.path.join(proxy_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
    return proxies