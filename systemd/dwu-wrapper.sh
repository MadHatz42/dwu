#!/bin/bash
# Wrapper script to find and execute dwu
# This script dynamically finds the dwu binary in the PATH

# Find dwu in PATH
DWU_BIN=$(command -v dwu)

if [ -z "$DWU_BIN" ]; then
    echo "Error: dwu command not found in PATH" >&2
    exit 1
fi

# Execute dwu with --today flag (runs once, checks for new wallpaper)
exec "$DWU_BIN" --today
