import pytest
from fastapi import HTTPException
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from app.llm import _invoke_llm


class _FakeGoogleError(Exception):
    def __init__(self, code: int):
        super().__init__(f"fake google error {code}")
        self.code = code


class _FakeChain:
    def __init__(self, code: int):
        self._code = code

    def invoke(self, payload):
        try:
            raise _FakeGoogleError(self._code)
        except _FakeGoogleError as e:
            raise ChatGoogleGenerativeAIError(f"Error calling model x: {self._code}") from e


def test_rate_limit_error_maps_to_http_429():
    with pytest.raises(HTTPException) as exc_info:
        _invoke_llm(_FakeChain(429), {})

    assert exc_info.value.status_code == 429


def test_other_google_errors_map_to_http_502():
    with pytest.raises(HTTPException) as exc_info:
        _invoke_llm(_FakeChain(404), {})

    assert exc_info.value.status_code == 502


def test_successful_call_returns_chain_result():
    class _OkChain:
        def invoke(self, payload):
            return "result"

    assert _invoke_llm(_OkChain(), {}) == "result"
