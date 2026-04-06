from routes import register_routes
from flask import Flask
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Registrar rutas desde archivo separado
register_routes(app)

if __name__ == "__main__":
    # Escuchar en todas las interfaces para que Kali pueda acceder
    app.run(host="0.0.0.0", port=5000, debug=False)
