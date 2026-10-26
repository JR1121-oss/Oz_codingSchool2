##  5️⃣ 회원 목록 조회 API (REQ-USER-004)

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 목록 조회 API |
| 설명 | 관리자가 회원관리 메뉴에서 모든 회원을 목록으로 조회한다. 이메일 또는 이름으로 검색하고, 부서별로 필터링할 수 있다. |
| 엔드포인트(Endpoint) | `/api/v1/users` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y (ADMIN 전용) |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer `<access_token>` | 관리자 권한 확인 |

#### 본문 필드

| 파라미터명 | 타입 | 필수 (Y / N) | 설명 |
| --- | --- | --- | --- |
| - | - | - | GET 요청이므로 요청 본문을 사용하지 않음 |

#### 쿼리 파라미터 (GET 요청시)

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| search | string | N | 이메일 또는 이름에 포함된 검색어 (부분 일치) |
| department | string | N | 부서 필터 (`MEDICAL` / `DEV` / `RESEARCH`) |

예시: `GET /api/v1/users?search=홍&department=MEDICAL`

### 3. 응답(Response)

#### 성공

- 200 OK

```json
[
  {
    "id": 1,
    "email": "example@example.com",
    "name": "홍길동",
    "department": "MEDICAL",
    "gender": "M",
    "phone_number": "01012345678",
    "is_active": true,
    "role": "STAFF"
  }
]
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 고유 ID |
| email | string | 이메일 |
| name | string | 이름 |
| department | string | 부서 (`MEDICAL` / `DEV` / `RESEARCH`) |
| gender | string | 성별 (`M` / `F`) |
| phone_number | string | 휴대폰 번호 |
| is_active | boolean | 계정 활성화 여부 |
| role | string | 현재 권한 (`PENDING` / `STAFF` / `ADMIN`) |

#### 실패

- 401 Unauthorized (토큰이 없거나, 잘못되었거나, 만료됨)

```json
{
  "detail": "유효하지 않거나 만료된 토큰입니다."
}
```

- 403 Forbidden (ADMIN이 아닌 유저가 호출, 또는 비활성 계정)

```json
{
  "detail": "접근 권한이 없습니다."
}
```

- 422 Unprocessable Entity (`department`가 허용된 값이 아닌 경우 등 입력 형식 오류)

```json
{
  "detail": [
    {
      "loc": ["query", "department"],
      "msg": "Input should be 'MEDICAL', 'DEV' or 'RESEARCH'",
      "type": "enum"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string / array | 오류 메시지 (422는 입력값 검증 오류 목록) |
| detail[].loc | array | (422) 오류가 발생한 필드 위치 |
| detail[].msg | string | (422) 오류 내용 |
| detail[].type | string | (422) 오류 종류 |

### 4. 비고

- 조건에 맞는 회원이 없으면 빈 배열 `[]`과 200을 응답한다.
- `search`와 `department`를 함께 쓰면 두 조건을 모두 만족하는 회원만 조회한다. 둘 다 없으면 전체 회원을 조회한다.
- `role`은 요구사항의 목록 항목에는 없지만, 같은 화면에서 권한을 변경하므로 현재 권한을 확인할 수 있게 응답에 포함한다.
- 비밀번호 관련 값(`hashed_password`)은 절대 응답에 포함하지 않는다.

---

## 6️⃣ 회원 권한 변경 API (REQ-USER-005)

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 권한 변경 API |
| 설명 | 관리자가 회원관리 목록에서 선택한 회원의 권한을 변경한다. |
| 엔드포인트(Endpoint) | `/api/v1/users/{user_id}/role` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y (ADMIN 전용) |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | Bearer `<access_token>` | 관리자 권한 확인 |
| Content-Type | application/json | 요청 본문이 JSON 형식 |

#### Path 파라미터

| 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| user_id | integer | Y | 권한을 변경할 회원의 ID |

#### 본문 필드

| 파라미터명 | 타입 | 필수 (Y / N) | 설명 |
| --- | --- | --- | --- |
| role | string | Y | 변경할 권한 (`PENDING` 대기자 / `STAFF` 스태프 / `ADMIN` 어드민) |

```json
{
  "role": "STAFF"
}
```

#### 쿼리 파라미터 (GET 요청시)

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | N | 쿼리 파라미터를 사용하지 않음 |

### 3. 응답(Response)

#### 성공

- 200 OK

```json
{
  "id": 2,
  "role": "STAFF"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 권한이 변경된 회원의 ID |
| role | string | 변경된 권한 |

#### 실패

- 400 Bad Request (본인 계정의 권한을 변경하려는 경우)

```json
{
  "detail": "본인의 권한은 변경할 수 없습니다."
}
```

- 404 Not Found (존재하지 않는 회원 ID)

```json
{
  "detail": "존재하지 않는 회원입니다."
}
```

- 401 Unauthorized, 403 Forbidden: 5️⃣와 같은 형식

```json
{
  "detail": "유효하지 않거나 만료된 토큰입니다."
}
```

```json
{
  "detail": "접근 권한이 없습니다."
}
```

- 422 Unprocessable Entity (`role`이 허용된 값이 아니거나 누락됨)

```json
{
  "detail": [
    {
      "loc": ["body", "role"],
      "msg": "Input should be 'PENDING', 'STAFF' or 'ADMIN'",
      "type": "enum"
    }
  ]
}
```

### 4. 비고

- 요구사항의 "목록에서 선택된 회원의 권한을 변경"은 회원 1명당 API를 1번 호출하는 방식으로 처리한다. 여러 명을 선택한 경우 클라이언트가 선택한 회원 수만큼 호출한다.
- 이미 같은 권한인 회원에게 같은 `role`을 보내도 200으로 응답한다. (멱등)
- 관리자가 자신의 권한을 낮춰 시스템에 관리자가 없어지는 상황을 막기 위해 본인 계정은 변경할 수 없게 했다. (설계상 추가한 제한, 팀 합의 필요)
- 권한별 접근 범위: 대기자(마이페이지 외 모든 서비스 접근 불가), 스태프(흉부 X-ray 관련 모든 읽기, 쓰기, 수정 가능), 어드민(모든 항목에 대한 데이터 접근 가능)