# app/main.py
# FastAPI 프로젝트의 '중앙 통제실'이자 '진입점(Entry Point)' 역할을 하는 파일
import os, asyncio, logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# 1. Auth & Admin 라우터 (routers/ 폴더)
from app.routers import auth, admin

# 2. v1 API 라우터 (apis/v1/ 폴더)
from app.apis.v1.user_me_apis import router as user_me_router
from app.apis.v1.patient_list_apis import router as patient_list_router
from app.apis.v1.patient_detail_apis import router as patient_detail_router
from app.apis.v1.patient_delete_apis import router as patient_delete_router
from app.apis.v1.medical_record_detail_apis import router as record_detail_router
from app.apis.v1.medical_record_list_apis import router as record_list_router
from app.apis.v1.medical_record_list_apis import patient_records_router
from app.apis.v1.prediction_apis import router as prediction_router

logger = logging.getLogger(__name__)


# 서버가 켜질 때 AI 모델을 미리 불러온다 (첫 예측 요청이 느리지 않게)
# 모델 파일(.pth)이 없어도 경고만 남기고 서버는 정상으로 켜진다
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.ai.inference import warmup
        await asyncio.to_thread(warmup)
        logger.info("AI 모델 로드 완료")
    except Exception:
        logger.warning("AI 모델을 미리 불러오지 못했습니다. 첫 예측 요청 때 다시 시도합니다.", exc_info=True)
    yield


app = FastAPI(title="Chest X-Ray AI User Service", lifespan=lifespan)

# ----------------------------------------------------------------
# 라우터 등록
# 주의: 모든 API 라우터는 아래 catch_all 라우트보다 먼저 등록해야 한다.
# prefix는 여기(main.py)에서만 지정하고, 각 라우터 파일의 APIRouter()에는 넣지 않는다.
# ----------------------------------------------------------------

# Auth & User
app.include_router(auth.router, prefix="/api/v1/users", tags=["Auth"])
app.include_router(user_me_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Patients
app.include_router(patient_list_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(patient_detail_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(patient_delete_router, prefix="/api/v1/patients", tags=["Patients"])

# Medical Records
app.include_router(record_detail_router, prefix="/api/v1/medical-records", tags=["Medical Records"])
app.include_router(record_list_router, prefix="/api/v1/medical-records", tags=["Medical Records"])
app.include_router(patient_records_router, prefix="/api/v1/patients", tags=["Medical Records"])

# AI Prediction
app.include_router(prediction_router, prefix="/api/v1/medical-records", tags=["AI Prediction"])


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