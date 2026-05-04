from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_carriers():
    conn = sqlite3.connect("insurance_guardian.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM carriers")
    results = cursor.fetchall()
    conn.close()
    return results

def get_procedures():
    conn = sqlite3.connect("insurance_guardian.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cdt_code, description FROM procedures")
    results = cursor.fetchall()
    conn.close()
    return results

def check_coverage(carrier_id, cdt_code):
    conn = sqlite3.connect("insurance_guardian.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT carriers.name, coverage_rules.cdt_code, coverage_rules.requirement, coverage_rules.frequency_limit_years, coverage_rules.notes
        FROM coverage_rules
        JOIN carriers ON carriers.id = coverage_rules.carrier_id
        WHERE carriers.id = ? AND coverage_rules.cdt_code = ?
    """, (carrier_id, cdt_code))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    carriers = get_carriers()
    procedures = get_procedures()
    result = None
    if request.method == "POST":
        carrier_id = request.form.get("carrier_id")
        cdt_code = request.form.get("cdt_code")
        result = check_coverage(carrier_id, cdt_code)
    return render_template("index.html", carriers=carriers, procedures=procedures, result=result)

if __name__ == "__main__":
    app.run(debug=True)
