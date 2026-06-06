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
    return render_template('home.html')
    

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/planner")
def planner():
    return render_template("planner.html",user_info=user_info, trip_details=trip_details)
                            

@app.route("/contact")
def contact():
    return render_template("contact.html")



if __name__ == "__main__":
    app.run(debug=True)