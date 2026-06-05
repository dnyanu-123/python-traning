from flask import Flask, render_template


app = Flask(__name__)

#project data dictonary

# 1. User Information
# 1. User Information
user_info = {
    "name": "vaibhavi",
    "age": 20,
    "email": "user@example.com"
}

# 2. Trip Details
trip_details = {
    "destination": "mahabaleshwar",
    "days": 5,
    "budget": 20000
}

# 3. Hotel Information
hotel_info = {
    "hotel_name": "shiv View Resort",
    "rating": 4.5,
    "price_per_night": 3000
}

# 4. Transport Information
transport_info = {
    "mode": "Train",
    "from": "Mumbai",
    "to": "mahabaleshwar",
    "fare": 1200
}

# 5. Places to Visit
places_info = {
    "place1": "venna lake",
    "place2": "Lingmala Waterfall",
    "place3": "Elphinstone Point"
}

@app.route("/")
def home():
    return f"""
    <h1>AI Trip Planner</h1>

    <h2>User Information</h2>
    <p>Name: {user_info['name']}</p>
    <p>Age: {user_info['age']}</p>

    <h2>Trip Details</h2>
    <p>Destination: {trip_details['destination']}</p>
    <p>Days: {trip_details['days']}</p>
    <p>Budget: ₹{trip_details['budget']}</p>

    <h2>Hotel</h2>
    <p>{hotel_info['hotel_name']}</p>

    <h2>Transport</h2>
    <p>{transport_info['mode']}</p>

    <h2>Places to Visit</h2>
    <ul>
        <li>{places_info['place1']}</li>
        <li>{places_info['place2']}</li>
        <li>{places_info['place3']}</li>
    </ul>
    """


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/places")
def places():
    return "<h1>Popular Places</h1><p>Here are some amazing places you can visit!</p>"

@app.route("/planner")
def planner():
    return "<h1>Trip Planner</h1><p>Use our AI-powered trip planner to create your perfect itinerary.</p>"


if __name__ == "__main__":
    app.run(debug=True)