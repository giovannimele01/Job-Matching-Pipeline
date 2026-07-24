import io
from pathlib import Path

import docx
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(content: bytes) -> str:
    document = docx.Document(io.BytesIO(content))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


async def extract_text(file: UploadFile) -> str:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato non supportato: '{extension}'. Usa PDF, DOCX o TXT.",
        )

    content = await file.read()

    if extension == ".pdf":
        text = _extract_pdf(content)
    elif extension == ".docx":
        text = _extract_docx(content)
    else:
        text = _extract_txt(content)

    if not text.strip():
        raise HTTPException(
            status_code=400, detail=f"Impossibile estrarre testo da '{file.filename}'."
        )
    return text
