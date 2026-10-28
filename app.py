from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Docker 7-Stage CI/CD Pipeline - Version 1</h1><p>Status: Running</p>"

@app.route("/health")
def health():
    return jsonify(status="healthy", version="v1"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)