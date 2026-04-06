from flask import render_template, request, session, redirect, url_for
from config import PHASE1_ANSWERS


def register_routes(app):

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
    @app.route("/phase1/unlocked")
    def phase1_unlocked():
        if not session.get("phase1_unlocked"):
            return redirect(url_for("phase1_quiz"))
        return render_template("phase1_unlocked.html")

    # --- Ruta oculta: simula un servicio expuesto (la "flag" de reconocimiento) ---
    # El atacante debe descubrirla con herramientas de enumeración,
    # pero en Fase 1 solo necesita saber que existe algo más.
    @app.route("/s3cr3t-status")
    def secret_status():
        return "FLAG{reconocimiento_completado_2025}", 200, {"Content-Type": "text/plain"}
