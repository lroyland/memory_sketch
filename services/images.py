import os
import base64
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ----- PROMPTS -----

SYSTEM_PROMPT = """
You are an image transformation assistant. Follow user instructions exactly.
Do not mention: narrative, escalation, plot, story structure, genre, analysis,
archetype, character arc, or any meta-writing terms.
"""

USER_TEXT = """
Create a black-and-white pencil police composite sketch based on the input photo. Distort the face in the photo to make it look 
assymetrical. Make the face slightly deformed. Have a wavy distortion on the shape of the face with slight deformity.
Use the style of an amateur 1980s police sketch but drawn by a child: slightly inaccurate proportions,
uneven pencil lines, simplified features, and rough shading. The eyes should be
a bit mismatched, and the hair rendered with loose,
imprecise strokes. Keep the likeness recognizable but clearly off. No background—
just a plain white forensic-sketch sheet. Make it look like a real composite 
someone might have drawn quickly during an interview. Make it look like a child trying to draw it.

"""

def build_prompt(system_prompt: str, user_text: str) -> str:
    """
    Safely merge system and user instructions for the Images API.
    """
    return f"{system_prompt.strip()}\n\n{user_text.strip()}"


def generate_sketch_from_bytes(image_bytes: bytes) -> str:
    """
    Image-to-image using GPT-Image-1 via raw REST API.
    Returns a data URL.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    url = "https://api.openai.com/v1/images/edits"

    prompt = build_prompt(SYSTEM_PROMPT, USER_TEXT)

    files = {
        "image": ("image.png", image_bytes, "image/png")
    }
    
    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024"
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        raise RuntimeError(
            f"Image API failed [{response.status_code}]: {response.text}"
        )

    response_data = response.json()
    image_data = response_data["data"][0]

    if "url" in image_data:
        img = requests.get(image_data["url"])
        img.raise_for_status()
        b64_out = base64.b64encode(img.content).decode("utf-8")
    elif "b64_json" in image_data:
        b64_out = image_data["b64_json"]
    else:
        raise RuntimeError("Unexpected API response format.")

    return f"data:image/png;base64,{b64_out}"
