"""MCP 도구 실행 컨텍스트 — Bearer 인증된 user/allowed_pages 를 ContextVar 로 전달.

AuthMiddleware 가 request.state 에 채운 정보를 mount된 Starlette 미들웨어에서
ContextVar 로 옮긴다. tool 함수는 본 모듈의 헬퍼로 user/allowed 를 얻는다.
"""

from __future__ import annotations

from contextvars import ContextVar

_current_user: ContextVar[dict | None] = ContextVar("mcp_current_user", default=None)
_current_allowed: ContextVar[list[str]] = ContextVar(
    "mcp_current_allowed_pages", default=[]
)


def set_request_context(user: dict | None, allowed_pages: list[str]) -> tuple:
    """미들웨어에서 호출. 반환된 토큰들을 finally 에서 reset 해야 함."""
    return (
        _current_user.set(user),
        _current_allowed.set(list(allowed_pages or [])),
    )


def reset_request_context(tokens: tuple) -> None:
    user_tok, allowed_tok = tokens
    _current_user.reset(user_tok)
    _current_allowed.reset(allowed_tok)


def require_user() -> dict:
    """tool 함수 안에서 사용. 인증된 user dict 반환, 없으면 RuntimeError."""
    user = _current_user.get()
    if user is None:
        raise RuntimeError("MCP 도구 실행 컨텍스트에 사용자 정보가 없습니다 (Bearer 인증 실패).")
    return user


def get_allowed_pages() -> list[str]:
    return list(_current_allowed.get())
