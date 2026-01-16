from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "CartApp Backend is Working"

# For local testing only
if __name__ == "__main__":
    app.run(debug=True)
