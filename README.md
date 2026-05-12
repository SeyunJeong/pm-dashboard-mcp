# PM Dashboard MCP

PM Dashboard(MediSolveAI 사내) 의 마일스톤·태스크를 **Claude Code** 등 MCP 클라이언트에서 자연어로 조작할 수 있게 해주는 MCP 서버.

> 본 패키지는 PM Dashboard REST API를 호출하는 얇은 래퍼입니다. 비즈니스 로직·DB 스키마는 포함되어 있지 않습니다.

- 버전: **0.1.0**
- 요구사항: Python **3.10+**, 활성화된 PM Dashboard 계정 + API 토큰
- 라이선스: MIT

## 노출되는 도구

### 탐색 (read-only)
- `list_services` — 서비스 목록 (service_key, jira_epic_key 등 식별 정보)
- `get_service_tasks` — 서비스 상세 (current / roadmap / backlog / completed 태스크 일괄)
- `list_milestone_tasks` — 특정 마일스톤의 태스크 + 메타데이터. `due_before` / `due_after` (YYYY-MM-DD), `status_in` (쉼표 구분) 필터 지원

### 마일스톤
- `list_milestones`, `create_milestone`, `update_milestone`
- `delete_milestone` (권한 필요), `close_milestone` / `reopen_milestone` (권한 필요)

### 태스크
- `get_task`, `create_task`, `delete_task` (권한 필요)
- `update_task_summary` (제목), `update_task_status`, `update_task_dates`
- `update_task_assignee`, `update_task_milestone`, `update_task_type`
- `update_task_backlog`, `update_task_memo`, `update_task_done_comment`

### 라벨
- `list_labels`, `create_label`, `update_label`, `delete_label`
- `get_task_labels`, `add_label_to_task`, `remove_label_from_task`

서비스 자체 CRUD(생성·수정·삭제)는 의도적으로 제외했습니다.

## 설치

### 옵션 A — GitHub에서 직접 (권장)
```bash
pip install git+https://github.com/SeyunJeong/pm-dashboard-mcp.git
```

### 옵션 B — 로컬 클론
```bash
git clone https://github.com/SeyunJeong/pm-dashboard-mcp.git
cd pm-dashboard-mcp
pip install -e .
```

설치 후 `pm-dashboard-mcp` 실행 파일이 PATH에 등록됩니다.

## 토큰 발급

1. PM Dashboard 웹에 로그인 (운영: https://pm.morgenai.news, 또는 로컬)
2. 우측 상단 프로필 클릭 → **API 토큰** 메뉴
3. **발급** 클릭 → 표시된 `ppdash_...` 토큰을 즉시 복사 (재표시 불가)

> 분실 시 동일 페이지에서 **재발급** — 기존 토큰은 자동 무효화됩니다.

## 환경 변수

| 이름 | 필수 | 기본값 | 설명 |
|------|:--:|--------|------|
| `PM_DASHBOARD_TOKEN` | ✅ | — | 발급받은 사용자 토큰 (`ppdash_...`) |
| `PM_DASHBOARD_API_URL` | | `http://49.50.128.163:8000` | 백엔드 API 베이스 URL. 로컬 개발 시 `http://localhost:8000` |

## Claude Code 등록

CLI 한 줄:
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

로컬 백엔드를 가리키려면 `env`에 `PM_DASHBOARD_API_URL`도 같이 넣어주세요.

## 사용 예시 (Claude Code)

```
> WBS의 BAY 서비스 마일스톤 보여줘
> "Q2 출시" 마일스톤 새로 만들어줘 (서비스: BAY)
> Q2 출시 마일스톤 이번 주 마감 태스크만 정리해줘
> ATCS-123 태스크 제목을 "결제 모듈 리팩터링"으로 바꿔줘
> ATCS-123을 진행 중으로 옮기고, 담당자를 김대정으로
> ATCS-456 완료 처리하고 코멘트 "QA 완료, 배포함" 추가
> "Q1 출시" 마일스톤 완료 처리
```

## 권한

요청은 토큰 발급자 본인의 권한으로 처리됩니다. 일부 도구는 추가 권한이 필요합니다.

| 도구 | 필요 권한 |
|------|----------|
| `delete_milestone` | `delete_milestone` |
| `close_milestone` / `reopen_milestone` | `milestone_complete` |
| `delete_task` | `delete_task` |

ADMIN 계정은 모든 권한이 자동 부여됩니다. 권한이 없으면 호출 시 `[403] ...권한이 없습니다` 응답이 반환됩니다.

## 보안 노트

- 토큰은 SHA-256 해시로 DB에 저장되며 평문은 발급 직후 1회만 노출됩니다.
- 사용자별 1개 토큰만 활성화됩니다 (재발급 시 기존 무효).
- 모든 변경 작업은 `audit_logs`에 기록됩니다 (토큰 사용자 정보 포함).

## 트러블슈팅

| 증상 | 확인 |
|------|------|
| `PM_DASHBOARD_TOKEN 환경변수가 비어있습니다` | Claude Code 설정의 `env`에 토큰이 들어있는지, 셸에서 직접 실행 시 export 되었는지 확인 |
| `[401] 토큰이 유효하지 않습니다` | 재발급되었을 가능성. 대시보드에서 재발급 후 클라이언트 설정 갱신 |
| `[403] ...권한이 없습니다` | ADMIN/권한 페이지에서 해당 권한 부여 |
| 연결 실패 / timeout | `PM_DASHBOARD_API_URL` 확인 (사내망 / VPN 필요 여부) |

## 개발

```bash
pip install -e .
PM_DASHBOARD_API_URL=http://localhost:8000 \
PM_DASHBOARD_TOKEN=ppdash_xxx \
  pm-dashboard-mcp
```

서버는 STDIO transport로 동작합니다 — 단독 실행 시 입력 대기 상태가 정상.

## 라이선스

MIT.
