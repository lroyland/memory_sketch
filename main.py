"""
Main entry point for the memory_sketch application.
"""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from services.images import generate_sketch_from_bytes
from services.backstories import generate_backstory_from_bytes

load_dotenv()

app = FastAPI()

# CORS – adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/memory-sketch")
async def memory_sketch(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        # You *could* parallelize these with asyncio.gather, but serialized is fine for now
        sketch_url = generate_sketch_from_bytes(image_bytes)
        backstory = generate_backstory_from_bytes(image_bytes)

        return JSONResponse(
            {
                "sketch_url": sketch_url,
                "backstory": backstory,
                "mode": "replicate+llm",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


