# 4일차: User API 설계

📋 흉부 X-Ray AI 진단 서비스의 사용자(User) 관련 API 명세서다. [4일차 - User 사용자 요구사항 정의서]를 기준으로 작성했다.

---

## 0️⃣️ 공통 사항

### 0-1. 기본 규칙

| 항목 | 내용 |
| --- | --- |
| 공통 prefix | `/api/v1/users` |
| 데이터 형식 | JSON (UTF-8) |
| 인증 방식 | `Authorization: Bearer <access_token>` 헤더 |
| 응답 시간 | **모든 API는 3초 이내 응답 (NFR-USER-003)** |

### 0-2. API 목록

| No | 요구사항 ID | API 이름 | 메서드 | 엔드포인트 | 인증 | 필요 권한 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | REQ-USER-001 | 회원가입 | POST | `/api/v1/users/signup` | N | - |
| 2 | REQ-USER-002 | 로그인 | POST | `/api/v1/users/login` | N | - |
| 3 | NFR-USER-001 | 액세스 토큰 재발급 | POST | `/api/v1/users/refresh` | 리프레시 쿠키 | - |
| 4 | REQ-USER-003 | 로그아웃 | POST | `/api/v1/users/logout` | Y | 로그인 유저 |
| 5 | REQ-USER-004 | 회원 목록 조회 | GET | `/api/v1/users` | Y | ADMIN |
| 6 | REQ-USER-005 | 회원 권한 변경 | PATCH | `/api/v1/users/roles` | Y | ADMIN |
| 7 | REQ-USER-006 | 마이페이지 조회 | GET | `/api/v1/users/me` | Y | 로그인 유저 |
| 8 | REQ-USER-007 | 회원 정보 수정 | PATCH | `/api/v1/users/me` | Y | 로그인 유저 |
| 9 | REQ-USER-008 | 비밀번호 변경 | PATCH | `/api/v1/users/me/password` | Y | 로그인 유저 |
| 10 | REQ-USER-009 | 회원 탈퇴 | DELETE | `/api/v1/users/me` | Y | 로그인 유저 |

> 비기능 요구사항 NFR-USER-002(비밀번호 입력 마스킹, 보기 아이콘)는 화면(프론트엔드)에서 처리하므로 별도 API를 만들지 않는다. 서버에서는 비밀번호를 해시로만 저장하고 응답에 절대 포함하지 않는 것으로 대응한다.

### 0-3. 인증 / 인가 (NFR-USER-001)

| 구분 | 내용 |
| --- | --- |
| 방식 | JWT (JSON Web Token) |
| 액세스 토큰 | 유효기간 **30분**. 로그인 응답 본문으로 전달하고, 이후 API 호출 시 `Authorization` 헤더에 담는다. |
| 리프레시 토큰 | 유효기간 **7일**. `HttpOnly` 쿠키로 전달해 클라이언트 JavaScript가 읽을 수 없게 한다. |
| 페이로드 | 최소 식별 정보인 `user_id`만 저장한다. (이메일, 권한 등은 넣지 않고 필요할 때 DB에서 조회) |
| 재발급 | 액세스 토큰이 만료되면 리프레시 토큰으로 재발급한다. 리프레시 토큰도 만료되면 다시 로그인한다. |
| 비밀번호 저장 | argon2 해시로 저장 (`hashed_password`) |


**< 권한(role)별 접근 범위 >**

| role | 값 | 설명 |
| --- | --- | --- |
| 대기자 | `PENDING` | 마이페이지 외 모든 서비스 접근 불가. 회원가입 직후 기본값 |
| 스태프 | `STAFF` | 내부 직원. 흉부 X-ray 관련 모든 읽기, 쓰기, 수정 가능 |
| 어드민 | `ADMIN` | 시스템 관리자. 모든 항목에 대한 데이터 접근 가능 |

- 이 문서의 User API는 `PENDING` 유저도 로그인, 마이페이지 조회/수정, 비밀번호 변경, 탈퇴를 할 수 있다. (마이페이지 접근 허용)
- 회원 목록 조회와 권한 변경은 `ADMIN`만 가능하다.
- 비활성화된 계정(`is_active = false`)은 로그인과 토큰 재발급, 인증이 필요한 모든 API 호출이 거부된다.

### 0-4. Enum 값

| 이름 | 값 | 의미 |
| --- | --- | --- |
| gender | `M`, `F` | 남, 여 |
| department | `MEDICAL`, `DEV`, `RESEARCH` | 의료, 개발, 연구 |
| role | `PENDING`, `STAFF`, `ADMIN` | 대기자, 스태프, 어드민 |

### 0-5. 입력값 검증 규칙

| 필드 | 규칙 |
| --- | --- |
| email | 이메일 형식, 최대 255자, 중복 불가 |
| password | 8~64자, 영문, 숫자, 특수문자를 각각 1개 이상 포함 |
| name | 2~20자 |
| phone_number | 하이픈 없이 숫자 11자리 (예: `01012345678`), 중복 불가 |
| department | `MEDICAL`, `DEV`, `RESEARCH` 중 하나 |
| gender | `M`, `F` 중 하나 |

### 0-6. 공통 에러 응답

인증이 필요한 모든 API에 아래 오류가 공통으로 적용된다. 각 API 명세에서는 중복해서 적지 않고 "공통 오류"로 표시한다.

- 401 Unauthorized (토큰이 없거나, 잘못되었거나, 만료됨)

```json
{
  "detail": "유효하지 않거나 만료된 토큰입니다."
}
```

- 403 Forbidden (비활성 계정 또는 권한 부족)

```json
{
  "detail": "비활성화된 사용자입니다."
}
```

```json
{
  "detail": "접근 권한이 없습니다."
}
```

- 422 Unprocessable Entity (필수 값 누락 또는 입력 형식 오류, FastAPI 기본 형식)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | array | 입력값 검증 오류 목록 |
| detail[].loc | array | 오류가 발생한 필드 위치 |
| detail[].msg | string | 오류 내용 |
| detail[].type | string | 오류 종류 |

<br>


## 1️⃣ REQ-USER-001. 회원가입 API

### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| API 이름 | 회원가입 API |
| 설명 | 사내 의료인, 개발 실무진 및 연구진이 회원가입을 통해 서비스를 이용할 수 있도록 계정을 생성한다. |
| 엔드포인트(Endpoint) | `/api/v1/users/signup` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 2. 요청(Request)

#### < Headers >

| Key | Value | 설명 |
| :--- | :--- | :--- |
| Content-Type | `application/json` | JSON 형식으로 회원가입 정보 전달 |

#### < 본문 필드 >

| 파라미터명 | 타입 | 필수 (Y / N) | 설명 |
| :--- | :--- | :--- | :--- |
| email | string | Y | 가입할 이메일 주소 |
| password | string | Y | 가입할 비밀번호 |
| name | string | Y | 사용자 이름 |
| department | string | Y | 부서 (`RESEARCH`, `MEDICAL`, `DEV`) |
| gender | string | Y | 성별 (`M`, `F`) |
| phone | string | Y | 휴대폰 번호 |

#### < 요청 본문 예시 (JSON) >

```json
{
  "email": "user@company.com",
  "password": "SecurePass123!",
  "name": "홍길동",
  "department": "MEDICAL",
  "gender": "M",
  "phone": "01012345678"
}
```

#### < 쿼리 파라미터 (GET 요청 시) >

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| :--- | :--- | :--- | :--- |
| 없음 | - | N | 회원가입 API는 요청 본문을 사용하며 쿼리 파라미터를 사용하지 않는다. |

### 3. 응답(Response)

#### < 성공 >

- **201 Created** — 회원가입 성공

```json
{
  "message": "회원가입이 완료되었습니다.",
  "user": {
    "id": 1,
    "email": "user@company.com",
    "name": "홍길동",
    "department": "MEDICAL",
    "gender": "M",
    "phone": "01012345678",
    "role": "PENDING"
  }
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| message | string | 회원가입 처리 결과 메시지 |
| user | object | 생성된 회원 정보 |
| user.id | integer | 사용자 고유 ID |
| user.email | string | 사용자 이메일 |
| user.name | string | 사용자 이름 |
| user.department | string | 사용자 부서 |
| user.gender | string | 사용자 성별 |
| user.phone | string | 사용자 휴대폰 번호 |
| user.role | string | 사용자 권한 (`PENDING`, `STAFF`, `ADMIN`) |

※ 회원가입 직후의 기본 권한은 `PENDING`으로 가정했다. 팀의 권한 정책에 따라 확정해야 한다. 비밀번호는 응답에 포함하지 않는다.

#### < 실패 >

- **409 Conflict** — 이미 가입된 이메일

```json
{
  "detail": "이미 가입된 이메일입니다."
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| detail | string | 이메일 중복 오류 메시지 |

- **422 Unprocessable Entity** — 필수 값 누락 또는 입력 형식 오류

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| detail | array | 입력값 검증 오류 목록 |
| detail[].loc | array | 오류가 발생한 위치 |
| detail[].msg | string | 오류 내용 |
| detail[].type | string | 오류 유형 |

※ 위 `422` 응답은 FastAPI의 기본 요청 검증 응답 형식을 예시로 사용했다.

### 4. 비고

- 회원가입은 로그인 전에도 이용할 수 있으므로 인증이 필요하지 않다.
- 이메일 중복 여부를 확인한 후 계정을 생성한다.
- 비밀번호는 안전한 해시 알고리즘으로 암호화하여 저장하며 평문으로 저장하지 않는다.
- 부서는 `RESEARCH`, `MEDICAL`, `DEV` 중 하나만 허용한다.
- 성별은 `M`, `F` 중 하나만 허용한다.
- 비밀번호 입력란의 마스킹 및 보기 아이콘은 프론트엔드에서 처리한다.
- API는 3초 이내에 처리하고 응답하도록 한다.

## 2️⃣ REQ-USER-002. 로그인 API

### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| API 이름 | 로그인 API |
| 설명 | 회원가입을 완료한 사용자가 이메일과 비밀번호를 입력하여 로그인하고, 인증에 필요한 JWT 토큰을 발급받는다. |
| 엔드포인트(Endpoint) | `/api/v1/users/login` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 2. 요청(Request)

#### < Headers >

| Key | Value | 설명 |
| :--- | :--- | :--- |
| Content-Type | `application/json` | JSON 형식으로 로그인 정보 전달 |

#### < 본문 필드 >

| 파라미터명 | 타입 | 필수 (Y / N) | 설명 |
| :--- | :--- | :--- | :--- |
| email | string | Y | 가입 시 등록한 이메일 |
| password | string | Y | 가입 시 등록한 비밀번호 |

#### < 요청 본문 예시 (JSON) >

```json
{
  "email": "user@company.com",
  "password": "SecurePass123!"
}
```

#### < 쿼리 파라미터 (GET 요청 시) >

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| :--- | :--- | :--- | :--- |
| 없음 | - | N | 로그인 API는 요청 본문을 사용하며 쿼리 파라미터를 사용하지 않는다. |

### 3. 응답(Response)

#### < 성공 >

- **200 OK** — 로그인 성공

```json
{
  "access_token": "JWT_ACCESS_TOKEN",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@company.com",
    "name": "홍길동",
    "role": "STAFF"
  }
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| access_token | string | 30분 동안 유효한 JWT 액세스 토큰 |
| token_type | string | 토큰 인증 방식 (`bearer`) |
| expires_in | integer | 액세스 토큰 만료 시간(초), 1800초 |
| user | object | 로그인한 사용자 정보 |
| user.id | integer | 사용자 고유 ID |
| user.email | string | 사용자 이메일 |
| user.name | string | 사용자 이름 |
| user.role | string | 사용자 권한 (`PENDING`, `STAFF`, `ADMIN`) |

#### < 응답 Headers >

| Key | 예시 값 | 설명 |
| :--- | :--- | :--- |
| Set-Cookie | `refresh_token=JWT_REFRESH_TOKEN; HttpOnly; Secure; SameSite=Lax; Max-Age=604800` | 유효기간 7일의 JWT 리프레시 토큰을 HttpOnly 쿠키로 전달 |

※ `Secure`는 HTTPS 연결에서 쿠키를 전송하도록 제한한다. `SameSite` 설정은 실제 프론트엔드와 백엔드의 배포 구조에 맞춰 확정한다.

#### < 실패 >

- **401 Unauthorized** — 이메일 또는 비밀번호 불일치

```json
{
  "detail": "이메일 또는 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| detail | string | 로그인 인증 실패 메시지 |

- **403 Forbidden** — 비활성화된 계정

```json
{
  "detail": "비활성화된 사용자입니다."
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| detail | string | 계정 비활성화로 인한 로그인 거부 메시지 |

- **422 Unprocessable Entity** — 필수 값 누락 또는 입력 형식 오류

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| detail | array | 입력값 검증 오류 목록 |
| detail[].loc | array | 오류가 발생한 위치 |
| detail[].msg | string | 오류 내용 |
| detail[].type | string | 오류 유형 |

※ "422" 응답은 FastAPI의 기본 요청 검증 응답 형식을 예시로 사용했다.

### 4. 비고

- 로그인은 인증 전 단계에서 호출하므로 인증이 필요하지 않다.
- 이메일과 비밀번호가 일치하는지 검증한 후 토큰을 발급한다.
- 액세스 토큰의 유효기간은 30분(1800초)이다.
- 리프레시 토큰의 유효기간은 7일(604800초)이다.
- 리프레시 토큰은 `HttpOnly` 쿠키로 전달하여 JavaScript에서 직접 접근할 수 없도록 한다.
- JWT 페이로드에는 최소 식별 정보인 `user_id`만 저장한다.
- 액세스 토큰 만료 시 리프레시 토큰으로 액세스 토큰을 재발급할 수 있다.
- 리프레시 토큰도 만료되면 재로그인이 필요하다.
- 비활성화된 계정은 로그인할 수 없다.
- 비밀번호 입력란의 마스킹 및 보기 아이콘은 프론트엔드에서 처리한다.
- API는 3초 이내에 처리하고 응답하도록 한다.