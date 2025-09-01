from __future__ import annotations
from pathlib import Path

def _extract_pdf(path: Path) -> list[str]:
    try:
        import fitz  # PyMuPDF
        text = []
        with fitz.open(path) as doc:
            for page in doc:
                text.append(page.get_text("text"))
        return text
    except Exception:
        # Conservative fallback: no text
        return []

def _extract_docx(path: Path) -> str:
    try:
        from docx2python import docx2python
        with docx2python(path) as doc:
            # Flatten section->paragraphs
            return "\n".join(["\n".join(p) for sec in doc.body for p in sec])
    except Exception:
        return ""

def _sentences(text: str) -> list[str]:
    if not text:
        return []
    try:
        import blingfire as bf
        return [s.strip() for s in bf.text_to_sentences(text).splitlines() if s.strip()]
    except Exception:
        import re
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def extract_text(path: Path):
    ext = path.suffix.lower()
    if ext == ".pdf":
        page_texts = _extract_pdf(path)
        text = "\n".join(page_texts)
        sents = _sentences(text)
        page_map = {i: page_text for i, page_text in enumerate(page_texts)}
    elif ext == ".docx":
        text = _extract_docx(path)
        sents = _sentences(text)
        page_map = {}
    else:
        text = ""
        sents = []
        page_map = {}
    return {"text": text, "sentences": sents, "page_map": page_map}
