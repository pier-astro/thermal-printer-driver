# PT210 Setup

USB setup on macOS for a GOOJPRT PT-210, or compatible, 48 mm ESC/POS thermal printer.

## Requirements

- macOS
- Printer connected by USB, powered on, and loaded with paper
- Poppler, for `pdftoppm`

If needed, install Poppler with Homebrew:

```sh
brew install poppler
```

## Install

From this repository:

```sh
cd pt210-tools
bin/install.sh
```

The installer automatically detects the usual USB device:

```sh
usb://GEZHI/micro-printer?serial=000000000004
```

If auto-detection fails, list devices and pass the URI manually:

```sh
lpinfo -v
bin/install.sh 'usb://GEZHI/micro-printer?serial=000000000004'
```

## Test

```sh
lp -d PT210_IPP "$HOME/Library/Application Support/PT210/test-pt210.pdf"
```

If it prints, use `PT210_IPP` from any app or with:

```sh
lp -d PT210_IPP document.pdf
```

## What It Installs

- `PT210_IPP`: normal macOS driverless printer
- `PT210_USB_BRIDGE`: internal USB queue for raw ESC/POS bytes
- `~/Library/Application Support/PT210`: runtime scripts and test PDF
- `~/Library/LaunchAgents/local.pt210-ipp.plist`: starts the local IPP bridge
- `/tmp/pt210-ipp.out.log` and `/tmp/pt210-ipp.err.log`: bridge logs

The visible printer is driverless. The internal USB queue exists because the PT-210 is a USB ESC/POS device, not a native IPP printer.

## Uninstall

```sh
cd pt210-tools
bin/uninstall.sh
```

Removes:

- `PT210_IPP`
- `PT210_USB_BRIDGE`
- old experimental queues, if present: `PT210_USB`, `PT210_USB_TEST`, `PT210_USB_FILTERTEST`
- `~/Library/Application Support/PT210`
- `~/Library/LaunchAgents/local.pt210-ipp.plist`
- `/tmp/pt210-ipp.out.log` and `/tmp/pt210-ipp.err.log`
