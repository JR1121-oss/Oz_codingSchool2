# REQ-PTNT-002 / REQ-PTNT-003 환자 조회 API 명세서

본 문서는 **진료기록 사용자 요구사항 정의서**(`REQ-PTNT-002`, `REQ-PTNT-003`) 및 시스템 공통 표준 규칙을 기반으로 작성된 **환자 목록 및 상세 조회 API 명세서**입니다.

---

## 0. 공통 사항
app/
│
├── ⚙️ [공통 모듈] 전역 인프라 및 보안/의존성 설정
│   ├── core/
│   │   ├── database.py             # DB 연결 설정 (Engine, SessionLocal, get_db)
│   │   ├── deps.py                 # 인증 및 권한 검증 의존성 (get_current_user, get_current_staff)
│   │   └── security.py             # JWT 토큰 생성/검증 및 비밀번호 암호화 유틸
│   │
│   └── models/                     # SQLAlchemy ORM 데이터베이스 모델
│       ├── enum.py                 # UserRole(STAFF/ADMIN), Gender, Department 등 공통 Enum
│       ├── user.py                 # 사용자(의료진/관리자) 테이블 모델
│       ├── patient.py              # 환자 정보 테이블 모델
│       └── medical_record.py       # 진료기록 및 X-Ray 이미지 경로 테이블 모델
│
└── 📦 [레이어별 분리] 웹 진입점 및 계층별 비즈니스 로직
    │
    ├── 🚦 routers/                 # [Auth & User Domain] 계정/인증 관리 라우터 (엔드포인트 분리)
    │   ├── auth.py                 # 로그인, 토큰 재발급, 로그아웃 API (`/api/v1/auth`)
    │   ├── admin.py                # 관리자 전용 회원 승인 및 권한 변경 API (`/api/v1/admin`)
    │   └── users.py                # 사용자 내 정보 조회 및 프로필 수정 API (`/api/v1/users`)
    │
    ├── 🌐 apis/                    # [Medical Domain] 핵심 진료/환자 비즈니스 API
    │   └── v1/
    │       ├── patient_api.py      # 환자 등록/조회/수정/삭제 API (`REQ-PTNT-001~005`)
    │       └── medical_record_api.py # 진료기록 등록 및 X-Ray 파일 처리 API (`REQ-MDR-001~005`)
    │
    ├── 🧠 services/                # [Business Logic] 순수 비즈니스 로직 및 예외 처리
    │   ├── user_service.py         # 회원가입, 비밀번호 검증, 권한 변경 로직
    │   ├── patient_service.py      # 환자 정보 검증 및 연쇄 삭제(CASCADE) 비즈니스 로직
    │   └── medical_record_service.py # X-Ray 파일 저장 유틸 호출 및 증상 100자 축약 로직
    │
    ├── 🗄️ repositories/            # [Data Access] SQLAlchemy 전용 DB CRUD 쿼리 계층
    │   ├── user_repository.py      # 유저 조회, Role 업데이트 DB 쿼리
    │   ├── patient_repository.py   # 환자 목록 검색/필터링 및 등록/삭제 쿼리
    │   └── medical_record_repository.py # 진료기록 저장 및 환자별 기록 조회 쿼리
    │
    └── 📋 schemas/                 # [DTO] Pydantic 요청/응답 데이터 유효성 검증
        ├── user.py                 # 로그인/회원가입 요청 및 유저 응답 규격
        ├── patient.py              # 환자 정보 등록/수정/조회 Pydantic 스키마
        └── medical_record.py       # 진료기록 및 파일 업로드 Form/JSON 스키마
│
└── 🚀 main.py                      # 중앙 진입점 (Static/Media 마운트, 라우터 통합, Catch-all)

### 0-1. 기본 규칙
- **Base URL**: `/api/v1`
- **데이터 응답 형식**: JSON (`application/json`)
- **인증 방식**: HTTP Bearer Token (`Authorization: Bearer <access_token>`)
- **응답 시간 목표**: 3초 이내 (`NFR-PTNT-001`)

### 0-2. 권한(Role)별 접근 범위
- `STAFF` / `ADMIN`: 조회 API 접근 허용
- `PENDING`: 접근 불가 (`403 Forbidden`)

### 0-3. 공통 에러 응답 구조
```json
{
  "detail": "에러 메시지 내용"
}
```

---

## 2. API 상세 명세

### 2-1. REQ-PTNT-002: 환자 목록 조회 API

#### 개요
- **기능**: 로그인된 사내 인원이 등록된 환자 정보 목록을 조회합니다. 이름 검색 및 성별, 나이범위 필터링 기능을 지원합니다.
- **HTTP Method**: `GET`
- **Endpoint**: `/api/v1/patients`
- **인증 필요 여부**: Y (`Bearer Token`)
- **권한**: `STAFF`, `ADMIN`

#### Request Query Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `name` | string | N | null | 이름 키워드 검색 (부분 일치) |
| `gender` | string | N | null | 성별 필터 (`M`: 남성, `F`: 여성) |
| `min_age` | integer | N | null | 최소 나이 범위 |
| `max_age` | integer | N | null | 최대 나이 범위 |

#### Response Headers
- `Content-Type: application/json`

#### Response Body (`200 OK`)
> 요구사항 명시 필드: 환자 고유 ID, 이름, 나이, 성별, 연락처, 생성일시, 수정일시

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "age": 45,
    "gender": "M",
    "phone_number": "01012345678",
    "created_at": "2026-10-27T10:00:00Z",
    "updated_at": "2026-10-27T10:00:00Z"
  },
  {
    "id": 2,
    "name": "김영희",
    "age": 32,
    "gender": "F",
    "phone_number": "01098765432",
    "created_at": "2026-10-27T11:20:00Z",
    "updated_at": "2026-10-27T11:20:00Z"
  }
]
```

#### Status Codes
- `200 OK`: 목록 조회 성공
- `401 Unauthorized`: 토큰 미제공 또는 만료
- `403 Forbidden`: 접근 권한 없음 (`PENDING` 상태)

---

### 2-2. REQ-PTNT-003: 환자 정보 상세 조회 API

#### 개요
- **기능**: 목록에서 특정 환자의 `상세보기` 요청 시 해당 환자의 상세 정보(이름, 성별, 연락처, 나이 등)를 조회합니다.
- **HTTP Method**: `GET`
- **Endpoint**: `/api/v1/patients/{patient_id}`
- **인증 필요 여부**: Y (`Bearer Token`)
- **권한**: `STAFF`, `ADMIN`

#### Path Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `patient_id` | integer | Y | 조회할 환자의 고유 ID |

#### Response Headers
- `Content-Type: application/json`

#### Response Body (`200 OK`)
> 요구사항 명시 필드: 이름, 성별, 연락처, 나이 (기본 메타 데이터 포함)

```json
{
  "id": 1,
  "name": "홍길동",
  "age": 45,
  "gender": "M",
  "phone_number": "01012345678",
  "created_at": "2026-10-27T10:00:00Z",
  "updated_at": "2026-10-27T10:00:00Z"
}
```

#### Status Codes
- `200 OK`: 상세 정보 조회 성공
- `401 Unauthorized`: 토큰 미제공 또는 만료
- `403 Forbidden`: 접근 권한 없음
- `404 Not Found`: 해당 `patient_id`를 가진 환자가 존재하지 않음

---

## 3. 담당 파트 구현 사양 가이드 (팀원 B / E 참고용)

- **Pydantic Schema**: `PatientRead` DTO 스키마 사용
- **Service Layer**: 
  - `get_patients(db, name, gender, min_age, max_age)`
  - `get_patient_by_id(db, patient_id)`
- **Repository Layer**:
  - `SQLAlchemy` Query / Filter 조건 (`ilike` 검색, `==` 조건, `>=` / `<=` 범위 조건) 적용