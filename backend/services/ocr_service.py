"""
JobShield AI — OCR Service

Wraps EasyOCR for extracting text from uploaded screenshots.
Supports WhatsApp, Telegram, LinkedIn, Gmail, SMS, and Instagram DM screenshots.
"""

import io
import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Dict
from PIL import Image, ImageEnhance, ImageFilter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# EasyOCR is loaded lazily to avoid slow startup
_reader = None


def _get_reader():
    """Lazy-load EasyOCR reader with auto-recovery for corrupt cache."""
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(
                ["en"],
                gpu=False,
                verbose=False,
            )
            print("[OK] EasyOCR reader loaded successfully")
        except ImportError:
            print("[WARN] EasyOCR not installed. Install with: pip install easyocr")
            return None
        except Exception as e:
            # Handle corrupt model cache automatically
            model_dir = Path.home() / ".EasyOCR" / "model"
            if "BadZipFile" in str(type(e).__name__) or "CRC" in str(e):
                print("[WARN] Corrupted OCR model cache detected. Cleaning up and retrying...")
                try:
                    if model_dir.exists():
                        for f in model_dir.glob("*.zip"):
                            f.unlink(missing_ok=True)
                    import easyocr
                    _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
                    print("[OK] EasyOCR reader recovered and loaded")
                    return _reader
                except Exception as retry_err:
                    print(f"[WARN] EasyOCR retry failed: {retry_err}")
                    return None
            print(f"[WARN] EasyOCR initialization failed: {e}")
            return None
    return _reader


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for fast, accurate OCR.
    Keeps size balanced to avoid heavy CPU convolution delay.
    """
    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size
    # If image is excessively large, scale down to max 1200px width for fast OCR
    if width > 1200:
        scale = 1200 / width
        image = image.resize(
            (int(width * scale), int(height * scale)),
            Image.Resampling.BILINEAR,
        )
    elif width < 600:
        # Scale up very small phone screenshots moderately
        scale = 800 / width
        image = image.resize(
            (int(width * scale), int(height * scale)),
            Image.Resampling.BILINEAR,
        )

    # Moderate contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.3)

    return image


def extract_text_from_image(image_bytes: bytes) -> Dict:
    """
    Extract text from an image using EasyOCR with fast greedy decoding.

    Args:
        image_bytes: Raw image bytes from uploaded file.

    Returns:
        Dict with extracted_text, confidence, line_count, and char_count.
    """
    reader = _get_reader()

    if reader is None:
        return {
            "success": False,
            "extracted_text": "",
            "confidence": 0.0,
            "error": "OCR engine not available. Install easyocr.",
        }

    try:
        # Open and preprocess image
        image = Image.open(io.BytesIO(image_bytes))
        image = preprocess_image(image)

        # Convert to bytes for EasyOCR
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="JPEG", quality=85)
        img_buffer.seek(0)

        # Run OCR with fast greedy decoding and paragraph grouping
        raw_results = reader.readtext(
            img_buffer.getvalue(),
            paragraph=True,
            decoder="greedy",
            batch_size=4,
            detail=1,
        )

        if not raw_results:
            return {
                "success": True,
                "extracted_text": "",
                "confidence": 0.0,
                "line_count": 0,
                "warning": "No text detected in the image.",
            }

        lines = []
        total_confidence = 0.0

        for item in raw_results:
            if len(item) >= 2:
                # When detail=1 and paragraph=True: (bbox, text) or (bbox, text, conf)
                text = str(item[1]).strip()
                if text:
                    lines.append(text)
                conf = float(item[2]) if len(item) >= 3 and isinstance(item[2], (int, float)) else 0.85
                total_confidence += conf

        extracted_text = "\n".join(lines)
        avg_confidence = total_confidence / len(raw_results) if raw_results else 0.85

        return {
            "success": True,
            "extracted_text": extracted_text,
            "confidence": round(float(avg_confidence), 4),
            "line_count": len(lines),
            "char_count": len(extracted_text),
            "engine": "easyocr",
        }

    except Exception as e:
        return {
            "success": False,
            "extracted_text": "",
            "confidence": 0.0,
            "error": f"OCR processing failed: {str(e)}",
        }


def extract_text_from_file(file_path: str) -> Dict:
    """Extract text from an image file on disk."""
    if not os.path.exists(file_path):
        return {
            "success": False,
            "extracted_text": "",
            "error": f"File not found: {file_path}",
        }

    with open(file_path, "rb") as f:
        return extract_text_from_image(f.read())
