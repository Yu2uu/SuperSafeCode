"""
Notes API

A small Flask service for storing and retrieving notes.
Backed by SQLite. Authenticated with a shared API key.
"""

import sqlite3
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# FIX (was: hardcoded secret committed to the repo - caught by Gitleaks)
# Secrets are injected at runtime. The app refuses to start without them.
API_KEY = os.environ.get("NOTES_API_KEY")
if not API_KEY:
    raise RuntimeError("NOTES_API_KEY must be set")
 
DB_PATH = os.environ.get("NOTES_DB_PATH", "notes.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify(error="unauthorised"), 401

    payload = request.get_json(silent=True) or {}
    owner = payload.get("owner")
    body = payload.get("body")

    if not owner or not body:
        return jsonify(error="owner and body are required"), 400

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (owner, body) VALUES (?, ?)", (owner, body)
        )
        note_id = cur.lastrowid

    return jsonify(id=note_id), 201


init_db()


