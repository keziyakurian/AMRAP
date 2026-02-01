from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Study(Base):
    __tablename__ = "studies"
    id = Column(Integer, primary_key=True, index=True)
    study_name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String, unique=True)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    metric_label = Column(String, unique=True) # e.g., "Good value for money"
    category = Column(String) # e.g., "Imagery", "KPI"

class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"))
    respondent_id = Column(String)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    metric_id = Column(Integer, ForeignKey("metrics.id"))
    value = Column(Float) # 1 or 0 for top-box, or 1-5 scale
    weight = Column(Float, default=1.0)
    
    # Metadata for filtering
    wave_no = Column(Integer)
    week_no = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    gender = Column(String)
    age_group = Column(String)
    region = Column(String)

class DataCheck(Base):
    __tablename__ = "data_checks"
    id = Column(Integer, primary_key=True, index=True)
    check_category = Column(String) # e.g., "Time Frame", "Labels"
    check_item = Column(String) # e.g., "Week No."
    status = Column(String) # "Pass", "Fail", "Warning"
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PreAnalysisResult(Base):
    __tablename__ = "preanalysis_results"
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))
    metric_id = Column(Integer, ForeignKey("metrics.id"))
    mean_score = Column(Float)
    base_size = Column(Integer)

class Correlation(Base):
    __tablename__ = "correlations"
    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"))
    metric_a_id = Column(Integer, ForeignKey("metrics.id"))
    metric_b_id = Column(Integer, ForeignKey("metrics.id"))
    correlation_coefficient = Column(Float)
