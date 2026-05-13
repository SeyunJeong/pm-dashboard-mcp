"""마일스톤 관련 MCP 도구."""

from __future__ import annotations

from typing import Any

from pm_dashboard.api.v1.wbs.milestones import (
    fetch_milestone_list,
    fetch_milestone_tasks,
    perform_close_milestone,
    perform_create_milestone,
    perform_delete_milestone,
    perform_reopen_milestone,
    perform_update_milestone,
)
from pm_dashboard.db.engine import get_session_factory
from pm_dashboard.mcp_server.context import get_allowed_pages, require_user


async def list_milestones(service_key: str) -> list[dict[str, Any]]:
    """특정 서비스의 마일스톤 목록.

    반환 필드: id, service_key, name, sort_order, total_count, done_count,
    in_progress_count, is_completed(자동 판정), status(active|closed), closed_at, closed_by.
    """
    factory = get_session_factory()
    async with factory() as db:
        return await fetch_milestone_list(db, service_key)


async def list_milestone_tasks(
    milestone_id: int,
    due_before: str | None = None,
    due_after: str | None = None,
    status_in: str | None = None,
) -> dict[str, Any]:
    """특정 마일스톤에 소속된 태스크 목록 + 마일스톤 메타데이터.

    "OOO 마일스톤의 일정 정리해줘", "이번 주 마감 태스크" 같은 요청에 사용.

    due_before / due_after: YYYY-MM-DD. 지난 마감(due_before=오늘) 또는 미래 일정(due_after=오늘).
    status_in: 쉼표 구분 상태 필터 (예: '해야 할 일,진행 중').
    """
    factory = get_session_factory()
    async with factory() as db:
        return await fetch_milestone_tasks(db, milestone_id, due_before, due_after, status_in)


async def create_milestone(service_key: str, name: str) -> dict[str, Any]:
    """새 마일스톤을 생성하고 id를 반환."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_create_milestone(db, user, service_key, name)


async def update_milestone(milestone_id: int, name: str) -> dict[str, Any]:
    """마일스톤 이름 변경."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_milestone(db, user, milestone_id, name)


async def delete_milestone(milestone_id: int) -> dict[str, Any]:
    """마일스톤 삭제 (소속 태스크는 마일스톤 미할당 상태로 전환). delete_milestone 권한 필요."""
    user = require_user()
    allowed = get_allowed_pages()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_delete_milestone(db, user, allowed, milestone_id)


async def close_milestone(milestone_id: int) -> dict[str, Any]:
    """마일스톤을 완료(closed) 처리. milestone_complete 권한 필요."""
    user = require_user()
    allowed = get_allowed_pages()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_close_milestone(db, user, allowed, milestone_id)


async def reopen_milestone(milestone_id: int) -> dict[str, Any]:
    """완료된 마일스톤을 다시 활성(active) 상태로 되돌림. milestone_complete 권한 필요."""
    user = require_user()
    allowed = get_allowed_pages()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_reopen_milestone(db, user, allowed, milestone_id)
