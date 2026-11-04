# 🩻 AI Health — 흉부 X-Ray 폐렴 환자 관리 백오피스

> 흉부 X-Ray 이미지 기반 폐렴 판독 모델을 활용한 **폐렴 환자 관리 백오피스** 구축 프로젝트 (6조)

| 구분 | 내용 |
| :--- | :--- |
| **Backend** | FastAPI (async), SQLAlchemy, Alembic, Pydantic |
| **Database** | MySQL 8.0 |
| **패키지 관리** | uv (`pyproject.toml`, `uv.lock`) |
| **AI** | 흉부 X-Ray 폐렴 예측 모델 (PyTorch, `worker/models`) + Grad-CAM 히트맵 |
| **협업** | Git & GitHub (PR 기반 코드 리뷰) |
| **배포 목표** | Docker 기반 웹 서비스 (`docker-compose.yml`) |

### 프로젝트 목표
- **버전 관리 및 협업**: Git & GitHub를 활용한 팀 프로젝트 버전 관리 및 협업 프로세스 숙달
- **AI 모델 서빙**: FastAPI를 활용한 인공지능 모델 서빙 API 구현
- **아키텍처 설계**: Docker 기반의 안정적인 웹 서비스 아키텍처 설계 및 배포
- **데이터 시각화**: 대시보드 구현을 통한 데이터 시각화 및 백오피스 기능 개발

---

## 🌟 프로젝트 과정 총 정리

```text
① Team Rule 정의 → ② 사용자 요구사항 정의 → ③ API 명세서 작성 → ④ Git & GitHub Branch 전략 구성 → ⑤ 프로젝트 세팅
```

| 일차 | 진행 내용 | 관련 문서 |
| :---: | :--- | :--- |
| 1일차 | Team Rule 정의 | [Day1](Day1/day1_team_rules.md) |
| 2일차 | Git & GitHub Branch 전략 학습·선택 | [Day2](Day2/docs_git_branch.md) |
| 3일차 | 프로젝트 템플릿 분석, DB 마이그레이션 | [Day3](Day3/day3_project_structure.md), [Day3 마이그레이션](Day3/day3_db_migration.md) |
| 4일차 | User API 설계, 디렉토리 구조 및 파트 분담 | [Day4](Day4/day4_USER_API_design.md) |
| 5일차 | 환자 관리·진료기록 API 설계 | [Day5](Day5/day5_001~004_api.md) |
| 6일차 | AI 폐렴 예측 API 설계 | [Day6](Day6/day6_prediction_API.md) |
| 7일차 | 통합 테스트 및 앱 실행 화면 확인 | [Day7](Day7/docs_image.md) |

---

### 1. Team Rule 정의

개발에 들어가기 전 **소통 → 버전 관리 → 일정 관리 → 협업 원칙** 네 영역으로 나눠 팀 규칙을 먼저 합의했습니다. 전체 내용은 [Day1 문서](Day1/day1_team_rules.md)에 있습니다.

#### 👥 팀원 소개

| 이름 | GitHub |
| :--- | :--- |
| 김정린 (팀장) | [@JR1121-oss](https://github.com/JR1121-oss) |
| 나영철 | [@loehcgnuoy-dev](https://github.com/loehcgnuoy-dev) |
| 여은지 | [@ey607928-ai](https://github.com/ey607928-ai) |
| 이재경 | [@worud01253-creator](https://github.com/worud01253-creator) |
| 조예진 | [@redisfree](https://github.com/redisfree) |

#### ☝🏻 소통 및 회의 규칙
- **코어 타임**: 오후 3시 10분 ~ 4시에 집중 소통·실시간 피드백. 자리 비움이나 일정 변동은 미리 공유
- **호칭 통일**: 서로를 "님"으로 부름
- **쿠션어 사용**: "아니요, 그게 아니라~" 대신 "~의견도 좋지만, 이런 방향은 어떨까요?"
- **적극적인 참여**: 회의, 디스코드, Zep 접속 시 마이크를 켜고 의견 내기

#### 🌿 Git & GitHub 버전 관리 규칙
- **`main` 직접 푸시 금지**: 개인 작업 브랜치에서 작업한 뒤 PR로 병합
- **코드 리뷰**: PR 병합 전 팀원 최소 1명의 리뷰·승인 필수, 본인 PR 셀프 승인 금지
- **커밋 메시지 태그**: `[Feat]` 기능 추가 / `[Fix]` 버그 수정 / `[Docs]` 문서 수정 / `[Refactor]` 코드 개선 / `[Test]` 테스트
- **변경 사항 확인**: 커밋 전 `git status`로 확인하고 관련 파일만 선택해 커밋
- **민감 정보 보호**: API 키, 비밀번호, `.env` 업로드 금지 (`.env.example`만 공유)
- **공용 코드 보호**: 협의 없는 강제 푸시, 다른 팀원 변경 사항 덮어쓰기 금지

#### 📋 일정 및 과제 관리 규칙
- 매일 오전 또는 회의 시간에 당일 To-Do와 담당자 공유
- 칸반보드로 상태 관리 (할 일 → 진행 중 → 완료)
- 막히는 오류는 혼자 오래 붙잡지 않고 코어 타임이나 회의에 공유, 지연이 예상되면 미리 공지
- 작업 완료 후 변경 사항, 해결 방법, 남은 이슈를 간단히 기록

#### 🤝 협업 시 공통 원칙
- 담당 파일을 사전에 확인하고, 다른 팀원 영역을 바꿔야 하면 먼저 협의
- Merge Conflict는 관련 팀원과 함께 내용을 확인해 해결하고, 이해하지 못한 코드를 임의로 삭제·덮어쓰지 않음
- 코드 리뷰 시 수정이 필요한 이유와 개선 방향을 구체적으로 전달

#### 🧩 프로젝트 진행 중 추가된 합의

| 항목 | 내용 |
| :--- | :--- |
| **역할 분담** | 도메인(인증/관리자/마이페이지/환자/진료기록/AI 예측) 단위로 파트(A~E)를 나눠 담당 |
| **공통 모듈 우선** | `core/`, `models/`는 모두가 공유하므로 개발 초기에 먼저 정의·통일 |
| **마이그레이션** | 충돌 방지를 위해 `alembic revision`은 한 명만 생성·커밋하고, 나머지는 `upgrade head`만 실행 |
| **프론트엔드** | `static/`(HTML·JS)은 수정하지 않고, 경로가 맞지 않으면 **백엔드를 프론트 호출 경로에 맞춤** |

---

### 2. 사용자 요구사항 정의

제공된 **사용자 요구사항 정의서**를 읽고, 도메인별 요구사항 ID를 기준으로 작업 범위를 나눴습니다. 요구사항 ID(`REQ-도메인-번호`)는 API 명세서, 브랜치, PR까지 같은 이름으로 추적하는 기준이 되었습니다.

| 도메인 | 요구사항 ID | 주요 기능 |
| :--- | :--- | :--- |
| 인증 (Auth) | `REQ-USER-001 ~ 003`, `NFR-USER-001` | 회원가입, 로그인, 로그아웃, 액세스 토큰 재발급 |
| 관리자 (Admin) | `REQ-USER-004 ~ 005` | 회원 목록 조회(검색·부서 필터), 회원 권한 변경 |
| 마이페이지 (Me) | `REQ-USER-006 ~ 009` | 내 정보 조회·수정, 비밀번호 변경, 회원 탈퇴 |
| 환자 (Patient) | `REQ-PTNT-001 ~ 004` + 삭제 | 환자 등록 / 목록 조회 / 상세 조회 / 수정 / 삭제 |
| 진료기록 (Medical Record) | `REQ-MDR-*` | 진료기록 등록, X-Ray 업로드, 목록·상세 조회 |
| AI 예측 (Prediction) | `REQ-PRED-001 ~ 002` | 업로드된 X-Ray로 폐렴 예측, 예측 결과 목록 조회 |

**비기능 요구사항**

| ID | 내용 |
| :--- | :--- |
| `NFR-USER-001` | JWT 인증 (액세스 토큰 30분, 리프레시 토큰 7일 HttpOnly 쿠키) |
| `NFR-USER-002` | 비밀번호 입력 마스킹·보기 아이콘 (프론트엔드에서 처리) |
| `NFR-USER-003`, `NFR-PTNT-001`, `NFR-PRED-002` | 모든 API 3초 이내 응답 |
| `NFR-PRED-001` | 모델 평가 기준: Recall 0.90 이상(우선), Accuracy 0.80 이상 |

**권한(Role) 정책**

| Role | 설명 |
| :--- | :--- |
| `ADMIN` | 전체 기능 + 회원 승인·권한 변경 |
| `STAFF` | 환자·진료기록·예측 기능 사용 |
| `PENDING` | 회원가입 직후 기본값. 마이페이지 외 접근 불가 (`403 Forbidden`) |

> 💡 **회고**: 이번에는 주어진 요구사항 정의서를 읽고 해석하는 방식이었습니다. 앞으로는 사용자 시나리오를 바탕으로 요구사항을 직접 도출·작성하는 연습이 필요합니다.

---

### 3. API 명세서 작성

요구사항 ID 단위로 API 명세서를 작성해, 구현 전에 **요청/응답 규격을 팀 전체가 합의**했습니다. 담당 파트별로 문서를 나눠 작성했고([Day4](Day4/day4_USER_API_design.md) · [Day5](Day5/day5_001~004_api.md) · [Day6](Day6/day6_prediction_API.md)), 파트별 문서를 합치면서 공통 규칙을 통일했습니다.

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
| Status Codes | `200`, `201`, `204`, `401`, `403`, `404`, `409`, `422` 등 상황별 응답 코드 |
| 구현 가이드 | 사용할 Schema, Service 함수, Repository 쿼리 조건 |

**API 목록 (실제 구현 기준)**

| 도메인 | Method | Endpoint | 설명 |
| :--- | :---: | :--- | :--- |
| Auth | `POST` | `/api/v1/users/signup` | 회원가입 |
| Auth | `POST` | `/api/v1/users/login` | 로그인 (액세스 토큰 + 리프레시 쿠키) |
| Auth | `POST` | `/api/v1/users/refresh` | 액세스 토큰 재발급 |
| Auth | `POST` | `/api/v1/users/logout` | 로그아웃 |
| Me | `GET` / `PATCH` / `DELETE` | `/api/v1/users/me` | 내 정보 조회 / 수정 / 회원 탈퇴 |
| Me | `PATCH` | `/api/v1/users/me/password` | 비밀번호 변경 |
| Admin | `GET` | `/api/v1/admin/users` | 회원 목록 조회 (검색·부서 필터) |
| Admin | `PATCH` | `/api/v1/admin/users/{user_id}/role` | 회원 권한 변경 |
| Patient | `POST` / `GET` | `/api/v1/patients` | 환자 등록 / 목록 조회 |
| Patient | `GET` / `PATCH` / `DELETE` | `/api/v1/patients/{patient_id}` | 환자 상세 조회 / 수정 / 삭제 |
| Medical Record | `POST` | `/api/v1/medical-records` | 진료기록 등록 (Form-Data, X-Ray 업로드) |
| Medical Record | `GET` | `/api/v1/patients/{patient_id}/medical-records` | 환자별 진료기록 목록 |
| Medical Record | `GET` | `/api/v1/medical-records/{record_id}` | 진료기록 상세 조회 |
| Medical Record | `GET` | `/api/v1/medical-records/{record_id}/image` | X-Ray 이미지 조회 |
| Prediction | `POST` | `/api/v1/medical-records/{record_id}/predict` | AI 폐렴 예측 (저장된 결과가 있으면 재사용) |
| Prediction | `GET` | `/api/v1/medical-records/{record_id}/analyses` | 예측 결과 목록 조회 |

> 📝 **명세와 구현의 차이**: 초기 명세서(예: 관리자 API는 `/api/v1/users`, 예측 API는 `/predictions`)와 최종 구현 경로가 일부 다릅니다. 팀 합의에 따라 프론트엔드(`static/apis.js`)가 실제로 호출하는 경로에 백엔드를 맞췄기 때문입니다. 변경 이력은 각 일차 문서에 남아 있습니다.

---

### 4. Git & GitHub Branch 전략 구성

[Git Flow와 GitHub Flow를 비교](Day2/docs_git_branch.md)한 뒤, `main`을 보호하면서도 가볍게 운영할 수 있도록 **`main` + 개인 `feature` 브랜치** 구조로 진행했습니다.

| 구분 | Git Flow | GitHub Flow |
| :--- | :--- | :--- |
| 특징 | 브랜치 역할을 세분화 | 단순하고 가벼움 |
| 주요 브랜치 | `main`, `develop`, `feature`, `release`, `hotfix` | `main`, `feature` |
| 적합한 환경 | 정기 릴리스·다단계 QA | 지속적 배포 웹 서비스 |

**브랜치 네이밍 규칙**: `feature/기능명_YYMMDD`

**작업 순서**

```bash
# 1. 최신 브랜치에서 작업 브랜치 생성
git switch main
git pull origin main
git switch -c feature/기능명_YYMMDD

# 2. 작업 후 최신 변경 사항 동기화
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
---

### 5. 프로젝트 세팅

#### 5-1. 레이어드 아키텍처

역할에 따라 계층을 분리해, 팀원들이 서로의 코드에 영향을 덜 주며 병렬로 작업할 수 있도록 구성했습니다.

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
│   └── heatmap.py        # Grad-CAM 히트맵
├── core/                 # 전역 공통 모듈
│   ├── config.py         # .env 환경변수 관리 (pydantic-settings)
│   ├── deps.py           # 인증·권한 의존성 (get_current_user 등)
│   ├── security.py       # JWT 생성/검증, 비밀번호 해싱 (argon2)
│   └── db/
│       ├── databases.py  # async engine, sessionmaker, get_db
│       └── models.py
├── models/               # enum, user, patient, medical_record, xray_image, ai_analysis_results
├── schemas/              # 요청/응답 Pydantic 스키마
├── repositories/         # 도메인별 DB 쿼리
├── services/             # 도메인별 비즈니스 로직
├── apis/v1/              # patient / medical_record / prediction / user_admin / user_me API
├── routers/              # auth.py, admin.py
└── main.py               # 엔트리포인트 (라우터 등록, static/media 마운트, catch-all)
worker/models/            # 폐렴 예측 모델 파일
scripts/evaluate_model.py # 모델 평가 (Recall, Accuracy)
static/                   # 프론트엔드 템플릿 (HTML/JS/CSS)
alembic/                  # DB 마이그레이션
```

#### 5-3. DB 설계 및 마이그레이션 ([Day3](Day3/day3_db_migration.md))

- 테이블 5개: `users`, `patients`, `medical_records`, `xray_images`, `ai_analysis_results`
- 외래 키: `medical_records.patient_id → patients.id`, `xray_images.record_id → medical_records.id`, `xray_images.uploader_id → users.id`, `ai_analysis_results.record_id → medical_records.id`
- SQLAlchemy 모델을 기준으로 Alembic 자동 마이그레이션을 생성하고, 적용 후 테이블·컬럼·외래 키가 모델과 일치하는지 DB 뷰어로 검증했습니다.

#### 5-4. API 구현 순서 (Request Lifecycle)

```text
1. models/       DB 테이블 정의 → Alembic 마이그레이션
2. schemas/      Request / Response 구조 작성
3. repositories/ CRUD 쿼리 구현
4. services/     비즈니스 로직 & 예외 처리
5. apis/         엔드포인트 작성
6. main.py       라우터 등록 (⚠️ catch_all 라우터보다 위에 등록)
```

#### 5-5. 개발 환경

- **의존성**: `uv`로 관리하고 `uv.lock`으로 팀원 간 동일한 버전을 보장합니다. (Python 3.13 이상)
- **환경변수**: `.env.example`을 복사해 `.env`를 만들고 값을 채웁니다. 실제 `.env`는 커밋하지 않습니다.
- **Docker**: `docker-compose.yml`로 FastAPI 서버와 MySQL 8.0을 함께 실행하며, 서버에는 `/healthcheck`를 두었습니다.
- **AI 모델 서빙**: 모델은 서버 시작 시 한 번만 로드(`lifespan`)하고, 추론은 `asyncio.to_thread`로 실행해 다른 요청을 막지 않게 했습니다.

---

## 🚀 실행 방법

```bash
# 1. 의존성 설치
uv sync

# 2. 환경변수 설정
cp .env.example .env
#   DB_USER, DB_PASSWORD, DB_ROOT_PASSWORD, DB_HOST, DB_PORT, DB_NAME : MySQL 접속 정보
#   JWT_SECRET_KEY : JWT 서명 키 (임의의 긴 문자열)
#   COOKIE_SECURE  : 로컬 HTTP 개발 시 false

# 3. DB 마이그레이션 적용
uv run alembic upgrade head

# 4. 서버 실행
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Docker로 실행하려면 `docker compose up --build`
- API 문서(Swagger): `http://localhost:8000/docs`
- 예측 모델 파일은 `worker/models/`에 두어야 AI 예측이 동작합니다. (모델 파일이 없으면 서버는 켜지지만 예측 요청은 실패합니다.)

## 🗄️ Alembic Migration Guide

이 프로젝트는 데이터베이스 마이그레이션을 위해 Alembic을 사용합니다.

### 1. 마이그레이션 파일 생성 (자동 생성)
모델(`app/models/`)이 변경된 경우 다음 명령어를 실행하여 마이그레이션 파일을 생성합니다.
```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"
```

### 2. 데이터베이스에 반영
생성된 마이그레이션을 데이터베이스에 적용하려면 다음 명령어를 실행합니다.
```bash
uv run alembic upgrade head
```

### 3. 이전 상태로 되돌리기 (Rollback)
마지막 마이그레이션을 취소하려면 다음 명령어를 실행합니다.
```bash
uv run alembic downgrade -1
```

> ⚠️ 새 모델을 추가했다면 `app/models/__init__.py`에 import해야 Alembic이 감지합니다.