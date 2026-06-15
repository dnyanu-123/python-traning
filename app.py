from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "traveller_secret_key"


def get_db():
    conn = sqlite3.connect("trip_planner.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS travellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        email TEXT,
        contact_no TEXT,
        destination TEXT,
        days INTEGER,
        budget REAL
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/add_traveller", methods=["GET", "POST"])
def add_traveller():

    if request.method == "POST":

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO travellers
            (name, age, email, contact_no, destination, days, budget)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
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
def planner():

    conn = get_db()

    travellers = conn.execute("""
        SELECT * FROM travellers
        ORDER BY id DESC
    """).fetchall()

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

    conn = get_db()

    destinations = conn.execute("""
        SELECT DISTINCT destination
        FROM travellers
        ORDER BY destination
    """).fetchall()

    query = "SELECT * FROM travellers WHERE 1=1"
    params = []

    if destination:
        query += " AND destination = ?"
        params.append(destination)

    if budget == "low":
        query += " AND budget < 10000"

    elif budget == "medium":
        query += " AND budget BETWEEN 10000 AND 50000"

    elif budget == "high":
        query += " AND budget > 50000"

    travellers = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "filter.html",
        travellers=travellers,
        destinations=destinations,
        selected_destination=destination,
        selected_budget=budget
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
    app.run(debug=True)