"""
Image-related services.
"""

import os
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
    output = replicate.run(
        "lucataco/sdxl-controlnet",  # or whichever model you choose
        input={
            "image": image_bytes,
            "prompt": PROMPT,
            "num_inference_steps": 20,
            "guidance_scale": 6,
        },
    )
    if isinstance(output, list) and output:
        return output[0]  # URL of generated sketch
    raise RuntimeError(f"Unexpected Replicate output: {output}")

