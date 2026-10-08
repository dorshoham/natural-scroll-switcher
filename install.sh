#!/bin/bash
# Installs NaturalScrollSwitcher as a login agent (runs in the background, restarts if it dies).
# Usage:  ./install.sh            install / reinstall
#         ./install.sh --uninstall
set -euo pipefail

LABEL="local.naturalscrollswitcher"
APP_DIR="$HOME/Library/Application Support/NaturalScrollSwitcher"
SCRIPT="$APP_DIR/natural_scroll_switcher.py"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/NaturalScrollSwitcher.log"
DOMAIN="gui/$(id -u)"
PY="/usr/bin/python3"

if [[ "${1:-}" == "--uninstall" ]]; then
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    rm -rf "$APP_DIR"
    echo "Uninstalled."
    exit 0
fi

SRC="$(cd "$(dirname "$0")" && pwd)/natural_scroll_switcher.py"
if [[ ! -f "$SRC" ]]; then
    echo "natural_scroll_switcher.py not found next to install.sh"
    exit 1
fi

mkdir -p "$APP_DIR" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cp "$SRC" "$SCRIPT"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>             <string>$LABEL</string>
    <key>ProgramArguments</key>  <array><string>$PY</string><string>$SCRIPT</string></array>
    <key>RunAtLoad</key>         <true/>
    <key>KeepAlive</key>         <true/>
    <key>ProcessType</key>       <string>Background</string>
    <key>StandardOutPath</key>   <string>$LOG</string>
    <key>StandardErrorPath</key> <string>$LOG</string>
</dict>
</plist>
EOF

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"

echo "Installed and running. It will start automatically at login."
echo
"$PY" "$SCRIPT" --list
echo
echo "Log: $LOG"
