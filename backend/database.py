from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind = engine)
Base = declarative_base()

## Create Table Schema for out database

# --- TABLE 1: Doctors ---
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialization = Column(String)
    email = Column(String)

# --- TABLE 2: Availability Slots ---
class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer)
    date = Column(String)           # e.g. "2025-05-02"
    start_time = Column(String)     # e.g. "10:00"
    end_time = Column(String)       # e.g. "10:30"
    is_booked = Column(Boolean, default=False)

# --- TABLE 3: Appointments ---
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer)
    patient_name = Column(String)
    patient_email = Column(String)
    date = Column(String)
    start_time = Column(String)
    reason = Column(String)
    status = Column(String, default="confirmed")
    google_event_id = Column(String, nullable=True)

# ---TABLE 4 : Prompt History
class PromptHistory(Base):
    __tablename__ = "prompt_history"

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    role = Column(String)  # "patient" or "doctor"
    user_message = Column(Text)
    agent_response = Column(Text)
    timestamp = Column(String)

Base.metadata.create_all(bind=engine)

# --- Helper: get a DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()