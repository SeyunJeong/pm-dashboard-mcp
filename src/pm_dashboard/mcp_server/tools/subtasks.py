"""태스크 하위작업(=서브태스크=체크리스트) CRUD 도구."""

from __future__ import annotations

from typing import Any

from pm_dashboard.api.v1.wbs.tasks import (
    fetch_checklist,
    perform_add_checklist_item,
    perform_delete_checklist_item,
    perform_update_checklist_item,
)
from pm_dashboard.db.engine import get_session_factory
from pm_dashboard.mcp_server.context import get_allowed_pages, require_user


async def list_subtasks(issue_key: str) -> list[dict[str, Any]]:
    """태스크의 하위작업(서브태스크/체크리스트) 목록 조회.

    별칭: list_checklist. 한 태스크 안에 들어있는 체크리스트 항목 전체를 sort_order 순으로 반환한다.
    각 항목 필드: id, content, description, due_date, is_checked, sort_order.
    """
    factory = get_session_factory()
    async with factory() as db:
        return await fetch_checklist(db, issue_key)


async def add_subtask(
    issue_key: str,
    content: str,
    description: str | None = None,
    due_date: str | None = None,
    assignee: str | None = None,
) -> dict[str, Any]:
    """하위작업(서브태스크/체크리스트 항목)을 태스크에 추가.

    별칭: add_checklist_item. content 는 항목 제목, description 은 상세 설명,
    due_date 는 'YYYY-MM-DD'. assignee 미지정 시 상위 태스크 담당자가 자동 지정된다.
    새 항목은 항상 맨 뒤(sort_order=max+1)에 붙는다.
    """
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_add_checklist_item(
            db, user, issue_key, content, description, due_date, assignee
        )


async def update_subtask(
    issue_key: str,
    item_id: int,
    content: str | None = None,
    description: str | None = None,
    due_date: str | None = None,
    assignee: str | None = None,
    is_checked: bool | None = None,
) -> dict[str, Any]:
    """하위작업(서브태스크/체크리스트 항목) 수정.

    별칭: update_checklist_item. is_checked 로 체크 상태 토글, content/description/due_date/assignee 로 내용 수정.
    None 으로 둔 필드는 변경되지 않는다. due_date·assignee 를 빈 문자열로 보내면 값이 해제된다.
    """
    user = require_user()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_checklist_item(
            db, user, issue_key, item_id,
            content=content, description=description,
            due_date=due_date, assignee=assignee, is_checked=is_checked,
        )


async def delete_subtask(issue_key: str, item_id: int) -> dict[str, Any]:
    """하위작업(서브태스크/체크리스트 항목) 삭제.

    별칭: delete_checklist_item. 태스크 삭제 권한이 필요하다.
    """
    user = require_user()
    allowed = get_allowed_pages()
    factory = get_session_factory()
    async with factory() as db:
        return await perform_delete_checklist_item(db, user, allowed, issue_key, item_id)
