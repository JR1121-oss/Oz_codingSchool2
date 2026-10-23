# 3일차: 프로젝트 템플릿 뜯어보기

본 문서는 FastAPI 기반 백엔드 프로젝트 템플릿의 핵심 구조, 파일별 역할, DB 연결, 마이그레이션 방법 및 API Request Lifecycle을 정리한 가이드입니다.

---

## 1. 프로젝트 구조 및 디렉터리별 역할

프로젝트는 역할에 따라 계층(Layer)을 분리하여 관리합니다.

```text
Client (HTTP Request)
  └─► app/apis/         [라우터/컨트롤러] 요청 받기 & 응답 반환
        └─► app/schemas/      [Pydantic] 입력 유효성 검증 & DTO
        └─► app/services/     [비즈니스 로직] 핵심 업무 규칙 및 가공
              └─► app/repositories/ [데이터 접근] DB direct CRUD 쿼리
                    └─► app/models/       [SQLAlchemy] DB 테이블 ORM 정의
                          └─► Database (MySQL)
```

| 구분/경로 | 역할 및 작성 내용 |
| :--- | :--- |
| **`app/core/`** | 프로젝트 전역 공통 모듈 (환경변수 설정, DB 연결, 보안/인증, 공통 예외 처리 등) |
| **`app/models/`** | DB 테이블과 1:1 매핑되는 SQLAlchemy ORM 클래스 정의 |
| **`app/repositories/`** | DB 세션을 주입받아 CRUD(SELECT, INSERT, UPDATE, DELETE) 쿼리를 수행하는 계층 |
| **`app/schemas/`** | API 요청(Request) 검증 및 응답(Response) 직렬화를 담당하는 Pydantic 모델 정의 |
| **`app/services/`** | 비즈니스 로직 처리, 데이터 가공 및 여러 Repository를 조합하는 트랜잭션 계층 |
| **`app/apis/`** | HTTP 요청 엔드포인트(Router) 정의 및 Service 호출 결과 반환 |

---

## 2. 주요 파일의 역할

* **`app/main.py`**
  * FastAPI 애플리케이션 엔트리포인트(Entry Point).
  * CORS 설정, 미들웨어, 정적 파일(static/media) 마운트 및 API 라우터(`include_router`) 등록.
  * **주의**: 와일드카드 라우터(`catch_all`)가 존재하는 경우, API 라우터는 반드시 `catch_all`보다 상단에 등록해야 404 에러를 방지할 수 있습니다.

* **`app/core/config.py`**
  * `pydantic-settings`를 활용해 `.env` 파일의 환경변수(DB 접속 정보, Secret Key 등)를 안전하게 객체로 불러와 관리.

* **`pyproject.toml`**
  * 파이썬 프로젝트 메타데이터(이름, 버전) 및 의존성 패키지(FastAPI, SQLAlchemy, Alembic 등) 목록 관리.

* **`uv.lock`**
  * 차세대 패키지 관리 도구 `uv`가 생성하는 잠금 파일. 의존성 버전을 고정하여 모든 팀원의 동일한 개발 환경을 보장.

---

## 3. 데이터베이스 연결 설정 (`app/core/db/databases.py`)

* **Engine 생성**: `config.py`의 `DATABASE_URL`을 바탕으로 `create_async_engine`을 호출하여 DB 통신 통로 생성.
* **SessionMaker**: DB 작업 단위(트랜잭션)를 생성하는 `async_sessionmaker` 팩토리 구성.
* **Base 클래스**: 모든 ORM 모델이 상속받을 `declarative_base()` 객체 선언.
* **의존성 주입 (`async_get_db`)**: API 요청마다 독립적인 DB 세션을 생성(`yield`)하고, 요청 완료 시 세션을 안전하게 종료(`close`)하는 제너레이터 함수.

---

## 4. 모델 작성 및 Alembic 마이그레이션

### ① SQLAlchemy 모델 작성
1. `app/models/` 디렉터리에 테이블별 파이썬 파일 생성.
2. `Base` 클래스를 상속받아 `__tablename__` 및 `Column` 지정.
3. **필수**: `app/models/__init__.py`에 작성한 모델을 import해야 Alembic이 구조를 감지합니다.

### ② Alembic 마이그레이션 순서

```bash
# 1. 모델 수정 사항을 감지하여 마이그레이션 스크립트 자동 생성
uv run alembic revision --autogenerate -m "설명문구"

# 2. 생성된 스크립트(alembic/versions/) 내용 검증

# 3. 작성된 마이그레이션 스크립트를 실제 DB에 반영
uv run alembic upgrade head
```

> **주의사항**: 팀원 간 마이그레이션 충돌 방지를 위해 `revision` 생성은 한 명이 수행하여 Git에 커밋하고, 다른 팀원은 `upgrade head`만 실행하는 것을 권장합니다.

---

## 5. API Request Lifecycle (구현 흐름)

새로운 API 기능을 개발할 때 아래 순서대로 작성합니다.

```text
1. models/       : DB 테이블 구조 정의 및 Alembic 마이그레이션 적용
2. schemas/      : Request/Response 데이터 구조 (Pydantic) 작성
3. repositories/ : DB CRUD 쿼리 메서드 구현
4. services/     : 비즈니스 로직 및 예외 처리 구문 작성
5. apis/         : HTTP 엔드포인트 및 라우터 작성
6. main.py       : 라우터 등록
```

### 전체 데이터 흐름 예시 (조회/생성 요청)
1. **Client**: HTTP 요청 전달 (`GET /api/v1/patients/1`)
2. **`apis/`**: Pydantic 스키마를 통해 입력값 자동 검증 후 `services/` 호출
3. **`services/`**: 비즈니스 로직(데이터 존재 여부 확인, 암호화 등) 검증 후 `repositories/` 호출
4. **`repositories/`**: SQLAlchemy를 통해 DB에서 데이터 조회/저장 수행
5. **`models/` & DB**: ORM을 거쳐 DB 데이터 반환
6. **`schemas/`**: 서비스/라우터를 거쳐 전달된 데이터를 Response DTO에 맞춰 클라이언트에 JSON 응답 반환