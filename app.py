from flask import (
    Flask, g, render_template, request,
    redirect, url_for, session, flash
)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Konfiguration
DATABASE = "forum.db"
SECRET_KEY = "poop1234"  

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=SECRET_KEY, DATABASE=DATABASE)

# Databas-hjälpfunktioner 
def get_db():
    # Returnerar en sqlite-connection som lagras i flask.g
    if "db" not in g:
        g.db = sqlite3.connect(
            app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  
    return g.db

@app.teardown_appcontext
def close_db(exc):
    # Stänger connection efter request
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    # Skapar tabeller från schema.sql om de inte redan finns
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()

with app.app_context():
    init_db()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    user = db.execute("SELECT id, username, display_name FROM users WHERE id = ?", (uid,)).fetchone()
    return user

def login_user(user_id):
    session.clear()
    session["user_id"] = user_id
