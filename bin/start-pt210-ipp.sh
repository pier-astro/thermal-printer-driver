#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PORT="${PT210_IPP_PORT:-8631}"

exec /usr/bin/ippeveprinter \
  -p "$PORT" \
  -r off \
  -M GOOJPRT \
  -m "PT-210 ESC/POS 48mm" \
  -f application/pdf \
  -F application/pdf \
  -c "$SCRIPT_DIR/pt210-ipp-command" \
  "PT210_IPP"
