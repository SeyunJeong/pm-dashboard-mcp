# PM Dashboard MCP

PM Dashboard(MediSolveAI 사내) 의 마일스톤·태스크를 **Claude Code** 등 MCP 클라이언트에서 자연어로 조작할 수 있게 해주는 MCP 서버.

> 본 패키지는 PM Dashboard REST API를 호출하는 얇은 래퍼입니다. 비즈니스 로직·DB 스키마는 포함되어 있지 않습니다.

## 노출되는 도구 (v0.1)

### 탐색 (read-only)
- `list_services` — 서비스 목록 (service_key, jira_epic_key 등 식별 정보)
- `get_service_tasks` — 서비스 상세 (current/roadmap/backlog/completed 태스크 모두)

### 마일스톤
- `list_milestones`, `create_milestone`, `update_milestone`, `delete_milestone`, `close_milestone`, `reopen_milestone`

### 태스크
- `get_task`, `create_task`, `delete_task`
- `update_task_summary` (제목), `update_task_status`, `update_task_dates`, `update_task_assignee`, `update_task_milestone`, `update_task_type`, `update_task_backlog`, `update_task_memo`, `update_task_done_comment`

### 라벨
- `list_labels`, `create_label`, `update_label`, `delete_label`
- `get_task_labels`, `add_label_to_task`, `remove_label_from_task`

서비스 자체 CRUD(생성·수정·삭제)는 의도적으로 제외했습니다.

## 설치

### 옵션 A — GitHub에서 직접
```bash
pip install git+https://github.com/SeyunJeong/pm-dashboard-mcp.git
```

### 옵션 B — 로컬 클론
```bash
git clone https://github.com/SeyunJeong/pm-dashboard-mcp.git
cd pm-dashboard-mcp
pip install -e .
```

## 토큰 발급

1. PM Dashboard 웹에 로그인 (https://pm.morgenai.news 또는 로컬)
2. 우측 상단 프로필 클릭 → **API 토큰** 메뉴
3. **발급** 클릭 → 표시된 `ppdash_...` 토큰을 즉시 복사 (재표시 불가)

## Claude Code 등록

```bash
claude mcp add pm-dashboard \
  -e PM_DASHBOARD_TOKEN=ppdash_xxx \
  -- pm-dashboard-mcp
```

또는 `~/.claude.json` 직접 편집:

```json
{
  "mcpServers": {
    "pm-dashboard": {
      "command": "pm-dashboard-mcp",
      "env": {
        "PM_DASHBOARD_TOKEN": "ppdash_xxx"
      }
    }
  }
}
```

다른 API URL을 쓰려면 `PM_DASHBOARD_API_URL` 환경변수로 덮어쓸 수 있습니다 (기본: `http://49.50.128.163:8000`).

## 사용 예시 (Claude Code)

```
> WBS의 BAY 서비스 마일스톤 보여줘
> "Q2 출시" 마일스톤 새로 만들어줘 (서비스: BAY)
> ATCS-123 태스크 제목을 "결제 모듈 리팩터링"으로 바꿔줘
> ATCS-123을 진행 중으로 옮기고, 담당자를 김대정으로
> ATCS-456 완료 처리하고 코멘트 "QA 완료, 배포함" 추가
> "Q1 출시" 마일스톤 완료 처리
```

## 권한

요청은 토큰 발급자 본인의 권한으로 처리됩니다. 일부 도구는 추가 권한이 필요할 수 있습니다.

- `delete_milestone` → `delete_milestone` 권한
- `close_milestone` / `reopen_milestone` → `milestone_complete` 권한
- `delete_task` → `delete_task` 권한
- ADMIN 계정은 모든 권한 자동 부여

권한이 없으면 호출 시 `[403] ...권한이 없습니다` 응답이 반환됩니다.

## 보안 노트

- 토큰은 SHA-256 해시로 DB에 저장되며 평문은 발급 직후 1회만 노출됩니다. 분실 시 대시보드 토큰 페이지에서 **재발급** (기존 토큰 자동 무효).
- 사용자별 1개 토큰만 활성화됩니다.
- 모든 변경 작업은 `audit_logs`에 기록됩니다 (토큰 사용자 정보 포함).

## 개발

```bash
pip install -e .
PM_DASHBOARD_TOKEN=ppdash_xxx pm-dashboard-mcp  # 로컬 백엔드 실행 중이면 PM_DASHBOARD_API_URL=http://localhost:8000 추가
```

## 라이선스

MIT.
