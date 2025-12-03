"""
Image-related services.
"""

import os
import io
import tempfile
import replicate

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

PROMPT = (
    "crude police composite sketch of the person in the reference image, "
    "black and white, pencil on rough paper, uneven line quality, "
    "inaccurate proportions, amateur witness drawing, simplified shading, "
    "low detail, slightly distorted facial features, grainy pencil texture, monochrome"
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
                "adirik/t2i-adapter-sdxl-sketch:3a14a915b013decb6ab672115c8bced7c088df86c2ddd0a89433717b9ec7d927",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "num_inference_steps": 20,
                    "guidance_scale": 6,
                },
            )
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

