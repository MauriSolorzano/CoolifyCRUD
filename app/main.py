from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.db import get_connection, init_db, seed_db

app = FastAPI(
    title="Coolify CRUD Demo",
    description="App de prueba con CRUD básico para validar GitHub → Coolify → Docker → PostgreSQL nativo.",
    version="1.0.0",
)


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = None


@app.on_event("startup")
def startup():
    init_db()
    seed_db()


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": "Coolify CRUD Demo",
        "message": "App corriendo en Docker y conectada a PostgreSQL nativo",
        "docs": "/docs",
    }


@app.get("/db-check")
def db_check():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user, now();")
                result = cur.fetchone()
        return {"status": "ok", "database": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/notes")
def list_notes():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, title, content, created_at, updated_at
                    FROM notes
                    ORDER BY id;
                    """
                )
                rows = cur.fetchall()
        return {"status": "ok", "count": len(rows), "notes": rows}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, title, content, created_at, updated_at
                    FROM notes
                    WHERE id = %s;
                    """,
                    (note_id,),
                )
                row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"status": "ok", "note": row}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO notes (title, content)
                    VALUES (%s, %s)
                    RETURNING id, title, content, created_at, updated_at;
                    """,
                    (note.title, note.content),
                )
                row = cur.fetchone()
                conn.commit()
        return {"status": "created", "note": row}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteUpdate):
    if note.title is None and note.content is None:
        raise HTTPException(status_code=400, detail="Nothing to update")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE notes
                    SET
                        title = COALESCE(%s, title),
                        content = COALESCE(%s, content),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id, title, content, created_at, updated_at;
                    """,
                    (note.title, note.content, note_id),
                )
                row = cur.fetchone()
                conn.commit()
        if not row:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"status": "updated", "note": row}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM notes
                    WHERE id = %s
                    RETURNING id, title, content, created_at, updated_at;
                    """,
                    (note_id,),
                )
                row = cur.fetchone()
                conn.commit()
        if not row:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"status": "deleted", "note": row}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
