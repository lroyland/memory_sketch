import os
import asyncio
import time
import logging
from dotenv import load_dotenv

# Load environment variables BEFORE importing services
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from services.images import generate_sketch_from_bytes
from services.backstories import generate_backstory_from_bytes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/memory-sketch")
async def memory_sketch(file: UploadFile = File(...)):
    request_start = time.time()
    logger.info("=" * 60)
    logger.info("Request started")
    
    image_bytes = await file.read()
    file_read_time = time.time() - request_start
    logger.info(f"File read: {file_read_time:.2f}s")

    # Run both API calls in parallel for faster response
    parallel_start = time.time()
    sketch_url, backstory = await asyncio.gather(
        generate_sketch_from_bytes(image_bytes),
        generate_backstory_from_bytes(image_bytes)
    )
    parallel_time = time.time() - parallel_start
    logger.info(f"Parallel execution (both APIs): {parallel_time:.2f}s")

    total_time = time.time() - request_start
    logger.info(f"Total request time: {total_time:.2f}s")
    logger.info("=" * 60)

    return {
        "sketch_url": sketch_url,
        "backstory": backstory,
        "mode": "gpt-image-1",
    }


