import os
import uuid
from PIL import Image
from google import genai
from config import Config


def ensure_upload_folder():
    os.makedirs(Config.UPLOAD_DIAGRAM_FOLDER, exist_ok=True)


def save_uploaded_diagram(file_obj):
    ensure_upload_folder()

    if not file_obj or file_obj.filename == "":
        return ""

    # 1. Validate file extension
    ext = os.path.splitext(file_obj.filename)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.webp']:
        raise ValueError("Invalid file extension. Only PNG, JPG, JPEG, and WEBP diagrams are allowed.")

    # 2. Validate file size (limit to 5MB)
    try:
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
    except Exception:
        # Fallback if seek is unsupported
        size = len(file_obj.read())
        file_obj.seek(0)

    if size > 5 * 1024 * 1024:
        raise ValueError("The uploaded diagram file exceeds the 5MB size limit.")

    # 3. Verify actual image payload using Pillow
    try:
        img = Image.open(file_obj)
        img.verify()
        file_obj.seek(0) # Reset stream pointer after verification
    except Exception:
        raise ValueError("Invalid image file payload. The file is corrupted or malicious.")

    # 4. Generate secure unique filename and save
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(Config.UPLOAD_DIAGRAM_FOLDER, unique_name)
    file_obj.save(save_path)

    return save_path.replace("\\", "/")


def generate_drawing_text_from_uploaded_image(data: dict, image_path: str) -> tuple[str, str]:
    default_caption = "FIG. 1 is a schematic view of the invention."
    default_description = (
        "FIG. 1 schematically illustrates one embodiment of the invention and its principal components."
    )

    if not Config.GEMINI_API_KEY:
        return default_caption, default_description

    if not image_path or not os.path.exists(image_path):
        return default_caption, default_description

    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)

        image = Image.open(image_path)

        prompt = f"""
You are drafting a patent specification.

Analyze the uploaded invention diagram together with the invention details below.

Write:
1. A one-line patent-style caption for FIG. 1.
2. A formal drawing description paragraph suitable for:
   - Brief Description of the Drawings
   - Detailed Description of the Invention

Invention title: {data.get('title', '')}
Field: {data.get('field', '')}
Problem: {data.get('problem', '')}
Proposed solution: {data.get('proposed_solution', '')}
Working: {data.get('working', '')}
Components: {data.get('components', '')}

Return exactly in this format:

CAPTION:
...

DESCRIPTION:
...
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )

        text = response.text.strip() if getattr(response, "text", None) else ""

        caption = default_caption
        description = default_description

        if "CAPTION:" in text and "DESCRIPTION:" in text:
            parts = text.split("DESCRIPTION:", 1)
            caption = parts[0].replace("CAPTION:", "").strip() or default_caption
            description = parts[1].strip() or default_description

        return caption, description

    except Exception:
        return default_caption, default_description