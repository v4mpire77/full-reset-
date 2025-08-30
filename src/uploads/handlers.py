from __future__ import annotations
from pathlib import Path
import hashlib

from ..config import settings

ALLOWED_EXTS = {".pdf", ".docx"}

def _sniff_mime(first_bytes: bytes) -> str:
    # Tiny, permissive sniff to reject obvious wrong types; full "python-magic" is optional later.
    header = first_bytes[:8]
    if header.startswith(b"%PDF"):
        return "application/pdf"
    if header.startswith(b"PK\x03\x04"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "application/octet-stream"

def save_upload_temp(filename: str, fileobj) -> Path:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")

    uploads = settings.STORAGE_DIR / "uploads"
    uploads.mkdir(exist_ok=True) # Ensure the specific uploads subdirectory exists
    tmp_path = uploads / f".part-{filename}"
    sha = hashlib.sha256()

    written = 0
    with open(tmp_path, "wb") as f:
        first = b""
        while True:
            chunk = fileobj.read(1024 * 1024)
            if not chunk:
                break
            if not first:
                first = chunk[:16]
            f.write(chunk)
            sha.update(chunk)
            written += len(chunk)
            if written > settings.MAX_UPLOAD_MB * 1024 * 1024:
                f.close()
                tmp_path.unlink(missing_ok=True)
                raise ValueError(f"File exceeds {settings.MAX_UPLOAD_MB} MB limit.")

    if written == 0:
        tmp_path.unlink(missing_ok=True)
        raise ValueError("Cannot save an empty file.")

    mime = _sniff_mime(first)
    if ext == ".pdf" and mime != "application/pdf":
        tmp_path.unlink(missing_ok=True)
        raise ValueError("File content is not a valid PDF.")
    if ext == ".docx" and not mime.endswith("wordprocessingml.document"):
        tmp_path.unlink(missing_ok=True)
        raise ValueError("File content is not a valid DOCX.")

    digest = sha.hexdigest()[:16]
    final_path = uploads / f"{Path(filename).stem}-{digest}{ext}"
    tmp_path.replace(final_path)
    return final_path
