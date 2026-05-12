"""태스크 CRUD 도구. 모든 필드 수정 가능 (필드별 endpoint를 PUT로 호출)."""

from __future__ import annotations

from typing import Any

from ..client import request

BASE = "/api/v1/tasks"

VALID_TASK_TYPES = ("qa", "planning", "design", "po")


async def get_task(issue_key: str) -> dict[str, Any]:
    """태스크 상세 조회.

    반환 필드: issue_key, epic_key, service_key, summary, status, assignee,
    fix_version, start_date, due_date, priority, pm_memo, task_type, milestone_id,
    milestone_name, done_comment, label_ids.
    """
    return await request("GET", f"{BASE}/{issue_key}")


async def create_task(
    summary: str,
    epic_key: str,
    priority: str = "Medium",
    task_type: str = "po",
    milestone_id: int | None = None,
) -> dict[str, Any]:
    """새 태스크 생성. epic_key는 service의 jira_epic_key.

    task_type: qa | planning | design | po
    priority: Highest | High | Medium | Low | Lowest
    """
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(f"task_type 은 {VALID_TASK_TYPES} 중 하나여야 합니다.")
    return await request(
        "POST",
        BASE,
        json={
            "summary": summary,
            "epic_key": epic_key,
            "priority": priority,
            "task_type": task_type,
            "milestone_id": milestone_id,
        },
    )


async def delete_task(issue_key: str) -> dict[str, Any]:
    """태스크 삭제. delete_task 권한 필요."""
    return await request("DELETE", f"{BASE}/{issue_key}")


async def update_task_summary(issue_key: str, summary: str) -> dict[str, Any]:
    """태스크 제목(summary) 수정."""
    return await request("PUT", f"{BASE}/{issue_key}/summary", json={"summary": summary})


async def update_task_status(
    issue_key: str,
    status: str,
    done_comment: str | None = None,
) -> dict[str, Any]:
    """태스크 상태 변경. 완료 상태로 보낼 때 done_comment 함께 기록 가능.

    status 한국어 예시: '해야 할 일', '진행 중', '완료', '미해결', '해결됨', '종료'.
    """
    payload: dict[str, Any] = {"status": status}
    if done_comment is not None:
        payload["done_comment"] = done_comment
    return await request("PUT", f"{BASE}/{issue_key}/status", json=payload)


async def update_task_dates(
    issue_key: str,
    start_date: str | None = None,
    due_date: str | None = None,
) -> dict[str, Any]:
    """태스크 일정(시작/마감일) 수정. ISO 날짜 형식 YYYY-MM-DD. null 전달 시 해당 일자 해제."""
    return await request(
        "PUT",
        f"{BASE}/{issue_key}/dates",
        json={"start_date": start_date, "due_date": due_date},
    )


async def update_task_assignee(issue_key: str, assignee: str | None) -> dict[str, Any]:
    """태스크 담당자 변경. null 전달 시 미할당."""
    return await request("PUT", f"{BASE}/{issue_key}/assignee", json={"assignee": assignee})


async def update_task_milestone(
    issue_key: str,
    milestone_id: int | None,
) -> dict[str, Any]:
    """태스크 소속 마일스톤 변경. null 전달 시 마일스톤 미할당."""
    return await request(
        "PUT", f"{BASE}/{issue_key}/milestone", json={"milestone_id": milestone_id}
    )


async def update_task_type(issue_key: str, task_type: str) -> dict[str, Any]:
    """태스크 타입 변경. qa | planning | design | po."""
    if task_type not in VALID_TASK_TYPES:
        raise ValueError(f"task_type 은 {VALID_TASK_TYPES} 중 하나여야 합니다.")
    return await request("PUT", f"{BASE}/{issue_key}/type", json={"task_type": task_type})


async def update_task_backlog(issue_key: str, is_backlog: bool) -> dict[str, Any]:
    """태스크의 백로그 플래그 변경 (True=백로그, False=로드맵)."""
    return await request(
        "PUT", f"{BASE}/{issue_key}/backlog", json={"is_backlog": is_backlog}
    )


async def update_task_memo(issue_key: str, memo: str | None) -> dict[str, Any]:
    """태스크 PM 메모 수정. null 전달 시 메모 삭제."""
    return await request("PUT", f"{BASE}/{issue_key}/memo", json={"memo": memo})


async def update_task_done_comment(
    issue_key: str, done_comment: str | None
) -> dict[str, Any]:
    """완료 코멘트 별도 수정. (상태 변경과 별개로 코멘트만 갱신할 때)"""
    return await request(
        "PUT", f"{BASE}/{issue_key}/done-comment", json={"done_comment": done_comment}
    )
