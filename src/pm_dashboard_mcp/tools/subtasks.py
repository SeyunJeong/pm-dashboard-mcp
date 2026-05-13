"""태스크 하위작업(=서브태스크=체크리스트) CRUD 도구.

PM Dashboard 태스크는 내부에 체크리스트 형태의 하위 항목을 가질 수 있다.
하위작업 / sub-task / subtask / 체크리스트 / checklist 모두 같은 개념을 가리킨다.
"""

from __future__ import annotations

from typing import Any

from ..client import request

BASE = "/api/v1/tasks"


async def list_subtasks(issue_key: str) -> list[dict[str, Any]]:
    """태스크의 하위작업(서브태스크/체크리스트) 목록 조회.

    별칭: list_checklist. 한 태스크 안에 들어있는 체크리스트 항목 전체를 sort_order 순으로 반환한다.
    각 항목 필드: id, content, description, due_date, is_checked, sort_order.
    """
    return await request("GET", f"{BASE}/{issue_key}/checklist")


async def add_subtask(
    issue_key: str,
    content: str,
    description: str | None = None,
    due_date: str | None = None,
) -> dict[str, Any]:
    """하위작업(서브태스크/체크리스트 항목)을 태스크에 추가.

    별칭: add_checklist_item. content 는 항목 제목, description 은 상세 설명,
    due_date 는 'YYYY-MM-DD'. 새 항목은 항상 맨 뒤(sort_order=max+1)에 붙는다.
    """
    payload: dict[str, Any] = {"content": content}
    if description is not None:
        payload["description"] = description
    if due_date is not None:
        payload["due_date"] = due_date
    return await request("POST", f"{BASE}/{issue_key}/checklist", json=payload)


async def update_subtask(
    issue_key: str,
    item_id: int,
    content: str | None = None,
    description: str | None = None,
    due_date: str | None = None,
    is_checked: bool | None = None,
) -> dict[str, Any]:
    """하위작업(서브태스크/체크리스트 항목) 수정.

    별칭: update_checklist_item. is_checked 로 체크 상태 토글, content/description/due_date 로 내용 수정.
    None 으로 둔 필드는 변경되지 않는다. due_date 를 빈 문자열로 보내면 마감일이 해제된다.
    """
    payload = {
        k: v
        for k, v in {
            "content": content,
            "description": description,
            "due_date": due_date,
            "is_checked": is_checked,
        }.items()
        if v is not None
    }
    return await request("PUT", f"{BASE}/{issue_key}/checklist/{item_id}", json=payload)


async def delete_subtask(issue_key: str, item_id: int) -> dict[str, Any]:
    """하위작업(서브태스크/체크리스트 항목) 삭제.

    별칭: delete_checklist_item. 태스크 삭제 권한이 필요하다.
    """
    return await request("DELETE", f"{BASE}/{issue_key}/checklist/{item_id}")
