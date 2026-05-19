import os
from PIL import Image

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image(filepath, procedure_type):
    try:
        img = Image.open(filepath)
        width, height = img.size
        mode = img.mode
        file_size = os.path.getsize(filepath)

        feedback = []
        warnings = []

        if width < 800 or height < 600:
            warnings.append("Image resolution may be too low. Higher resolution images provide better documentation.")
        else:
            feedback.append("Image resolution appears adequate for documentation.")

        if file_size < 50000:
            warnings.append("File size is very small. Ensure image quality is sufficient for carrier review.")
        else:
            feedback.append("File size appears adequate.")

        if mode not in ['RGB', 'RGBA', 'L']:
            warnings.append("Unusual image format detected. Consider saving as standard JPEG or PNG.")
        else:
            feedback.append("Image format is acceptable.")

        procedure_feedback = get_procedure_feedback(procedure_type)
        feedback.extend(procedure_feedback)

        return {
            "success": True,
            "width": width,
            "height": height,
            "file_size": file_size,
            "mode": mode,
            "feedback": feedback,
            "warnings": warnings,
            "checklist_satisfied": len(warnings) == 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_procedure_feedback(procedure_type):
    feedback_map = {
        "D2740": [
    "For crown documentation: ensure the image clearly shows the affected tooth",
    "Cusp fracture or decay should be visible and unambiguous",
    "If showing cusp involvement, the image should demonstrate at least 50% cusp loss",
    "CLINICAL NOTE: If this tooth is root canal treated (RCT), a crown is the standard of care and is typically covered by most carriers regardless of cusp involvement percentage",
    "For RCT teeth: ensure the periapical radiograph showing the completed root canal is included in documentation",
    "Most carriers including Delta Dental, Cigna, and MetLife will cover a crown on an RCT tooth — document the RCT in your clinical notes and include the post-op periapical radiograph"
],
        "D4341": [
            "For SRP documentation: periodontal probing photos should show pocket depth measurements",
            "Radiograph should clearly demonstrate bone loss levels",
            "Bleeding on probing should be documented in clinical notes"
        ],
        "D3330": [
            "For root canal documentation: periapical radiograph should show the full root length",
            "Periapical pathology should be clearly visible",
            "Pre and post-operative radiographs are recommended"
        ],
        "D7240": [
            "For bony impaction documentation: panoramic or periapical radiograph required",
            "Full bony coverage of the impacted tooth should be clearly visible",
            "Relationship to adjacent structures should be documented"
        ],
        "D2950": [
            "For buildup documentation: preoperative photo should show insufficient tooth structure",
            "Remaining tooth structure should be clearly visible in image"
        ],
    }
    return feedback_map.get(procedure_type, [
        "Ensure image clearly documents the clinical finding requiring treatment",
        "Image should be in focus and properly exposed",
        "Clinical finding should be unambiguous to an independent reviewer"
    ])