class Config:
    API_PREFIX = "/api/v1"
    PROXY_DIR = "prox"
    PROXY_FILES = ["proxies.txt"]
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
    WORKERS = 4
    MAX_CONCURRENT_REQUESTS = 100000
    PROXY_ROTATION_INTERVAL = 50
    ATTACK_TIMEOUT = 30
    PROXY_CHECK_URL = "http://httpbin.org/ip"