from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from src.config.db import Base

class ProfilingLog(Base):
    __tablename__ = "profiling_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    endpoint = Column(String(255), nullable=False) 
    method = Column(String(10), nullable=False)     
    model_name = Column(String(100), nullable=True) 
    
    total_time_ms = Column(Float, nullable=False)
    num_predictions = Column(Integer, nullable=False, default=0)
    
    time_preprocessing_ms = Column(Float, nullable=True)
    time_inference_ms = Column(Float, nullable=True)
    time_database_ms = Column(Float, nullable=True)
    time_serialization_ms = Column(Float, nullable=True)
    
    top_functions = Column(JSON, nullable=True)
    
    ncalls_total = Column(Integer, nullable=True)
    ncalls_pandas = Column(Integer, nullable=True)
    ncalls_database = Column(Integer, nullable=True)
    
    cpu_percent = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    
    full_profile = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ProfilingLog {self.endpoint} - {self.total_time_ms}ms>"