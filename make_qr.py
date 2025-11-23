#!/usr/bin/env python3
"""
make_qr.py

Usage: python make_qr.py <url> [output.png]

Generates a QR code PNG for the given URL. Requires `qrcode` and `Pillow`.
Example:
    python make_qr.py http://localhost:8501 qr.png

The generated file will be written to the workspace so you can scan it from your phone.
"""
import sys
from pathlib import Path

try:
    import qrcode
except Exception as e:
    print("Missing required package 'qrcode'. Install with: pip install qrcode[pil]")
    raise


def make_qr(url: str, out_path: Path):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python make_qr.py <url> [output.png]")
        sys.exit(1)
    url = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("qr.png")
    make_qr(url, out)
    print(f"Saved QR to {out.resolve()}")


if __name__ == "__main__":
    main()
