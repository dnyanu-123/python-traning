from flask import Flask
app = Flask(__name__)

@app.router('/')
def home():
    return'<h1>welcome to my project</h1>'

if __name__ =='__main__':
    app.run(debug=True)