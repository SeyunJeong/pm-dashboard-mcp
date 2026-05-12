"""라벨 CRUD + 태스크↔라벨 연결 도구."""

from __future__ import annotations

from typing import Any

from ..client import request

BASE = "/api/v1/labels"


async def list_labels() -> list[dict[str, Any]]:
    """전체 라벨 목록. 라벨에 태스크를 붙이려면 먼저 이 도구로 id를 얻는다."""
    return await request("GET", BASE)


async def create_label(name: str, color_hex: str = "#6B7280") -> dict[str, Any]:
    """새 라벨 생성."""
    return await request("POST", BASE, json={"name": name, "color_hex": color_hex})


async def update_label(
    label_id: int,
    name: str | None = None,
    color_hex: str | None = None,
    sort_order: int | None = None,
) -> dict[str, Any]:
    """라벨 속성 수정."""
    payload = {
        k: v
        for k, v in {"name": name, "color_hex": color_hex, "sort_order": sort_order}.items()
        if v is not None
    }
    return await request("PUT", f"{BASE}/{label_id}", json=payload)


async def delete_label(label_id: int) -> dict[str, Any]:
    """라벨 삭제 (붙어있던 태스크에서도 자동 해제)."""
    return await request("DELETE", f"{BASE}/{label_id}")


async def get_task_labels(issue_key: str) -> list[dict[str, Any]]:
    """특정 태스크의 라벨 목록."""
    return await request("GET", f"{BASE}/tasks/{issue_key}")


async def add_label_to_task(issue_key: str, label_id: int) -> dict[str, Any]:
    """태스크에 라벨 부여."""
    return await request("POST", f"{BASE}/tasks/{issue_key}/{label_id}")


async def remove_label_from_task(issue_key: str, label_id: int) -> dict[str, Any]:
    """태스크에서 라벨 제거."""
    return await request("DELETE", f"{BASE}/tasks/{issue_key}/{label_id}")
