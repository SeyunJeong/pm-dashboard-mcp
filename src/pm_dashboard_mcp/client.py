"""PM Dashboard 백엔드 HTTP 클라이언트 — Bearer 토큰 자동 첨부."""

from __future__ import annotations

from typing import Any

import httpx

from . import config


class ApiError(Exception):
    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"[{status}] {detail}")


_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=config.get_api_url(),
            headers={
                "Authorization": f"Bearer {config.get_token()}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )
    return _client


async def request(method: str, path: str, **kwargs: Any) -> Any:
    """HTTP 요청 → JSON 디코드. 비정상 응답은 ApiError 로 변환."""
    res = await _get_client().request(method, path, **kwargs)
    if res.status_code == 204:
        return {"status": "ok"}
    try:
        body = res.json()
    except ValueError:
        body = {"detail": res.text}
    if not res.is_success:
        detail = body.get("detail") if isinstance(body, dict) else str(body)
        raise ApiError(res.status_code, str(detail))
    return body


async def aclose() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
