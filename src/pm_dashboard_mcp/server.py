"""PM Dashboard MCP 서버 진입점.

설치/실행:
    pip install pm-dashboard-mcp     (또는 pip install -e .)
    export PM_DASHBOARD_TOKEN=ppdash_xxx
    pm-dashboard-mcp                  # stdio 모드

Claude Code 등록 예:
    claude mcp add pm-dashboard -e PM_DASHBOARD_TOKEN=ppdash_xxx -- pm-dashboard-mcp
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import discovery, labels, milestones, tasks

mcp = FastMCP("pm-dashboard")

# ── 탐색 (서비스/태스크 목록) ──────────────────────────────────
mcp.tool()(discovery.list_services)
mcp.tool()(discovery.get_service_tasks)

# ── 마일스톤 ───────────────────────────────────────────────────
mcp.tool()(milestones.list_milestones)
mcp.tool()(milestones.list_milestone_tasks)
mcp.tool()(milestones.create_milestone)
mcp.tool()(milestones.update_milestone)
mcp.tool()(milestones.delete_milestone)
mcp.tool()(milestones.close_milestone)
mcp.tool()(milestones.reopen_milestone)

# ── 태스크 ─────────────────────────────────────────────────────
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

# ── 라벨 ───────────────────────────────────────────────────────
mcp.tool()(labels.list_labels)
mcp.tool()(labels.create_label)
mcp.tool()(labels.update_label)
mcp.tool()(labels.delete_label)
mcp.tool()(labels.get_task_labels)
mcp.tool()(labels.add_label_to_task)
mcp.tool()(labels.remove_label_from_task)


def main() -> None:
    """pyproject.toml [project.scripts] 진입점."""
    mcp.run()


if __name__ == "__main__":
    main()
