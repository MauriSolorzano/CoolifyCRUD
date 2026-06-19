import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "db_app1"),
        "user": os.getenv("DB_USER", "db_app1"),
        "password": os.getenv("DB_PASSWORD", "therian_app1"),
        "cursor_factory": RealDictCursor,
    }


@contextmanager
def get_connection() -> Iterator[psycopg2.extensions.connection]:
    conn = psycopg2.connect(**get_db_config())
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()


def seed_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM notes;")
            count = cur.fetchone()["count"]
            if count == 0:
                cur.execute(
                    """
                    INSERT INTO notes (title, content, status)
                    VALUES
                        (%s, %s, %s),
                        (%s, %s, %s);
                    """,
                    (
                        "Primera nota",
                        "Dato inicial creado automáticamente por la app.",
                        "pending",
                        "Prueba Coolify",
                        "Esta nota valida el flujo GitHub → Coolify → Docker → PostgreSQL.",
                        "done",
                    ),
                )
                conn.commit()


def list_notes() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content, status, created_at, updated_at
                FROM notes
                ORDER BY id DESC;
                """
            )
            return cur.fetchall()


def get_note(note_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content, status, created_at, updated_at
                FROM notes
                WHERE id = %s;
                """,
                (note_id,),
            )
            return cur.fetchone()


def create_note(title: str, content: str | None, status: str) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notes (title, content, status)
                VALUES (%s, %s, %s)
                RETURNING id, title, content, status, created_at, updated_at;
                """,
                (title, content, status),
            )
            row = cur.fetchone()
            conn.commit()
            return row


def update_note(note_id: int, title: str, content: str | None, status: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE notes
                SET title = %s,
                    content = %s,
                    status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, title, content, status, created_at, updated_at;
                """,
                (title, content, status, note_id),
            )
            row = cur.fetchone()
            conn.commit()
            return row


def delete_note(note_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted
