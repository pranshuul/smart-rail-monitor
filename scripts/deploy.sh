#!/bin/bash

echo "🚀 Starting Smart Railway Project Deployment..."

# Step 1: Check Python and pip
echo "🔍 Checking Python..."
if ! command -v python3 &>/dev/null; then
  echo "❌ Python3 not found. Please install Python 3.x"
  exit 1
fi

if ! command -v pip3 &>/dev/null; then
  echo "❌ pip3 not found. Please install pip for Python 3"
  exit 1
fi

# Step 2: Set up Python virtual environment
echo "📦 Setting up virtual environment..."
cd flask_dashboard
python3 -m venv .venv
source .venv/bin/activate

# Step 3: Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Step 4: Launch Flask dashboard
echo "🌐 Launching Flask dashboard..."
export FLASK_APP=flask_app.py
export FLASK_ENV=development

export YOUR_THINGSPEAK_READ_KEY=NDF06NG7FIFAWDNK
export YOUR_CHANNEL_ID=2925813
export YOUR_THINGSPEAK_API_KEY=3GDTO22V308LUSY5

flask run --host=0.0.0.0 --port=5000

# Step 5 (Reminder): Flash ESP32 firmware
echo ""
echo "⚠️  NOTE: To upload the firmware to ESP32, use Arduino IDE or ESP32 CLI tools."
echo "   Firmware is located at: firmware/firmware.ino"
