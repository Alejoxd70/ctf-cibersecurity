from flask import render_template, request, session, redirect, url_for, make_response
from config import PHASE1_ANSWERS, PHASE1_FLAG


def register_routes(app):

    # --- Header personalizado en TODAS las respuestas (pista para recon) ---
    @app.after_request
    def add_recon_headers(response):
        response.headers["X-Backend-Server"] = "StarkTower-JARVIS-Internal"
        response.headers["X-Powered-By"] = "JARVIS/Flask"
        return response

    # --- robots.txt: pista clásica de reconocimiento ---
    @app.route("/robots.txt")
    def robots():
        content = "User-agent: *\nDisallow: /jarvis-status\nDisallow: /stark-admin\nDisallow: /arc-reactor-backup\n"
        return content, 200, {"Content-Type": "text/plain"}

    @app.route("/")
    def index():
        return render_template("index.html")

    # --- FASE 1: Quiz ---
    @app.route("/phase1", methods=["GET", "POST"])
    def phase1_quiz():
        error = None

        if request.method == "POST":
            # Obtener respuestas del formulario y normalizar
            q1 = request.form.get("q1", "").strip().lower()
            q2 = request.form.get("q2", "").strip().lower()
            q3 = request.form.get("q3", "").strip().lower()

            # Validar las 3 respuestas
            if (q1 == PHASE1_ANSWERS["q1"] and
                q2 == PHASE1_ANSWERS["q2"] and
                    q3 == PHASE1_ANSWERS["q3"]):
                # Marcar fase 1 como desbloqueada en la sesión
                session["phase1_unlocked"] = True
                return redirect(url_for("phase1_unlocked"))
            else:
                error = "Una o más respuestas son incorrectas. Investiga y vuelve a intentar."

        return render_template("phase1_quiz.html", error=error)

    # --- FASE 1: Contenido desbloqueado ---
    @app.route("/phase1/unlocked", methods=["GET", "POST"])
    def phase1_unlocked():
        if not session.get("phase1_unlocked"):
            return redirect(url_for("phase1_quiz"))

        flag_error = None
        flag_success = False

        if request.method == "POST":
            submitted = request.form.get("flag", "").strip()
            if submitted == PHASE1_FLAG:
                flag_success = True
                session["phase1_flag_found"] = True
            else:
                flag_error = "Flag incorrecta. Sigue escaneando la Torre con tus herramientas."

        return render_template("phase1_unlocked.html",
                               flag_error=flag_error,
                               flag_success=flag_success)

    # --- Ruta oculta: simula un servicio expuesto (la "flag" de reconocimiento) ---
    # El atacante debe descubrirla con herramientas de enumeración,
    # pero en Fase 1 solo necesita saber que existe algo más.
    @app.route("/jarvis-status")
    def secret_status():
        return "FLAG{stark_tower_recon_2025}", 200, {"Content-Type": "text/plain"}

    # --- Ruta señuelo: aparece en robots.txt pero no existe ---
    @app.route("/stark-admin")
    def admin_panel():
        return "403 Forbidden - Acceso denegado", 403, {"Content-Type": "text/plain"}
