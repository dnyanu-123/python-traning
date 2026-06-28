#------------------------import sections-----------------------


from flask import Flask, render_template, request, redirect, url_for, flash, abort


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

    def __init__(self, id, username, email, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
#**************************database initialization**************************


def init_db():
    print("init_db is running...")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
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
            user["password"],
            user["role"]
        )

    return None

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

#**************************Register section**************************
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
            (username, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, password, "user"))

        conn.commit()
        conn.close()

        flash("Registration successful!", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


#**************************Login section**************************

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
                user["password"],
                user["role"]
            ))

            return redirect(url_for("planner"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")

#**************************logout section****************************

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))

#**************************Add traveller section**************************

@app.route("/add_traveller", methods=["GET", "POST"])
@login_required
def add_traveller():
    if current_user.role != "admin":
        abort(403)  # Forbidden access for non-admin users
    
    if request.method == "POST":

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
    INSERT INTO travellers
    (user_id, name, age, email, contact_no, destination, days, budget, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    current_user.id,
    request.form["name"],
    request.form["age"],
    request.form["email"],
    request.form["contact_no"],
    request.form["destination"],
    request.form["days"],
    request.form["budget"],
    request.form["status"]
))

        conn.commit()
        flash("Traveller added successfully!", "success")
        conn.close()

        return redirect(url_for("planner"))

    return render_template("add_traveller.html")

#*******************************Planner section****************************


@app.route("/planner")
@login_required
def planner():

    conn = get_db()

    travellers = conn.execute("""
        SELECT
            travellers.*,
            users.username
        FROM travellers
        INNER JOIN users
        ON travellers.user_id = users.id
        ORDER BY travellers.id DESC
    """).fetchall()

    conn.close()

    total_travellers = len(travellers)

    return render_template(
        "planner.html",
        travellers=travellers,
        total_travellers=total_travellers
    )
#********************************Search section***********************************

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

#******************************Filter section*******************************

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

#****************************Delete section******************************

@app.route("/delete/<int:id>", methods=["POST"])
def delete_traveller(id):

    if current_user.role != "admin":
        abort(403)
        
    conn = get_db()

    conn.execute(
        "DELETE FROM travellers WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Traveller deleted successfully!", "success")

    return redirect(url_for("planner"))

#****************************Edit section******************************

@app.route("/edit_traveller/<int:id>", methods=["GET", "POST"])
def edit_traveller(id):

    if current_user.role != "admin":
        abort(403)

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
                budget = ?,
                status = ?
            WHERE id = ?
        """, (
            request.form["name"],
            request.form["age"],
            request.form["email"],
            request.form["contact_no"],
            request.form["destination"],
            request.form["days"],
            request.form["budget"],
            request.form["status"],
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

#*******************************RELATIONSHIP_DEMO****************************************
'''@app.route("/relationship_demo")
@login_required
def relationship_demo():

    conn = get_db()

    travellers_raw = conn.execute("""
        SELECT id, name, user_id
        FROM travellers
    """).fetchall()

    travellers_joined = conn.execute("""
        SELECT
            travellers.name AS traveller_name,
            users.username
        FROM travellers
        INNER JOIN users
        ON travellers.user_id = users.id
    """).fetchall()

    return render_template(
        "relationship_demo.html",
        travellers_raw=travellers_raw,
        travellers_joined=travellers_joined
    )'''


if __name__ == "__main__":
    init_db()
    app.run(debug=True)