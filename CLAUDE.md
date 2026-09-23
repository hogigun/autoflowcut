# autoflowcut 작업 메모

이 저장소는 사용자(hogigun)가 [AutoFlowCut](https://github.com/touchizen/AutoFlowCut)(AGPL-3.0)을
클로드 코드로 활용하기 위한 작업 공간이다. 사용자의 주 목적은 **야담 원고 작성**이다.
세션이 바뀌어도 아래 내용을 기억하고 쉬운 말로 안내할 것.

## AutoFlowCut이 뭔가
- 데스크톱 앱. 대본 → 장면별 AI 이미지/영상 생성 → 캡컷(CapCut)/프리미어/Vrew 프로젝트로 원클릭 내보내기.
- 클로드 코드와 연결되는 통로가 두 가지 있다.

## 1. MCP 서버 = 클로드 코드가 앱을 "리모컨"처럼 조종
공식 설명서: https://touchizen.com/guide/ko/autoflowcut/mcp-guide.html
(원문 요약본: touchizen/AutoFlowCut 저장소의 `mcp-server/README.md`)

연결 방법 (사용자 PC에서):
1. 앱 설치 → 앱 **설정 > MCP HTTP 서버 > ON** (포트 3210)
2. `cd AutoFlowCut/mcp-server && npm install`
3. `claude mcp add --scope user --transport stdio flow2capcut -- node /경로/AutoFlowCut/mcp-server/index.js`
4. `claude mcp list`로 확인
- `app_*` 도구는 앱이 켜져 있고 HTTP 서버가 ON일 때만 동작.
- 클라우드 세션(claude.ai/code)에서는 사용자 PC의 앱에 접속 불가 → 앱 조종은 PC의 클로드 코드에서만.

할 수 있는 일 (도구 이름 → 쉬운 말):
| 분류 | 도구 | 하는 일 |
|---|---|---|
| 장면(CSV) | `load_csv`, `save_csv` | 장면 목록 파일 열기/저장 |
| | `list_scenes`, `get_scene`, `search_scenes`, `get_stats` | 장면 보기·검색·통계 |
| | `update_prompt`, `batch_update_prompts`, `update_field` | 장면 프롬프트 하나/여러 개 한꺼번에 고치기 |
| | `list_problem_scenes`, `get_scene_image` | 문제 있는 장면 골라내기, 이미지 위치 확인 |
| 레퍼런스 | `list_references`, `get_reference`, `update_reference_prompt` | 캐릭터·배경 설정 보기/고치기 |
| 앱 직접 조작 | `app_status` | 앱 연결 확인 |
| | `app_get_scenes`, `app_update_scene` | 앱 화면의 장면 보기/고치기 |
| | `app_get_references`, `app_update_reference` | 앱 화면의 레퍼런스 보기/고치기 |
| | `app_generate_scene`, `app_generate_reference` | 이미지 한 장 다시 만들기 |
| | `app_start_scene_batch`, `app_start_ref_batch` | 이미지 일괄 생성 시작 (스타일 지정 가능) |
| | `app_batch_status`, `app_wait_batch` | 생성 진행 상황 확인/완료까지 대기 |
| 기타 | `list_styles` | 스타일 프리셋 목록 |
| | `export_capcut` | 캡컷으로 내보내기 |
| | `install_skill`, `list_skills` | 스토리 엔진 스킬 설치/확인 |
| | `get_progress` | 스토리 엔진 진행 상태 읽기 |

말로 시키는 예:
- "모든 장면 프롬프트를 수채화 스타일로 바꿔줘"
- "이미지 실패한 장면만 찾아서 다시 생성해줘"
- "주인공 레퍼런스 외모를 '30대 선비, 갓, 흰 도포'로 바꾸고 전부 다시 만들어줘"
- "한국 애니 스타일로 전체 이미지 일괄 생성 시작하고 끝나면 캡컷으로 내보내줘"

## 2. 스토리 엔진 = 야담 원고를 쓰는 스킬 (사용자가 원하는 것)
스킬: `story-engine`, `story-new`, `story-execute`, `story-step`, `story-next`, `story-rewrite`
(앱 첫 실행 시 자동 설치. 원본은 touchizen/AutoFlowCut의 `skills/`)

- 시작: `/story-new 1 --genre yadam` 또는 "새 에피소드, 주제는 ○○ 야담"
- 한국어 + 야담/민담/조선/설화/전설 → 자동으로 야담 장르
- 9단계: W1 스토리 설계 → W2 20챕터 시놉시스 → **W3 대본 작성·검토(목표 9.5점)** → 🛑 사용자 승인
  → W4~W5 음성/효과음(TTS 키 필요) → W6~W7 스토리보드·이미지(앱 필요) → W8 캡컷 내보내기(앱 필요) → W9 업로드 정보
- **원고만 원하면 W1~W3까지만** 하면 되고, 이 부분은 앱 없이 클라우드 세션에서도 가능
  (작업 폴더 경로는 앱 대신 사용자에게 물어보면 됨).
- 핵심 원칙: 궁금증 + 기대감 = 몰입도. 진실은 16~17챕터에서 폭로, 15챕터 전에 드러나면 실패.
