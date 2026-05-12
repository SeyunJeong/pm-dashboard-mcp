"""읽기 전용 탐색 도구 — service_key, epic_key, task issue_key 식별용.

서비스 자체 CRUD는 포함하지 않음 (조회만).
"""

from __future__ import annotations

from typing import Any

from ..client import request


async def list_services() -> list[dict[str, Any]]:
    """등록된 서비스 목록 + 요약 (마일스톤·태스크 카운트, 신호등 등).

    이후 마일스톤/태스크 도구의 service_key, epic_key 식별 용도.
    """
    return await request("GET", "/api/v1/services")


async def get_service_tasks(service_key: str) -> dict[str, Any]:
    """서비스 상세 — current/roadmap/backlog/completed 태스크 리스트를 모두 포함.

    각 태스크의 key 필드가 issue_key (예: ATCS-123 또는 LOCAL-EPIC-XXX-N).
    이후 update_task_* 도구의 issue_key 입력.
    """
    return await request("GET", f"/api/v1/services/{service_key}")
