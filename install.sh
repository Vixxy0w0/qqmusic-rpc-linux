#!/bin/bash

# --- CONFIGURATION ---
APP_NAME="qqmusic-rpc"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
SERVICE_DIR="$HOME/.config/systemd/user"
VENV_DIR="$INSTALL_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# --- UPDATE MODE ---
# Running './install.sh --update' pulls the latest files and restarts the service
if [[ "$1" == "--update" ]]; then
    echo -e "${BLUE}🔄 Updating QQ Music Discord RPC...${NC}"

    # Must be run from inside the cloned repo
    if ! git -C "$(pwd)" rev-parse --is-inside-work-tree &>/dev/null; then
        echo -e "${RED}❌ Not inside a git repo. Run this from your cloned qqmusic-rpc-linux folder.${NC}"
        exit 1
    fi

    git pull || { echo -e "${RED}❌ git pull failed.${NC}"; exit 1; }

    echo "📂 Copying updated files..."
    cp qqmusic_rpc.py "$INSTALL_DIR/"
    cp requirements.txt "$INSTALL_DIR/"

    echo "🐍 Updating dependencies..."
    "$VENV_PIP" install -q -r "$INSTALL_DIR/requirements.txt"

    echo "🔁 Restarting service..."
    systemctl --user restart "$APP_NAME"

    echo -e "${GREEN}✅ Update complete!${NC}"
    exit 0
fi

# --- FRESH INSTALL ---
echo -e "${BLUE}🎵 Installing QQ Music Discord RPC...${NC}"

# 1. Preflight: make sure python3 and python3-venv are available
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ python3 not found. Please install it first.${NC}"
    exit 1
fi

if ! python3 -c "import venv" &>/dev/null; then
    echo -e "${RED}❌ python3-venv not found.${NC}"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    echo "  Arch/CachyOS:  sudo pacman -S python (venv is included)"
    echo "  Fedora:        sudo dnf install python3"
    exit 1
fi

# 2. Create Directories
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SERVICE_DIR"

# 3. Copy Files
echo "📂 Copying files..."
cp qqmusic_rpc.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# 4. Create an isolated Python venv
echo "🐍 Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "📦 Installing dependencies into venv..."
"$VENV_PIP" install -q -r "$INSTALL_DIR/requirements.txt"

# 5. Create a wrapper script in ~/bin so 'qqmusic-rpc' works from the terminal
echo "🔗 Creating command shortcut..."
cat > "$BIN_DIR/$APP_NAME" <<WRAPPER
#!/bin/bash
exec "$VENV_PYTHON" "$INSTALL_DIR/qqmusic_rpc.py" "\$@"
WRAPPER
chmod +x "$BIN_DIR/$APP_NAME"

# 6. Systemd service with security hardening
echo "⚙️  Creating systemd service..."
cat > "$SERVICE_DIR/$APP_NAME.service" <<EOF
[Unit]
Description=QQ Music Discord RPC
After=network.target sound.target graphical-session.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_PYTHON $INSTALL_DIR/qqmusic_rpc.py
Restart=on-failure
RestartSec=5

# --- Security hardening ---
NoNewPrivileges=true
PrivateTmp=true
RestrictSUIDSGID=true
ProtectHostname=true
LockPersonality=true

[Install]
WantedBy=default.target
EOF

# 7. Enable and start
echo "🚀 Starting service..."
systemctl --user daemon-reload
systemctl --user enable "$APP_NAME"
systemctl --user restart "$APP_NAME"

# 8. Confirm it's running
sleep 2
if systemctl --user is-active --quiet "$APP_NAME"; then
    echo -e "${GREEN}✅ Installation complete! Service is running.${NC}"
else
    echo -e "${YELLOW}⚠️  Service may have failed to start. Check logs:${NC}"
    echo "   journalctl --user -u $APP_NAME -n 20 --no-pager"
fi

echo "------------------------------------------------"
echo "👉 Play a song in QQ Music and check Discord."
echo "👉 View logs:    journalctl --user -u $APP_NAME -f"
echo "👉 Update later: ./install.sh --update"
echo "------------------------------------------------"
