import os
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app import db

APP_TITLE = os.getenv("APP_TITLE", "Therian CRUD Demo")

app = FastAPI(title=APP_TITLE)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    status: str = "pending"


@app.on_event("startup")
def startup() -> None:
    db.init_db()
    db.seed_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    notes = db.list_notes()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": APP_TITLE,
            "notes": notes,
            "editing_note": None,
            "db_host": os.getenv("DB_HOST", ""),
            "db_name": os.getenv("DB_NAME", ""),
            "db_user": os.getenv("DB_USER", ""),
        },
    )


@app.get("/edit/{note_id}", response_class=HTMLResponse)
def edit_page(request: Request, note_id: int):
    note = db.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    notes = db.list_notes()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": APP_TITLE,
            "notes": notes,
            "editing_note": note,
            "db_host": os.getenv("DB_HOST", ""),
            "db_name": os.getenv("DB_NAME", ""),
            "db_user": os.getenv("DB_USER", ""),
        },
    )


@app.post("/web/notes")
def web_create_note(
    title: str = Form(...),
    content: str = Form(""),
    status: str = Form("pending"),
):
    db.create_note(title=title, content=content, status=status)
    return RedirectResponse(url="/", status_code=303)


@app.post("/web/notes/{note_id}/update")
def web_update_note(
    note_id: int,
    title: str = Form(...),
    content: str = Form(""),
    status: str = Form("pending"),
):
    updated = db.update_note(note_id=note_id, title=title, content=content, status=status)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return RedirectResponse(url="/", status_code=303)


@app.post("/web/notes/{note_id}/delete")
def web_delete_note(note_id: int):
    db.delete_note(note_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/db-check")
def db_check():
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
                result = cur.fetchone()
        return {"status": "ok", **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/notes")
def api_list_notes():
    return {"status": "ok", "notes": db.list_notes()}


@app.get("/api/notes/{note_id}")
def api_get_note(note_id: int):
    note = db.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "ok", "note": note}


@app.post("/api/notes")
def api_create_note(note: NoteCreate):
    return {"status": "created", "note": db.create_note(note.title, note.content, note.status)}


@app.put("/api/notes/{note_id}")
def api_update_note(note_id: int, note: NoteCreate):
    updated = db.update_note(note_id, note.title, note.content, note.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "updated", "note": updated}


@app.delete("/api/notes/{note_id}")
def api_delete_note(note_id: int):
    deleted = db.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "deleted", "id": note_id}
