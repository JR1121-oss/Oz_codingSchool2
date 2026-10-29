# 5일차 환자관리 및 진료기록 API 설계서

## REQ-MDR-003: 진료기록 상세 조회 API

- **기능 요약**: 진료기록 상세 조회
- **HTTP Method**: `GET`
- **엔드포인트 (Endpoint)**: `/api/v1/records/{record_id}`
- **설명**: 환자 상세 정보 페이지 또는 진료기록 목록에서 선택한 진료기록의 고유 ID를 기반으로 상세 내용(차트 번호, 증상, X-Ray 사진 경로, 작성일시)을 조회합니다.
- **접근 권한 (Access Role)**: 사내 개발진, 의료 실무진, 연구진 (인증 필수)

---

### 1. 요청 파라미터 (Request Parameters)

#### Path Parameter
| 파라미터명 | 타입 | 필수 여부 | 설명 | 예시 |
| :--- | :---: | :---: | :--- | :--- |
| `record_id` | `integer` | 필수 (Required) | 조회할 진료기록 고유 식별 번호 | `1` |

---

### 2. 응답 명세 (Response)

#### 200 OK (조회 성공)
```json
{
  "id": 1,
  "chart_number": "CHT-2026-0001",
  "patient_id": 1,
  "symptoms": "지속적인 기침 및 미열, 호흡 곤란 증세 호소",
  "xray_image_url": "/media/xrays/sample_xray_01.png",
  "created_at": "2026-10-28T09:00:00"
}
```
#### 404 Not Found (진료기록 미존재)
```
{
  "detail": "진료 기록을 찾을 수 없습니다."
}
```
#### 422 Unprocessable Entity (파라미터 타입 불일치)
```
{
  "detail": [
    {
      "loc": ["path", "record_id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```
### 3. 구현 코드 참고 (record_detail_apis.py)

```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

records_db = [
    {
        "id": 1,
        "chart_number": "CHT-2026-0001",
        "patient_id": 1,
        "symptoms": "지속적인 기침 및 미열, 호흡 곤란 증세 호소",
        "xray_image_url": "/media/xrays/sample_xray_01.png",
        "created_at": "2026-10-28T09:00:00"
    },
    {
        "id": 2,
        "chart_number": "CHT-2026-0002",
        "patient_id": 2,
        "symptoms": "정기 건강검진 흉부 촬영 진행, 특이 소견 없음",
        "xray_image_url": "/media/xrays/sample_xray_02.png",
        "created_at": "2026-10-28T11:15:00"
    },
    {
        "id": 3,
        "chart_number": "CHT-2026-0003",
        "patient_id": 3,
        "symptoms": "흉통 및 답답함 호소, 정밀 흉부 판독 요망",
        "xray_image_url": "/media/xrays/sample_xray_03.png",
        "created_at": "2026-10-28T14:30:00"
    }
]

@router.get("/records/{record_id}", summary="진료기록 상세 조회")
async def get_record(record_id: int):
    for record in records_db:
        if record["id"] == record_id:
            return record
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="진료 기록을 찾을 수 없습니다."
    )
    ```
    