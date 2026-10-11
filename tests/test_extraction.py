import asyncio
import io

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.extraction import extract_text


def _upload(filename: str, content: bytes) -> UploadFile:
    return UploadFile(file=io.BytesIO(content), filename=filename)


def test_extract_text_reads_plain_txt():
    upload = _upload("cv.txt", b"Python developer with FastAPI experience.")

    text = asyncio.run(extract_text(upload))

    assert text == "Python developer with FastAPI experience."


def test_extract_text_rejects_unsupported_extension():
    upload = _upload("cv.rtf", b"some content")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(extract_text(upload))

    assert exc_info.value.status_code == 400


def test_extract_text_rejects_empty_content():
    upload = _upload("cv.txt", b"   ")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(extract_text(upload))

    assert exc_info.value.status_code == 400
