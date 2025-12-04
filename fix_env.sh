#!/bin/bash
# Script to fix environment variable issues on the server
# Run this on the server: ssh administrator@93.127.137.244 'bash -s' < fix_env.sh

echo "=== Fixing Environment Variables ==="
echo ""

APP_DIR="/opt/memory_sketch"
cd "$APP_DIR" || { echo "❌ Cannot access $APP_DIR"; exit 1; }

echo "1. Checking .env file..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    echo "Contents:"
    cat .env
    echo ""
    
    # Check if keys are set
    if grep -q "OPENAI_API_KEY" .env && grep -q "REPLICATE_API_TOKEN" .env; then
        echo "✅ API keys found in .env"
    else
        echo "❌ API keys missing in .env"
        exit 1
    fi
else
    echo "❌ .env file not found!"
    echo "Creating .env file template..."
    cat > .env << 'EOF'
REPLICATE_API_TOKEN=your_replicate_token_here
OPENAI_API_KEY=your_openai_key_here
EOF
    echo "⚠️  Please edit .env file with your actual API keys"
    exit 1
fi

echo ""
echo "2. Testing environment variable loading..."
source .venv/bin/activate 2>/dev/null || echo "⚠️  Virtual env not found or already activated"

python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('REPLICATE_API_TOKEN:', 'SET' if os.getenv('REPLICATE_API_TOKEN') else 'NOT SET')
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
"

echo ""
echo "3. Checking how the server is started..."
if systemctl is-active --quiet memory_sketch 2>/dev/null; then
    echo "✅ Running as systemd service"
    echo "Service file location:"
    systemctl status memory_sketch | head -5
    echo ""
    echo "⚠️  If using systemd, you may need to add EnvironmentFile in service file"
elif pgrep -f "uvicorn main:app" > /dev/null; then
    echo "✅ Running as uvicorn process"
    ps aux | grep "uvicorn main:app" | grep -v grep
    echo ""
    echo "⚠️  Make sure the process is started with environment variables loaded"
else
    echo "❌ Server not running"
fi

echo ""
echo "=== Fix Instructions ==="
echo ""
echo "If environment variables are not loading:"
echo ""
echo "Option 1: Restart the server with environment loaded:"
echo "  cd $APP_DIR"
echo "  source .venv/bin/activate"
echo "  export \$(cat .env | xargs)"
echo "  uvicorn main:app --host 0.0.0.0 --port 8001"
echo ""
echo "Option 2: If using systemd, update service file to include:"
echo "  EnvironmentFile=/opt/memory_sketch/.env"
echo ""
echo "Option 3: Add to systemd service file:"
echo "  [Service]"
echo "  EnvironmentFile=/opt/memory_sketch/.env"
echo "  Environment=\"REPLICATE_API_TOKEN=\${REPLICATE_API_TOKEN}\""
echo "  Environment=\"OPENAI_API_KEY=\${OPENAI_API_KEY}\""

