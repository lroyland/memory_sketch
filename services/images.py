import os
import base64
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ----- PROMPTS -----

SKETCH_USER_PROMPT = """
Convert this portrait into a black-and-white, rough, amateur police composite sketch.
Style requirements:
- Hand-drawn pencil look
- Uneven sketchy lines
- Imperfect proportions
- No grayscale shading, only pencil lines
- Not an exact likeness; slightly off is good
"""


def generate_sketch_from_bytes(image_bytes: bytes) -> str:
    """
    Image-to-image using GPT-Image-1 via raw REST API.
    Returns a data URL.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    url = "https://api.openai.com/v1/images/edits"

    # Use multipart/form-data as required by the API
    files = {
        "image": ("image.png", image_bytes, "image/png")
    }
    
    data = {
        "model": "gpt-image-1",
        "prompt": SKETCH_USER_PROMPT,
        "size": "1024x1024"
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
        # Don't set Content-Type - requests will set it automatically for multipart
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        error_text = response.text
        # Provide helpful error messages for common issues
        if response.status_code == 403:
            try:
                error_data = response.json()
                if "gpt-image-1" in error_text and "verified" in error_text.lower():
                    raise RuntimeError(
                        "Your OpenAI organization needs to be verified to use gpt-image-1. "
                        "Please visit https://platform.openai.com/settings/organization/general "
                        "and click 'Verify Organization'. Access may take up to 15 minutes to propagate."
                    )
            except (ValueError, KeyError):
                pass
        
        raise RuntimeError(
            f"Image API failed [{response.status_code}]: {error_text}"
        )

    response_data = response.json()

    # Extract image - check for both URL and base64 formats
    image_data = response_data["data"][0]
    
    if "url" in image_data:
        # Response contains URL - download and convert to base64
        image_url = image_data["url"]
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        b64_out = base64.b64encode(img_response.content).decode("utf-8")
    elif "b64_json" in image_data:
        # Response contains base64 directly
        b64_out = image_data["b64_json"]
    else:
        # Unexpected response format
        raise RuntimeError(
            f"Unexpected API response format. Expected 'url' or 'b64_json' in response. "
            f"Got: {list(image_data.keys())}"
        )
    
    return f"data:image/png;base64,{b64_out}"
