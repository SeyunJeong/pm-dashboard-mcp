"""라벨 CRUD + 태스크↔라벨 연결 도구."""

from __future__ import annotations

from typing import Any

from pm_dashboard.api.v1.wbs.labels import (
    fetch_label_list,
    fetch_task_labels,
    perform_add_label_to_task,
    perform_create_label,
    perform_delete_label,
    perform_remove_label_from_task,
    perform_update_label,
)
from pm_dashboard.db.engine import get_session_factory


async def list_labels() -> list[dict[str, Any]]:
    """전체 라벨 목록. 라벨에 태스크를 붙이려면 먼저 이 도구로 id를 얻는다."""
    factory = get_session_factory()
    async with factory() as db:
        return await fetch_label_list(db)


async def create_label(name: str, color_hex: str = "#6B7280") -> dict[str, Any]:
    """새 라벨 생성."""
    factory = get_session_factory()
    async with factory() as db:
        return await perform_create_label(db, name, color_hex)


async def update_label(
    label_id: int,
    name: str | None = None,
    color_hex: str | None = None,
    sort_order: int | None = None,
) -> dict[str, Any]:
    """라벨 속성 수정."""
    factory = get_session_factory()
    async with factory() as db:
        return await perform_update_label(db, label_id, name, color_hex, sort_order)


async def delete_label(label_id: int) -> dict[str, Any]:
    """라벨 삭제 (붙어있던 태스크에서도 자동 해제)."""
    factory = get_session_factory()
    async with factory() as db:
        return await perform_delete_label(db, label_id)


async def get_task_labels(issue_key: str) -> list[dict[str, Any]]:
    """특정 태스크의 라벨 목록."""
    factory = get_session_factory()
    async with factory() as db:
        return await fetch_task_labels(db, issue_key)


async def add_label_to_task(issue_key: str, label_id: int) -> dict[str, Any]:
    """태스크에 라벨 부여."""
    factory = get_session_factory()
    async with factory() as db:
        return await perform_add_label_to_task(db, issue_key, label_id)


async def remove_label_from_task(issue_key: str, label_id: int) -> dict[str, Any]:
    """태스크에서 라벨 제거."""
    factory = get_session_factory()
    async with factory() as db:
        return await perform_remove_label_from_task(db, issue_key, label_id)
