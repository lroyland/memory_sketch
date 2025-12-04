# Memory Sketch

A FastAPI application that transforms photos into rough pencil sketches and generates fictional "memory" style backstories using AI.

## Features

- **Sketch Generation**: Converts uploaded images into black-and-white, rough amateur police composite-style sketches using OpenAI's `gpt-image-1` model
- **Memory Backstories**: Creates playful, fictional "I vaguely remember meeting you" style stories using OpenAI's GPT-4o vision model
- **Web Interface**: Beautiful, modern web UI for easy interaction
- **RESTful API**: Simple FastAPI endpoint for programmatic access

## Requirements

- Python 3.10+
- OpenAI API key (with access to `gpt-image-1` model)
- Your OpenAI organization must be verified to use `gpt-image-1`

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
OPENAI_API_KEY=your_openai_key_here
```

**Note**: To use `gpt-image-1`, your OpenAI organization must be verified. Visit [OpenAI Organization Settings](https://platform.openai.com/settings/organization/general) and click "Verify Organization". Access may take up to 15 minutes to propagate.

## Usage

1. Start the FastAPI server:
```bash
source .venv/bin/activate
export $(cat .env | xargs)
uvicorn main:app --port 8001 --host 0.0.0.0 --reload
```

2. Open the web interface:
   - Navigate to `http://localhost:8001/` in your browser
   - Upload an image and click "Generate sketch & backstory"

3. Or use the API directly:
```bash
curl -X POST "http://localhost:8001/memory-sketch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

## API Endpoints

### `GET /`
Serves the web interface (HTML page).

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
  "sketch_url": "data:image/png;base64,...",
  "backstory": "I vaguely remember meeting you at...",
  "mode": "gpt-image-1"
}
```

The `sketch_url` is a base64-encoded data URL that can be displayed directly in HTML.

## Project Structure

```
memory_sketch/
├── .env                 # Environment variables (not in git)
├── .gitignore
├── main.py              # FastAPI application
├── README.md
├── requirements.txt     # Python dependencies
├── services/
│   ├── __init__.py
│   ├── images.py        # Sketch generation via gpt-image-1
│   └── backstories.py   # Memory-style backstory generation
└── static/
    └── index.html       # Web interface
```

## Technologies

- **FastAPI**: Modern web framework for building APIs
- **OpenAI gpt-image-1**: Image-to-image transformation for sketch generation
- **OpenAI GPT-4o**: Vision model for backstory generation
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for API calls

## Branches

- **`master`**: Stable version (may use different image generation models)
- **`gpt-image-1`**: Current development branch using OpenAI's gpt-image-1 model
- **`experimental-sketch-updates`**: Experimental branch with various sketch model experiments

## Troubleshooting

### Organization Verification Error
If you see an error about organization verification:
1. Visit https://platform.openai.com/settings/organization/general
2. Click "Verify Organization"
3. Wait up to 15 minutes for access to propagate

### API Errors
- Ensure your OpenAI API key is set in `.env`
- Check that your organization has access to `gpt-image-1`
- Verify the API key has sufficient credits

## License

This project is open source and available under the MIT License.
