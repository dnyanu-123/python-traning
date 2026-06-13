import sqlite3
from webbrowser import get
from flask import Flask, render_template, request 

app = Flask(__name__)
app.secret_key ='linkkivi2026'

# same 2 function as before 
def get_db():
    conn = get_db()
        conn = sqlite3.connect('practice.db')
    conn.row_factory = sqlite3.Row
    return conn