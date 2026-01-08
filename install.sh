#!/bin/bash

# --- CONFIGURATION ---
APP_NAME="qqmusic-rpc"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
SERVICE_DIR="$HOME/.config/systemd/user"
PYTHON_EXEC=$(which python3)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎵 Installing QQ Music Discord RPC...${NC}"

# 1. Create Directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SERVICE_DIR"

# 2. Copy Files
echo "📂 Copying files..."
cp qqmusic_rpc.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# 3. Dependencies
echo "🐍 Installing Python requirements..."
pip3 install -r "$INSTALL_DIR/requirements.txt" --break-system-packages

# 4. Executable Shortcut
echo "🔗 Creating command shortcut..."
chmod +x "$INSTALL_DIR/qqmusic_rpc.py"
rm -f "$BIN_DIR/$APP_NAME"
ln -s "$INSTALL_DIR/qqmusic_rpc.py" "$BIN_DIR/$APP_NAME"

# 5. SERVICE FILE
echo "⚙️  Creating Systemd Service..."
cat <<EOF > "$SERVICE_DIR/$APP_NAME.service"
[Unit]
Description=QQ Music Discord RPC
After=network.target sound.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$PYTHON_EXEC $INSTALL_DIR/qqmusic_rpc.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

# 6. Enable and Start
echo "🚀 Starting service..."
systemctl --user daemon-reload
systemctl --user enable $APP_NAME
systemctl --user restart $APP_NAME

echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "------------------------------------------------"
echo "👉 Run 'qqmusic-rpc' to test manually if you want."
echo "👉 The service is already running in the background."
echo "------------------------------------------------"
