#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PRINT_WIDTH_DOTS = 384
PRINT_WIDTH_BYTES = PRINT_WIDTH_DOTS // 8


def find_pdftoppm():
    env = os.environ.get("PDFTOPPM_BIN")
    if env:
        return env
    for candidate in (
        shutil.which("pdftoppm"),
        "/opt/homebrew/bin/pdftoppm",
        "/usr/local/bin/pdftoppm",
    ):
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("pdftoppm not found. Install Poppler, e.g. `brew install poppler`.")


def read_token(f):
    token = bytearray()
    while True:
        b = f.read(1)
        if not b:
            return None if not token else token.decode("ascii")
        if b == b"#":
            f.readline()
            continue
        if b.isspace():
            if token:
                return token.decode("ascii")
            continue
        token.extend(b)


def read_pbm(path):
    with open(path, "rb") as f:
        magic = read_token(f)
        if magic != "P4":
            raise ValueError(f"{path} is {magic}, expected raw PBM P4")
        width = int(read_token(f))
        height = int(read_token(f))
        row_bytes = (width + 7) // 8
        data = f.read(row_bytes * height)
    if len(data) != row_bytes * height:
        raise ValueError(f"{path} ended before all PBM data was read")
    return width, height, row_bytes, data


def bit_is_set(row, x):
    return bool(row[x // 8] & (0x80 >> (x % 8)))


def resample_row(src, src_width):
    out = bytearray(PRINT_WIDTH_BYTES)
    for x in range(PRINT_WIDTH_DOTS):
        src_x = min((x * src_width) // PRINT_WIDTH_DOTS, src_width - 1)
        if bit_is_set(src, src_x):
            out[x // 8] |= 0x80 >> (x % 8)
    return bytes(out)


def normalize_rows(width, height, row_bytes, data):
    rows = []
    left_pad = max((PRINT_WIDTH_DOTS - width) // 2, 0)
    left_bytes = left_pad // 8

    for y in range(height):
        src = data[y * row_bytes : (y + 1) * row_bytes]
        if width == PRINT_WIDTH_DOTS:
            row = src[:PRINT_WIDTH_BYTES]
        elif width < PRINT_WIDTH_DOTS and left_pad % 8 == 0:
            row = (b"\x00" * left_bytes + src)[:PRINT_WIDTH_BYTES]
            row = row.ljust(PRINT_WIDTH_BYTES, b"\x00")
        else:
            row = resample_row(src, width)
        rows.append(row)
    return b"".join(rows)


def row_bit(rows, x, y):
    row_start = y * PRINT_WIDTH_BYTES
    return bool(rows[row_start + x // 8] & (0x80 >> (x % 8)))


def escpos_escstar(rows, height):
    out = bytearray()
    out += b"\x1b@"      # initialize
    out += b"\x1ba\x01"  # center
    out += b"\x1b3\x18"  # line spacing = 24 dots

    n_l = PRINT_WIDTH_DOTS & 0xFF
    n_h = (PRINT_WIDTH_DOTS >> 8) & 0xFF

    for band_y in range(0, height, 24):
        out += b"\x1b*\x21" + bytes([n_l, n_h])
        for x in range(PRINT_WIDTH_DOTS):
            for byte_idx in range(3):
                value = 0
                for bit in range(8):
                    y = band_y + byte_idx * 8 + bit
                    if y < height and row_bit(rows, x, y):
                        value |= 0x80 >> bit
                out.append(value)
        out += b"\n"

    out += b"\x1b2"  # restore default line spacing
    out += b"\n\n\n"
    return bytes(out)


def convert_pdf(pdf_path):
    with tempfile.TemporaryDirectory(prefix="pt210-") as tmp:
        prefix = Path(tmp) / "page"
        subprocess.run(
            [
                find_pdftoppm(),
                "-q",
                "-r",
                "203",
                "-scale-to-x",
                str(PRINT_WIDTH_DOTS),
                "-scale-to-y",
                "-1",
                "-mono",
                str(pdf_path),
                str(prefix),
            ],
            check=True,
        )

        pages = sorted(Path(tmp).glob("page-*.pbm"))
        if not pages:
            single = Path(tmp) / "page.pbm"
            pages = [single] if single.exists() else []
        if not pages:
            raise RuntimeError("pdftoppm did not produce any pages")

        payload = bytearray()
        for page in pages:
            width, height, row_bytes, data = read_pbm(page)
            rows = normalize_rows(width, height, row_bytes, data)
            payload += escpos_escstar(rows, height)
        return bytes(payload)


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF to PT-210 ESC/POS bytes.")
    parser.add_argument("pdf", help="input PDF")
    parser.add_argument("-o", "--output", help="output .escpos file; defaults to stdout")
    args = parser.parse_args()

    payload = convert_pdf(Path(args.pdf))
    if args.output:
        Path(args.output).write_bytes(payload)
    else:
        sys.stdout.buffer.write(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
