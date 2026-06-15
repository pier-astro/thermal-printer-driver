# 🚀 AirPrint/CUPS Driver for GOOJPRT PT-210 (MacOS / Apple Silicon)

Portable thermal ticket printers are now incredibly affordable and highly versatile for printing tickets, booking notifications, QR codes, or quick notes.

However, the software is often a major roadblock. The cheap consumer apps bundled with these printers are frequently unstable, restrictive, and cumbersome to use.

**This project changes that.** We provide the drivers necessary to load your thermal printer as a native MacOS printer. This allows you to use your favorite editors, applications, or scripts to design whatever you need (PDF, PNG, JPEG, Bitmaps, etc.) and seamlessly print directly from your Mac.

> 💡 **Note:** This project was specifically created and tested for the **"GOOJPRT PT-210 58mm Mini Portable Printer"** running on **Apple Silicon (M1/M2/M3/M4) MacOS Tahoe**.

# PT210 Tools

MacOS tools for a GOOJPRT PT-210, or compatible, 48 mm ESC/POS thermal printer.

After completing `SETUP.md`, print to the normal macOS printer named:

```sh
PT210_IPP
```

## Print

From any app, choose `PT210_IPP` in the print dialog.

From Terminal:

```sh
lp -d PT210_IPP document.pdf
```

Built-in test:

```sh
lp -d PT210_IPP "$HOME/Library/Application Support/PT210/test-pt210.pdf"
```

## PDF Notes

The printer is 48 mm wide, 203 dpi, black and white. PDFs are converted to a 384-dot-wide ESC/POS image before printing.

For best results, use narrow PDFs close to receipt width. A normal A4/Letter page will be scaled down and may become hard to read.

## What Runs

`PT210_IPP` is the user-facing driverless printer.

Internally, it sends jobs to `PT210_USB_BRIDGE`, a local USB queue used only to pass raw ESC/POS bytes to the printer.

Logs:

```sh
/tmp/pt210-ipp.out.log
/tmp/pt210-ipp.err.log
```

## Convert Only

To create ESC/POS bytes without printing:

```sh
bin/pt210-pdf-to-escpos.py document.pdf -o document.escpos
```

## Uninstall

```sh
bin/uninstall.sh
```
