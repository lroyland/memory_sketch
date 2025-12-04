import os
from dotenv import load_dotenv

# Load environment variables BEFORE importing services
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from services.images import generate_sketch_from_bytes
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/memory-sketch")
async def memory_sketch(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


