import sqlite3

def check_coverage(carrier_name, cdt_code):
    conn = sqlite3.connect("insurance_guardian.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT carriers.name, coverage_rules.cdt_code, coverage_rules.requirement, coverage_rules.frequency_limit_years, coverage_rules.notes
        FROM coverage_rules
        JOIN carriers ON carriers.id = coverage_rules.carrier_id
        WHERE carriers.name = ? AND coverage_rules.cdt_code = ?
    """, (carrier_name, cdt_code))
    result = cursor.fetchone()
    conn.close()
    return result

def main():
    print("================================")
    print("   AI Insurance Guardian v0.1   ")
    print("================================")
    print("")
    carrier = input("Enter carrier name: ")
    code = input("Enter procedure code: ")
    print("")
    result = check_coverage(carrier, code)
    if result:
        print("COVERAGE REQUIREMENTS:")
        print("----------------------")
        print("Carrier:", result[0])
        print("Procedure:", result[1])
        print("Requirement:", result[2])
        print("Frequency Limit:", str(result[3]), "years")
        print("Notes:", result[4])
    else:
        print("No coverage rules found for this carrier and procedure.")
    print("")

main()
