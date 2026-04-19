import os

# Clave secreta para sesiones Flask
SECRET_KEY = os.urandom(24)

# Estado de fases desbloqueadas (en memoria, se reinicia al reiniciar el server)
# En producción usarías una DB, aquí basta con la sesión.

# Respuestas correctas del quiz Fase 1 (lowercase para comparar)
PHASE1_ANSWERS = {
    "q1": "nmap -p",    # Descubrir puertos abiertos
    "q2": "nmap -ss",   # Escaneo sigiloso SYN scan
    "q3": "nmap -sv",   # Identificar servicios y versiones
}

# Flag de reconocimiento: oculta en header HTTP, visible con curl -v o nmap scripts
PHASE1_FLAG = "FLAG{stark_tower_recon_2025}"
