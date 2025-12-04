"""
Image-related services.
"""

import os
import io
import tempfile
import replicate
from replicate.exceptions import ModelError
from PIL import Image
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

PROMPT = (
    "black and white pencil sketch, monochrome grayscale, rough amateur police composite sketch, "
    "uneven pencil lines, basic shading, simplified features, witness drawing style, "
    "forensic composite, black and white only, no color"
)

NEGATIVE_PROMPT = (
    "color, colorful, colored, child, children, childish, kid, kids, "
    "clean lines, smooth shading, photorealistic, professional, detailed, "
    "perfect proportions, polished, refined, artistic, vibrant colors, color palette"
)

def generate_sketch_from_bytes(image_bytes: bytes) -> str:
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name
    
    try:
        # Open the file for Replicate - pass file object directly
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "fofr/sdxl-multi-controlnet-lora:89eb212b3d1366a83e949c12a4b45dfe6b6b313b594cb8268e864931ac9ffb16",
                input={
                    "image": f,
                    "control_type": "lineart",
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "style_strength": 0.9,  # Higher to enforce the rough style
                    "guidance_scale": 3,  # Lower to allow more variation/roughness
                    "safety_tolerance": 2,  # Try to reduce NSFW filtering (0-6, higher = less strict)
                },
            )
    except ModelError as e:
        # Handle NSFW detection or other model errors
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)
    if isinstance(output, list) and output:
        # Return the last item (final output), or first if only one item
        result = output[-1] if len(output) > 1 else output[0]
        # Extract URL if it's a FileOutput object, otherwise use as-is
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)
        
        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to grayscale if it's not already
            if img.mode != 'L':
                img = img.convert('L')
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Convert to base64 data URL
            img_b64 = base64.b64encode(img_bytes.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            # If conversion fails, return original URL
            # Log the error but don't fail completely
            print(f"Warning: Could not convert to grayscale: {e}")
            return url
    
    raise RuntimeError(f"Unexpected Replicate output: {output}")

