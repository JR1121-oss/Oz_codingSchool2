# FastAPI 프로젝트의 '중앙 통제실'이자 '진입점(Entry Point)' 역할을 하는 파일
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# 1. Auth & User 라우터 (routers/ 폴더 내 파일들)
from app.routers import auth, admin, users

# 2. Patients v1 API 라우터 (apis/v1/ 폴더 내 파일들)
from app.apis.v1 import router as patient_list_router
from app.apis.v1.patient_detail_apis import router as patient_detail_router
from app.apis.v1.patient_delete_apis import router as patient_delete_router
# from app.apis.practice_apis_jk import router as mypage_router - 재경님 코드와 맞춰 수정 필요

app = FastAPI(title="Chest X-Ray AI User Service")

# ----------------------------------------------------------------
# 라우터 등록
# 주의: 모든 API 라우터는 아래 catch_all 라우트보다 먼저 등록해야 한다.
# prefix는 여기(main.py)에서만 지정하고, 각 라우터 파일의 APIRouter()에는 넣지 않는다.
# ----------------------------------------------------------------

# Auth & User
app.include_router(auth.router, prefix="/api/v1/users", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Patients
app.include_router(patient_list_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(patient_detail_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(patient_delete_router, prefix="/api/v1/patients", tags=["Patients"])

# Practice (practice_apis_jk.py 안의 APIRouter에 prefix가 있으면 여기서는 붙이지 않는다)
# app.include_router(practice_router, tags=["Practice"])
# 여기도 수정 필요

# ----------------------------------------------------------------
# app/main.py 위치 기준 parent.parent는 프로젝트 최상위 루트 디렉토리입니다.
BASE_DIR = Path(__file__).resolve().parent.parent

# 만약 static, media 폴더가 존재하지 않으면 생성
if not (BASE_DIR / "static").exists():
    os.mkdir(BASE_DIR / "static")
if not (BASE_DIR / "media").exists():
    os.mkdir(BASE_DIR / "media")

# 'static' 폴더를 '/static' 경로로 마운트 (CSS, JS 파일 서빙용)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
# 'media' 폴더를 '/media' 경로로 마운트 (사용자 업로드 파일 서빙용)
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

# 기본 라우트
@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")

# SPA(프론트 라우팅)용: 위에서 매칭되지 않은 경로는 모두 index.html로 보낸다.
# 반드시 파일 맨 마지막에 둘 것.
@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    # API나 정적 파일 경로는 제외 (FastAPI가 먼저 매칭하지 못한 경우에만 실행됨)
    if (
        path.startswith("api/v1")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")