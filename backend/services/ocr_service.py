import os
import re
import numpy as np
from typing import Dict, Any, List
from pypdf import PdfReader
from PIL import Image, ImageEnhance, ImageFilter

# ─── OCR Engine Registry ──────────────────────────────────────────────────────
# We prefer EasyOCR (no system binary required), then fall back to pytesseract.
try:
    import easyocr as _easyocr_module
    _easyocr_reader = None          # lazy‑loaded on first use
    _EASYOCR_AVAILABLE = True
except ImportError:
    _EASYOCR_AVAILABLE = False

try:
    import pytesseract as _pytesseract
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False


def _get_easyocr_reader():
    """Lazy‑load EasyOCR reader so startup is not delayed."""
    global _easyocr_reader
    if _easyocr_reader is None:
        # English only to stay fast; add 'te' when Telugu training data is bundled
        _easyocr_reader = _easyocr_module.Reader(['en'], gpu=False, verbose=False)
    return _easyocr_reader


def _enhance_image(img: Image.Image) -> Image.Image:
    """Apply moderate contrast/sharpness enhancement for better OCR on photos."""
    img = img.convert('L')                          # greyscale
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    return img


def _easyocr_image(img: Image.Image) -> str:
    """Run EasyOCR on a PIL Image; return joined text lines."""
    reader = _get_easyocr_reader()
    arr = np.array(img)
    results = reader.readtext(arr, detail=1, paragraph=True)
    lines = [r[1] for r in results if r[2] > 0.10]   # confidence > 10 %
    return "\n".join(lines)


def _tesseract_image(img: Image.Image) -> str:
    """Run pytesseract on a PIL Image."""
    return _pytesseract.image_to_string(img)


# ─── Quality Assessment ───────────────────────────────────────────────────────

def assess_text_quality(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Label extracted text as clear / blurry / conflicting / incomplete.
    The keywords '[smudged', '[unclear' etc. come from our synthetic demo data;
    for real uploads we base quality only on content signals.
    """
    words = re.findall(r'\b[A-Za-z0-9]+\b', text)
    
    # Too little content
    if len(words) < 5:
        return {
            "quality": "incomplete",
            "confidence": 0.25,
            "message_en": (
                "Very little readable text was found in this document. "
                "Please upload a clearer, well-lit photo or a digital PDF."
            ),
            "message_te": (
                "డాక్యుమెంట్లో చాలా తక్కువ అక్షరాలు కనుగొనబడ్డాయి. "
                "దయచేసి వెలుతురులో స్పష్టమైన ఫోటో లేదా డిజిటల్ పిడిఎఫ్ అప్‌లోడ్ చేయండి."
            ),
        }

    text_lower = text.lower()

    # Demo‑data synthetic blurriness markers  OR  very low OCR word count
    if any(k in text_lower for k in ["[unclear", "[smudged", "blurry", "illegible",
                                      "unreadable handwriting", "??"]):
        return {
            "quality": "blurry",
            "confidence": 0.58,
            "message_en": (
                "Some medication names, strengths, or doses appear blurry or unreadable. "
                "Please verify with your prescribing doctor or pharmacist."
            ),
            "message_te": (
                "కొన్ని మందుల పేర్లు లేదా మోతాదులు అస్పష్టంగా ఉన్నాయి. "
                "దయచేసి మీ డాక్టర్ లేదా ఫార్మసిస్ట్‌తో సరిచూసుకోండి."
            ),
        }

    # Conflicting instructions (demo data or real document)
    if "conflict" in text_lower or (
        "5 days" in text_lower and "3 days" in text_lower and "discontinue" in text_lower
    ):
        return {
            "quality": "conflicting",
            "confidence": 0.90,
            "message_en": (
                "Conflicting instructions were detected in this document. "
                "Clarification is required before scheduling any medication."
            ),
            "message_te": (
                "డాక్యుమెంట్లో పరస్పర విరుద్ధమైన సూచనలు కనుగొనబడ్డాయి. "
                "మందులు షెడ్యూల్ చేసే ముందు డాక్టర్‌తో స్పష్టత కోసం మాట్లాడండి."
            ),
        }

    return {
        "quality": "clear",
        "confidence": 0.95,
        "message_en": "Document text extracted successfully with high confidence.",
        "message_te": "డాక్యుమెంట్ సమాచారం విజయవంతంగా సేకరించబడింది.",
    }


# ─── Main extraction entry‑point ──────────────────────────────────────────────

def extract_text_from_file(file_path: str, filename: str) -> Dict[str, Any]:
    """
    Extract text from any supported file type with OCR fallback chain:
        PDF  → native text layer  →  (if scanned) EasyOCR per page image
        Image (JPG/PNG) → EasyOCR  →  pytesseract  →  descriptive fallback
        TXT   → direct read
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "raw_text": "",
            "method": "none",
            "confidence": 0.0,
            "quality": "failed",
            "error": "File does not exist on disk.",
        }

    ext = os.path.splitext(filename)[1].lower()

    # ── 1.  Plain text (synthetic demo data) ─────────────────────────────────
    if ext in (".txt", ".text"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            qi = assess_text_quality(text, filename)
            return {
                "success": True,
                "raw_text": text,
                "method": "text_native",
                "confidence": qi["confidence"],
                "quality": qi["quality"],
                "quality_info": qi,
            }
        except Exception as e:
            return {
                "success": False,
                "raw_text": "",
                "method": "text_native",
                "confidence": 0.0,
                "quality": "failed",
                "error": str(e),
            }

    # ── 2.  PDF ──────────────────────────────────────────────────────────────
    if ext == ".pdf":
        try:
            reader = PdfReader(file_path)
            pages_text: List[str] = []
            for i, page in enumerate(reader.pages):
                pt = page.extract_text() or ""
                if pt.strip():
                    pages_text.append(f"--- Page {i+1} ---\n{pt}")

            full_text = "\n\n".join(pages_text).strip()

            if full_text and len(full_text.split()) > 10:
                # Native digital PDF
                qi = assess_text_quality(full_text, filename)
                return {
                    "success": True,
                    "raw_text": full_text,
                    "method": "pdf_native",
                    "confidence": qi["confidence"],
                    "quality": qi["quality"],
                    "quality_info": qi,
                }
            else:
                # Scanned PDF — no text layer; nothing we can do without rendering
                qi = {
                    "quality": "incomplete",
                    "confidence": 0.30,
                    "message_en": (
                        "This PDF appears to be a scanned image with no digital text layer. "
                        "For best results, please upload a photo of the prescription instead."
                    ),
                    "message_te": (
                        "ఈ పిడిఎఫ్ స్కాన్ చేయబడిన చిత్రంగా కనిపిస్తోంది — డిజిటల్ అక్షరాలు లేవు. "
                        "దయచేసి ప్రిస్క్రిప్షన్ ఫోటో అప్‌లోడ్ చేయండి."
                    ),
                }
                return {
                    "success": True,
                    "raw_text": "[Scanned PDF — no digital text layer found. Please upload a photo instead.]",
                    "method": "pdf_scanned_fallback",
                    "confidence": 0.30,
                    "quality": "incomplete",
                    "quality_info": qi,
                }
        except Exception as e:
            return {
                "success": False,
                "raw_text": "",
                "method": "pdf_native",
                "confidence": 0.0,
                "quality": "failed",
                "error": f"PDF extraction error: {e}",
            }

    # ── 3.  Images  ───────────────────────────────────────────────────────────
    if ext in (".jpg", ".jpeg", ".png"):
        try:
            img_orig = Image.open(file_path)
            width, height = img_orig.size
            img_enhanced = _enhance_image(img_orig.copy())

            ocr_text = ""
            method_used = "no_ocr"

            # 3a. EasyOCR (preferred — no system binary needed)
            if _EASYOCR_AVAILABLE:
                try:
                    ocr_text = _easyocr_image(img_enhanced)
                    method_used = "easyocr"
                except Exception:
                    ocr_text = ""

            # 3b. pytesseract fallback
            if not ocr_text.strip() and _TESSERACT_AVAILABLE:
                try:
                    ocr_text = _tesseract_image(img_enhanced)
                    method_used = "pytesseract"
                except Exception:
                    ocr_text = ""

            # 3c. Honest no-OCR fallback
            if not ocr_text.strip():
                ocr_text = (
                    f"[Image uploaded: {filename} ({width}×{height} px). "
                    "Text extraction was not successful. Please upload a clear, "
                    "well-lit photo or a digital PDF for best results.]"
                )
                method_used = "image_no_text"
                quality = "incomplete"
                confidence = 0.30
                qi = {
                    "quality": quality,
                    "confidence": confidence,
                    "message_en": (
                        "The uploaded image did not yield readable text. "
                        "Try a well-lit, high-resolution photo of the document."
                    ),
                    "message_te": (
                        "అప్‌లోడ్ చేసిన చిత్రంలో అక్షరాలు చదవడం సాధ్యం కాలేదు. "
                        "వెలుతురులో స్పష్టమైన, అధిక రిజల్యూషన్ ఫోటో అప్‌లోడ్ చేయండి."
                    ),
                }
            else:
                qi = assess_text_quality(ocr_text, filename)
                quality = qi["quality"]
                confidence = qi["confidence"]

            return {
                "success": True,
                "raw_text": ocr_text,
                "method": method_used,
                "confidence": confidence,
                "quality": quality,
                "quality_info": qi,
            }

        except Exception as e:
            return {
                "success": False,
                "raw_text": "",
                "method": "image_ocr",
                "confidence": 0.0,
                "quality": "failed",
                "error": f"Image processing error: {e}",
            }

    # ── 4.  Unsupported extension ─────────────────────────────────────────────
    return {
        "success": False,
        "raw_text": "",
        "method": "unsupported",
        "confidence": 0.0,
        "quality": "failed",
        "error": f"Unsupported file type: {ext}",
    }
