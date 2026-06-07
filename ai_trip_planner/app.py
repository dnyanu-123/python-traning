from flask import Flask, render_template, request
app = Flask(__name__)

travellers = []

#project data dictonary
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
@app.route('/add_traveller', methods=['GET', 'POST'])
def add_traveller():

    if request.method == 'POST':

        traveller = {
            "name": request.form["name"],
            "age": request.form["age"],
            "email": request.form["email"],
            "gender": request.form["gender"],
            "contact_no": request.form["contact_no"]
        }

        travellers.append(traveller)

        return render_template(
            "planner.html",
            travellers=travellers,
            trip_details=trip_details
        )

    return render_template("add_traveller.html")
@app.route("/planner")
def planner():
    return render_template("planner.html",travellers=travellers,trip_details=trip_details)
                            
@app.route("/contact")
def contact():
    return render_template("contact.html")
if __name__ == "__main__":
    app.run(debug=True)