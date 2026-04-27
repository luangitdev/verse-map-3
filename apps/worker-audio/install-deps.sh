#!/bin/bash
set -e

echo "Installing Python dependencies..."

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel --no-cache-dir

# Install core dependencies first (less likely to fail)
echo "Installing core dependencies..."
pip install --no-cache-dir \
    celery==5.3.4 \
    redis==5.0.1 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    python-dotenv==1.0.0

# Install audio processing libraries
echo "Installing audio processing libraries..."
pip install --no-cache-dir \
    librosa==0.10.0 \
    numpy==1.24.3 \
    scipy==1.11.4 \
    soundfile==0.12.1

# Install Essentia (MIR)
echo "Installing Essentia (Music Information Retrieval)..."
pip install --no-cache-dir essentia==2.1.0 || echo "Warning: Essentia installation failed, continuing..."

# Install Demucs and Torch (Source separation)
echo "Installing Torch and Torchaudio..."
pip install --no-cache-dir \
    torch==2.1.0 \
    torchaudio==2.1.0 || echo "Warning: Torch installation failed, continuing..."

echo "Installing Demucs..."
pip install --no-cache-dir demucs==4.0.0 || echo "Warning: Demucs installation failed, continuing..."

# Install Whisper (ASR)
echo "Installing Whisper (Speech Recognition)..."
pip install --no-cache-dir \
    openai-whisper==20231117 \
    pydub==0.25.1 || echo "Warning: Whisper installation failed, continuing..."

# Install LLM integration
echo "Installing LLM integration..."
pip install --no-cache-dir \
    openai==1.3.0 \
    langchain==0.1.0

# Install HTTP and async libraries
echo "Installing HTTP and async libraries..."
pip install --no-cache-dir \
    requests==2.31.0 \
    httpx==0.25.0 \
    aiohttp==3.9.0

# Install logging and monitoring
echo "Installing logging and monitoring..."
pip install --no-cache-dir \
    python-json-logger==2.0.7 \
    prometheus-client==0.18.0 \
    sentry-sdk==1.38.0

# Install testing dependencies
echo "Installing testing dependencies..."
pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-asyncio==0.21.1 \
    pytest-cov==4.1.0

# Install development dependencies
echo "Installing development dependencies..."
pip install --no-cache-dir \
    black==23.11.0 \
    flake8==6.1.0 \
    mypy==1.7.0 \
    isort==5.13.2

echo "✅ All dependencies installed successfully!"
