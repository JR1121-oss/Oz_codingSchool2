# AI Health Web Assignment

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
# 흉부 X-ray AI 분석 웹 서비스 프로젝트 (Chest X-Ray AI Service)

본 문서는 팀 프로젝트 진행 과정과 세부 수행 작업 내역을 정리한 최종 보고서입니다.

---------------------------------------------------------------------------

## 📌 프로젝트 진행 단계별 정리

### -이재경- 

### 1. Team Rule 정의
- Git 커밋 컨벤션, 브랜치 네이밍 규칙, 일일 스크럼 및 코드 리뷰 원칙 수립
- 담당 도메인별 R&R(역할 및 책임) 분배

### 2. 사용자 요구사항 정의
- 병원 의료진 및 관리자를 위한 핵심 기능 도출
- 회원 인증, 환자 관리, X-ray 이미지 업로드 및 AI 판독 결과 조회, 진료기록 관리 요구사항 분석

### 3. API 명세서 작성
- RESTful 원칙에 기반한 엔드포인트 URI 및 HTTP 메서드 설계
- Swagger(OpenAPI) 스키마를 고려한 Request/Response DTO 규격 정의

### 4. Git & Github Branch 전략 구성
- Git-Flow 변형 전략 적용 (`main` <- `integration-test` <- 개인 작업 브랜치)
- Pull Request(PR) 기반의 코드 병합 및 충돌 방지 절차 수립

### 5. 프로젝트 세팅
- FastAPI 기반 비동기 웹 프레임워크 환경 구축
- SQLAlchemy 비동기 ORM(`asyncmy`) 및 Pydantic 설정


---

## 🛠️ 개발 참고: Alembic 마이그레이션 가이드

### 1. 마이그레이션 파일 생성 (자동 생성)
```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"