import speech_recognition as sr
import re

DENTAL_TRIGGERS = [
    "crown", "buildup", "filling", "amalgam", "composite",
    "root canal", "extraction", "implant", "bridge", "denture",
    "partial", "SRP", "scaling", "root planing", "bone loss",
    "pocket depth", "recession", "furcation", "bleeding",
    "periapical", "abscess", "pulpitis", "pulpotomy",
    "cusp fracture", "caries", "decay", "cavitation",
    "sealant", "prophylaxis", "cleaning", "x-ray", "radiograph",
    "bitewing", "panoramic", "buildup", "onlay", "inlay"
]

CDT_KEYWORDS = {
    "crown": "D2740",
    "buildup": "D2950",
    "root canal molar": "D3330",
    "root canal premolar": "D3320",
    "root canal anterior": "D3310",
    "extraction surgical": "D7210",
    "extraction simple": "D7140",
    "SRP": "D4341",
    "scaling root planing": "D4341",
    "deep cleaning": "D4341",
    "prophylaxis": "D1110",
    "cleaning": "D1110",
    "sealant": "D1351",
    "implant": "D6010",
    "denture": "D5110",
    "partial": "D5211",
    "filling": "D2393",
    "composite": "D2393",
    "amalgam": "D2160",
    "panoramic": "D0330",
    "bitewing": "D0274",
}

def detect_procedures(text):
    text_lower = text.lower()
    detected = []
    for keyword, cdt_code in CDT_KEYWORDS.items():
        if keyword.lower() in text_lower:
            detected.append({
                "keyword": keyword,
                "cdt_code": cdt_code,
                "text": text
            })
    return detected

def detect_tooth_number(text):
    patterns = [
        r'tooth\s+(?:number\s+)?(\d+)',
        r'#(\d+)',
        r'number\s+(\d+)',
        r'tooth\s+(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            tooth_num = int(match.group(1))
            if 1 <= tooth_num <= 32:
                return str(tooth_num)
    return ""

def listen_for_procedures():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            text = recognizer.recognize_google(audio)
            print(f"Heard: {text}")
            procedures = detect_procedures(text)
            tooth = detect_tooth_number(text)
            return {
                "success": True,
                "text": text,
                "procedures": procedures,
                "tooth": tooth
            }
        except sr.WaitTimeoutError:
            return {"success": False, "error": "No speech detected"}
        except sr.UnknownValueError:
            return {"success": False, "error": "Could not understand audio"}
        except sr.RequestError:
            return {"success": False, "error": "Speech service unavailable"}