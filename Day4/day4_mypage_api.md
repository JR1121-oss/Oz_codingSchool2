## Part D: Mypage API (`/api/v1/users/me`)

> **공통 안내 (Common Note)**: 마이페이지의 모든 API는 로그인이 필요합니다. 따라서 요청 헤더에 `Authorization: Bearer {access_token}`이 반드시 포함되어야 합니다.

---

### 요약 표 (Summary Table)

| 번호 (No.) | 기능 (Feature) | HTTP 메서드 | 엔드포인트 (Endpoint) | 설명 (Description) |
| :--- | :--- | :---: | :--- | :--- |
| 1 | 내 정보 조회 | `GET` | `/api/v1/users/me` | 사용자 프로필 정보 조회 (`REQ-USER-006`) |
| 2 | 내 정보 수정 | `PATCH` | `/api/v1/users/me` | 부서 및 전화번호 Partial 수정 (`REQ-USER-007`) |
| 3 | 비밀번호 변경 | `PATCH` | `/api/v1/users/me/password` | 기존 비밀번호 확인 후 새 비밀번호로 변경 (`REQ-USER-008`) |
| 4 | 회원 탈퇴 | `DELETE` | `/api/v1/users/me` | Database에서 관련 정보 즉시 삭제 (`REQ-USER-009`) |

---

### 1. 내 정보 조회 (Get My Profile - `REQ-USER-006`)
* **HTTP Method**: `GET`
* **Endpoint**: `/api/v1/users/me`
* **설명**: 현재 로그인된 사용자의 상세 프로필 정보를 조회합니다.
* **접근 권한 (Access Role)**: 인증된 모든 유저 (Pending, Staff, Admin)
* **Request Body**: 없음 (None)
* **Response (200 OK)**:
```json
{
  "email": "user@example.com",
  "name": "Hong Gildong",
  "department": "Medical",
  "gender": "M",
  "phone_number": "010-1234-5678",
  "role": "Staff"
}
```

---

### 2. 내 정보 수정 (Update My Profile - `REQ-USER-007`)
* **HTTP Method**: `PATCH`
* **Endpoint**: `/api/v1/users/me`
* **설명**: 현재 로그인된 사용자의 정보 중 부서(Department)와 전화번호(Phone Number)를 부분 수정합니다.
* **접근 권한 (Access Role)**: 인증된 유저
* **Request Body (JSON)**:
```json
{
  "department": "Research",
  "phone_number": "010-9876-5432"
}
```
* **Response (200 OK)**:
```json
{
  "message": "Profile updated successfully.",
  "data": {
    "email": "user@example.com",
    "name": "Hong Gildong",
    "department": "Research",
    "gender": "M",
    "phone_number": "010-9876-5432",
    "role": "Staff"
  }
}
```

---

### 3. 비밀번호 변경 (Change Password - `REQ-USER-008`)
* **HTTP Method**: `PATCH`
* **Endpoint**: `/api/v1/users/me/password`
* **설명**: 현재 비밀번호를 검증하고 일치할 경우 새로운 비밀번호로 변경합니다.
* **접근 권한 (Access Role)**: 인증된 유저
* **Request Body (JSON)**:
```json
{
  "current_password": "old_password123!",
  "new_password": "new_password456!"
}
```
* **Response**:
  * **200 OK (성공 시)**:
```json
{
  "message": "Password changed successfully."
}
```
  * **400 Bad Request (현재 비밀번호 불일치 시)**:
```json
{
  "detail": "Current password does not match."
}
```

---

### 4. 회원 탈퇴 (Delete Account - `REQ-USER-009`)
* **HTTP Method**: `DELETE`
* **Endpoint**: `/api/v1/users/me`
* **설명**: 회원탈퇴 시 Database에서 회원과 관련된 정보는 모두 즉시 삭제합니다.
* **접근 권한 (Access Role)**: 인증된 유저
* **Request Body**: 없음 (None)
* **Response (200 OK)**:
```json
{
  "message": "Account successfully deleted."
}
```