from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>AI Trip Planner</h1>"

@app.route("/about")
def about():
    return "<h1>About AI Trip Planner</h1><p>This application helps you plan your trips using AI.</p>"


@app.route("/places")
def places():
    return "<h1>Popular Places</h1><p>Here are some amazing places you can visit!</p>"

@app.route("/planner")
def planner():
    return "<h1>Trip Planner</h1><p>Use our AI-powered trip planner to create your perfect itinerary.</p>"


if __name__ == "__main__":
    app.run(debug=True)