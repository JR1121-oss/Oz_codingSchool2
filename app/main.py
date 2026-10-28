# FastAPI 프로젝트의 '중앙 통제실'이자 '진입점(Entry Point)' 역할을 하는 파일
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from app.apis.practice_apis_jk import router as mypage_router
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# 1. Auth & User 라우터 (routers/ 폴더 내 파일들)
from app.routers import auth, admin, users

# 2. Patients v1 API 라우터 (apis/v1/ 폴더 내 파일들)
from app.apis.v1 import patient_apis
from app.apis.v1.patient_detail_apis import router as patient_detail_router
from app.apis.v1.patient_delete_apis import router as patient_delete_router

app = FastAPI(title="Chest X-Ray AI User Service")

# Auth & User
app.include_router(auth.router, prefix="/api/v1/users", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Patients
app.include_router(patient_apis.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(patient_detail_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(patient_delete_router, prefix="/api/v1/patients", tags=["Patients"])

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
app.include_router(mypage_router)

@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


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
