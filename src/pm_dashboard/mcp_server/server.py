"""PM Dashboard MCP — FastAPI 본체에 mount 되는 streamable-http MCP 서버.

마운트 위치: /mcp
인증: 본체 AuthMiddleware 가 Bearer ppdash_... 토큰 검증 → request.state.api_user
     이 모듈의 _UserContextMiddleware 가 ContextVar 로 옮겨 tool 함수에 노출.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP
from starlette.types import ASGIApp, Receive, Scope, Send

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


class _UserContextASGI:
    """본체 AuthMiddleware 가 채운 api_user 를 ContextVar 로 옮긴다.

    Pure ASGI 미들웨어 — BaseHTTPMiddleware 가 streamable-http 응답 헤더(특히
    Content-Type) 를 잃어버리는 케이스를 피하기 위해 직접 scope 를 다룬다.
    인증되지 않은 요청은 본체 AuthMiddleware 에서 이미 401 로 끊긴다.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        state = scope.get("state")
        user = getattr(state, "api_user", None) if state is not None else None
        if user is None:
            body = json.dumps(
                {"detail": "Bearer 토큰 인증이 필요합니다 (Authorization: Bearer ppdash_...)."},
                ensure_ascii=False,
            ).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json; charset=utf-8"),
                    (b"www-authenticate", b'Bearer realm="pm-dashboard"'),
                    (b"content-length", str(len(body)).encode()),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        allowed = getattr(state, "api_allowed_pages", None) or []
        tokens = context.set_request_context(user, list(allowed))
        try:
            await self.app(scope, receive, send)
        finally:
            context.reset_request_context(tokens)


def build_mcp_app() -> ASGIApp:
    """FastAPI 에 mount 할 ASGI 앱 — streamable-http transport.

    호출 후 mcp.session_manager 가 사용 가능해진다.
    실제 동작을 위해서는 본체 lifespan 에서 `async with mcp.session_manager.run():` 진입 필수.
    """
    return _UserContextASGI(mcp.streamable_http_app())
