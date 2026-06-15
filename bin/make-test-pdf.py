#!/usr/bin/env python3
from pathlib import Path


def esc(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(path):
    width = 136
    height = 210  # Altezza dimezzata
    
    lines = [
        (18, "PT-210"),
        (13, "TEST LARGE"),
        (10, "48mm / 203dpi"),
        (9, "If you read this,"),
        (9, "setup works."),
        (8, "----------------"),
        (8, "0123456789"),
    ]

    content = ["BT"]
    # Imposta la y iniziale in base all'altezza (es: 30 punti dal bordo superiore)
    y = height - 30 
    
    for size, text in lines:
        content.append(f"/F1 {size} Tf")
        content.append(f"1 0 0 1 8 {y} Tm")
        content.append(f"({esc(text)}) Tj")
        y -= size + 8
    content.append("ET")
    stream = "\n".join(content).encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [3 0 R] /Count 1 /MediaBox [0 0 {width} {height}] >>".encode(),
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{idx} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode()
    pdf += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    Path(path).write_bytes(pdf)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "test-pt210.pdf"
    make_pdf(out)
    print(out)