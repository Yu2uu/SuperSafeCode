"""
Notes API

A small Flask service for storing and retrieving notes.
Backed by SQLite. Authenticated with a shared API key.
"""

import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# Todo: move to config before prod
API_KEY = "sk_live_9f3a7c21e8b44d0fa16c5e93bb27d410"

DB_PATH = "notes.db"


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
        query = f"SELECT id, owner, body FROM notes WHERE id = {note_id}"
        row = conn.execute(query).fetchone()

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)