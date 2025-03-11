#!/bin/bash

set -e  # Exit script if any command fails

# Detect OS (Linux or Windows)
OS="$(uname -s)"
if [[ "$OS" == "Linux" ]]; then
    USER_HOME="$HOME"
elif [[ "$OS" == "MINGW64_NT"* || "$OS" == "CYGWIN_NT"* || "$OS" == "MSYS_NT"* ]]; then
    USER_HOME="$(cygpath -u "$USERPROFILE")"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

# Define the volume directory
VOLUME_DIR="$USER_HOME/docker/hestia-logs"

# Create the directory if it doesn't exist
if [ ! -d "$VOLUME_DIR" ]; then
    echo "📁 Creating directory: $VOLUME_DIR"
    mkdir -p "$VOLUME_DIR"
else
    echo "✅ Directory already exists: $VOLUME_DIR"
fi

# Set permissions
if [[ "$OS" == "Linux" ]]; then
    echo "🔑 Setting permissions on Linux"
    sudo chmod -R 777 "$VOLUME_DIR"
elif [[ "$OS" == "MINGW64_NT"* || "$OS" == "CYGWIN_NT"* || "$OS" == "MSYS_NT"* ]]; then
    echo "🔑 Windows detected, setting full access"
    icacls "$(cygpath -w "$VOLUME_DIR")" /grant Everyone:F /T
fi

# Start Docker Compose
echo "🚀 Starting Docker Compose..."
docker compose up --build -d

echo "🎉 Setup complete! Logs will be stored in: $VOLUME_DIR"
