# 📁 프로젝트 디렉토리 구조 (Directory Structure)

```text
app/
│
├── ⚙️ [공통 모듈] 팀원이 함께 공유하여 작성/사용
│   ├── core/
│   │   ├── database.py       # DB 연결 (get_db)
│   │   ├── deps.py           # 토큰 검증 및 유저 인증 의존성 (get_current_user)
│   │   └── security.py       # JWT 토큰 생성/디코딩 & 비밀번호 해싱 (A, B 파트 공통)
│   └── models/
│       ├── enum.py           # Department, Gender, Role 등 Enum 정의
│       └── user.py           # User 테이블 SQLAlchemy 모델
│
└── 📦 [레이어별 분리] 기능 단위로 파일 추가
    ├── apis/
    │   ├── user_auth_apis.py # [A&B] 회원가입, 로그인, 토큰재발급, 로그아웃 API
    │   ├── user_admin_apis.py# [C] 회원 목록 조회, 권한 변경 API
    │   └── user_me_apis.py   # [D] 마이페이지 API
    │
    ├── services/
    │   ├── user_auth_service.py    # [A&B] 인증 비즈니스 로직
    │   ├── user_admin_service.py   # [C] 관리자 비즈니스 로직
    │   └── user_me_service.py      # [D] 마이페이지 비즈니스 로직
    │
    ├── repositories/
    │   ├── user_auth_repository.py # [A&B] 인증 관련 DB 쿼리
    │   ├── user_admin_repository.py# [C] 관리자 관련 DB 쿼리
    │   └── user_me_repository.py   # [D] 마이페이지 관련 DB 쿼리
    │
    └── schemas/
        └── user.py           # [A, B, C, D] 요청/응답 Pydantic 규격 (DTO)
```

---

## 📌 주요 레이어 설명

1. **`core/` & `models/` (공통 모듈)**
   * 팀원 전체가 공유하는 공통 인프라 로직 및 DB 엔티티/Enum 정의
   * 개발 초기 단계에서 우선적으로 정의하여 통일이 필요한 영역

2. **`apis/` (Presentation Layer)**
   * 클라이언트 요청을 받아 라우팅 및 응답 데이터 처리를 담당하는 엔드포인트 정의

3. **`services/` (Business Layer)**
   * 핵심 비즈니스 로직(검증, 연산, 알고리즘 처리 등) 구현

4. **`repositories/` (Data Access Layer)**
   * SQLAlchemy 등을 활용한 실제 데이터베이스 CRUD 쿼리 처리

5. **`schemas/` (Data Transfer Object)**
   * Pydantic 기반 데이터 유효성 검증 및 API 입출력 형식 정의