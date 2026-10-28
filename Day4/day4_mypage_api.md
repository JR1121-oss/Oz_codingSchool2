## Part D: Mypage API (`/api/v1/users/me`)

> **File Location**: `app/apis/v1/practice_apis_jk.py`  
> **Common Note**: All Mypage APIs require authentication. Therefore, the `Authorization: Bearer {access_token}` header must be included in the request.

---

### Summary Table

| No. | Feature | HTTP Method | Endpoint | Description |
| :--- | :--- | :---: | :--- | :--- |
| 1 | Get My Profile | `GET` | `/api/v1/users/me` | Retrieves user profile (`REQ-USER-006`) |
| 2 | Update My Profile | `PATCH` | `/api/v1/users/me` | Updates department & phone (`REQ-USER-007`) |
| 3 | Change Password | `PATCH` | `/api/v1/users/me/password` | Changes password (`REQ-USER-008`) |
| 4 | Delete Account | `DELETE` | `/api/v1/users/me` | Withdraws account (`REQ-USER-009`) |

---

### 1. Get My Profile (`REQ-USER-006`)
- **HTTP Method**: `GET`
- **Endpoint**: `/api/v1/users/me`
- **Description**: Retrieves the detailed profile information of the currently authenticated user.
- **Access Role**: Authenticated User (Pending, Staff, Admin)
- **Request Body**: None
- **Response (200 OK)**:
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
### 2. Update My Profile (REQ-USER-007)
HTTP Method: PATCH

Endpoint: /api/v1/users/me

Description: Partially updates the profile information of the currently authenticated user (Department and Phone Number only).

Access Role: Authenticated User

Request Body (JSON):
{
  "department": "Research",
  "phone_number": "010-9876-5432"
}
Response (200 OK):
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
### 3. Change Password (REQ-USER-008)
HTTP Method: PATCH

Endpoint: /api/v1/users/me/password

Description: Validates the current password and updates it to a new password.

Access Role: Authenticated User

Request Body (JSON):
{
  "current_password": "old_password123!",
  "new_password": "new_password456!"
}
Response:

200 OK:
{
  "message": "Password changed successfully."
}
400 Bad Request (When current password does not match):
{
  "detail": "Current password does not match."
}
### 4. Delete Account / Withdraw (REQ-USER-009)
HTTP Method: DELETE

Endpoint: /api/v1/users/me

Description: Deletes the user account and permanently removes all related user information from the database.

Access Role: Authenticated User

Request Body: None

Response (200 OK):
{
  "message": "Account successfully deleted."
}