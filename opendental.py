import requests
import json

OPENDENTAL_BASE_URL = "http://localhost:8080/api/v1"
OPENDENTAL_API_KEY = "your_api_key_here"

headers = {
    "Authorization": OPENDENTAL_API_KEY,
    "Content-Type": "application/json"
}

def get_patient(patient_id):
    try:
        response = requests.get(f"{OPENDENTAL_BASE_URL}/patients/{patient_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": f"Status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Open Dental. Make sure Open Dental is running."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_patient_insurance(patient_id):
    try:
        response = requests.get(f"{OPENDENTAL_BASE_URL}/insplans?PatNum={patient_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": f"Status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Open Dental."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_treatment_plan(patient_id):
    try:
        response = requests.get(f"{OPENDENTAL_BASE_URL}/proctp?PatNum={patient_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": f"Status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Open Dental."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_patients(last_name):
    try:
        response = requests.get(f"{OPENDENTAL_BASE_URL}/patients?LName={last_name}", headers=headers, timeout=5)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": f"Status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Open Dental."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_connection():
    try:
        response = requests.get(f"{OPENDENTAL_BASE_URL}/patients", headers=headers, timeout=5)
        if response.status_code in [200, 401]:
            return {"success": True, "message": "Open Dental API is reachable"}
        return {"success": False, "error": f"Unexpected status: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Open Dental. Make sure Open Dental is running and API is enabled."}
    except Exception as e:
        return {"success": False, "error": str(e)}