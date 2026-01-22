#!/bin/bash
# Installation script for DWU systemd timer service
# This script sets up automatic wallpaper updates using systemd
# Can be run from the repository root or from the systemd directory

set -e

# Find the systemd directory - works whether script is run from repo root or systemd dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in the systemd directory (script is install.sh, dwu.service should be in same dir)
if [ -f "$SCRIPT_DIR/dwu.service" ]; then
    # Running from systemd directory (e.g., cd systemd && ./install.sh)
    SYSTEMD_DIR="$SCRIPT_DIR"
# Check if we're in repo root (systemd subdirectory should exist)
elif [ -d "$SCRIPT_DIR/systemd" ] && [ -f "$SCRIPT_DIR/systemd/dwu.service" ]; then
    # Running from repo root (e.g., ./systemd/install.sh)
    SYSTEMD_DIR="$SCRIPT_DIR/systemd"
# Check parent directory in case script was run with full path from systemd dir
elif [ -f "$(dirname "$SCRIPT_DIR")/dwu.service" ]; then
    # Parent directory has the service file
    SYSTEMD_DIR="$(dirname "$SCRIPT_DIR")"
else
    echo "Error: Could not find systemd files." >&2
    echo "Please run this script from the repository root: ./systemd/install.sh" >&2
    echo "Or from the systemd directory: cd systemd && ./install.sh" >&2
    exit 1
fi

SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "Installing DWU systemd timer service..."

# Create systemd user directory if it doesn't exist
mkdir -p "$SYSTEMD_USER_DIR"

# Copy service, timer, and wrapper script
echo "Copying systemd files..."
cp "$SYSTEMD_DIR/dwu.service" "$SYSTEMD_USER_DIR/"
cp "$SYSTEMD_DIR/dwu.timer" "$SYSTEMD_USER_DIR/"
cp "$SYSTEMD_DIR/dwu-wrapper.sh" "$SYSTEMD_USER_DIR/"
chmod +x "$SYSTEMD_USER_DIR/dwu-wrapper.sh"

# Verify dwu is in PATH
if ! command -v dwu >/dev/null 2>&1; then
    echo "Warning: 'dwu' command not found in PATH."
    echo "Make sure dwu is installed and in your PATH before enabling the service."
    echo "You can check with: which dwu"
    echo ""
fi

# Reload systemd
echo "Reloading systemd daemon..."
systemctl --user daemon-reload

# Enable and start the timer
echo "Enabling and starting dwu.timer..."
systemctl --user enable --now dwu.timer

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  Check timer status:    systemctl --user status dwu.timer"
echo "  Check next run time:   systemctl --user list-timers dwu.timer"
echo "  View logs:             journalctl --user -u dwu.service -f"
echo "  Stop the timer:        systemctl --user stop dwu.timer"
echo "  Disable the timer:     systemctl --user disable dwu.timer"
