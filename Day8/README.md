# 흉부 X-Ray AI 폐렴 진단 웹 서비스

흉부 X-Ray 이미지를 AI 모델로 분석해 폐렴 여부를 예측하는 사내 의료 웹 서비스입니다.
회원·권한 관리, 환자·진료기록 관리, AI 폐렴 예측 기능을 제공합니다.

## 팀원

| 이름 | 역할 | 담당 |
| --- | --- | --- |
| 김정린 | 팀장 | API 명세서·코드 작성 참여, 블랜치 병합(Merge)과 커밋 메시지 정리, 병합 과정에서 필요한 부분 수정 |
| 여은지 | 팀원 | 일차별로 분배된 파트의 API 명세서·코드 작성 |
| 나영철 | 팀원 | 일차별로 분배된 파트의 API 명세서·코드 작성 |
| 조예진 | 팀원 | 일차별로 분배된 파트의 API 명세서·코드 작성 |
| 이재경 | 팀원 | 일차별로 분배된 파트의 API 명세서·코드 작성 |

담당 파트는 고정하지 않고 작업하는 날마다 그날의 요구사항과 작업량에 맞춰 나눴습니다. 모든 팀원이 API 명세서 작성과 코드 작성에 참여했고, 개인 일정이 있는 날에는 그날 참여할 수 있는 팀원끼리 파트를 나눠 진행했습니다.

## 프로젝트 과정 한눈에 보기

| 단계 | 한 일 | 결과물 |
| --- | --- | --- |
| 1. Team Rule 정의 | 예시로 제공된 규칙에서 필요한 부분과 수정될 부분 추가하여 작성 | [1번 항목](#1-team-rule-정의) |
| 2. 사용자 요구사항 정의 | 요구사항 정의서 분석 및 API 명세서 작성을 위해 파트 분배 | [2번 항목](#2-사용자-요구사항-정의) |
| 3. API 명세서 작성 | 요구사항을 엔드포인트로 설계, 파트별 분담 | [3번 항목](#3-api-명세서-작성) |
| 4. Git & GitHub Branch 전략 | 브랜치, PR, 코드 리뷰, 병합 흐름 | [4번 항목](#4-git--github-branch-전략) |
| 5. 프로젝트 세팅 | 기술 스택, 폴더 구조, 실행 환경 | [5번 항목](#5-프로젝트-세팅) |

---

## 1. Team Rule 정의

### 진행 방식
- 요구사항 ID 단위로 **파트를 나눠** 맡았고, 파일명에 작업한 파트명을 표시했습니다.
- 병합 전에 PR을 올리고 **팀장님 코드 리뷰**를 거쳤습니다.

### 코드 컨벤션 
(작업 내용과 차이가 있지만 참고하면 좋을 것 같아 내용 첨부합니다.)

| 항목 | 규칙 |
| --- | --- |
| 계층 구조 | `apis`(요청/응답) → `services`(업무 로직) → `repositories`(DB 쿼리) → `models`/`schemas` |
| 라우터 | 각 파일은 `router = APIRouter()`만 선언하고, `prefix`와 `tags`는 `main.py`에서만 지정 |
| 파일 이름 | `{도메인}_{기능}_apis.py` (예: `patient_delete_apis.py`) |
| DB 접근 | SQLAlchemy 비동기(`AsyncSession`), 세션은 `Depends(async_get_db)`로 주입 |
| 인증·권한 | 보호 API는 `Depends(get_current_user)` 또는 `get_approved_user`로 로그인·권한 확인 |
| 응답·에러 | 명세서의 상태 코드와 한국어 메시지 사용, 에러 형식은 `{"detail": "메시지"}` |
| 요구사항 추적 | 코드 주석에 요구사항 ID 표기 (예: `# REQ-PRED-001`) |
| 보안 | 비밀번호는 해시로만 저장, 응답에 비밀번호·해시 포함 금지 |
| 비밀값·대용량 파일 | `.env`로 설정 관리, AI 모델 파일(`*.pth`)은 용량 문제로 git 제외 |
| 프론트엔드 | `static/`은 수정하지 않고, 백엔드 API를 프론트가 호출하는 형태에 맞춤 |

---

## 2. 사용자 요구사항 정의

### 진행 방식
- 제공된 **사용자 요구사항 정의서**를 읽고 분석한 뒤, 팀원들의 파트를 분배했습니다.
- 요구사항마다 **누가 쓰는지(권한)**, **입력과 출력**, **예외 상황**을 확인한 뒤 API로 옮겼습니다.

### 권한 정의
- 권한(`role`): `PENDING`(가입 직후, 마이페이지만 사용 가능) · `STAFF`(서비스 사용) · `ADMIN`(관리자)
- 부서(`department`): `MEDICAL`(의료) · `DEV`(개발) · `RESEARCH`(연구) — 부서에 따른 기능 차이는 없음

### 기능 요구사항

| 도메인 | 요구사항 ID | 기능 |
| --- | --- | --- |
| 회원 | REQ-USER-001 ~ 003 | 회원가입, 로그인, 로그아웃 |
| 회원 | REQ-USER-004, 005 | 회원 목록 조회, 권한 변경 (관리자) |
| 회원 | REQ-USER-006 ~ 009 | 마이페이지 조회, 정보 수정, 비밀번호 변경, 회원 탈퇴 |
| 환자 | REQ-PTNT-001 ~ 004 | 환자 등록, 목록 조회(이름·성별·나이 필터), 상세 조회, 정보 수정 |
| 환자 | REQ-PTNT-005 | 환자 정보 삭제 (관련 진료기록·X-Ray 이미지 함께 영구 삭제) |
| 진료기록 | REQ-MDR-001 ~ 003 | 진료기록 상세 조회 (진료기록 등록·목록 조회 포함) |
| AI 예측 | REQ-PRED-001 | AI 폐렴 예측 (같은 모델의 저장된 결과가 있으면 재사용) |
| AI 예측 | REQ-PRED-002 | AI 예측 결과 목록 조회 |

### 비기능 요구사항

| 요구사항 ID | 내용 |
| --- | --- |
| NFR-USER-001 | JWT 인증: Access Token 30분, Refresh Token 7일(HTTP-only 쿠키) |
| NFR-USER-002 | 비밀번호 입력 보안(비밀번호 보기 아이콘 클릭을 통해 확인 가능) |
| NFR-USER-003 / NFR-PTNT-001 / NFR-MDR-001 / NFR-PRED-002 | 모든 API는 3초 이내에 응답 |
| NFR-PRED-001 | 모델 평가 기준: Recall(민감도) ≥ 0.90, Accuracy ≥ 0.80 (FN, 즉 폐렴을 놓치는 오진이 가장 위험) |

---

## 3. API 명세서 작성

### 진행 방식
1. 요구사항을 파트로 나눴습니다. (4일차 기준)
   - 파트 A: 회원가입, 로그인
   - 파트 B: JWT 토큰 재발급, 로그아웃
   - 파트 C: 관리자 회원 관리 (목록 조회, 권한 변경)
   - 파트 D: 마이페이지 (조회, 수정, 비밀번호 변경, 탈퇴)
2. 각자 맡은 파트의 URL, Method, Request/Response 예시를 문서로 작성하고 PR로 리뷰했습니다.
3. 5일차(환자·진료기록)와 6일차(AI 예측)도 같은 방식으로 이어갔고, 6일차에는 추론 모듈(AI), 평가·성능 점검(NFR)을 파트로 따로 나눴습니다.

### 엔드포인트 요약

| 구분 | Method & URL | 설명 | 권한 |
| --- | --- | --- | --- |
| 인증 | `POST /api/v1/users/signup` | 회원가입 (201) | 누구나 |
| 인증 | `POST /api/v1/users/login` | 로그인 (form-data: 이메일, 비밀번호). Access Token 응답 + Refresh Token 쿠키 | 누구나 |
| 인증 | `POST /api/v1/users/refresh` | Refresh 쿠키로 Access Token 재발급 | 쿠키 필요 |
| 인증 | `POST /api/v1/users/logout` | Refresh 쿠키 삭제 (Access Token이 만료돼도 성공) | 누구나 |
| 회원 | `/api/v1/users/me` , `/api/v1/users/me/password - 비밀번호 변경` | 내 정보 조회·수정, 비밀번호 변경, 회원 탈퇴 | 로그인 |
| 관리자 | `/api/v1/admin/...` | 회원 목록 조회, 권한 변경 | ADMIN |
| 환자 | `/api/v1/patients/...` | 환자 등록·목록·상세·수정 | STAFF, ADMIN |
| 환자 | `DELETE /api/v1/patients/{patient_id}` | 환자 삭제 (진료기록·이미지·히트맵 파일까지 영구 삭제) | STAFF, ADMIN |
| 진료기록 | `GET /api/v1/medical-records/{record_id}` | 진료기록 상세 조회 | STAFF, ADMIN |
| AI 예측 | `POST /api/v1/medical-records/{record_id}/predict` | 폐렴 예측. 새로 예측하면 201, 저장된 결과가 있으면 200 | STAFF, ADMIN |
| AI 예측 | `GET /api/v1/medical-records/{record_id}/analyses` | 예측 결과 목록 (최신순 배열) | STAFF, ADMIN |

### 공통 상태 코드

| 코드 | 의미 |
| --- | --- |
| 200 / 201 | 성공 / 생성 성공 |
| 204 | No Content (응답 본문 없음) |
| 400 | Bad Request (수정할 항목을 하나도 보내지 않음) |
| 401 | 토큰 없음, 만료, 위조 |
| 403 | 권한 없음 (예: `PENDING` 계정) |
| 404 | 대상 없음 (환자, 진료기록 등) |
| 409 | Conflict (이미 등록된 전화번호) |
| 422 | 요청 형식 오류 |

---

## 4. Git & GitHub Branch 전략

### 브랜치 구성

| 브랜치 | 용도 | 규칙 |
| --- | --- | --- |
| `main` | 병합이 끝난 안정된 코드 | 직접 push 금지, PR과 리뷰를 거친 코드만 병합 |
| `<type>/<설명>` | 작업 브랜치 (예: `[Feat]/UserAPI-이니셜`) | `main`에서 새로 만들고 병합 후 삭제 |

- 브랜치 이름 접두사: `[Docs]`(문서) · `[Feat]`(기능) · `[Fix]`(버그 수정)

### 작업 흐름 (GitHub Desktop)
1. `main`을 **Fetch/Pull**로 최신화
2. 새 브랜치 생성 (예: `[Feat]/UserAPI-이니셜`)
3. VS Code에서 코드·문서 작성 후 저장
4. 변경 내용을 확인하고 커밋 메시지를 적어 **Commit**
5. **Publish branch**(Push)
6. GitHub에서 **Pull Request** 생성
7. 팀원 **코드 리뷰** (수정 요청이 있으면 같은 브랜치에 커밋 추가)
8. 리뷰 승인 후 `main`에 **Merge**
9. 병합된 작업 브랜치 삭제, 다음 작업 전에 다시 `main` Pull

### 충돌을 줄이기 위한 규칙
- 각자 맡은 파트에 대한 코드 파일 생성 후 작성하고 브랜치 생성 후 push
- 모두가 쓰는 공통 파일(`deps.py`, `security.py`, `main.py`, DB 모델)은 수정 전에 사전 공유 및 합의
- 작업 시작 전과 PR 올리기 전에 `main`을 Pull해서 최신 상태 유지
- 병합 후에는 충돌 표시나 중복 코드(`import`, 함수)가 남지 않았는지 확인

---

## 5. 프로젝트 세팅

### 기술 스택

| 구분 | 사용 기술 |
| --- | --- |
| Backend | Python 3.13, FastAPI |
| 패키지 관리 | uv |
| Database | MySQL, SQLAlchemy 2.0(비동기, asyncmy), Alembic(마이그레이션) |
| 인증·보안 | JWT(Access/Refresh), HTTP-only 쿠키, 비밀번호 해시 |
| AI | PyTorch, torchvision — EfficientNet-B0 + ResNet50 + ConvNeXt-Tiny 앙상블, Grad-CAM 히트맵 |
| Frontend | HTML, CSS, JavaScript (`static/`) |
| 실행 환경 | Docker, docker-compose |

### 폴더 구조

```
.
├── app/
│   ├── main.py            # 진입점, 라우터 등록
│   ├── routers/           # 인증, 관리자 라우터
│   ├── apis/v1/           # 환자, 진료기록, AI 예측 등 API 엔드포인트
│   ├── services/          # 업무 로직
│   ├── repositories/      # DB 쿼리
│   ├── schemas/           # 요청/응답 스키마 (Pydantic)
│   ├── models/            # DB 테이블 모델 (SQLAlchemy)
│   ├── core/              # 설정, DB 연결, 인증 의존성, 보안
│   └── ai/                # 추론(inference.py), 히트맵(heatmap.py), 모델 파일(models/*.pth)
├── alembic/               # DB 마이그레이션
├── static/                # 프론트엔드 (HTML, JS, CSS)
├── scripts/               # 모델 평가 스크립트 등
├── Day1~6/                # 일차별 설계 문서
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

### 실행 방법

```bash
# 1. 패키지 설치
uv sync

# 2. 환경변수 설정: 프로젝트 루트에 .env 파일 생성 (아래 표 참고)

# 3. DB 실행 (docker-compose.yml)
docker compose up -d

# 4. 테이블 생성
uv run alembic upgrade head

# 5. AI 모델 파일 배치 (아래 참고)

# 6. 서버 실행
uv run uvicorn app.main:app --reload
```

- 접속: `http://localhost:8000` (화면), `http://localhost:8000/docs` (Swagger)

### 환경변수 (`.env`)

| 변수 | 설명 |
| --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL 접속 정보 |
| JWT 비밀키 등 | `app/core/config.py`의 설정 항목 참고 |

> `.env`는 git에 올리지 않습니다. 

### AI 모델 파일

`*.pth`는 용량 문제로 git에 올리지 않습니다. 담당자(AI 파트)에게 받아서 아래 3개를 정확히 이 이름으로 `app/ai/models/`에 넣어야 예측이 동작합니다.

- `efficientnet_b0.pth`
- `resnet50.pth`
- `convnext_tiny.pth`

서버 시작 로그에 `AI 모델 로드 완료`가 보이면 정상입니다. 파일이 없으면 서버는 켜지지만 예측 요청이 500 에러가 납니다.

### 모델 평가

```bash
uv run python -m scripts.evaluate_model --data_dir <테스트 이미지 폴더>
```

- 폴더 안에 `NORMAL/`, `PNEUMONIA/` 하위 폴더 필요
- Recall ≥ 0.90, Accuracy ≥ 0.80 기준(NFR-PRED-001)을 만족하는지 출력

---

## 6. 회고: 진행하며 겪은 점

- **프론트가 먼저 정해져 있었다.** `static/`의 호출 경로와 응답 모양이 이미 고정되어 있어서, 명세서와 달라진 부분(예: AI 예측 경로 `/predict`, `/analyses`, 목록 응답을 배열로)은 백엔드를 프론트에 맞췄습니다. 앞으로는 명세 단계에서 프론트 호출부를 함께 확인합니다.
- **공통 파일 하나가 모두의 코드를 좌우한다.** `get_current_user`가 `User` 객체를 돌려주는지에 따라 환자·진료기록·예측 API 전부가 영향을 받았습니다. 공통 파일은 먼저 정하고 병합한 뒤 각자 작업합니다.
- **같은 파일을 여럿이 고치면 충돌한다.** API를 파일 단위로 나누고, 공유 파일은 수정 전에 알리는 규칙으로 줄였습니다.
- **대용량 파일은 git 밖에서 공유한다.** 100메가가 넘어가는 파일은 따로 공유해야 했습니다.
- **같은 요청이 두 번 와도 안전해야 한다.** AI 예측은 같은 진료기록·같은 모델이면 저장된 결과를 재사용하고, DB에 `(진료기록, 모델)` 중복 방지 제약을 두어 동시 클릭에도 결과가 두 번 저장되지 않게 했습니다.
- **요구사항은 앞으로 직접 작성해야 한다.** 이번에는 정의서를 읽고 해석했지만, 다음 프로젝트에서는 사용자 시나리오부터 직접 쓰고 권한, 예외 상황, 성능 기준까지 명시합니다.
