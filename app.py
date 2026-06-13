from flask import Flask, render_template, request, redirect
import sqlite3
app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('trip_planner.db')
    cursor = conn.cursor()

    cursor.execute('''
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
    ''')

    conn.commit()
    conn.close()

init_db()

travellers = []

#project data dictonary

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/add_traveller', methods=['GET', 'POST'])
def add_traveller():

    if request.method == 'POST':

        conn = sqlite3.connect('trip_planner.db')
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

        return redirect("/planner")

    return render_template("add_traveller.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/planner")
def planner():

    conn = sqlite3.connect("trip_planner.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM travellers")
    travellers = cursor.fetchall()

    conn.close()

    total_travellers = len(travellers)

    return render_template(
        "planner.html",
        travellers=travellers,
        total_travellers=total_travellers
    )


@app.route("/delete_traveller/<int:id>")
def delete_traveller(id):
    conn = sqlite3.connect("trip_planner.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM travellers WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/planner")

@app.route("/edit_traveller/<int:id>", methods=["GET", "POST"])
def edit_traveller(id):
    conn = sqlite3.connect("trip_planner.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        email = request.form["email"]
        destination = request.form["destination"]
        days = request.form["days"]
        budget = request.form["budget"]
        contact_no = request.form["contact_no"]

        cursor.execute("""
            UPDATE travellers
            SET name=?, age=?, email=?, contact_no=?, destination=?, days=?, budget=?
            WHERE id=?
        """, (name, age, email, contact_no, destination, days, budget, id))

        conn.commit()
        conn.close()

        return redirect("/planner")

    cursor.execute("SELECT * FROM travellers WHERE id=?", (id,))
    traveller = cursor.fetchone()

    conn.close()

    return render_template("edit_traveller.html", traveller=traveller)


if __name__ == "__main__":
     app.run(debug=True)