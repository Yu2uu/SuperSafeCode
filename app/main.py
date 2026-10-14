"""
Notes API

A small Flask service for storing and retrieving notes.
Backed by SQLite. Authenticated with a shared API key.
"""

import sqlite3
import os
from contextlib import contextmanager
from hmac import compare_digest
from flask import Flask, jsonify, request

app = Flask(__name__)

API_KEY = os.environ.get("NOTES_API_KEY")
if not API_KEY:
    raise RuntimeError("NOTES_API_KEY must be set")
 
DB_PATH = os.environ.get("NOTES_DB_PATH", "notes.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


@app.before_request
def authenticate_notes():
    if request.endpoint in {"get_note", "create_note"}:
        supplied = request.headers.get("X-API-Key", "")
        if not compare_digest(supplied.encode("utf-8"), API_KEY.encode("utf-8")):
            return jsonify(error="unauthorised"), 401


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found"), 404


def init_db():
    with get_db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "owner TEXT NOT NULL, "
            "body TEXT NOT NULL)"
        )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/notes/<note_id>")
def get_note(note_id):
    with get_db() as conn:
        query = "SELECT id, owner, body FROM notes WHERE id = ?"
        row = conn.execute(query, (note_id,)).fetchone()

    if row is None:
        return jsonify(error="not found"), 404

    return jsonify(dict(row))


@app.post("/notes")
def create_note():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="JSON object is required"), 400
    owner = payload.get("owner")
    body = payload.get("body")

    if not isinstance(owner, str) or not isinstance(body, str) or not owner or not body:
        return jsonify(error="owner and body are required"), 400

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (owner, body) VALUES (?, ?)", (owner, body)
        )
        note_id = cur.lastrowid

    return jsonify(id=note_id), 201


init_db()
