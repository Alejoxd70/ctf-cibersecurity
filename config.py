import os

# Clave secreta para sesiones Flask
SECRET_KEY = os.urandom(24)

# Estado de fases desbloqueadas (en memoria, se reinicia al reiniciar el server)
# En producción usarías una DB, aquí basta con la sesión.

# Respuestas correctas del quiz Fase 1 (lowercase para comparar)
PHASE1_ANSWERS = {
    "q1": "nmap",        # ¿Herramienta estándar para escaneo de puertos?
    "q2": "22",           # ¿Puerto por defecto de SSH?
    "q3": "whatweb",      # ¿Herramienta para identificar tecnologías web?
}
