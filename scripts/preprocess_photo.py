#!/usr/bin/env python3
"""
preprocess_photo.py — Background removal + subject isolation for dithering.
Uses rembg (U²-Net) to remove background, composites subject on black (dark mode)
or white (light mode), saves to assets/portrait-dark.png and assets/portrait-light.png.

Usage:
    python preprocess_photo.py <photo_path>
"""

import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

def remove_background(photo_path):
    """Remove background using rembg and return RGBA image."""
    try:
        from rembg import remove
        with open(photo_path, "rb") as f:
            data = f.read()
        result = remove(data)
        from io import BytesIO
        img = Image.open(BytesIO(result)).convert("RGBA")
        print(f"  Background removed via rembg: {img.size}")
        return img
    except Exception as e:
        print(f"  rembg failed ({e}), using luminance fallback")
        return None

def make_portrait(rgba_img, bg_color=(0, 0, 0)):
    """Composite RGBA over a solid background colour."""
    bg = Image.new("RGB", rgba_img.size, bg_color)
    bg.paste(rgba_img, mask=rgba_img.split()[3])
    return bg

def crop_to_portrait(img, target_w=320, target_h=340):
    """Crop to head+shoulders portrait ratio."""
    w, h = img.size
    target_ratio = target_w / target_h

    # Find where the subject is (top of non-black pixels)
    arr = np.array(img.convert("L"))
    rows_with_content = np.where(arr.max(axis=1) > 10)[0]
    top = int(rows_with_content[0]) if len(rows_with_content) > 0 else 0

    # Crop to portrait aspect from top of subject
    crop_h = min(h - top, int((w) / target_ratio))
    crop_w = int(crop_h * target_ratio)
    if crop_w > w:
        crop_w = w
        crop_h = int(crop_w / target_ratio)

    left = (w - crop_w) // 2
    img = img.crop((left, top, left + crop_w, top + crop_h))
    return img.resize((target_w, target_h), Image.LANCZOS)

def main():
    if len(sys.argv) < 2:
        print("Usage: python preprocess_photo.py <photo_path>")
        sys.exit(1)

    photo_path = sys.argv[1]
    out_dir = "assets"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading: {photo_path}")
    rgba = remove_background(photo_path)

    if rgba is None:
        # Fallback: no background removal
        img = Image.open(photo_path).convert("RGB")
        dark_img = img
        light_img = img
    else:
        # Dark mode: subject on pure black → face is bright dots on dark bg
        dark_img = make_portrait(rgba, bg_color=(0, 0, 0))
        # Light mode: subject on pure white → face is dark on light bg
        light_img = make_portrait(rgba, bg_color=(255, 255, 255))

    for name, img in [("portrait-dark.png", dark_img), ("portrait-light.png", light_img)]:
        cropped = crop_to_portrait(img)
        # Enhance
        from PIL import ImageOps
        cropped = ImageOps.autocontrast(cropped, cutoff=1)
        cropped = ImageEnhance.Contrast(cropped).enhance(1.25)
        cropped = cropped.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
        out = os.path.join(out_dir, name)
        cropped.save(out, "PNG")
        print(f"  Saved: {out} ({os.path.getsize(out)//1024}KB)")

    print("Done — now run: python scripts/generate_banner.py assets/portrait-dark.png .")

if __name__ == "__main__":
    main()
