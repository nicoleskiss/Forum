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