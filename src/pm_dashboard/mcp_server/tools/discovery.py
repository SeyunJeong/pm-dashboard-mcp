"""읽기 전용 탐색 도구 — service_key, epic_key, issue_key 식별용."""

from __future__ import annotations

from typing import Any

from pm_dashboard.api.v1.wbs.services import fetch_service_detail, fetch_service_summaries
from pm_dashboard.db.engine import get_session_factory


async def list_services() -> list[dict[str, Any]]:
    """등록된 서비스 목록 + 요약 (마일스톤·태스크 카운트, 신호등 등).

    이후 마일스톤/태스크 도구의 service_key, epic_key 식별 용도.
    """
    factory = get_session_factory()
    async with factory() as db:
        summaries = await fetch_service_summaries(db)
        return [s.model_dump() for s in summaries]


async def get_service_tasks(service_key: str) -> dict[str, Any]:
    """서비스 상세 — current/roadmap/backlog/completed 태스크 리스트를 모두 포함.

    각 태스크의 key 필드가 issue_key. 이후 update_task_* 도구의 issue_key 입력.
    """
    factory = get_session_factory()
    async with factory() as db:
        detail = await fetch_service_detail(db, service_key)
        return detail.model_dump()
