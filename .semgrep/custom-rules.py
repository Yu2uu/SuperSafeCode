"""Fixtures for the interpolated-sql-execute Semgrep rule."""


def unsafe_assigned(conn, note_id):
    query = f"SELECT id, owner, body FROM notes WHERE id = {note_id}"
    # ruleid: interpolated-sql-execute
    return conn.execute(query).fetchone()


def unsafe_inline(conn, note_id):
    # ruleid: interpolated-sql-execute
    return conn.execute(
        f"SELECT id FROM notes WHERE id = {note_id}"
    ).fetchone()


def safe_parameterised(conn, note_id):
    # ok: interpolated-sql-execute
    return conn.execute(
        "SELECT id FROM notes WHERE id = ?", (note_id,)
    ).fetchone()


def safe_assigned(conn, note_id):
    query = "SELECT id FROM notes WHERE id = ?"
    # ok: interpolated-sql-execute
    return conn.execute(query, (note_id,)).fetchone()


def safe_static(conn):
    # ok: interpolated-sql-execute
    return conn.execute("SELECT id FROM notes").fetchall()