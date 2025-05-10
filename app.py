from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World from k3s!- a demo app for testing github actions"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
