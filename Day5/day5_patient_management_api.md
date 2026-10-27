# REQ-PTNT-002 / REQ-PTNT-003 환자 조회 API 명세서

본 문서는 **진료기록 사용자 요구사항 정의서**(`REQ-PTNT-002`, `REQ-PTNT-003`) 및 시스템 공통 표준 규칙을 기반으로 작성된 **환자 목록 및 상세 조회 API 명세서**입니다.

---

## 1. 공통 사항

### 1-1. 기본 규칙
- **Base URL**: `/api/v1`
- **데이터 응답 형식**: JSON (`application/json`)
- **인증 방식**: HTTP Bearer Token (`Authorization: Bearer <access_token>`)
- **응답 시간 목표**: 3초 이내 (`NFR-PTNT-001`)

### 1-2. 권한(Role)별 접근 범위
- `STAFF` / `ADMIN`: 조회 API 접근 허용
- `PENDING`: 접근 불가 (`403 Forbidden`)

### 1-3. 공통 에러 응답 구조
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