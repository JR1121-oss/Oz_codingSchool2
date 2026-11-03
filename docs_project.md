# 🩻 AI Health — 폐렴 환자 관리 백오피스

> 흉부 X-Ray 이미지 기반 폐렴 판독 모델을 활용한 **폐렴 환자 관리 백오피스** 구축 프로젝트

| 구분 | 내용 |
| :--- | :--- |
| **Backend** | FastAPI (async), SQLAlchemy, Alembic, Pydantic |
| **Database** | MySQL |
| **패키지 관리** | uv (`pyproject.toml`, `uv.lock`) |
| **AI** | 흉부 X-Ray 폐렴 예측 모델 (`worker/models`) |
| **협업** | Git & GitHub (GitHub Flow) |
| **배포 목표** | Docker 기반 웹 서비스 배포 |

### 프로젝트 목표
- **버전 관리 및 협업**: Git & GitHub를 활용한 팀 프로젝트 버전 관리 및 협업 프로세스 숙달
- **AI 모델 서빙**: FastAPI를 활용한 인공지능 모델 서빙 API 구현
- **아키텍처 설계**: Docker 기반의 안정적인 웹 서비스 아키텍처 설계 및 배포
- **데이터 시각화**: 대시보드 구현을 통한 데이터 시각화 및 백오피스 기능 개발

---

## 🌟 프로젝트 과정 총 정리

```text
① Team Rule 정의 → ② 사용자 요구사항 정의 → ③ API 명세서 작성 → ④ Branch 전략 구성 → ⑤ 프로젝트 세팅
```

### 1. Team Rule 정의

개발에 들어가기 전 **소통 → 버전 관리 → 일정 관리 → 협업 원칙** 네 영역으로 나눠 팀 규칙을 먼저 합의했습니다.

#### 👥 팀원 소개 (6조)

| 이름 | GitHub |
| :--- | :--- |
| 김정린 (팀장) | [@JR1121-oss](https://github.com/JR1121-oss) |
| 나영철 | [@loehcgnuoy-dev](https://github.com/loehcgnuoy-dev) |
| 여은지 | [@ey607928-ai](https://github.com/ey607928-ai) |
| 이재경 | [@worud01253-creator](https://github.com/worud01253-creator) |
| 조예진 | [@redisfree](https://github.com/redisfree) |

#### ☝🏻 소통 및 회의 규칙 (Communication)
> 팀원 간 오해를 줄이고 정보 격차를 없애기 위한 규칙

- **코어 타임**: 오후 3시 10분 ~ 4시에 집중 소통·실시간 피드백. 자리 비움이나 일정 변동은 미리 공유
- **상호 존중과 호칭**: 서로를 부르는 호칭을 "님"으로 통일
- **쿠션어 사용**: "아니요, 그게 아니라~" 대신 "~의견도 좋지만, 이런 방향은 어떨까요?"
- **적극적인 참여**: 회의, 디스코드, Zep 접속 시 마이크를 켜고 의견 내기

#### 🌿 Git & GitHub 버전 관리 규칙 (Version Control)
> 코드 충돌을 최소화하고 변경 이력을 체계적으로 관리하기 위한 규칙

- **`main` 직접 푸시 금지**: 개인 작업 브랜치에서 작업한 뒤 PR로 병합 (자세한 흐름은 [4. Branch 전략](#4-git--github-branch-전략-구성))
- **코드 리뷰**: PR 병합 전 팀원 최소 1명의 리뷰·승인 필수, 본인 PR 셀프 승인 금지
- **커밋 메시지 태그**

  | 태그 | 의미 |
  | :--- | :--- |
  | `[Feat]` | 기능 추가 |
  | `[Fix]` | 버그 수정 |
  | `[Docs]` | 문서 수정 |
  | `[Refactor]` | 코드 개선 |
  | `[Test]` | 테스트 추가 및 수정 |

- **변경 사항 확인**: 커밋 전 `git status`로 확인하고 관련 파일만 선택해 커밋
- **민감 정보 보호**: API 키, 비밀번호, `.env` 업로드 금지
- **공용 코드 보호**: 협의 없는 강제 푸시나 다른 팀원 변경 사항 덮어쓰기 금지
- **1일 1커밋 (선택)**: 꾸준한 기록을 권장하되 의미 없는 커밋은 지양

#### 📋 일정 및 과제 관리 규칙 (Task Management)
> 진행 상황을 공유하고 마감까지 과제를 체계적으로 완수하기 위한 규칙

- **작업 분배 및 공유**: 매일 오전 또는 회의 시간에 당일 To-Do와 담당자 공유
- **진행 상황 업데이트**: 팀 칸반보드에 상태 업데이트 (할 일 → 진행 중 → 완료)
- **이슈 즉시 공유**: 막히는 오류는 혼자 오래 붙잡지 않고 코어 타임이나 회의에 공유
- **작업 지연 사전 공지**: 일정 내 완료가 어려우면 미리 알리고 일정·역할 조정
- **작업 결과 기록**: 완료 후 변경 사항, 해결 방법, 남은 이슈를 간단히 기록

#### 🤝 협업 시 공통 원칙 (Collaboration)

- **작업 범위 준수**: 담당 작업과 수정할 파일을 사전에 확인하고, 다른 팀원 영역을 바꿔야 하면 먼저 협의
- **충돌 발생 시 협의**: Merge Conflict는 관련 팀원과 함께 내용을 확인해 해결하고, 이해하지 못한 코드를 임의로 삭제·덮어쓰지 않음
- **소통과 피드백**: 코드 리뷰 시 수정이 필요한 이유와 개선 방향을 구체적으로 전달
- **공유 저장소 기준 준수**: 브랜치명, 커밋 메시지, PR 작성·병합 방식은 합의한 규칙을 공통 적용

#### 🧩 프로젝트 진행 중 추가된 합의

| 항목 | 내용 |
| :--- | :--- |
| **역할 분담** | 도메인(인증/관리자/마이페이지/환자/진료기록/AI 예측) 단위로 파트(A~E) 분배 |
| **공통 모듈 우선** | `core/`, `models/`는 모두가 공유하므로 개발 초기에 먼저 정의·통일 |
| **마이그레이션** | 충돌 방지를 위해 `alembic revision`은 한 명만 생성·커밋, 나머지는 `upgrade head`만 실행 |
| **프론트엔드** | `static/`(HTML·JS)은 수정하지 않고, 경로 불일치 시 **백엔드를 프론트 호출 경로에 맞춤** |

### 2. 사용자 요구사항 정의

제공된 **사용자 요구사항 정의서**를 읽고 도메인별 요구사항 ID를 기준으로 작업 범위를 나눴습니다.
요구사항 ID(`REQ-도메인-번호`)는 이후 API 명세서·브랜치·PR까지 같은 이름으로 추적하는 기준이 되었습니다.

| 도메인 | 요구사항 ID | 주요 기능 |
| :--- | :--- | :--- |
| 인증 (Auth) | TODO | 회원가입, 로그인, 토큰 재발급, 로그아웃 |
| 관리자 (Admin) | TODO | 회원 목록 조회, 회원 승인 및 권한 변경 |
| 마이페이지 (Me) | TODO | 내 정보 조회 및 수정 |
| 환자 (Patient) | `REQ-PTNT-001 ~ 005` | 환자 등록 / 목록 조회 / 상세 조회 / 수정 / 삭제 |
| 진료기록 (Medical Record) | `REQ-MDR-001 ~ 005` | 진료기록 등록, X-Ray 업로드, 목록·상세 조회 |
| AI 예측 (Prediction) | `REQ-PRED-*` | 업로드된 X-Ray 이미지로 폐렴 여부 예측 |

**비기능 요구사항 예시**
- `NFR-PTNT-001`: 환자 조회 API 응답 시간 3초 이내

**권한(Role) 정책**
- `ADMIN`: 전체 기능 + 회원 승인·권한 변경
- `STAFF`: 환자·진료기록·예측 기능 사용
- `PENDING`: 가입 승인 대기 상태로 기능 접근 불가 (`403 Forbidden`)

> 💡 회고: 이번에는 주어진 요구사항 정의서를 읽고 해석하는 방식이었지만, 앞으로는 직접 사용자 시나리오를 바탕으로 요구사항을 도출·작성하는 연습이 필요합니다.

### 3. API 명세서 작성

요구사항 ID 단위로 API 명세서를 작성해, 구현 전에 **요청/응답 규격을 팀 전체가 합의**했습니다.

**공통 규칙**
- **Base URL**: `/api/v1`
- **응답 형식**: JSON (`application/json`)
- **인증 방식**: HTTP Bearer Token (`Authorization: Bearer <access_token>`)
- **에러 응답 구조**: `{ "detail": "에러 메시지 내용" }`

**명세서 항목 구성**

| 항목 | 내용 |
| :--- | :--- |
| 개요 | 기능 설명, HTTP Method, Endpoint, 인증 여부, 허용 권한 |
| Request | Path / Query Parameter, Request Body (타입·필수 여부·설명) |
| Response | Response Body 예시(JSON), 필드 정의 |
| Status Codes | `200`, `201`, `401`, `403`, `404` 등 상황별 응답 코드 |
| 구현 가이드 | 사용할 Schema, Service 함수, Repository 쿼리 조건 |

**예시 — `REQ-PTNT-002` 환자 목록 조회**

| Method | Endpoint | 권한 | Query |
| :---: | :--- | :---: | :--- |
| `GET` | `/api/v1/patients` | STAFF, ADMIN | `name`(부분 일치), `gender`(M/F), `min_age`, `max_age` |

**API 목록 (요약)**

| 도메인 | Method | Endpoint | 설명 |
| :--- | :---: | :--- | :--- |
| Auth | TODO | `/api/v1/auth/...` | 회원가입 / 로그인 / 토큰 재발급 / 로그아웃 |
| Admin | TODO | `/api/v1/admin/...` | 회원 목록, 권한 변경 |
| Me | TODO | `/api/v1/users/me` | 내 정보 조회·수정 |
| Patient | `POST` / `GET` | `/api/v1/patients` | 환자 등록 / 목록 조회 |
| Patient | `GET` / `PATCH` / `DELETE` | `/api/v1/patients/{patient_id}` | 상세 조회 / 수정 / 삭제 |
| Medical Record | TODO | TODO | 진료기록 등록·조회 |
| Prediction | TODO | TODO | X-Ray 폐렴 예측 |

### 4. Git & GitHub Branch 전략 구성

**Git Flow**와 **GitHub Flow**를 비교한 뒤, `main`을 보호하면서도 가볍게 운영할 수 있도록 **`main` + 통합 브랜치 + 개인 `feature` 브랜치** 구조로 시작했습니다.

| 구분 | Git Flow | GitHub Flow |
| :--- | :--- | :--- |
| 특징 | 브랜치 역할을 세분화 | 단순하고 가벼움 |
| 주요 브랜치 | `main`, `develop`, `feature`, `release`, `hotfix` | `main`, `feature` |
| 적합한 환경 | 정기 릴리스·다단계 QA | 지속적 배포 웹 서비스 |

**브랜치 네이밍 규칙**: `feature/기능명_YYMMDD`

**작업 순서 (Team Rule 기준)**

```bash
# 1. 최신 통합 브랜치에서 작업 브랜치 생성
git switch main
git pull origin main
git switch -c feature/기능명_YYMMDD

# 2. 작업 후 통합 브랜치 변경 사항 동기화
git switch main
git pull origin main
git switch feature/기능명_YYMMDD
git merge main

# 3. 확인 → 커밋 → 업로드
git status
git add <파일 경로>
git commit -m "[Feat] 기능 설명"
git push -u origin feature/기능명_YYMMDD

# 4. GitHub에서 PR 생성 → 팀원 1명 이상 리뷰·승인 → 병합
```

**운영하면서 바뀐 흐름**

```text
[1단계] feature/* ── PR ──► integration-test ──► main
[2단계] feature/* ── PR ──► ai-prediction-test ──► main
```

1. 처음에는 통합 브랜치(`integration-test`)에 각자의 기능을 모아 통합 테스트를 진행했습니다.
2. 통합 테스트가 끝난 뒤 `integration-test`를 `main`에 병합하고 브랜치를 삭제했습니다.
3. AI 예측 테스트를 위해 통합 브랜치(`ai-prediction-test`)에 각자의 기능을 모아 통합 테스트를 진행했습니다.
4. 통합한 코드로 서버를 실행해, 프론트엔드 화면에서 X-Ray 업로드부터 AI 예측 결과 확인까지 정상적으로 동작하는 것을 확인했습니다.
5. 검증 후 `ai-prediction-test`를 `main`에 병합하고 브랜치를 삭제했습니다.

### 5. 프로젝트 세팅

#### 5-1. 레이어드 아키텍처

역할에 따라 계층을 분리해 팀원들이 서로의 코드에 영향을 덜 주며 병렬로 작업할 수 있도록 구성했습니다.

```text
Client (HTTP Request)
  └─► app/apis/          요청 수신 & 응답 반환
        └─► app/schemas/       입력 검증 & DTO (Pydantic)
        └─► app/services/      비즈니스 로직
              └─► app/repositories/  DB CRUD 쿼리
                    └─► app/models/        ORM 정의 (SQLAlchemy)
                          └─► MySQL
```

#### 5-2. 디렉토리 구조

```text
app/
├── ai/
│   ├── inference.py      # 모델 로드(1회) & 예측 & 확신도 계산
│   ├── heatmap.py        # Grad-CAM 히트맵 (ResNet50 기준)
├── core/                 # 전역 공통 모듈
│   ├── config.py         # .env 환경변수 관리 (pydantic-settings)
│   ├── deps.py           # 인증·권한 의존성 (get_current_user 등)
│   ├── security.py       # JWT 생성/검증, 비밀번호 해싱
│   └── db/
│       ├── databases.py  # async engine, sessionmaker, get_db
│       └── models.py
├── models/               # enum, user, patient, medical_record, xray_image, ai_analysis_results
├── schemas/              # 요청/응답 Pydantic 스키마
├── repositories/         # 도메인별 DB 쿼리
├── services/             # 도메인별 비즈니스 로직
├── apis/v1/              # patient / medical_record / prediction / user_admin / user_me API
├── routers/              # auth.py, admin.py
├── ai/                   # 모델 추론 (inference.py)
└── main.py               # 엔트리포인트 (라우터 등록, static/media 마운트, catch-all)
worker/
└── models/               # 폐렴 예측 모델 파일
static/                   # 프론트엔드 템플릿 (HTML/JS/CSS)
alembic/                  # DB 마이그레이션
```

> 모델 로드 코드가 `model.py`(초기 단독 버전)와 `app/ai/inference.py`(서비스용) 두 곳에 중복되어, 모델이 메모리에 두 번 올라가거나 임계값·전처리가 어긋날 수 있었습니다. `inference.py` 하나를 기준으로 정하고 `model.py`는 제거했습니다.

#### 5-3. API 구현 순서 (Request Lifecycle)

```text
1. models/       DB 테이블 정의 → Alembic 마이그레이션
2. schemas/      Request / Response 구조 작성
3. repositories/ CRUD 쿼리 구현
4. services/     비즈니스 로직 & 예외 처리
5. apis/         엔드포인트 작성
6. main.py       라우터 등록 (⚠️ catch_all 라우터보다 위에 등록)
```

---

## 🚀 실행 방법

```bash
# 1. 의존성 설치
uv sync

# 2. 환경변수 설정 (.env)
DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME : MySQL 접속 정보
JWT_SECRET_KEY : JWT 서명 키 (임의의 긴 문자열)
COOKIE_SECURE  : 로컬 HTTP 개발 시 false

# 3. DB 마이그레이션 적용
uv run alembic upgrade head

# 4. 서버 실행
uv run uvicorn app.main:app
```

## 🗄️ Alembic Migration Guide

### 1. 마이그레이션 파일 생성 (자동 생성)
모델(`app/models/`)이 변경된 경우 다음 명령어를 실행하여 마이그레이션 파일을 생성합니다.
```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"
```

### 2. 데이터베이스에 반영
```bash
uv run alembic upgrade head
```

### 3. 이전 상태로 되돌리기 (Rollback)
```bash
uv run alembic downgrade -1
```

> ⚠️ 새 모델을 추가했다면 `app/models/__init__.py`에 import해야 Alembic이 감지합니다.
gi