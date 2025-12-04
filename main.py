import os
import asyncio
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables BEFORE importing services
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from services.images import (
    generate_sketch_from_bytes,
    generate_sketch_from_bytes_sketch_lora,
    generate_sketch_from_bytes_photo2lineart,
    generate_sketch_from_bytes_pencil_sketch,
)
from services.backstories import generate_backstory_from_bytes

app = FastAPI()

# If frontend and backend are same origin, you can later tighten CORS or even remove it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (including index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/variants", response_class=HTMLResponse)
def variants_page():
    """Debug page for viewing sketch variants."""
    with open(os.path.join("static", "variants.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/memory-sketch")
async def memory_sketch(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        # Use sketch_lora model - rough sketch style
        sketch_url = generate_sketch_from_bytes_sketch_lora(
            image_bytes,
            prompt_strength=0.45,  # Balance: sketch-like but preserve features (eyes, etc.)
            guidance_scale=3.5,
            num_inference_steps=28,
            lora_scale=1.6,  # Strong sketch style but not too extreme
            model="dev",  # Better quality
            realistic_sketch=True,  # Use realistic portrait prompt
        )
        backstory = generate_backstory_from_bytes(image_bytes)

        return JSONResponse(
            {
                "sketch_url": sketch_url,
                "backstory": backstory,
                "mode": "replicate+llm",
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/sketch-variants")
async def sketch_variants(file: UploadFile = File(...)):
    """
    Returns several sketch variants for the same input image,
    so you can visually compare control_type / strength / guidance.
    
    Adds delays between generations to avoid rate limiting.
    """
    image_bytes = await file.read()

    # Different "recipes" to compare
    # Format: (model_type, params_dict, label)
    settings_list = [
        # Sketch LoRA variant (testing this one)
        ("sketch_lora", {
            "prompt_strength": 0.3,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "lora_scale": 1.2,
            "model": "dev",
        }, "Sketch LoRA: police composite"),
    ]

    variants: List[Dict] = []
    
    # Delay between requests to avoid rate limiting (10 seconds = 6 requests per minute)
    DELAY_SECONDS = 10

    for i, (model_type, params, label) in enumerate(settings_list):
        # Add delay before each request (except the first one)
        if i > 0:
            await asyncio.sleep(DELAY_SECONDS)
        
        try:
            if model_type == "controlnet":
                url = generate_sketch_from_bytes(
                    image_bytes=image_bytes,
                    **params
                )
                variant_data = {
                    "model": "controlnet",
                    "label": label,
                    "control_type": params.get("control_type", "lineart"),
                    "control_strength": params.get("control_strength", 1.0),
                    "style_strength": params.get("style_strength", 0.8),
                    "guidance_scale": params.get("guidance_scale", 3.5),
                    "steps": params.get("steps", 22),
                    "prompt_strength": params.get("prompt_strength", 0.25),
                    "url": url,
                }
            elif model_type == "sketch_lora":
                url = generate_sketch_from_bytes_sketch_lora(
                    image_bytes=image_bytes,
                    **params
                )
                variant_data = {
                    "model": "sketch_lora",
                    "label": label,
                    "prompt_strength": params.get("prompt_strength", 0.3),
                    "guidance_scale": params.get("guidance_scale", 3.5),
                    "num_inference_steps": params.get("num_inference_steps", 28),
                    "lora_scale": params.get("lora_scale", 1.2),
                    "model_type": params.get("model", "dev"),
                    "url": url,
                }
            elif model_type == "photo2lineart":
                url = generate_sketch_from_bytes_photo2lineart(
                    image_bytes=image_bytes,
                    **params
                )
                variant_data = {
                    "model": "photo2lineart",
                    "label": label,
                    "prompt_strength": params.get("prompt_strength", 0.25),
                    "guidance_scale": params.get("guidance_scale", 3.5),
                    "num_inference_steps": params.get("num_inference_steps", 20),
                    "url": url,
                }
            elif model_type == "pencil_sketch":
                url = generate_sketch_from_bytes_pencil_sketch(
                    image_bytes=image_bytes,
                    **params
                )
                variant_data = {
                    "model": "pencil_sketch",
                    "label": label,
                    "prompt_strength": params.get("prompt_strength", 0.25),
                    "guidance_scale": params.get("guidance_scale", 3.5),
                    "num_inference_steps": params.get("num_inference_steps", 20),
                    "url": url,
                }
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            variants.append(variant_data)
        except Exception as e:
            variants.append(
                {
                    "model": model_type,
                    "label": label,
                    "error": str(e),
                }
            )

    return {"variants": variants}


