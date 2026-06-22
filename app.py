from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.secret_key = "traveller_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def get_db():
    conn = sqlite3.connect("trip_planner.db")
    conn.row_factory = sqlite3.Row
    return conn

class User(UserMixin):

    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

def init_db():
    print("init_db is running...")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS travellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT,
        age INTEGER,
        email TEXT,
        contact_no TEXT,
        destination TEXT,
        days INTEGER,
        budget REAL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully")

@app.route("/")
def home():
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    if user:
        return User(
            user["id"],
            user["username"],
            user["email"],
            user["password"]
        )

    return None

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]

        password = generate_password_hash(
            request.form["password"]
        )

        conn = get_db()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing_user:
            flash("Username or email already registered", "danger")
            conn.close()
            return redirect(url_for("register"))

        conn.execute("""
            INSERT INTO users
            (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, password))

        conn.commit()
        conn.close()

        flash("Registration successful!", "success")

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            login_user(User(
                user["id"],
                user["username"],
                user["email"],
                user["password"]
            ))

            return redirect(url_for("planner"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


@app.route("/add_traveller", methods=["GET", "POST"])
@login_required
def add_traveller():

    if request.method == "POST":

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO travellers
            (user_id, name, age, email, contact_no, destination, days, budget)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            current_user.id,
            request.form["name"],
            request.form["age"],
            request.form["email"],
            request.form["contact_no"],
            request.form["destination"],
            request.form["days"],
            request.form["budget"]
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("planner"))

    return render_template("add_traveller.html")

@app.route("/planner")
@login_required
def planner():

    conn = get_db()

    travellers = conn.execute("""
        SELECT * FROM travellers
        WHERE user_id = ?
        ORDER BY id DESC
    """, (current_user.id,)).fetchall()

    conn.close()

    total_travellers = len(travellers)

    return render_template(
        "planner.html",
        travellers=travellers,
        total_travellers=total_travellers
    )

@app.route("/search")
def search():

    q = request.args.get("q", "")

    conn = get_db()

    travellers = conn.execute("""
        SELECT * FROM travellers
        WHERE name LIKE ?
        OR destination LIKE ?
        ORDER BY id DESC
    """, (f"%{q}%", f"%{q}%")).fetchall()

    conn.close()

    return render_template(
        "search.html",
        travellers=travellers,
        query=q
    )


@app.route("/filter")
def filter_trips():

    destination = request.args.get("destination", "")
    budget = request.args.get("budget", "")
    days = request.args.get("days", "")

    conn = get_db()

    destinations = conn.execute("""
        SELECT DISTINCT destination
        FROM travellers
        ORDER BY destination
    """).fetchall()

    query = "SELECT * FROM travellers WHERE 1=1"
    params = []

    # Destination filter
    if destination:
        query += " AND destination = ?"
        params.append(destination)

    # Budget filter
    if budget == "low":
        query += " AND budget < 10000"

    elif budget == "medium":
        query += " AND budget BETWEEN 10000 AND 50000"

    elif budget == "high":
        query += " AND budget > 50000"

    # Days filter
    if days == "1-3":
        query += " AND days BETWEEN 1 AND 3"

    elif days == "4-7":
        query += " AND days BETWEEN 4 AND 7"

    elif days == "8+":
        query += " AND days >= 8"

    travellers = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "filter.html",
        travellers=travellers,
        destinations=destinations,
        selected_destination=destination,
        selected_budget=budget,
        selected_days=days
    )


@app.route("/delete/<int:id>", methods=["POST"])
def delete_traveller(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM travellers WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Traveller deleted successfully!", "success")

    return redirect(url_for("planner"))


@app.route("/edit_traveller/<int:id>", methods=["GET", "POST"])
def edit_traveller(id):

    conn = get_db()

    if request.method == "POST":

        conn.execute("""
            UPDATE travellers
            SET name = ?,
                age = ?,
                email = ?,
                contact_no = ?,
                destination = ?,
                days = ?,
                budget = ?
            WHERE id = ?
        """, (
            request.form["name"],
            request.form["age"],
            request.form["email"],
            request.form["contact_no"],
            request.form["destination"],
            request.form["days"],
            request.form["budget"],
            id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("planner"))

    traveller = conn.execute(
        "SELECT * FROM travellers WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_traveller.html",
        traveller=traveller
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)