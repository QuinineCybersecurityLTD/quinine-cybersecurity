"""SYNTHETIC vulnerable Flask app - insecure patterns for SAST training only."""
import hashlib, sqlite3, subprocess
from flask import Flask, request
app = Flask(__name__)

@app.route("/user")
def get_user():
    uid = request.args.get("id")
    db = sqlite3.connect("app.db")
    return str(db.execute("SELECT * FROM users WHERE id = '" + uid + "'").fetchall())

@app.route("/ping")
def ping():
    return subprocess.check_output("ping -c1 " + request.args.get("host"), shell=True)

@app.route("/calc")
def calc():
    return str(eval(request.args.get("expr")))

def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
