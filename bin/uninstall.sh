#!/bin/sh
set -eu

APP_DIR="${HOME}/Library/Application Support/PT210"
PLIST="${HOME}/Library/LaunchAgents/local.pt210-ipp.plist"
QUEUES="${PT210_REMOVE_QUEUES:-PT210_IPP PT210_USB_BRIDGE PT210_USB PT210_USB_TEST PT210_USB_FILTERTEST}"

/bin/launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
rm -f "$PLIST"

for queue in $QUEUES; do
  if /usr/bin/lpstat -p "$queue" >/dev/null 2>&1; then
    if ! /usr/sbin/lpadmin -x "$queue" >/dev/null 2>&1; then
      sudo /usr/sbin/lpadmin -x "$queue" >/dev/null 2>&1 || true
    fi
  fi
done

rm -rf "$APP_DIR"
rm -f /tmp/pt210-ipp.out.log /tmp/pt210-ipp.err.log

echo "Removed PT210 queues, LaunchAgent, runtime files, and logs."
