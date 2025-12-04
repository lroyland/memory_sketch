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
    "low-budget police composite sketch based on vague witness memory, "
    "black and white, harsh pencil outlines, simplified and slightly wrong facial features, "
    "awkward proportions, some features exaggerated, smudged shading, "
    "grainy photocopy texture, monochrome pencil sketch"
)

NEGATIVE_PROMPT = (
    "color, colorful, soft portrait, photorealistic, smooth skin, perfect proportions, "
    "studio lighting, digital art, painting, highly detailed, glamorous, artistic rendering, "
    "photograph, photo, realistic photo, smooth, polished, refined, perfect"
)

def generate_sketch_from_bytes(
    image_bytes: bytes,
    control_type: str = "lineart",
    style_strength: float = 0.8,
    guidance_scale: float = 3.5,
    control_strength: float = 1.0,
    steps: int = 22,
    prompt_strength: float = 0.25,
) -> str:
    """
    Generate a rough police-style sketch from image bytes.

    Args:
        image_bytes: The image data as bytes
        control_type: "lineart", "canny", etc.
        style_strength: how strongly the LoRA/style is applied (0–1)
        guidance_scale: how closely to follow the prompt (lower = looser, more weird)
        control_strength: how strongly ControlNet follows the detected edges (0–1)
        steps: diffusion steps (more = slightly slower, a bit more detail)
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
                         0.2–0.35 recommended for preserving identity.

    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "fofr/sdxl-multi-controlnet-lora:89eb212b3d1366a83e949c12a4b45dfe6b6b313b594cb8268e864931ac9ffb16",
                input={
                    "image": f,
                    "control_type": control_type,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "style_strength": style_strength,
                    "guidance_scale": guidance_scale,
                    "control_strength": control_strength,
                    "num_inference_steps": steps,
                    "prompt_strength": prompt_strength,  # Key: keep most of original face
                    "safety_tolerance": 2,
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_pencil_sketch(
    image_bytes: bytes,
    prompt_strength: float = 0.25,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 20,
) -> str:
    """
    Generate a pencil sketch using tjrndll/pencil-sketch model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
        guidance_scale: how closely to follow the prompt
        num_inference_steps: number of diffusion steps
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "tjrndll/pencil-sketch:805d15ded16b6a626554ce04f4907ce2223ef5f95e7e336bde805f0b8e8bebc6",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps,
                    "prompt_strength": prompt_strength,  # Keep most of original face
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_photo2lineart(
    image_bytes: bytes,
    prompt_strength: float = 0.25,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 20,
) -> str:
    """
    Generate a pencil sketch using t2i-adapter/sdxl-photo2lineart model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
        guidance_scale: how closely to follow the prompt
        num_inference_steps: number of diffusion steps
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "t2i-adapter/sdxl-photo2lineart:latest",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps,
                    "adapter_conditioning_scale": 1.0,  # How strongly to follow the lineart
                    "adapter_conditioning_factor": 1.0,  # Conditioning factor
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_pencil_sketch(
    image_bytes: bytes,
    prompt_strength: float = 0.25,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 20,
) -> str:
    """
    Generate a pencil sketch using tjrndll/pencil-sketch model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
        guidance_scale: how closely to follow the prompt
        num_inference_steps: number of diffusion steps
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "tjrndll/pencil-sketch:805d15ded16b6a626554ce04f4907ce2223ef5f95e7e336bde805f0b8e8bebc6",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps,
                    "prompt_strength": prompt_strength,  # Keep most of original face
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_sketch_lora(
    image_bytes: bytes,
    prompt_strength: float = 0.3,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 28,
    lora_scale: float = 1.2,
    model: str = "dev",
    realistic_sketch: bool = False,
) -> str:
    """
    Generate a pencil sketch using crivera/sketch-lora model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
                        0.25-0.3 recommended for preserving identity.
        guidance_scale: how closely to follow the prompt (2-3.5 recommended)
        num_inference_steps: number of denoising steps (28 for dev model, 4 for schnell)
        lora_scale: how strongly the sketch LoRA is applied (0-1.5, higher = more sketchy)
        model: "dev" (better quality) or "schnell" (faster, needs 4 steps)
        realistic_sketch: If True, uses realistic portrait prompt; if False, uses police composite style
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            # Choose prompt based on style
            if realistic_sketch:
                # Rough sketch style - visible pencil lines, sketchy appearance, paper background
                sketch_prompt = (
                    "rough pencil sketch, hand-drawn pencil portrait, "
                    "visible pencil strokes, sketchy lines, black and white pencil drawing, "
                    "pencil shading, not smooth, rough sketch style, pencil on paper texture, "
                    "paper background, sketch paper texture, white paper background, "
                    "artistic sketch, not a photograph, sketchy appearance, all features visible"
                )
            else:
                # Police composite sketch style
                sketch_prompt = PROMPT
            
            output = replicate.run(
                "crivera/sketch-lora:32d7a493bcbd5212bf43e6a3f48b7ba716f9f159eabd13ccdbe5d0bcd747ff08",
                input={
                    "image": f,
                    "prompt": sketch_prompt,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "prompt_strength": prompt_strength,  # Keep most of original face
                    "num_inference_steps": num_inference_steps,
                    "model": model,
                    "lora_scale": lora_scale,  # Emphasize sketch style
                    "output_format": "png",  # Better quality for grayscale conversion
                    "go_fast": False,  # Quality over speed
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_pencil_sketch(
    image_bytes: bytes,
    prompt_strength: float = 0.25,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 20,
) -> str:
    """
    Generate a pencil sketch using tjrndll/pencil-sketch model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
        guidance_scale: how closely to follow the prompt
        num_inference_steps: number of diffusion steps
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "tjrndll/pencil-sketch:805d15ded16b6a626554ce04f4907ce2223ef5f95e7e336bde805f0b8e8bebc6",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps,
                    "prompt_strength": prompt_strength,  # Keep most of original face
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_photo2lineart(
    image_bytes: bytes,
    prompt_strength: float = 0.25,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 20,
) -> str:
    """
    Generate a pencil sketch using t2i-adapter/sdxl-photo2lineart model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
        guidance_scale: how closely to follow the prompt
        num_inference_steps: number of diffusion steps
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "t2i-adapter/sdxl-photo2lineart:latest",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps,
                    "adapter_conditioning_scale": 1.0,  # How strongly to follow the lineart
                    "adapter_conditioning_factor": 1.0,  # Conditioning factor
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")


def generate_sketch_from_bytes_pencil_sketch(
    image_bytes: bytes,
    prompt_strength: float = 0.25,
    guidance_scale: float = 3.5,
    num_inference_steps: int = 20,
) -> str:
    """
    Generate a pencil sketch using tjrndll/pencil-sketch model.
    
    Args:
        image_bytes: The image data as bytes
        prompt_strength: denoising strength (0–1). Lower = keep more of original face.
        guidance_scale: how closely to follow the prompt
        num_inference_steps: number of diffusion steps
        
    Returns:
        Base64-encoded data URL of the grayscale sketch image
    """
    # Replicate needs a file object, so we'll use a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, 'rb') as f:
            output = replicate.run(
                "tjrndll/pencil-sketch:805d15ded16b6a626554ce04f4907ce2223ef5f95e7e336bde805f0b8e8bebc6",
                input={
                    "image": f,
                    "prompt": PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "guidance_scale": guidance_scale,
                    "num_inference_steps": num_inference_steps,
                    "prompt_strength": prompt_strength,  # Keep most of original face
                },
            )
    except ModelError as e:
        error_msg = str(e)
        if "NSFW" in error_msg:
            raise ValueError(
                "The image was flagged by content moderation. "
                "This can happen with certain images. Please try a different image or try again."
            )
        raise
    finally:
        os.unlink(tmp_file_path)

    if isinstance(output, list) and output:
        result = output[-1] if len(output) > 1 else output[0]
        if hasattr(result, 'url'):
            url = result.url
        else:
            url = str(result)

        # Force grayscale conversion by downloading, converting, and returning as data URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))

            if img.mode != 'L':
                img = img.convert('L')

            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            img_b64 = base64.b64encode(img_bytes_io.read()).decode('utf-8')
            return f"data:image/png;base64,{img_b64}"
        except Exception as e:
            print(f"Warning: Could not convert to grayscale: {e}")
            return url

    raise RuntimeError(f"Unexpected Replicate output: {output}")

