from fastapi import APIRouter
import os
from app.core.database import patients_db, records_db

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.delete("/{patient_id}")
def delete_patient(patient_id: int):
    global patients_db, records_db # in-memory DB 수정 시 필요
    
    patients_db[:] = [p for p in patients_db if p["id"] != patient_id]
    
    records_to_delete = [r for r in records_db if r["patient_id"] == patient_id]
    for r in records_to_delete:
        if os.path.exists(r["xray_image_path"]):
            os.remove(r["xray_image_path"])
            
    records_db[:] = [r for r in records_db if r["patient_id"] != patient_id]
    
    return {"message": "환자 및 관련 진료기록이 확인했습니다(삭제 완료)."}