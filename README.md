# PM Dashboard MCP

PM Dashboard(메디솔브 사내) 의 마일스톤·태스크를 **Claude Code** 등 MCP 클라이언트에서 자연어로 조작할 수 있게 해주는 MCP 서버.

> **이 리포는 코드 미러입니다.** 실제 서버는 PM Dashboard 백엔드에 mount 된 streamable-http MCP 엔드포인트로 운영됩니다. 본 리포의 `src/pm_dashboard/mcp_server/` 는 본체 리포(`SeyunJeong/pm-dashboard`, private)에서 자동 동기화됩니다.

- 엔드포인트: `https://mcp.morgenai.news/mcp/`
- 인증: Bearer 토큰 (`ppdash_...`, PM Dashboard 웹에서 발급)
- 프로토콜: MCP streamable-http (1.27.x)
- 라이선스: MIT

## 등록 (Claude Code)

`~/.claude.json`:

```json
{
  "mcpServers": {
    "pm-dashboard": {
      "type": "http",
      "url": "https://mcp.morgenai.news/mcp/",
      "headers": {
        "Authorization": "Bearer ppdash_xxx"
      }
    }
  }
}
```

Claude Code 재시작하면 36개 도구가 노출됩니다. **Python·pip·SSH 설치 불필요.**

## 토큰 발급

1. PM Dashboard 웹 (https://pm.morgenai.news) 로그인
2. 우측 상단 프로필 → **API 토큰** → **발급**
3. 표시된 `ppdash_...` 즉시 복사 (재표시 불가, 분실 시 재발급)

> 사용자별 1개 토큰만 활성. 재발급 시 기존 무효.

## 노출 도구 (36개)

### 탐색 (2)
- `list_services` — 등록 서비스 요약 (마일스톤·태스크 카운트, 신호등)
- `get_service_tasks` — 서비스 상세 (current / roadmap / backlog / completed)

### 마일스톤 (7)
- `list_milestones`, `list_milestone_tasks` (`due_before` / `due_after` / `status_in` 필터)
- `create_milestone`, `update_milestone`
- `delete_milestone` (`delete_milestone` 권한)
- `close_milestone` / `reopen_milestone` (`milestone_complete` 권한)

### 태스크 (12)
- `get_task`, `create_task`, `delete_task` (`delete_task` 권한)
- `update_task_summary` (제목), `update_task_status`, `update_task_dates`
- `update_task_assignee`, `update_task_milestone`, `update_task_type`
- `update_task_backlog`, `update_task_memo`, `update_task_done_comment`

### 하위작업 / 체크리스트 (4 + 4 별칭)
- `list_subtasks` (별칭 `list_checklist`)
- `add_subtask` (별칭 `add_checklist_item`)
- `update_subtask` (별칭 `update_checklist_item`) — `is_checked` 로 체크/해제
- `delete_subtask` (별칭 `delete_checklist_item`)

### 라벨 (7)
- `list_labels`, `create_label`, `update_label`, `delete_label`
- `get_task_labels`, `add_label_to_task`, `remove_label_from_task`

서비스 자체 CRUD(생성·수정·삭제)는 의도적으로 제외.

## 사용 예시 (Claude Code)

```
> WBS의 BAY 서비스 마일스톤 보여줘
> "Q2 출시" 마일스톤 새로 만들어줘 (서비스: BAY)
> Q2 출시 마일스톤 이번 주 마감 태스크만 정리해줘
> ATCS-123 태스크 제목을 "결제 모듈 리팩터링"으로 바꿔줘
> ATCS-123을 진행 중으로 옮기고, 담당자를 김대정으로
> ATCS-456 완료 처리하고 코멘트 "QA 완료, 배포함" 추가
> "Q1 출시" 마일스톤 완료 처리
> ATCS-123에 "디자인 QA" 하위작업 추가해줘
> ATCS-123 체크리스트 3번 항목 체크 처리
```

## 권한

| 도구 | 필요 권한 |
|---|---|
| `delete_milestone` | `delete_milestone` |
| `close_milestone` / `reopen_milestone` | `milestone_complete` |
| `delete_task` / `delete_subtask` | `delete_task` |

ADMIN 계정은 자동 부여. 권한 없으면 호출 시 `[403] ...권한이 없습니다` 응답.

## 보안 노트

- 토큰은 SHA-256 해시로 DB 저장. 평문은 발급 직후 1회만 노출.
- 모든 변경 작업은 `audit_logs` 에 기록 (토큰 사용자 정보 포함).
- 토큰 분실 시 즉시 PM Dashboard 웹에서 재발급 (기존 자동 무효).

## 피드백 / 기여

- **Issues** — 도구 동작 이슈, 자연어 인식 어색함, 도구 추가 제안 등 환영합니다.
- **Pull Requests** — 받아서 본체 리포에 반영 후 다음 동기화에 자동 반영됩니다. (이 리포는 자동 미러라 PR 을 직접 머지하지는 않습니다.)

PR 작성 시 어느 도구 / 어느 service 함수 영향인지 명시해주세요.

## 트러블슈팅

| 증상 | 확인 |
|---|---|
| `로그인이 필요합니다` (401) | `Authorization` 헤더에 Bearer 토큰 있는지, 토큰이 `ppdash_` 로 시작하는지 |
| `토큰이 유효하지 않습니다` (401) | 다른 곳에서 재발급됐을 가능성. 대시보드에서 재발급 후 config 갱신 |
| `...권한이 없습니다` (403) | ADMIN 또는 권한 페이지에서 해당 권한 부여 |
| `Invalid Host header` (421) | 보통 reverse-proxy 설정 이슈. 운영자에게 문의 |
| 연결 실패 | `mcp.morgenai.news` HTTPS 가 사내망에서 닿는지 확인 |

## 변경 이력

- **v0.3.0 (2026-05-13)** — stdio → HTTP transport 전환. `pip install` 폐기. mcp.morgenai.news/mcp/ 엔드포인트로 통일.
- v0.2.0 — 하위작업/체크리스트 CRUD 4개 + 별칭 4개 추가
- v0.1.0 — 초기 stdio 패키지 (하위작업/체크리스트 CRUD 4개 + 별칭 4개 추가)

> stdio 방식 사용 이력이 있다면 `~/.claude.json` 의 `pm-dashboard` 블록을 위 HTTP 방식으로 교체하세요. `pip uninstall pm-dashboard-mcp` 로 옛 패키지 정리는 선택.

## 라이선스

MIT.
