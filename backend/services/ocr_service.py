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
    Preprocess image for better OCR accuracy.

    Steps:
    1. Convert to RGB if needed
    2. Upscale small images
    3. Enhance contrast
    4. Sharpen
    """
    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Upscale small images (improves OCR on phone screenshots)
    width, height = image.size
    if width < 1000:
        scale = 1500 / width
        image = image.resize(
            (int(width * scale), int(height * scale)),
            Image.Resampling.LANCZOS,
        )

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    return image


def extract_text_from_image(image_bytes: bytes) -> Dict:
    """
    Extract text from an image using EasyOCR.

    Args:
        image_bytes: Raw image bytes from uploaded file.

    Returns:
        Dict with extracted_text, confidence, line_count, and raw_results.
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
        image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Run OCR
        results = reader.readtext(img_buffer.getvalue())

        if not results:
            return {
                "success": True,
                "extracted_text": "",
                "confidence": 0.0,
                "line_count": 0,
                "warning": "No text detected in the image.",
            }

        # Aggregate results
        lines = []
        total_confidence = 0.0

        for (bbox, text, confidence) in results:
            lines.append(text)
            total_confidence += confidence

        extracted_text = "\n".join(lines)
        avg_confidence = total_confidence / len(results) if results else 0.0

        return {
            "success": True,
            "extracted_text": extracted_text,
            "confidence": round(avg_confidence, 4),
            "line_count": len(lines),
            "char_count": len(extracted_text),
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
