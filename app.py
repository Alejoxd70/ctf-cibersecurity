from routes import register_routes
from flask import Flask
from config import SECRET_KEY
from database import init_db

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Inicializar base de datos SQLite con usuarios y tabla CTF
init_db()

# Registrar rutas desde archivo separado
register_routes(app)

if __name__ == "__main__":
    # Escuchar en todas las interfaces para que Kali pueda acceder
    app.run(host="0.0.0.0", port=5000, debug=False)
