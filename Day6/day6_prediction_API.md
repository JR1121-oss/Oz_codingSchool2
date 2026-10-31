# 6일차 AI 폐렴 예측 API 설계

요구사항 정의서(REQ-PRED-001, 002 / NFR-PRED-001, 002)를 기준으로 정리한 API 명세입니다.
URL과 응답 형식은 프론트엔드(`static/apis.js`, `static/pages.js`)가 실제로 호출하는 형태에 맞췄습니다. (팀 규칙: 프론트는 수정하지 않고 백엔드를 맞춘다)

> **변경 이력 (2026-10-31)**
> - 예측 URL: `/predictions` → `/predict`
> - 목록 URL: `/predictions` → `/analyses`, 응답을 객체에서 **배열**로 변경 (`xray_image_url` 제외)
> - 권한 의존성: `get_approved_user` 사용
> - 모델 이름: `settings.AI_MODEL_NAME` → `app/ai/inference.py`의 `MODEL_VERSION`
> - `heatmap_url` nullable, `UNIQUE(record_id, ai_model)` 추가 (마이그레이션 필요)

## 1. 엔드포인트 요약

| 요구사항 ID | 기능 | Method & URL | 권한 | 성공 응답 |
| --- | --- | --- | --- | --- |
| REQ-PRED-001 | AI 폐렴 예측 (저장된 결과가 있으면 재사용) | `POST /api/v1/medical-records/{record_id}/predict` | STAFF, ADMIN | 201 새로 예측 / 200 저장된 결과 |
| REQ-PRED-002 | 예측 결과 목록 조회 | `GET /api/v1/medical-records/{record_id}/analyses` | STAFF, ADMIN | 200 |
| NFR-PRED-001 | 모델 평가 기준 (Recall, Accuracy) | API 없음. 모델 평가 스크립트로 검증 (4-1) | - | - |
| NFR-PRED-002 | 모든 API 3초 이내 응답 | 위 두 API에 모두 적용 (4-2) | - | - |

## 2. 공통 규칙

- **인증**: `Authorization: Bearer {access_token}`. 토큰이 없거나 만료되면 401.
- **권한**: "사내 의료인, 개발팀, 연구자"는 부서(MEDICAL, DEV, RESEARCH) 구분 없이 모두 허용합니다. `role`이 `STAFF` 또는 `ADMIN`인 로그인 유저만 사용할 수 있고, `PENDING`은 403입니다. 구현은 `app/core/deps.py`의 `get_approved_user`를 씁니다.
- **에러 형식**: `{"detail": "에러 메시지"}` (FastAPI 기본 형식)
- **저장 테이블**: `ai_analysis_results` (`record_id`, `is_pneumonia`, `confidence`, `heatmap_url`, `ai_model`, `created_at`)

## 3. API 상세

### 3-1. AI 폐렴 예측 (REQ-PRED-001)

`POST /api/v1/medical-records/{record_id}/predict`

| 구분 | 내용 |
| --- | --- |
| Path | `record_id`: 진료기록 ID |
| Body | 없음. 사용할 모델 이름은 `app/ai/inference.py`의 `MODEL_VERSION`으로 정하고, X-ray 이미지는 진료기록 저장 시 업로드한 이미지를 씁니다. |

**처리 흐름**

1. 로그인과 권한(STAFF, ADMIN)을 확인합니다.
2. `record_id`의 진료기록이 없으면 404.
3. 현재 모델 이름(`MODEL_VERSION`)으로 `ai_analysis_results`에서 `(record_id, ai_model)` 결과를 찾습니다.
4. **결과가 있으면** AI 추론 없이 저장된 데이터를 그대로 **200**으로 응답합니다.
5. 결과가 없으면 진료기록의 X-ray 이미지를 찾습니다. 이미지가 없으면 404.
6. 이미지 파일을 읽어 모델로 추론합니다. 폐렴 여부와 confidence를 구하고, 히트맵 이미지를 만들어 `media/heatmaps/` 아래에 저장합니다.
7. 결과를 `ai_analysis_results`에 저장하고 **201**로 응답합니다.

**Response 200 / 201**

```json
{
  "id": 12,
  "record_id": 3,
  "is_pneumonia": true,
  "confidence": 97.35,
  "heatmap_url": "/media/heatmaps/3f2a9c1e.png",
  "ai_model": "pneumonia-ensemble-v1",
  "created_at": "2026-11-02T10:15:30"
}
```

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | int | 예측 결과 고유 ID |
| `record_id` | int | 진료기록 ID |
| `is_pneumonia` | bool | 폐렴 여부 (True, False) |
| `confidence` | number | 예측 확신도 (0~100, 소수 둘째 자리) |
| `heatmap_url` | string \| null | 병변 표시 이미지 URL (선택사항, 생성하지 못하면 `null`) |
| `ai_model` | string | 예측에 사용한 모델 |
| `created_at` | datetime | 예측 수행 일시 |

**에러**

| 상태 코드 | 상황 | detail |
| --- | --- | --- |
| 401 | 토큰 없음, 위조, 만료 | 유효하지 않거나 만료된 토큰입니다. |
| 401 | 존재하지 않거나 비활성 계정 | 유효하지 않은 사용자입니다. |
| 403 | PENDING 계정 | 승인 대기 중인 사용자입니다. 관리자의 승인 이후에 사용 가능합니다. |
| 404 | 진료기록 없음 | 진료기록을 찾을 수 없습니다. |
| 404 | 진료기록에 X-ray 이미지 없음 | 예측에 사용할 X-ray 이미지가 없습니다. |
| 500 | 이미지 파일이 없거나 손상되어 읽을 수 없음 | X-ray 이미지 파일을 불러올 수 없습니다. |
| 500 | 모델 로딩 또는 추론 실패 | AI 예측 중 오류가 발생했습니다. |
| 500 | 결과 저장 실패 | 예측 결과를 저장하지 못했습니다. |

### 3-2. AI 예측 결과 목록 조회 (REQ-PRED-002)

`GET /api/v1/medical-records/{record_id}/analyses`

| 구분 | 내용 |
| --- | --- |
| Path | `record_id`: 진료기록 ID |
| Query | 없음. 한 진료기록의 결과는 모델 수만큼이라 적어서 페이지네이션은 두지 않습니다. |
| 정렬 | 예측 수행 일시(`created_at`) 최신순 |

**Response 200** (배열)

```json
[
  {
    "id": 12,
    "is_pneumonia": true,
    "confidence": 97.35,
    "heatmap_url": "/media/heatmaps/3f2a9c1e.png",
    "created_at": "2026-11-02T10:15:30",
    "ai_model": "pneumonia-ensemble-v1"
  }
]
```

- 예측을 한 번도 하지 않았으면 빈 배열 `[]`이고, 상태 코드는 200입니다.
- 프론트(`pages.js`의 `renderRecordDetail`)가 `analyses.length`, `analyses.map()`으로 쓰기 때문에 객체로 감싸지 않고 배열을 바로 돌려줍니다.
- "해당 환자의 흉부 X-Ray 사진과 예측 결과를 함께 확인"하는 요구사항은, 화면이 X-ray 사진을 진료기록 상세 조회(`GET /api/v1/medical-records/{record_id}`)에서 받고 예측 결과를 이 API에서 받아 한 화면에 함께 보여주는 방식으로 충족합니다.
- 목록 항목의 필드는 요구사항 그대로입니다 (고유 ID, 폐렴 여부, Confidence, Heatmap Image URL, 예측 수행 일시, 사용한 모델).

**에러**: 401, 403은 3-1과 같고, 진료기록이 없으면 404 (진료기록을 찾을 수 없습니다.)

## 4. 비기능 요구사항 처리

### 4-1. 모델 평가 기준 (NFR-PRED-001)

API가 아니라 **모델을 배포하기 전에 통과해야 하는 검증 기준**입니다.

| 지표 | 계산식 | 기준 |
| --- | --- | --- |
| Recall (민감도) | TP / (TP + FN) | 최소 0.90 (목표 0.95) |
| Accuracy (보조) | (TP + TN) / 전체 표본 수 | 0.80 이상 (목표 0.90) |

- FN(폐렴 환자를 정상으로 오진)이 가장 위험하므로 **Recall을 우선**합니다. 판정 임계값은 검증 데이터에서 Recall ≥ 0.90이 되도록 정하고, 학습에 쓰지 않은 테스트 데이터로 최종 확인합니다.
- `scripts/evaluate_model.py`가 서비스와 같은 전처리(`inference.eval_transform`)로 TP, FP, FN, TN과 Recall, Accuracy를 출력합니다. `--threshold` 옵션으로 임계값을 바꿔 가며 확인할 수 있습니다. 결과는 문서(모델 카드)에 남깁니다.
  ```bash
  uv run python -m scripts.evaluate_model --data_dir /path/to/test --threshold 0.3
  ```
- 기준을 통과한 모델만 배포합니다. 가중치, 임계값, 전처리를 바꾸면 `MODEL_VERSION`을 올려서, 이전 모델의 저장 결과가 재사용되지 않고 새로 예측되게 합니다.

### 4-2. API 성능 (NFR-PRED-002)

- 모델은 요청마다 읽지 않고 **한 번만 로드해 재사용**합니다. `main.py`의 lifespan에서 서버 시작 시 미리 읽어 둡니다. (모델 파일이 없으면 경고만 남기고 다른 API는 정상 동작)
- 추론은 CPU 연산이라 `asyncio.to_thread(...)`로 별도 스레드에서 실행합니다. 그렇지 않으면 추론하는 동안 서버의 다른 요청이 모두 멈춥니다.
- 저장된 결과가 있으면 DB 조회만 하므로 빠릅니다. 3초를 넘길 수 있는 건 처음 예측하는 경우뿐이고, 이때 목표는 추론 + 히트맵 생성 2초 이내입니다. (2초를 넘으면 경고 로그)
- 히트맵이 시간을 많이 쓰면 `inference.ENABLE_HEATMAP = False`로 끄고 `heatmap_url`을 `null`로 응답합니다. (선택사항이라 허용)

## 5. 팀 결정 사항

| 번호 | 내용 | 결정 |
| --- | --- | --- |
| 1 | URL 구조 | ✅ 프론트 호출 경로에 맞춤: `POST .../{record_id}/predict`, `GET .../{record_id}/analyses`. `main.py`에 `prefix="/api/v1/medical-records"`로 등록 |
| 2 | `confidence`의 의미와 단위 | 0~100(%). 판정한 쪽의 확신도 (`inference.CONFIDENCE_MODE = "predicted"`). 항상 폐렴 확률로 보여줄지는 추가 논의 |
| 3 | 히트맵이 선택사항인데 `heatmap_url`이 `nullable=False` | ✅ `nullable=True`로 변경. 모델 파일 수정 완료, **Alembic 마이그레이션 필요** |
| 4 | 한 진료기록에 X-ray 이미지가 여러 장일 때 | ✅ 가장 최근 이미지 1장으로 예측 |
| 5 | 버튼을 동시에 두 번 눌러 중복 저장되는 경우 | ✅ `UNIQUE(record_id, ai_model)` 추가 (마이그레이션에 포함). 중복 에러가 나면 기존 결과를 반환 |
| 6 | 모델 이름 관리 | ✅ `app/ai/inference.py`의 `MODEL_VERSION` 하나로 관리 (50자 이내) |
| 7 | 목록 응답에 `xray_image_url` 포함 | ✅ 포함하지 않음. 프론트가 진료기록 상세 조회에서 사진을 받음 |

## 6. 구현 구조와 파트 분담

```
app/
  apis/v1/prediction_apis.py       POST /predict, GET /analyses 라우터 (router = APIRouter())
  schemas/prediction.py            응답 스키마 (PredictionResponse, PredictionItem)
  services/prediction_service.py   저장된 결과 확인 → 이미지 조회 → 추론 → 저장 흐름
  ai/inference.py                  모델 로딩, 전처리, 추론
  ai/heatmap.py                    Grad-CAM 히트맵 생성
  ai/models/*.pth                  모델 가중치 (git 제외)
scripts/evaluate_model.py          NFR-PRED-001 평가 스크립트
tests/                             권한, 재사용, 404 케이스
```

| 파트 | 요구사항 | 맡는 일 |
| --- | --- | --- |
| A | REQ-PRED-001 | POST 라우터, 서비스 흐름(저장된 결과 확인, 이미지 조회, 저장), 에러 처리 |
| B | REQ-PRED-002 | GET 라우터, 응답 스키마, 목록 조회 쿼리, 테스트 |
| C | REQ-PRED-001 (AI 부분) | 모델 로딩, 전처리, 추론 함수, 히트맵 생성과 저장 |
| D | NFR-PRED-001, 002 | 평가 스크립트, 임계값 결정, 마이그레이션(결정 3, 5), 성능 점검 |