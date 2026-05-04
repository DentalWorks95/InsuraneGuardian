import sqlite3

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

def main():
    print("================================")
    print("   AI Insurance Guardian v0.2   ")
    print("================================")
    print("")

    carriers = get_carriers()
    print("SELECT CARRIER:")
    print("---------------")
    for carrier in carriers:
        print(str(carrier[0]) + ". " + carrier[1])
    print("")
    carrier_choice = input("Enter carrier number: ")
    carrier_id = int(carrier_choice)
    print("")

    print("SELECT PROCEDURE:")
    print("-----------------")
    procedures = get_procedures()
    for i, proc in enumerate(procedures):
        print(str(i+1) + ". " + proc[0] + " - " + proc[1])
    print("")
    proc_choice = input("Enter procedure number: ")
    proc_index = int(proc_choice) - 1
    cdt_code = procedures[proc_index][0]
    print("")

    result = check_coverage(carrier_id, cdt_code)
    if result:
        print("COVERAGE REQUIREMENTS:")
        print("----------------------")
        print("Carrier:", result[0])
        print("Procedure:", result[1])
        print("Requirement:", result[2])
        print("Frequency Limit:", str(result[3]), "years")
        print("Notes:", result[4])
    else:
        print("No coverage rules found for this combination.")
    print("")

main()
