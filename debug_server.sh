#!/bin/bash
# Debug script to run on the remote server
# Usage: ssh administrator@93.127.137.244 'bash -s' < debug_server.sh

echo "=== Memory Sketch Server Debug Script ==="
echo ""

# Find the application directory
echo "1. Finding application directory..."
APP_DIR=$(find ~ -name "memory_sketch" -type d 2>/dev/null | head -1)
if [ -z "$APP_DIR" ]; then
    APP_DIR=$(find /home -name "memory_sketch" -type d 2>/dev/null | head -1)
fi
if [ -z "$APP_DIR" ]; then
    APP_DIR=$(find /var/www -name "memory_sketch" -type d 2>/dev/null | head -1)
fi

if [ -z "$APP_DIR" ]; then
    echo "❌ Application directory not found!"
    exit 1
fi

echo "✅ Found application at: $APP_DIR"
cd "$APP_DIR"
echo ""

# Check if virtual environment exists
echo "2. Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found"
fi
echo ""

# Check if .env file exists
echo "3. Checking environment variables..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "REPLICATE_API_TOKEN" .env && grep -q "OPENAI_API_KEY" .env; then
        echo "✅ API keys found in .env"
    else
        echo "❌ API keys missing in .env"
    fi
else
    echo "❌ .env file not found!"
fi
echo ""

# Check if required files exist
echo "4. Checking required files..."
[ -f "main.py" ] && echo "✅ main.py exists" || echo "❌ main.py missing"
[ -f "requirements.txt" ] && echo "✅ requirements.txt exists" || echo "❌ requirements.txt missing"
[ -d "services" ] && echo "✅ services/ directory exists" || echo "❌ services/ directory missing"
[ -d "static" ] && echo "✅ static/ directory exists" || echo "❌ static/ directory missing"
echo ""

# Check if dependencies are installed
echo "5. Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    exit 1
fi

echo "Using: $PYTHON_CMD"
$PYTHON_CMD -c "import fastapi; print('✅ fastapi installed')" 2>/dev/null || echo "❌ fastapi not installed"
$PYTHON_CMD -c "import replicate; print('✅ replicate installed')" 2>/dev/null || echo "❌ replicate not installed"
$PYTHON_CMD -c "import openai; print('✅ openai installed')" 2>/dev/null || echo "❌ openai not installed"
$PYTHON_CMD -c "from PIL import Image; print('✅ Pillow installed')" 2>/dev/null || echo "❌ Pillow not installed"
echo ""

# Check if server is running
echo "6. Checking if server is running..."
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo "✅ uvicorn process found:"
    ps aux | grep "uvicorn main:app" | grep -v grep
else
    echo "❌ uvicorn process not running"
fi
echo ""

# Check what's listening on common ports
echo "7. Checking listening ports..."
netstat -tlnp 2>/dev/null | grep -E ":8000|:8001|:80" || ss -tlnp 2>/dev/null | grep -E ":8000|:8001|:80"
echo ""

# Try to import the application
echo "8. Testing application import..."
cd "$APP_DIR"
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
$PYTHON_CMD -c "from main import app; print('✅ Application imports successfully')" 2>&1
echo ""

# Check recent logs (if any)
echo "9. Checking for log files..."
find "$APP_DIR" -name "*.log" -type f -mtime -1 2>/dev/null | head -5
if [ -f "/var/log/memory_sketch.log" ]; then
    echo "Recent log entries:"
    tail -20 /var/log/memory_sketch.log
fi
echo ""

echo "=== Debug Complete ==="

