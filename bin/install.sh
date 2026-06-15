#!/bin/sh
set -eu

APP_DIR="${HOME}/Library/Application Support/PT210"
LAUNCH_AGENTS="${HOME}/Library/LaunchAgents"
PLIST="${LAUNCH_AGENTS}/local.pt210-ipp.plist"
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
IPP_QUEUE="${PT210_IPP_QUEUE:-PT210_IPP}"
BRIDGE_QUEUE="${PT210_BRIDGE_QUEUE:-PT210_USB_BRIDGE}"
IPP_PORT="${PT210_IPP_PORT:-8631}"
DEVICE_URI="${1:-}"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing: $1" >&2
    exit 1
  }
}

need lp
need lpadmin
need ippeveprinter
need python3

if ! command -v pdftoppm >/dev/null 2>&1 &&
   [ ! -x /opt/homebrew/bin/pdftoppm ] &&
   [ ! -x /usr/local/bin/pdftoppm ]; then
  echo "Missing pdftoppm. Install Poppler first: brew install poppler" >&2
  exit 1
fi

if [ -z "$DEVICE_URI" ]; then
  DEVICE_URI=$(/usr/sbin/lpinfo -v | awk '/usb:\/\/GEZHI\/micro-printer/ { print $2; exit }')
fi

if [ -z "$DEVICE_URI" ]; then
  echo "PT-210 USB printer not found. Connect it over USB and retry." >&2
  echo "You can also pass a device URI manually:" >&2
  echo "  bin/install.sh 'usb://GEZHI/micro-printer?serial=000000000004'" >&2
  exit 1
fi

mkdir -p "$APP_DIR" "$LAUNCH_AGENTS"
rm -rf "$APP_DIR/bin"
cp -R "$SOURCE_DIR/bin" "$APP_DIR/"
chmod +x "$APP_DIR"/bin/*

tmp_err=$(mktemp "${TMPDIR:-/tmp}/pt210-lpadmin.XXXXXX")
if ! /usr/sbin/lpadmin -p "$BRIDGE_QUEUE" -E -v "$DEVICE_URI" -m drv:///sample.drv/generic.ppd -o printer-is-shared=false 2>"$tmp_err"; then
  if ! sudo /usr/sbin/lpadmin -p "$BRIDGE_QUEUE" -E -v "$DEVICE_URI" -m drv:///sample.drv/generic.ppd -o printer-is-shared=false 2>"$tmp_err"; then
    cat "$tmp_err" >&2
    rm -f "$tmp_err"
    exit 1
  fi
fi
rm -f "$tmp_err"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>local.pt210-ipp</string>
  <key>ProgramArguments</key>
  <array>
    <string>${APP_DIR}/bin/start-pt210-ipp.sh</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PT210_BRIDGE_QUEUE</key>
    <string>${BRIDGE_QUEUE}</string>
    <key>PT210_IPP_PORT</key>
    <string>${IPP_PORT}</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/pt210-ipp.out.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/pt210-ipp.err.log</string>
</dict>
</plist>
EOF
chmod 644 "$PLIST"

/bin/launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
/bin/launchctl bootstrap "gui/$(id -u)" "$PLIST"
sleep 1

tmp_err=$(mktemp "${TMPDIR:-/tmp}/pt210-lpadmin.XXXXXX")
if ! /usr/sbin/lpadmin -p "$IPP_QUEUE" -E -v "ipp://localhost:${IPP_PORT}/ipp/print" -m everywhere 2>"$tmp_err"; then
  if ! sudo /usr/sbin/lpadmin -p "$IPP_QUEUE" -E -v "ipp://localhost:${IPP_PORT}/ipp/print" -m everywhere 2>"$tmp_err"; then
    cat "$tmp_err" >&2
    rm -f "$tmp_err"
    exit 1
  fi
fi
rm -f "$tmp_err"

/usr/bin/python3 "$APP_DIR/bin/make-test-pdf.py" >/dev/null

echo "Installed:"
echo "  User printer: ${IPP_QUEUE}"
echo "  Internal USB bridge: ${BRIDGE_QUEUE}"
echo "  Runtime files: ${APP_DIR}"
echo
echo "Test:"
echo "  lp -d ${IPP_QUEUE} '${APP_DIR}/test-pt210.pdf'"
