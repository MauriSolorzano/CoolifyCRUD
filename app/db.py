import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "10.5.0.122"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "db_app1"),
        "user": os.getenv("DB_USER", "db_app1"),
        "password": os.getenv("DB_PASSWORD", "therian_app1"),
    }


@contextmanager
def get_connection():
    conn = psycopg2.connect(**get_db_config(), cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()


def seed_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM notes;")
            total = cur.fetchone()["total"]
            if total == 0:
                cur.execute(
                    """
                    INSERT INTO notes (title, content)
                    VALUES
                    (%s, %s),
                    (%s, %s);
                    """,
                    (
                        "Primera nota",
                        "Dato inicial para probar PostgreSQL + Docker + Coolify",
                        "Segunda nota",
                        "Registro creado automáticamente por la app al iniciar",
                    ),
                )
                conn.commit()
