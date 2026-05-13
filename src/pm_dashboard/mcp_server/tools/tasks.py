"""태스크 CRUD + 필드 수정 MCP 도구."""

from __future__ import annotations

from typing import Any

from pm_dashboard.api.v1.wbs.tasks import (
    VALID_TASK_TYPES,
    fetch_task_detail,
    perform_create_task,
    perform_delete_task,
    perform_update_task_assignee,
    perform_update_task_backlog,
    perform_update_task_dates,
    perform_update_task_done_comment,
    perform_update_task_memo,
    perform_update_task_milestone,
    perform_update_task_status,
    perform_update_task_summary,
    perform_update_task_type,
)
from pm_dashboard.db.engine import get_session_factory
from pm_dashboard.mcp_server.context import get_allowed_pages, require_user


async def get_task(issue_key: str) -> dict[str, Any]:
    """태스크 상세 조회.

    반환 필드: issue_key, epic_key, service_key, summary, status, assignee,
    fix_version, start_date, due_date, priority, pm_memo, task_type, milestone_id,
    milestone_name, done_comment, label_ids.
    """
    factory = get_session_factory()
    async with factory() as db:
        return await fetch_task_detail(db, issue_key)


async def create_task(
    summary: str,
    epic_key: str,
    priority: str = "Medium",
    task_type: str = "po",
    milestone_id: int | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
) -> dict[str, Any]:
    """새 태스크 생성. epic_key는 service의 jira_epic_key.

    task_type: qa | planning | design | po
    priority: Highest | High | Medium | Low | Lowest
    start_date / due_date: YYYY-MM-DD (옵셔널, 생성과 동시에 일정 지정)
    """
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(f"task_type 은 {sorted(VALID_TASK_TYPES)} 중 하나여야 합니다.")
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_create_task(
            db, user,
            summary=summary, epic_key=epic_key, priority=priority,
            task_type=task_type, milestone_id=milestone_id,
            start_date=start_date, due_date=due_date,
        )


async def delete_task(issue_key: str) -> dict[str, Any]:
    """태스크 삭제. delete_task 권한 필요."""
    user = require_user()
    allowed = get_allowed_pages()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_delete_task(db, user, allowed, issue_key)


async def update_task_summary(issue_key: str, summary: str) -> dict[str, Any]:
    """태스크 제목(summary) 수정."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_summary(db, user, issue_key, summary)


async def update_task_status(
    issue_key: str, status: str, done_comment: str | None = None,
) -> dict[str, Any]:
    """태스크 상태 변경. 완료 상태로 보낼 때 done_comment 함께 기록 가능.

    status 한국어 예시: '해야 할 일', '진행 중', '완료', '미해결', '해결됨', '종료'.
    """
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_status(db, user, issue_key, status, done_comment)


async def update_task_dates(
    issue_key: str, start_date: str | None = None, due_date: str | None = None,
) -> dict[str, Any]:
    """태스크 일정(시작/마감일) 수정. ISO 날짜 형식 YYYY-MM-DD. null 전달 시 해당 일자 해제."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_dates(db, user, issue_key, start_date, due_date)


async def update_task_assignee(issue_key: str, assignee: str | None) -> dict[str, Any]:
    """태스크 담당자 변경. null 전달 시 미할당."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_assignee(db, user, issue_key, assignee)


async def update_task_milestone(
    issue_key: str, milestone_id: int | None,
) -> dict[str, Any]:
    """태스크 소속 마일스톤 변경. null 전달 시 마일스톤 미할당."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_milestone(db, user, issue_key, milestone_id)


async def update_task_type(issue_key: str, task_type: str) -> dict[str, Any]:
    """태스크 타입 변경. qa | planning | design | po."""
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(f"task_type 은 {sorted(VALID_TASK_TYPES)} 중 하나여야 합니다.")
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_type(db, user, issue_key, task_type)


async def update_task_backlog(issue_key: str, is_backlog: bool) -> dict[str, Any]:
    """태스크의 백로그 플래그 변경 (True=백로그, False=로드맵)."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_backlog(db, user, issue_key, is_backlog)


async def update_task_memo(issue_key: str, memo: str | None) -> dict[str, Any]:
    """태스크 PM 메모 수정. null 전달 시 메모 삭제."""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_memo(db, user, issue_key, memo)


async def update_task_done_comment(
    issue_key: str, done_comment: str | None,
) -> dict[str, Any]:
    """완료 코멘트 별도 수정. (상태 변경과 별개로 코멘트만 갱신할 때)"""
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_task_done_comment(db, user, issue_key, done_comment)
