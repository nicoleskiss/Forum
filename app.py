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

@app.route("/")
def index():
    db = get_db()
    topics = db.execute("""
        SELECT t.id, t.title, t.created_at, u.username, u.display_name
        FROM topics t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    """).fetchall()
    return render_template("index.html", topics=topics, user=current_user())

@app.route("/topic/new", methods=["GET", "POST"])
def new_topic():
    user = current_user()
    if not user:
        flash("Du måste vara inloggad för att skapa ett nytt ämne.")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title:
            flash("Titel får inte vara tom.")
            return render_template("new_topic.html", user=user)
        if not content:
            flash("Inlägg får inte vara tomt.")
            return render_template("new_topic.html", user=user)

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        cursor = db.execute(
            "INSERT INTO topics (title, user_id, created_at) VALUES (?, ?, ?)",
            (title, user["id"], now)
        )
        topic_id = cursor.lastrowid
        db.execute(
            "INSERT INTO posts (topic_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
            (topic_id, user["id"], content, now)
        )
        db.commit()
        flash("Tråd skapad.")
        return redirect(url_for("view_topic", topic_id=topic_id))
    return render_template("new_topic.html", user=user)
