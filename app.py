#------------------------import sections-----------------------


from flask import Flask, render_template, request, redirect, url_for, flash, abort

import os
import sqlite3

from dotenv import load_dotenv
from groq import Groq



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
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "ai_trip_planner_secret_2026"
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def get_db():                       #connection with the SQLite
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "trip_planner.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn



class User(UserMixin):
#User class and load_user() function are used by Flask-Login to manage user sessions and authentication.
    def __init__(self, id, username, email, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role

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

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")

def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        traveller_id INTEGER NOT NULL,
        trip_name TEXT,
        destination TEXT,
        travel_date TEXT,
        days INTEGER,
        budget REAL,
        transport TEXT,
        status TEXT DEFAULT 'Planned',
        ai_itinerary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (traveller_id) REFERENCES travellers(id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully")
    
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

        admin_exists = conn.execute(
        "SELECT * FROM users WHERE role = 'admin'"
        ).fetchone()

        role = "admin" if admin_exists is None else "user"

        conn.execute("""
            INSERT INTO users
            (username, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, password, role))

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
#*************************************my_trips***********************************
@app.route("/my_trips")
@login_required
def my_trips():

    conn = get_db()

    # ADMIN → see ALL trips
    if current_user.role == "admin":

        trips = conn.execute("""
            SELECT
                trips.*,
                travellers.name
            FROM trips
            INNER JOIN travellers
                ON trips.traveller_id = travellers.id
            ORDER BY trips.id DESC
        """).fetchall()

    # NORMAL USER → see only own trips
    else:

        traveller = conn.execute("""
            SELECT id
            FROM travellers
            WHERE user_id = ?
        """, (current_user.id,)).fetchone()

        if not traveller:
            conn.close()
            return render_template("my_trips.html", trips=[])

        trips = conn.execute("""
            SELECT *
            FROM trips
            WHERE traveller_id = ?
            ORDER BY id DESC
        """, (traveller["id"],)).fetchall()

    conn.close()

    return render_template("my_trips.html", trips=trips)
#**************************Add traveller section**************************


@app.route("/add_traveller", methods=["GET", "POST"])
@login_required
def add_traveller():

    conn = get_db()

    if request.method == "POST":

        # admin can assign user_id manually (optional)
        if current_user.role == "admin":
            user_id = request.form.get("user_id", current_user.id)
        else:
            # normal user can only add for self
            user_id = current_user.id

        # Check if traveller profile already exists
        existing = conn.execute(
            "SELECT id FROM travellers WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if existing:
            conn.close()
            flash("Traveller Profile Already Exists!", "warning")
            return redirect(url_for("planner"))

        conn.execute("""
            INSERT INTO travellers
            (user_id, name, age, email, contact_no )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            request.form["name"],
            request.form["age"],
            request.form["email"],
            request.form["contact_no"]
        ))

        conn.commit()
        conn.close()

        flash("Traveller added successfully!", "success")
        return redirect(url_for("planner"))

    conn.close()
    return render_template("add_traveller.html")

#*********************************************ADD TRIP SECTION**********************************************
@app.route("/add_trip", methods=["GET", "POST"])
@login_required
def add_trip():

    conn = get_db()

    # Logged-in user ki traveller profile nikalo
    traveller = conn.execute("""
        SELECT id
        FROM travellers
        WHERE user_id = ?
    """, (current_user.id,)).fetchone()

    if not traveller:
        flash("Please create your traveller profile first.", "warning")
        conn.close()
        return redirect(url_for("add_traveller"))

    if request.method == "POST":

        conn.execute("""
            INSERT INTO trips
            (
                traveller_id,
                trip_name,
                destination,
                travel_date,
                days,
                budget,
                transport
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (

            traveller["id"],

            request.form["trip_name"],
            request.form["destination"],
            request.form["travel_date"],
            request.form["days"],
            request.form["budget"],
            request.form["transport"]

        ))

        conn.commit()
        conn.close()

        flash("Trip added successfully!", "success")
        return redirect(url_for("planner"))

    conn.close()
    return render_template("add_trip.html")

#*******************************Planner section****************************

@app.route("/planner")
@login_required
def planner():

    conn = get_db()

    # ADMIN → see all travellers
    if current_user.role == "admin":

        travellers = conn.execute("""
            SELECT
                travellers.*,
                users.username
            FROM travellers
            INNER JOIN users
                ON travellers.user_id = users.id
            ORDER BY travellers.id ASC
        """).fetchall()

    # NORMAL USER → see only own traveller profile
    else:

        travellers = conn.execute("""
            SELECT
                travellers.*,
                users.username
            FROM travellers
            INNER JOIN users
                ON travellers.user_id = users.id
            WHERE travellers.user_id = ?
            ORDER BY travellers.id DESC
        """, (current_user.id,)).fetchall()

    conn.close()

    return render_template(
        "planner.html",
        travellers=travellers,
        total_travellers=len(travellers)
    )
    #***************************************************dashboard section**********************************************

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db()

    total_users = conn.execute("""
        SELECT COUNT(*) AS count
        FROM users
    """).fetchone()["count"]

    total_travellers = conn.execute("""
        SELECT COUNT(*) AS count
        FROM travellers
    """).fetchone()["count"]

    total_trips = conn.execute("""
        SELECT COUNT(*) AS count
        FROM trips
    """).fetchone()["count"]

    total_budget = conn.execute("""
        SELECT COALESCE(SUM(budget),0) AS total
        FROM trips
    """).fetchone()["total"]

    # Destination Budget Analysis
    chart_data = conn.execute("""
        SELECT destination, SUM(budget) AS total_budget
        FROM trips
        GROUP BY destination
        ORDER BY total_budget DESC
    """).fetchall()

    labels = []
    budgets = []

    for row in chart_data:
        labels.append(row["destination"])
        budgets.append(row["total_budget"])

    conn.close()

    return render_template(
    "dashboard.html",
    total_users=total_users,
    total_travellers=total_travellers,
    total_trips=total_trips,
    total_budget=total_budget,
    labels=labels,
    budgets=budgets
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
#********************************SEARCH SECTION****************************
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    conn = get_db()
    results = []

    if request.method == "POST":
        query = request.form["query"]

        results = conn.execute("""
            SELECT
                travellers.*,
                users.username
            FROM travellers
            INNER JOIN users
                ON travellers.user_id = users.id
            WHERE travellers.name LIKE ?
               OR travellers.destination LIKE ?
        """, (f"%{query}%", f"%{query}%")).fetchall()

    conn.close()

    return render_template("search.html", results=results)
#*************************************view***********************

@app.route("/view_traveller/<int:traveller_id>")
@login_required
def view_traveller(traveller_id):

    conn = get_db()

    traveller = conn.execute("""
        SELECT *
        FROM travellers
        WHERE id = ?
    """, (traveller_id,)).fetchone()

    conn.close()

    if traveller is None:
        abort(404)

    return render_template(
        "view_traveller.html",
        traveller=traveller
    )
#****************************Delete section******************************

from flask_login import login_required, current_user
from flask import abort, redirect, url_for, flash

@app.route("/delete_traveller/<int:id>", methods=["POST"])
@login_required
def delete_traveller(id):

    # Only admin can delete
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

#*******************************delete section***************************
@app.route("/delete_trip/<int:trip_id>", methods=["POST"])
@login_required
def delete_trip(trip_id):

    conn = get_db()

    # Admin can delete any trip
    if current_user.role == "admin":
        trip = conn.execute(
            "SELECT * FROM trips WHERE id=?",
            (trip_id,)
        ).fetchone()

    # Normal user can delete only their own trip
    else:
        trip = conn.execute("""
            SELECT trips.*
            FROM trips
            JOIN travellers
            ON trips.traveller_id = travellers.id
            WHERE trips.id=? AND travellers.user_id=?
        """, (trip_id, current_user.id)).fetchone()

    if not trip:
        conn.close()
        flash("Trip not found or access denied.", "danger")
        return redirect(url_for("my_trips"))

    conn.execute(
        "DELETE FROM trips WHERE id=?",
        (trip_id,)
    )

    conn.commit()
    conn.close()

    flash("Trip deleted successfully!", "success")
    return redirect(url_for("my_trips"))
#************************************************edit trip section**********************************************
@app.route("/edit_trip/<int:trip_id>", methods=["GET", "POST"])
@login_required
def edit_trip(trip_id):

    conn = get_db()

    # Admin can edit any trip
    if current_user.role == "admin":
        trip = conn.execute("""
            SELECT *
            FROM trips
            WHERE id = ?
        """, (trip_id,)).fetchone()

    # Normal user can edit only their own trip
    else:
        trip = conn.execute("""
            SELECT trips.*
            FROM trips
            JOIN travellers
            ON trips.traveller_id = travellers.id
            WHERE trips.id = ? AND travellers.user_id = ?
        """, (trip_id, current_user.id)).fetchone()

    if not trip:
        conn.close()
        flash("Trip not found or access denied.", "danger")
        return redirect(url_for("my_trips"))

    if request.method == "POST":

        conn.execute("""
            UPDATE trips
            SET
                trip_name = ?,
                destination = ?,
                travel_date = ?,
                days = ?,
                budget = ?,
                transport = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            request.form["trip_name"],
            request.form["destination"],
            request.form["travel_date"],
            request.form["days"],
            request.form["budget"],
            request.form["transport"],
            request.form["status"],
            trip_id
        ))

        conn.commit()
        conn.close()

        flash("Trip updated successfully!", "success")
        return redirect(url_for("my_trips"))

    conn.close()

    return render_template(
        "edit_trip.html",
        trip=trip
    )

#****************************Edit section******************************

@app.route("/edit_traveller/<int:id>", methods=["GET", "POST"])
@login_required
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

@app.route("/relationship_demo")
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
    )

#**************************recommedation section**************************
@app.route("/recommend_trip", methods=["GET", "POST"])
@login_required
def recommend_trip():

    itinerary = None

    if request.method == "POST":

        destination = request.form["destination"]
        budget = request.form["budget"]
        days = request.form["days"]

        travel_type = request.form.get(
            "travel_type",
            "Solo"
        )

        hotel_preference = request.form.get(
            "hotel_preference",
            "Standard"
        )

        transport = request.form.get(
            "transport",
            "Bus"
        )

        season = request.form.get(
            "season",
            "Summer"
        )

        prompt = f"""
Create a detailed travel itinerary.

Destination: {destination}
Budget: ₹{budget}
Days: {days}

Travel Type: {travel_type}
Hotel Preference: {hotel_preference}
Transport Type: {transport}
Season: {season}

Generate:

1. Day wise itinerary
2. Famous places to visit
3. Local food recommendations
4. Recommended hotels
5. Estimated expenses
6. Travel tips
7. Packing suggestions

Generate the itinerary specifically for {destination}.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        itinerary = (
            response
            .choices[0]
            .message
            .content
        )

    return render_template(
        "recommend_trip.html",
        itinerary=itinerary
    )
'''@app.route("/recommend_trip", methods=["GET", "POST"])
@login_required
def recommend_trip():

    itinerary = ""

    places = {

        "Goa": [
            "Baga Beach",
            "Fort Aguada",
            "Calangute Beach",
            "Anjuna Market",
            "Dudhsagar Falls",
            "Chapora Fort",
            "Cruise Dinner"
        ],

        "Manali": [
            "Mall Road",
            "Hadimba Temple",
            "Solang Valley",
            "Atal Tunnel",
            "Rohtang Pass",
            "Jogini Falls",
            "Local Shopping"
        ],

        "Kashmir": [
            "Dal Lake",
            "Gulmarg",
            "Mughal Gardens",
            "Pahalgam",
            "Sonmarg",
            "Shankaracharya Temple",
            "Local Market"
        ],

        "Jaipur": [
            "Hawa Mahal",
            "City Palace",
            "Amer Fort",
            "Jal Mahal",
            "Nahargarh Fort",
            "Albert Hall Museum",
            "Local Shopping"
        ],

        "Kerala": [
            "Munnar",
            "Tea Gardens",
            "Alleppey Houseboat",
            "Kochi",
            "Athirapally Falls",
            "Thekkady",
            "Beach Visit"
        ],

        "Ooty": [
            "Botanical Garden",
            "Ooty Lake",
            "Toy Train",
            "Doddabetta Peak",
            "Tea Factory",
            "Rose Garden",
            "Pykara Lake"
        ]
    }

    if request.method == "POST":

        destination = request.form["destination"]
        budget = int(request.form["budget"])
        days = int(request.form["days"])

        itinerary = f"Destination: {destination}\n"
        itinerary += f"Days: {days}\n"
        itinerary += f"Budget: ₹{budget}\n\n"

        if budget < 10000:
            itinerary += "Hotel: Budget Hotel\n\n"
        elif budget < 30000:
            itinerary += "Hotel: 3-Star Hotel\n\n"
        else:
            itinerary += "Hotel: Luxury Resort\n\n"

        activities = places[destination]

        for i in range(days):
            place = activities[i % len(activities)]
            itinerary += f"Day {i+1}: Visit {place}\n"

    return render_template(
        "recommend_trip.html",
        itinerary=itinerary
    )'''

#****************************************************ai chatbot*********************************************
@app.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():

    response_text = ""

    if request.method == "POST":

        user_message = request.form["message"]

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """
                You are an AI Travel Assistant for an AI Trip Planner application.
                Help users with travel planning, destinations, budgets,
                hotels, restaurants, itineraries and travel tips.
                Keep answers concise and helpful.
                """
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )

            response_text = response.choices[0].message.content

        except Exception as e:
            response_text = f"Error: {str(e)}"

    return render_template(
        "chatbot.html",
        response=response_text
    )
#***********************************************generate AI section**********************************************
@app.route("/generate_ai/<int:trip_id>")
@login_required
def generate_ai(trip_id):

    conn = get_db()

    # Admin can access any trip
    if current_user.role == "admin":
        trip = conn.execute("""
            SELECT *
            FROM trips
            WHERE id = ?
        """, (trip_id,)).fetchone()

    # Normal user can access only their own trip
    else:
        trip = conn.execute("""
            SELECT trips.*
            FROM trips
            JOIN travellers
            ON trips.traveller_id = travellers.id
            WHERE trips.id = ?
            AND travellers.user_id = ?
        """, (trip_id, current_user.id)).fetchone()

    if not trip:
        conn.close()
        flash("Trip not found or access denied.", "danger")
        return redirect(url_for("my_trips"))

    destination = trip["destination"]
    days = trip["days"]
    budget = trip["budget"]
    transport = trip["transport"]

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": f"""
Create a detailed travel itinerary.

Destination: {destination}
Duration: {days} days
Budget: ₹{budget}
Transport: {transport}

Please include:

1. Recommended hotel type according to budget
2. Day-wise itinerary
3. Famous places to visit
4. Food recommendations
5. Local travel tips
6. Estimated daily spending

Keep the response clean and easy to read.
"""
                }
            ],

            temperature=0.7,
            max_tokens=1200
        )

        itinerary = response.choices[0].message.content

    except Exception as e:
        conn.close()
        flash(f"Groq API Error: {str(e)}", "danger")
        return redirect(url_for("my_trips"))

    conn.execute("""
        UPDATE trips
        SET ai_itinerary = ?
        WHERE id = ?
    """, (
        itinerary,
        trip_id
    ))

    conn.commit()
    conn.close()

    flash("AI itinerary generated successfully!", "success")

    return redirect(url_for("my_trips"))

#****************************************hotel recommendation section**********************************************
@app.route("/hotel_recommendation/<int:trip_id>")
@login_required
def hotel_recommendation(trip_id):

    conn = get_db()

    # Admin can access any trip
    if current_user.role == "admin":

        trip = conn.execute("""
            SELECT *
            FROM trips
            WHERE id = ?
        """, (trip_id,)).fetchone()

    # Normal user can access only own trip
    else:

        trip = conn.execute("""
            SELECT trips.*
            FROM trips
            JOIN travellers
            ON trips.traveller_id = travellers.id
            WHERE trips.id = ?
            AND travellers.user_id = ?
        """, (
            trip_id,
            current_user.id
        )).fetchone()

    if not trip:
        conn.close()
        flash(
            "Trip not found or access denied.",
            "danger"
        )
        return redirect(
            url_for("my_trips")
        )

    destination = trip["destination"]
    budget = trip["budget"]
    days = trip["days"]

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": f"""
Suggest 5 hotels in {destination}
for a budget of ₹{budget}
for a trip of {days} days.

For each hotel provide:

1. Hotel Name
2. Approximate price per night
3. Hotel Type
4. Why it is recommended
5. Nearby attractions

Format nicely with headings and bullet points.
"""
                }
            ],

            temperature=0.7,
            max_tokens=1000
        )

        hotels = response.choices[0].message.content

    except Exception as e:

        hotels = f"Error: {str(e)}"

    conn.close()

    return render_template(
        "hotel_recommendation.html",
        trip=trip,
        hotels=hotels
    )
#********************************************expence traker section**********************************************
@app.route("/expense_calculator/<int:trip_id>")
@login_required
def expense_calculator(trip_id):

    conn = get_db()

    trip = conn.execute(
        """
        SELECT *
        FROM trips
        WHERE id = ?
        """,
        (trip_id,)
    ).fetchone()

    conn.close()

    if not trip:
        flash("Trip not found!", "danger")
        return redirect(url_for("my_trips"))

    total_budget = trip["budget"]

    hotel_cost = total_budget * 0.35
    food_cost = total_budget * 0.15
    local_transport = total_budget * 0.10
    sightseeing = total_budget * 0.10
    shopping = total_budget * 0.30

    return render_template(
        "expense_calculator.html",
        trip=trip,
        hotel_cost=hotel_cost,
        food_cost=food_cost,
        local_transport=local_transport,
        sightseeing=sightseeing,
        shopping=shopping
    )
#*****************************************trip details section**********************************************

@app.route("/trip/<int:trip_id>")
@login_required
def trip_details(trip_id):

    conn = get_db()

    # Admin can view any trip
    if current_user.role == "admin":
        trip = conn.execute("""
            SELECT trips.*, travellers.name
            FROM trips
            JOIN travellers
            ON trips.traveller_id = travellers.id
            WHERE trips.id = ?
        """, (trip_id,)).fetchone()

    # User can view only their own trip
    else:
        trip = conn.execute("""
            SELECT trips.*, travellers.name
            FROM trips
            JOIN travellers
            ON trips.traveller_id = travellers.id
            WHERE trips.id = ?
            AND travellers.user_id = ?
        """, (trip_id, current_user.id)).fetchone()

    conn.close()

    if not trip:
        flash("Trip not found or access denied.", "danger")
        return redirect(url_for("my_trips"))

    return render_template("trip_details.html", trip=trip)
if __name__ == "__main__":

    init_db()
    app.run(debug=True)