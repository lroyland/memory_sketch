import os
import base64
import json
import time
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)

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
- Mouth and jaw should be simple and neutral — avoid exaggerated grins or overly expressive features
- PRIMARY FOCUS: Distorted, twisted, unnatural head shape — lopsided, elongated, crooked, asymmetrical, warped, or contorted. The head shape should be the most noticeable distortion.
- Child-like, sincere, unskilled — but more detailed than a typical kid drawing
- Expression should be neutral or slightly confused — avoid overly smiley or happy expressions
- Plain white background, no extra elements



Focus: The head shape distortion should be the most prominent feature. It should still feel naive and crude, but with more pencil marks, more shading attempts, more effort that still went wrong. Prioritize unusual, twisted head shapes over facial expressions.
"""

def build_prompt(system_prompt: str, user_text: str) -> str:
    """
    Safely merge system and user instructions for the Images API.
    """
    return f"{system_prompt.strip()}\n\n{user_text.strip()}"


async def generate_sketch_from_bytes(image_bytes: bytes) -> str:
    """
    Image-to-image using GPT-Image-1 via raw REST API (async).
    Returns a data URL.
    """
    func_start = time.time()
    logger.info("[IMAGE] Starting sketch generation...")

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

    async with httpx.AsyncClient(timeout=120.0) as client:
        api_start = time.time()
        response = await client.post(url, headers=headers, files=files, data=data)
        api_time = time.time() - api_start
        logger.info(f"[IMAGE] API POST request: {api_time:.2f}s")

        if response.status_code != 200:
            error_text = response.text
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
        image_data = response_data["data"][0]

        if "url" in image_data:
            download_start = time.time()
            img_response = await client.get(image_data["url"])
            img_response.raise_for_status()
            download_time = time.time() - download_start
            logger.info(f"[IMAGE] Image download: {download_time:.2f}s")
            
            encode_start = time.time()
            b64_out = base64.b64encode(img_response.content).decode("utf-8")
            encode_time = time.time() - encode_start
            logger.info(f"[IMAGE] Base64 encoding: {encode_time:.2f}s")
        elif "b64_json" in image_data:
            b64_out = image_data["b64_json"]
            logger.info("[IMAGE] Received base64 directly (no download needed)")
        else:
            raise RuntimeError("Unexpected API response format.")

    total_time = time.time() - func_start
    logger.info(f"[IMAGE] Total sketch generation: {total_time:.2f}s")
    return f"data:image/png;base64,{b64_out}"


# Keep synchronous version for backwards compatibility if needed
def generate_sketch_from_bytes_sync(image_bytes: bytes) -> str:
    """
    Synchronous version for backwards compatibility.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(generate_sketch_from_bytes(image_bytes))
