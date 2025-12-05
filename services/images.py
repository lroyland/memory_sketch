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
Create a black-and-white pencil portrait of a fictional person loosely based on the input photo, but not posed the same. It should look like a police sketch portrait drawn by a younger child with very poor observational ability.



Style requirements:
- Extremely simple shapes and thick, clumsy linework
- Many visible pencil strokes and overlapping lines — rough shading, repeated attempts, sketchy hair texture
- Very uneven, mismatched eyes and facial features (too close, one bigger, wrong alignment)
- Exaggerated cartoon-like mouth and jaw — big grin or stretched proportions
- Distorted, unnatural head shape (lopsided, elongated, crooked)
- Child-like, sincere, unskilled — but more detailed than a typical kid drawing
- Expression can be smiley, confused, or surprised, but never sinister, moody, or dark
- Plain white background, no extra elements



Focus: It should still feel naive and crude, but with more pencil marks, more shading attempts, more effort that still went wrong.
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
