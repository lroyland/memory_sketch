# Memory Sketch

A web application that transforms photos into rough black and white pencil sketches (like amateur police composite drawings) and generates humorous mistaken backstories using AI.

## Features

- **Sketch Generation**: Converts uploaded images into rough, amateur-style black and white pencil sketches using Replicate's SDXL Multi-ControlNet LoRA model
- **Backstory Generation**: Creates intentionally mistaken and humorous backstories using OpenAI's GPT-4o vision model
- **Web Interface**: Simple, clean web UI for uploading images and viewing results
- **RESTful API**: FastAPI backend for easy integration

## Demo

Upload a selfie and get:
- A rough black and white pencil sketch (like a witness drawing)
- A humorous mistaken backstory about the person

## Requirements

- Python 3.10+
- Replicate API token ([Get one here](https://replicate.com))
- OpenAI API key ([Get one here](https://platform.openai.com))

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/lroyland/memory_sketch.git
cd memory_sketch
```

2. **Create a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
REPLICATE_API_TOKEN=your_replicate_token_here
OPENAI_API_KEY=your_openai_key_here
```

## Usage

### Running the Server

1. **Start the FastAPI server:**
```bash
source .venv/bin/activate
export $(cat .env | xargs)  # Load environment variables
uvicorn main:app --host 0.0.0.0 --port 8001
```

2. **Access the web interface:**
Open your browser and navigate to:
```
http://localhost:8001
```

3. **Upload an image:**
- Click "Choose File" and select an image
- Click "Generate"
- Wait for the sketch and backstory to appear

### API Endpoints

#### `GET /`
Serves the web interface (HTML page).

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### `POST /memory-sketch`
Upload an image to generate a sketch and backstory.

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "sketch_url": "data:image/png;base64,...",
  "backstory": "I don't know who that is exactly, but he looks like...",
  "mode": "replicate+llm"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8001/memory-sketch" \
  -H "accept: application/json" \
  -F "file=@path/to/your/image.jpg"
```

## Project Structure

```
memory_sketch/
├── .env                 # Environment variables (not in git)
├── .gitignore
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── README.md
├── debug_server.sh      # Server debugging script
├── fix_env.sh          # Environment troubleshooting script
├── services/
│   ├── __init__.py
│   ├── images.py        # Sketch generation service (Replicate)
│   └── backstories.py   # Backstory generation service (OpenAI)
├── static/
│   └── index.html       # Web interface
└── test_*.py           # Test scripts
```

## Technologies

- **FastAPI**: Modern, fast web framework for building APIs
- **Replicate**: AI model hosting for sketch generation (fofr/sdxl-multi-controlnet-lora)
- **OpenAI**: GPT-4o for backstory generation
- **Pillow**: Image processing (grayscale conversion)
- **python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server

## How It Works

1. **Image Upload**: User uploads an image through the web interface
2. **Sketch Generation**: 
   - Image is sent to Replicate's SDXL Multi-ControlNet LoRA model
   - Model generates a rough pencil sketch using lineart control
   - Image is automatically converted to grayscale
3. **Backstory Generation**:
   - Same image is sent to OpenAI's GPT-4o vision model
   - Model generates a humorous, mistaken backstory
4. **Response**: Both sketch and backstory are returned to the user

## Configuration

### Sketch Generation Parameters

The sketch generation uses the following parameters (configured in `services/images.py`):
- **Model**: `fofr/sdxl-multi-controlnet-lora`
- **Control Type**: `lineart`
- **Style**: Rough, amateur police composite sketch
- **Output**: Black and white (automatically converted to grayscale)

### Backstory Generation

The backstory generation uses:
- **Model**: `gpt-4o` (OpenAI)
- **Style**: Humorous, mistaken witness descriptions
- **Length**: 2-3 sentences

## Troubleshooting

### Environment Variables Not Loading

If you see errors about missing API keys:

1. **Check `.env` file exists:**
```bash
cat .env
```

2. **Verify environment variables are loaded:**
```bash
source .venv/bin/activate
export $(cat .env | xargs)
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

3. **Use the debug script:**
```bash
bash debug_server.sh
```

### Server Issues

- **Port already in use**: Change the port in the uvicorn command
- **Module not found**: Make sure virtual environment is activated and dependencies are installed
- **NSFW content errors**: The model may flag certain images; try adjusting `safety_tolerance` parameter

### Testing

Run the test scripts to verify everything works:

```bash
# Test Replicate (sketch generation)
python test_replicate.py

# Test OpenAI (backstory generation)
python test_openai.py

# Test full API
python test_full_api.py
```

## Deployment

### Production Considerations

- Use a process manager like `systemd` or `supervisor` to keep the server running
- Set up a reverse proxy (nginx) in front of the application
- Use environment variables for configuration (never commit `.env`)
- Consider rate limiting for API endpoints
- Set up proper logging and monitoring

### Example systemd Service

Create `/etc/systemd/system/memory_sketch.service`:

```ini
[Unit]
Description=Memory Sketch FastAPI Application
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/memory_sketch
EnvironmentFile=/opt/memory_sketch/.env
ExecStart=/opt/memory_sketch/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable memory_sketch
sudo systemctl start memory_sketch
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created by [lroyland](https://github.com/lroyland)
