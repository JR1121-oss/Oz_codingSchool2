# AI Health Web Assignment

흉부 X-Ray 이미지 기반의 폐렴 판독 모델을 활용한 **폐렴 환자 관리 백오피스**입니다.
의료진이 환자와 진료기록을 관리하고, 업로드한 X-Ray 이미지로 AI 폐렴 예측 결과를 확인할 수 있습니다.

## Project Overview

### 1. 주요 기능
- **회원 관리**: 회원가입, 로그인(JWT), 마이페이지, 관리자 권한 변경
- **환자 관리**: 환자 등록, 목록 조회(이름 검색, 성별·나이 필터), 상세 조회, 수정, 삭제
- **진료기록 관리**: X-Ray 이미지를 포함한 진료기록 등록, 목록·상세 조회
- **AI 폐렴 예측**: ResNet50 · EfficientNet-B0 · ConvNeXt-Tiny 앙상블 모델로 폐렴 여부와 Confidence 예측

### 2. 기술 스택
- **Backend**: Python 3.13+, FastAPI, SQLAlchemy (async), Pydantic
- **Database**: MySQL, Alembic
- **AI**: PyTorch, torchvision
- **Tools**: uv, Git & GitHub, Docker

### 3. 실행 방법
환경변수 파일을 만들고 값을 채운 뒤, 의존성 설치 → 마이그레이션 → 서버 실행 순서로 진행합니다.
모델 가중치(`.pth`)는 `worker/models/`에 둡니다.
```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- 웹: `http://127.0.0.1:8000`
- API 문서(Swagger): `http://127.0.0.1:8000/docs`

## Alembic Migration Guide

이 프로젝트는 데이터베이스 마이그레이션을 위해 Alembic을 사용합니다.

### 1. 마이그레이션 파일 생성 (자동 생성)
모델(`app/models/`)이 변경된 경우 다음 명령어를 실행하여 마이그레이션 파일을 생성합니다.
```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"
```

### 2. 데이터베이스에 반영
생성된 마이그레이션을 데이터베이스에 적용하려면 다음 명령어를 실행합니다.
```bash
uv run alembic upgrade head
```

### 3. 이전 상태로 되돌리기 (Rollback)
마지막 마이그레이션을 취소하려면 다음 명령어를 실행합니다.
```bash
uv run alembic downgrade -1
```