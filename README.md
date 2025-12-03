# Memory Sketch

A FastAPI application that transforms photos into police composite sketches and generates humorous mistaken backstories using AI.

## Features

- **Sketch Generation**: Converts uploaded images into crude police composite sketches using Replicate's SDXL ControlNet model
- **Backstory Generation**: Creates intentionally mistaken and humorous backstories using OpenAI's GPT-4o vision model
- **RESTful API**: Simple FastAPI endpoint for easy integration

## Requirements

- Python 3.10+
- Replicate API token
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lroyland/memory_sketch.git
cd memory_sketch
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
REPLICATE_API_TOKEN=your_replicate_token_here
OPENAI_API_KEY=your_openai_key_here
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`

3. Test the health endpoint:
```bash
curl http://localhost:8000/health
```

4. Upload an image to generate a sketch and backstory:
```bash
curl -X POST "http://localhost:8000/memory-sketch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### `POST /memory-sketch`
Upload an image to generate a sketch and backstory.

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "sketch_url": "https://replicate.delivery/...",
  "backstory": "A confused witness describes...",
  "mode": "replicate+llm"
}
```

## Project Structure

```
memory_sketch/
├── .env                 # Environment variables (not in git)
├── .gitignore
├── main.py              # FastAPI application
├── README.md
└── services/
    ├── __init__.py
    ├── images.py        # Sketch generation service
    └── backstories.py   # Backstory generation service
```

## Technologies

- **FastAPI**: Modern web framework for building APIs
- **Replicate**: AI model hosting for sketch generation
- **OpenAI**: GPT-4o for backstory generation
- **python-dotenv**: Environment variable management

## License

This project is open source and available under the MIT License.

