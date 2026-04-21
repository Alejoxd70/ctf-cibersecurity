import sqlite3
from config import DATABASE_PATH


def init_db():
    """Initialize SQLite database with CTF tables and seed data."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # ------------------------------------------------------------------ #
    # Tabla pública: users (6 columnas — la que ataca el login)           #
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            email TEXT,
            description TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            (
                "tony_stark",
                "arc_reactor_9000",
                "admin",
                "tony@stark.com",
                # Distracción — NO contiene la flag real
                "CEO de Stark Industries. Clearance OMEGA. "
                "Registros clasificados del reactor almacenados en subsistema interno. "
                "[NOTA: este perfil no almacena activos de inteligencia en texto plano]",
            ),
            (
                "pepper_potts",
                "rescue_v2_pep",
                "user",
                "pepper@stark.com",
                "COO de Stark Industries. Acceso operativo limitado.",
            ),
            (
                "james_rhodes",
                "warmachine_mk7",
                "operator",
                "rhodey@military.gov",
                "Coronel James Rhodes. Acceso militar de nivel 5.",
            ),
            (
                "nick_fury",
                "shield_director_1",
                "admin",
                "fury@shield.gov",
                "Director de S.H.I.E.L.D. Nivel máximo de autorización.",
            ),
            (
                "jarvis_system",
                "J.A.R.V.I.S._core_v2",
                "system",
                "jarvis@internal.stark",
                "IA central de la Torre Stark. Acceso sistema restringido.",
            ),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, role, email, description) VALUES (?, ?, ?, ?, ?)",
            users,
        )
    else:
        # Asegurar que tony_stark nunca tenga la flag en description
        cursor.execute(
            "UPDATE users SET description = ? WHERE username = 'tony_stark'",
            (
                "CEO de Stark Industries. Clearance OMEGA. "
                "Registros clasificados del reactor almacenados en subsistema interno. "
                "[NOTA: este perfil no almacena activos de inteligencia en texto plano]",
            ),
        )

    # ------------------------------------------------------------------ #
    # Tabla oculta: arc_reactor_logs — contiene la flag real              #
    # Descubrible via: UNION SELECT name,2,3,4,5,6 FROM sqlite_master     #
    # Flag en: UNION SELECT data,2,3,4,5,6 FROM arc_reactor_logs          #
    # (6 columnas para hacer el UNION compatible con users)               #
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arc_reactor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id TEXT,
            classification TEXT,
            data TEXT,
            timestamp TEXT,
            clearance TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM arc_reactor_logs")
    if cursor.fetchone()[0] == 0:
        logs = [
            (
                "ARC-LOG-0001",
                "CONFIDENTIAL",
                "Prueba de estabilidad del reactor — nominal.",
                "2025-01-10 03:14:00",
                "LEVEL-3",
            ),
            (
                "ARC-LOG-0042",
                "SECRET",
                "Sobreexposición de paladio detectada en núcleo mk4. Resuelto.",
                "2025-03-22 11:05:33",
                "LEVEL-4",
            ),
            (
                "ARC-LOG-0099",
                "TOP SECRET",
                # ← FLAG REAL
                "FLAG{union_select_arc_reactor_extracted}",
                "2025-09-01 00:00:01",
                "LEVEL-5-OMEGA",
            ),
            (
                "ARC-LOG-0100",
                "TOP SECRET",
                "Acceso root al subsistema JARVIS confirmado. Protocolo Ultron activado.",
                "2025-09-01 00:01:42",
                "LEVEL-5-OMEGA",
            ),
        ]
        cursor.executemany(
            "INSERT INTO arc_reactor_logs (log_id, classification, data, timestamp, clearance)"
            " VALUES (?, ?, ?, ?, ?)",
            logs,
        )

    # ------------------------------------------------------------------ #
    # Tabla oculta: stark_wordlist — lista de contraseñas para Hydra       #
    # Descubrible via sqlite_master, útil para ataques de fuerza bruta    #
    # (6 columnas para mantener compatibilidad con UNION SELECT)          #
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stark_wordlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            source TEXT,
            verified TEXT,
            notes TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM stark_wordlist")
    if cursor.fetchone()[0] == 0:
        wordlist = [
            ("tony_stark",    "arc_reactor_9000",  "StarkDB-dump",
             "YES", "Credencial admin confirmada"),
            ("pepper_potts",  "rescue_v2_pep",      "StarkDB-dump",
             "YES", "Credencial COO confirmada"),
            ("james_rhodes",  "warmachine_mk7",     "StarkDB-dump",
             "YES", "Credencial militar confirmada"),
            ("nick_fury",     "shield_director_1",  "StarkDB-dump",
             "YES", "Credencial SHIELD confirmada"),
            ("jarvis_system", "J.A.R.V.I.S._core_v2", "StarkDB-dump",
             "YES", "Credencial sistema confirmada"),
            ("admin",         "admin",               "common",
             "NO",  "Contraseña trivial"),
            ("admin",         "password",
             "common",          "NO",  "Contraseña trivial"),
            ("admin",         "123456",              "common",
             "NO",  "Contraseña trivial"),
            ("tony",          "ironman",
             "wordlist-marvel", "NO",  "Contraseña temática"),
            ("tony",          "pepper",
             "wordlist-marvel", "NO",  "Contraseña temática"),
            ("stark",         "jarvis",
             "wordlist-marvel", "NO",  "Contraseña temática"),
            ("fury",          "shield",
             "wordlist-marvel", "NO",  "Contraseña temática"),
            ("root",          "toor",                "common",
             "NO",  "Contraseña trivial"),
            ("root",          "root",                "common",
             "NO",  "Contraseña trivial"),
        ]
        cursor.executemany(
            "INSERT INTO stark_wordlist (username, password, source, verified, notes)"
            " VALUES (?, ?, ?, ?, ?)",
            wordlist,
        )

    conn.commit()
    conn.close()
