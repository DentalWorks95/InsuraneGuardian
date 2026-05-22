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


def get_tooth_location(tooth_number):
    try:
        tooth = int(tooth_number)
        anterior = [6, 7, 8, 9, 10, 11, 22, 23, 24, 25, 26, 27]
        if tooth in anterior:
            return "Anterior"
        elif 1 <= tooth <= 32:
            return "Posterior"
        else:
            return "Unknown"
    except Exception:
        return "Unknown"


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
        tooth_numbers = request.form.getlist("tooth_numbers")
        cdt_codes = [c for c in cdt_codes if c]
        for i, cdt_code in enumerate(cdt_codes):
            result = check_coverage(carrier_id, cdt_code)
            alert_level = get_alert_level(result)
            tooth = tooth_numbers[i] if i < len(tooth_numbers) else ""
            tooth_location = get_tooth_location(tooth) if tooth else ""
            results.append({"cdt_code": cdt_code, "result": result, "alert_level": alert_level, "tooth": tooth, "tooth_location": tooth_location})
            log_action(current_user.username, "COVERAGE_CHECK", f"Patient: {patient_name} | {cdt_code} | Tooth: {tooth} | carrier_id: {carrier_id} | Alert: {alert_level}")
    return render_template("index.html", carriers=carriers, procedures=procedures, results=results, patient_name=patient_name)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    search_name = None
    records = []
    if request.method == "POST":
        search_name = request.form.get("search_name")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log WHERE action = 'COVERAGE_CHECK' AND details LIKE ? ORDER BY timestamp DESC", (f"%Patient: {search_name}%",))
        records = cursor.fetchall()
        conn.close()
        log_action(current_user.username, "HISTORY_SEARCH", f"Searched history for: {search_name}")
    return render_template("history.html", records=records, search_name=search_name)


@app.route("/audit")
@login_required
def audit():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100")
    records = cursor.fetchall()
    conn.close()
    return render_template("audit.html", records=records)
@app.route("/voice", methods=["POST"])
@login_required
def voice():
    from voice import listen_for_procedures
    from flask import jsonify
    result = listen_for_procedures()
    return jsonify(result)
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    from flask import jsonify
    from image_analysis import allowed_file, analyze_image
    import os
    result = None
    if request.method == "POST":
        if "file" not in request.files:
            result = {"error": "No file uploaded"}
        else:
            file = request.files["file"]
            procedure_type = request.form.get("procedure_type", "")
            if file.filename == "":
                result = {"error": "No file selected"}
            elif allowed_file(file.filename):
                filename = file.filename
                upload_path = os.path.join("uploads", filename)
                file.save(upload_path)
                result = analyze_image(upload_path, procedure_type)
                log_action(current_user.username, "IMAGE_UPLOAD", f"Uploaded {filename} for procedure {procedure_type}")
            else:
                result = {"error": "File type not allowed"}
    carriers = get_carriers()
    procedures = get_procedures()
    return render_template("upload.html", result=result, carriers=carriers, procedures=procedures)
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'COVERAGE_CHECK'")
    total_checks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'COVERAGE_CHECK' AND details LIKE '%Alert: red%'")
    total_red = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'COVERAGE_CHECK' AND details LIKE '%Alert: yellow%'")
    total_yellow = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'COVERAGE_CHECK' AND details LIKE '%Alert: green%'")
    total_green = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM audit_log WHERE action = 'COVERAGE_CHECK' ORDER BY timestamp DESC LIMIT 10")
    recent_checks = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", total_checks=total_checks, total_red=total_red, total_yellow=total_yellow, total_green=total_green, recent_checks=recent_checks)
if __name__ == "__main__":
    init_users_table()
    app.run(debug=True, host="0.0.0.0", port=5000)