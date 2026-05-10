from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from audit import log_action
import sqlite3
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "insuranceguardian2024secretkey"
app.permanent_session_lifetime = timedelta(minutes=30)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    def get_id(self):
        return str(self.id)

def get_db():
    conn = sqlite3.connect("insurance_guardian.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_users_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'staff')")
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", generate_password_hash("dental123"), "admin"))
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(row["id"], row["username"], row["role"])
    return None

def get_carriers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM carriers")
    results = cursor.fetchall()
    conn.close()
    return results

def get_procedures():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT cdt_code, description FROM procedures ORDER BY cdt_code")
    results = cursor.fetchall()
    conn.close()
    return results

def check_coverage(carrier_id, cdt_code):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT carriers.name, coverage_rules.cdt_code, coverage_rules.requirement, coverage_rules.frequency_limit_years, coverage_rules.notes FROM coverage_rules JOIN carriers ON carriers.id = coverage_rules.carrier_id WHERE carriers.id = ? AND coverage_rules.cdt_code = ?", (carrier_id, cdt_code))
    result = cursor.fetchone()
    conn.close()
    return result

def get_alert_level(result):
    if not result:
        return "unknown"
    requirement = result[2].lower()
    notes = result[4].lower() if result[4] else ""
    combined = requirement + " " + notes
    if "pre-authorization required" in combined:
        return "red"
    yellow_triggers = ["required", "must be", "charting", "radiograph", "photograph", "documentation", "narrative", "evidence", "pocket depth", "bone loss", "bleeding", "recommended", "verify", "submitted", "showing"]
    for word in yellow_triggers:
        if word in combined:
            return "yellow"
    return "green"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and check_password_hash(row["password"], password):
            user = User(row["id"], row["username"], row["role"])
            login_user(user)
            session.permanent = True
            log_action(username, "LOGIN", "User logged in successfully")
            return redirect(url_for("index"))
        else:
            log_action(username, "FAILED_LOGIN", "Invalid login attempt")
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    log_action(current_user.username, "LOGOUT", "User logged out")
    logout_user()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    carriers = get_carriers()
    procedures = get_procedures()
    results = []
    patient_name = None
    if request.method == "POST":
        carrier_id = request.form.get("carrier_id")
        patient_name = request.form.get("patient_name")
        cdt_codes = request.form.getlist("cdt_codes")
        cdt_codes = [c for c in cdt_codes if c]
        for cdt_code in cdt_codes:
            result = check_coverage(carrier_id, cdt_code)
            alert_level = get_alert_level(result)
            results.append({"cdt_code": cdt_code, "result": result, "alert_level": alert_level})
            log_action(current_user.username, "COVERAGE_CHECK", f"Patient: {patient_name} | {cdt_code} | carrier_id: {carrier_id} | Alert: {alert_level}")
    return render_template("index.html", carriers=carriers, procedures=procedures, results=results, patient_name=patient_name)

if __name__ == "__main__":
    init_users_table()
    app.run(debug=True)
