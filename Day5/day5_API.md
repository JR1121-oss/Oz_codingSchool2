# 5일차 환자 관리 및 진료기록 API 명세서

## 1. 환자 정보 관리 (Patient API)
| 기능 요약 | HTTP Method | Endpoint | Request Parameter / Body | Response / 제약 사항 |
| :--- | :---: | :--- | :--- | :--- |
| **환자 정보 등록** | `POST` | `/patients` | **Body (JSON):** 이름, 나이, 성별, 연락처 | 필수 입력 항목 검증. 성공 시 201 응답 및 환자 정보 반환[cite: 12]. |
| **환자 목록 조회** | `GET` | `/patients` | **Query:** `name` (이름 검색), `gender` (성별 필터링), `min_age`, `max_age` (나이 범위) | 조건에 맞는 환자 목록 반환. (조회 항목: ID, 이름, 나이, 성별, 연락처, 생성/수정 일시)[cite: 12] |
| **환자 정보 상세 조회** | `GET` | `/patients/{patient_id}` | **Path:** `patient_id` | 단일 환자의 상세 정보 반환[cite: 12]. |
| **환자 정보 수정** | `PATCH` | `/patients/{patient_id}` | **Path:** `patient_id`<br>**Body (JSON):** 이름, 연락처 | 이름과 연락처만 수정 가능[cite: 12]. |
| **환자 정보 삭제** | `DELETE` | `/patients/{patient_id}` | **Path:** `patient_id` | 환자 삭제 시 관련된 진료기록과 X-Ray 이미지도 함께 영구 삭제[cite: 12]. |

## 2. 진료 기록 관리 (Medical Record API)
| 기능 요약 | HTTP Method | Endpoint | Request Parameter / Body | Response / 제약 사항 |
| :--- | :---: | :--- | :--- | :--- |
| **진료기록 등록** | `POST` | `/patients/{patient_id}/records` | **Path:** `patient_id`<br>**Form-Data:** 차트 넘버, 진료된 증상, 흉부 X-ray 이미지 파일 | X-Ray 이미지는 로컬 저장소에 저장[cite: 12]. |
| **진료기록 목록 조회** | `GET` | `/patients/{patient_id}/records` | **Path:** `patient_id` | 특정 환자의 진료기록 목록 반환. (증상은 100자 초과 시 줄임표 처리)[cite: 12] |
| **진료기록 상세 조회** | `GET` | `/records/{record_id}` | **Path:** `record_id` | 특정 진료기록의 차트 넘버, 증상, X-Ray 이미지 경로, 생성 일시 반환[cite: 12]. |

* 공통 비기능 요구사항: 모든 API는 최대 3초 이내 처리 및 응답[cite: 12].