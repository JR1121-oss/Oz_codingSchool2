from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.databases import Base

class AiAnalysisResult(Base):
    __tablename__ = "ai_analysis_results"

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )
    
    # medical_records.id 참조 (BigInteger, CASCADE 삭제)
    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
        comment="진료 기록 id"
    )
    
    is_pneumonia: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment="폐렴 진단 여부"
    )
    confidence: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, comment="AI 예측 신뢰도"
    )
    heatmap_url: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="AI가 판별한 병변 표시 이미지 url"
    )
    ai_model: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="AI 예측에 사용된 모델명 혹은 모델파일"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="AI 폐렴 예측 결과 생성일시"
    )
    
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=func.now(),
        comment="수정 일시"
    )