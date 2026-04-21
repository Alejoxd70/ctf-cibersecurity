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
PHASE1_FLAG = "FLAG{stark_tower_recon}"

# --- FASE 2: SQL Injection ---

# Respuestas correctas del quiz Fase 2
PHASE2_ANSWERS = {
    "q1": "'",       # Caracter para escapar strings en SQL
    "q2": "union",   # Cláusula para combinar múltiples SELECT
    "q3": "--",      # Comentario de línea en SQL
}

# Flag de SQL Injection: oculta en tabla arc_reactor_logs, campo data
# Extraíble via: ' UNION SELECT data,2,3,4,5,6 FROM arc_reactor_logs WHERE clearance='LEVEL-5-OMEGA' --
PHASE2_FLAG = "FLAG{union_select_arc_reactor_extracted}"

# Ruta al archivo de base de datos SQLite
DATABASE_PATH = "ctf_stark.db"
