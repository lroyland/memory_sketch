"""
Image-related services.
"""

import os
import io
import tempfile
import replicate
from replicate.exceptions import ModelError

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

PROMPT = (
    "loose and childish composite sketch, rough lineart, uneven pencil strokes, simplified facial geometry, black and white pencil"
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
                    "style_strength": 0.7,
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
            return result.url
        return str(result)  # Convert to string if it's already a URL
    raise RuntimeError(f"Unexpected Replicate output: {output}")

