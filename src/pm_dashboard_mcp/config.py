"""환경 변수 설정.

PM_DASHBOARD_TOKEN: 사용자 본인의 API 토큰 (필수)
    대시보드 → 프로필 드롭다운 → "API 토큰" 페이지에서 발급
PM_DASHBOARD_API_URL: 백엔드 API 베이스 URL (선택, 기본 운영 서버)
"""

from __future__ import annotations

import os

DEFAULT_API_URL = "http://49.50.128.163:8000"


def get_api_url() -> str:
    return os.environ.get("PM_DASHBOARD_API_URL", DEFAULT_API_URL).rstrip("/")


def get_token() -> str:
    token = os.environ.get("PM_DASHBOARD_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "PM_DASHBOARD_TOKEN 환경변수가 비어있습니다. "
            "대시보드 프로필 드롭다운의 'API 토큰'에서 발급 후 설정하세요."
        )
    return token
