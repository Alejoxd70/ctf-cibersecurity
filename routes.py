import sqlite3
from flask import render_template, request, session, redirect, url_for, make_response
from config import PHASE1_ANSWERS, PHASE1_FLAG, PHASE2_ANSWERS, PHASE2_FLAG, DATABASE_PATH


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
        content = (
            "User-agent: *\n"
            "Disallow: /stark-admin\n"
            "Disallow: /arc-reactor-backup\n"
            "Disallow: /hexdump-lab\n"
            "Disallow: /exiftool-lab\n"
            "Disallow: /binwalk-lab\n"
            "Disallow: /stark-intel\n"
            "Disallow: /phase2\n"
            "Disallow: /phase2/login\n"
        )
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

    # --- Ruta señuelo: aparece en robots.txt pero no existe ---
    @app.route("/stark-admin")
    def admin_panel():
        return "403 Forbidden - Acceso denegado", 403, {"Content-Type": "text/plain"}

    # --- Rutas de laboratorio de herramientas forenses (descubiertas via robots.txt) ---
    @app.route("/hexdump-lab")
    def hexdump_lab():
        return render_template("tool_hexdump.html")

    @app.route("/exiftool-lab")
    def exiftool_lab():
        return render_template("tool_exiftool.html")

    @app.route("/binwalk-lab")
    def binwalk_lab():
        return render_template("tool_binwalk.html")

    # --- Repositorio de inteligencia Stark: contiene gem.jpg con metadatos de usuarios ---
    @app.route("/stark-intel")
    def stark_intel():
        return render_template("stark_intel.html")

    # =========================================================================
    # FASE 2: SQL INJECTION
    # =========================================================================

    # --- FASE 2: Quiz previo (requiere haber encontrado la flag de Fase 1) ---
    @app.route("/phase2", methods=["GET", "POST"])
    def phase2_quiz():
        if not session.get("phase1_flag_found"):
            return redirect(url_for("phase1_quiz"))

        error = None

        if request.method == "POST":
            q1 = request.form.get("q1", "").strip()
            q2 = request.form.get("q2", "").strip().lower()
            q3 = request.form.get("q3", "").strip()

            if (q1 == PHASE2_ANSWERS["q1"] and
                    q2 == PHASE2_ANSWERS["q2"] and
                    q3 == PHASE2_ANSWERS["q3"]):
                session["phase2_quiz_unlocked"] = True
                return redirect(url_for("phase2_login"))
            else:
                error = "Respuestas incorrectas. Los secretos de JARVIS no se revelan tan fácilmente."

        return render_template("phase2_quiz.html", error=error)

    # --- FASE 2: Login intencionalmente vulnerable a SQL Injection ---
    @app.route("/phase2/login", methods=["GET", "POST"])
    def phase2_login():
        if not session.get("phase2_quiz_unlocked"):
            return redirect(url_for("phase2_quiz"))

        error = None
        sql_error = None
        debug_query = None

        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")

            # VULNERABILIDAD INTENCIONAL: concatenación directa sin parametrización
            # Esto es exactamente lo que NO debes hacer en producción
            query = (
                f"SELECT * FROM users WHERE username = '{username}'"
                f" AND password = '{password}'"
            )
            debug_query = query  # Filtración de debug — error pedagógico clásico

            try:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute(query)   # Sin parámetros — VULNERABLE
                # fetchall: devuelve TODOS los registros (permite ver UNION completo)
                rows = cursor.fetchall()
                conn.close()

                if rows:
                    first = rows[0]
                    session["phase2_unlocked"] = True
                    session["logged_user"] = first[1]        # username
                    session["logged_role"] = first[3]        # role
                    session["logged_email"] = first[4]       # email
                    # description (distracción — no contiene flag)
                    session["logged_description"] = first[5]
                    # UNION detected → exponer todas las filas inyectadas (rows[1:] son las del UNION)
                    # Sin UNION → solo mostrar perfil del usuario autenticado
                    is_union = "union" in username.lower()
                    session["union_rows"] = [
                        list(r) for r in rows[1:]] if is_union else []
                    return redirect(url_for("phase2_success"))
                else:
                    error = "Acceso denegado. JARVIS no reconoce esas credenciales."
            except Exception as e:
                # Exposición deliberada del error SQL — revela estructura de la BD
                raw = str(e)
                sql_error = (
                    f"{raw}\n"
                    f"--- [StarkDB v2.1 · Debug Context] ---\n"
                    f"Interesante. SQLite guarda sus secretos en algún lugar... \n"
                    f"aunque dicen que hasta los sistemas más ordenados\n"
                    f"llevan un registro interno de todo lo que contienen.\n"
                    f"Qué pena que no sepas dónde buscarlo."
                )

        return render_template(
            "phase2_login.html",
            error=error,
            sql_error=sql_error,
            debug_query=debug_query,
        )

    # --- FASE 2: Panel desbloqueado tras explotación exitosa ---
    @app.route("/phase2/success", methods=["GET", "POST"])
    def phase2_success():
        if not session.get("phase2_unlocked"):
            return redirect(url_for("phase2_login"))

        flag_error = None
        flag_success = False

        if request.method == "POST":
            submitted = request.form.get("flag", "").strip()
            if submitted == PHASE2_FLAG:
                flag_success = True
                session["phase2_flag_found"] = True
            else:
                flag_error = "Flag incorrecta. El sistema sigue siendo más inteligente que tú... por ahora."

        return render_template(
            "phase2_success.html",
            logged_user=session.get("logged_user"),
            logged_role=session.get("logged_role"),
            logged_email=session.get("logged_email"),
            logged_description=session.get("logged_description"),
            union_rows=session.get("union_rows", []),
            flag_error=flag_error,
            flag_success=flag_success,
        )
