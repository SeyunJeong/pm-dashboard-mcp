"""마일스톤 CRUD 도구."""

from __future__ import annotations

from typing import Any

from ..client import request

BASE = "/api/v1/milestones"


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
    params: dict[str, Any] = {}
    if due_before:
        params["due_before"] = due_before
    if due_after:
        params["due_after"] = due_after
    if status_in:
        params["status_in"] = status_in
    return await request("GET", f"{BASE}/{milestone_id}/tasks", params=params or None)


async def list_milestones(service_key: str) -> list[dict[str, Any]]:
    """특정 서비스의 마일스톤 목록.

    반환 필드: id, service_key, name, sort_order, total_count, done_count,
    in_progress_count, is_completed(자동 판정), status(active|closed), closed_at, closed_by.
    """
    return await request("GET", BASE, params={"service_key": service_key})


async def create_milestone(service_key: str, name: str) -> dict[str, Any]:
    """새 마일스톤을 생성하고 id를 반환."""
    return await request("POST", BASE, json={"service_key": service_key, "name": name})


async def update_milestone(milestone_id: int, name: str) -> dict[str, Any]:
    """마일스톤 이름 변경."""
    return await request("PATCH", f"{BASE}/{milestone_id}", json={"name": name})


async def delete_milestone(milestone_id: int) -> dict[str, Any]:
    """마일스톤 삭제 (소속 태스크는 마일스톤 미할당 상태로 전환). delete_milestone 권한 필요."""
    return await request("DELETE", f"{BASE}/{milestone_id}")


async def close_milestone(milestone_id: int) -> dict[str, Any]:
    """마일스톤을 완료(closed) 처리. milestone_complete 권한 필요."""
    return await request("POST", f"{BASE}/{milestone_id}/close")


async def reopen_milestone(milestone_id: int) -> dict[str, Any]:
    """완료된 마일스톤을 다시 활성(active) 상태로 되돌림. milestone_complete 권한 필요."""
    return await request("POST", f"{BASE}/{milestone_id}/reopen")
