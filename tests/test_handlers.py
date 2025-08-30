import io
import pytest
from pathlib import Path

# This assumes that pytest is run from the root of the project
from src.uploads.handlers import save_upload_temp
from src.config import settings

# Dummy content for testing
PDF_CONTENT = b'%PDF-1.4\n'
DOCX_CONTENT = b'PK\x03\x04' + b'\x00' * 26 # A valid docx starts with PK\x03\x04
TEXT_CONTENT = b'This is a text file.'

@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    """Create a temporary storage directory for each test."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    monkeypatch.setattr(settings, "STORAGE_DIR", storage_dir)
    # The handler creates an 'uploads' subdirectory, so we need to return the base
    return storage_dir

def test_save_pdf_successfully(temp_storage):
    """Test that a valid PDF file is saved correctly."""
    filename = "test.pdf"
    file_obj = io.BytesIO(PDF_CONTENT)
    final_path = save_upload_temp(filename, file_obj)
    assert final_path.exists()
    assert final_path.name.startswith("test-")
    assert final_path.suffix == ".pdf"
    assert final_path.parent.name == "uploads"
    assert final_path.parent.parent == temp_storage
    with open(final_path, "rb") as f:
        assert f.read() == PDF_CONTENT

def test_save_docx_successfully(temp_storage):
    """Test that a valid DOCX file is saved correctly."""
    filename = "test.docx"
    file_obj = io.BytesIO(DOCX_CONTENT)
    final_path = save_upload_temp(filename, file_obj)
    assert final_path.exists()
    assert final_path.name.startswith("test-")
    assert final_path.suffix == ".docx"
    assert final_path.parent.name == "uploads"
    assert final_path.parent.parent == temp_storage
    with open(final_path, "rb") as f:
        assert f.read() == DOCX_CONTENT

def test_unsupported_file_type():
    """Test that an unsupported file type raises a ValueError."""
    filename = "test.txt"
    file_obj = io.BytesIO(TEXT_CONTENT)
    with pytest.raises(ValueError, match="Unsupported file type"):
        save_upload_temp(filename, file_obj)

def test_file_too_large(monkeypatch):
    """Test that a file exceeding the size limit raises a ValueError."""
    monkeypatch.setattr(settings, "MAX_UPLOAD_MB", 1)
    filename = "large.pdf"
    # Create content larger than MAX_UPLOAD_MB (which is 1)
    large_content = PDF_CONTENT + b'a' * (1 * 1024 * 1024)
    file_obj = io.BytesIO(large_content)
    with pytest.raises(ValueError, match=f"File exceeds 1 MB limit"):
        save_upload_temp(filename, file_obj)

def test_invalid_pdf_content():
    """Test that a .pdf file with invalid content raises a ValueError."""
    filename = "fake.pdf"
    file_obj = io.BytesIO(TEXT_CONTENT)
    with pytest.raises(ValueError, match="File content is not a valid PDF"):
        save_upload_temp(filename, file_obj)

def test_invalid_docx_content():
    """Test that a .docx file with invalid content raises a ValueError."""
    filename = "fake.docx"
    file_obj = io.BytesIO(PDF_CONTENT) # Use PDF content for a docx file
    with pytest.raises(ValueError, match="File content is not a valid DOCX"):
        save_upload_temp(filename, file_obj)

def test_save_empty_file():
    """Test that saving an empty file raises a ValueError."""
    filename = "empty.pdf"
    file_obj = io.BytesIO(b"")
    with pytest.raises(ValueError, match="Cannot save an empty file"):
        save_upload_temp(filename, file_obj)
