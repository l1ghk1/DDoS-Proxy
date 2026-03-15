from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class AttackRequest(BaseModel):
    target: str
    attack_type: str
    duration: int = 300
    intensity: int = 1000

class AttackResponse(BaseModel):
    attack_id: str
    status: str

class AttackStatus(BaseModel):
    attack_id: str
    type: str
    target: str
    start_time: float
    duration: int
    intensity: int
    status: str

class Proxy(BaseModel):
    ip: str
    port: int
    country: str = ""
    protocol: str = "http"
    anonymity: str = ""
    last_checked: float = 0.0
    active: bool = True
    fail_count: int = 0
    response_time: float = 0.0
    last_used: float = 0.0

class Stats(BaseModel):
    active_attacks: int
    proxies: Dict