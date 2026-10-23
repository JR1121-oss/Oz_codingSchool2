from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.db.databases import Base


class MedicalRecord(Base):
  __tablename__ = "medical_records"

  id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
  patient_id = Column(
      Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
  )
  chart_number = Column(String(50), nullable=False)
  symptoms = Column(Text, nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
  updated_at = Column(
      DateTime,
      default=datetime.utcnow,
      onupdate=datetime.utcnow,
      nullable=True,
  )

  patient = relationship("Patient", back_populates="medical_records")
  xray_images = relationship("XrayImage", back_populates="medical_record")
  ai_analysis_results = relationship(
      "AiAnalysisResult", back_populates="medical_record"
  )