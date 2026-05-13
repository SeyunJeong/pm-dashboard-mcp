"""PM Dashboard MCP — FastAPI 본체에 mount 되는 streamable-http MCP 서버.

마운트 위치: /mcp
인증: 본체 AuthMiddleware 가 Bearer ppdash_... 토큰 검증 → request.state.api_user
     이 모듈의 _UserContextMiddleware 가 ContextVar 로 옮겨 tool 함수에 노출.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from pm_dashboard.mcp_server import context
from pm_dashboard.mcp_server.tools import (
    discovery,
    labels,
    milestones,
    subtasks,
    tasks,
)

mcp = FastMCP("pm-dashboard")
# FastAPI 의 /mcp 에 mount → 내부 path 는 / 로 (그대로 두면 최종 URL 이 /mcp/mcp 가 됨)
mcp.settings.streamable_http_path = "/"

# ── 도구 등록 ────────────────────────────────────────────────────

# 탐색
mcp.tool()(discovery.list_services)
mcp.tool()(discovery.get_service_tasks)

# 마일스톤
mcp.tool()(milestones.list_milestones)
mcp.tool()(milestones.list_milestone_tasks)
mcp.tool()(milestones.create_milestone)
mcp.tool()(milestones.update_milestone)
mcp.tool()(milestones.delete_milestone)
mcp.tool()(milestones.close_milestone)
mcp.tool()(milestones.reopen_milestone)

# 태스크
mcp.tool()(tasks.get_task)
mcp.tool()(tasks.create_task)
mcp.tool()(tasks.delete_task)
mcp.tool()(tasks.update_task_summary)
mcp.tool()(tasks.update_task_status)
mcp.tool()(tasks.update_task_dates)
mcp.tool()(tasks.update_task_assignee)
mcp.tool()(tasks.update_task_milestone)
mcp.tool()(tasks.update_task_type)
mcp.tool()(tasks.update_task_backlog)
mcp.tool()(tasks.update_task_memo)
mcp.tool()(tasks.update_task_done_comment)

# 하위작업 / 서브태스크 / 체크리스트 (동일 핸들러를 두 이름으로 노출)
mcp.tool()(subtasks.list_subtasks)
mcp.tool()(subtasks.add_subtask)
mcp.tool()(subtasks.update_subtask)
mcp.tool()(subtasks.delete_subtask)
mcp.tool(name="list_checklist")(subtasks.list_subtasks)
mcp.tool(name="add_checklist_item")(subtasks.add_subtask)
mcp.tool(name="update_checklist_item")(subtasks.update_subtask)
mcp.tool(name="delete_checklist_item")(subtasks.delete_subtask)

# 라벨
mcp.tool()(labels.list_labels)
mcp.tool()(labels.create_label)
mcp.tool()(labels.update_label)
mcp.tool()(labels.delete_label)
mcp.tool()(labels.get_task_labels)
mcp.tool()(labels.add_label_to_task)
mcp.tool()(labels.remove_label_from_task)


class _UserContextMiddleware(BaseHTTPMiddleware):
    """Bearer 인증 결과를 ContextVar 로 옮기고, 인증 없으면 401."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        user = getattr(request.state, "api_user", None)
        if user is None:
            return JSONResponse(
                {"detail": "Bearer 토큰 인증이 필요합니다 (Authorization: Bearer ppdash_...)."},
                status_code=401,
            )
        allowed = getattr(request.state, "api_allowed_pages", []) or []
        tokens = context.set_request_context(user, list(allowed))
        try:
            return await call_next(request)
        finally:
            context.reset_request_context(tokens)


def build_mcp_app() -> ASGIApp:
    """FastAPI 에 mount 할 ASGI 앱 — streamable-http transport.

    호출 후 mcp.session_manager 가 사용 가능해진다.
    실제 동작을 위해서는 본체 lifespan 에서 `async with mcp.session_manager.run():` 진입 필수.
    """
    inner: ASGIApp = mcp.streamable_http_app()
    # Starlette 앱이라 add_middleware 사용 가능
    inner.add_middleware(_UserContextMiddleware)
    return inner
