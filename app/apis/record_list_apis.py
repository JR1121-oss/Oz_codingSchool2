# app/apis/record_list_apis.py
from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime
import shutil
from app.core.database import records_db, get_next_record_id, IMAGE_DIR

router = APIRouter(prefix="/patients", tags=["Medical Records"])

@router.post("/{patient_id}/records", status_code=201)
def create_medical_record(
    patient_id: int,
    chart_number: str = Form(...),
    symptom: str = Form(...),
    xray_image: UploadFile = File(...)
):
    record_id = get_next_record_id()
    file_location = f"{IMAGE_DIR}/{record_id}_{xray_image.filename}"
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(xray_image.file, file_object)
        
    new_record = {
        "id": record_id,
        "patient_id": patient_id,
        "chart_number": chart_number,
        "symptom": symptom,
        "xray_image_path": file_location,
        "created_at": datetime.now()
    }
    records_db.append(new_record)
    return new_record

@router.get("/{patient_id}/records")
def get_patient_records(patient_id: int):
    records = [r for r in records_db if r["patient_id"] == patient_id]
    for r in records:
        if len(r["symptom"]) > 100:
            r["symptom"] = r["symptom"][:100] + "..."
    return records