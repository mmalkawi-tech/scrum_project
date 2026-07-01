"""
MedAppoint - Patient Appointment Management API
"""
import os
from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local_dev.db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    date_of_birth = Column(String(20), nullable=False)
    phone = Column(String(30))
    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_name = Column(String(120), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    reason = Column(String(255))
    patient = relationship("Patient", back_populates="appointments")


Base.metadata.create_all(engine)


@app.get("/health")
def health():
    return jsonify(status="ok", time=datetime.utcnow().isoformat()), 200


@app.get("/patients")
def list_patients():
    session = SessionLocal()
    try:
        patients = session.query(Patient).all()
        return jsonify([
            {"id": p.id, "full_name": p.full_name, "date_of_birth": p.date_of_birth, "phone": p.phone}
            for p in patients
        ])
    finally:
        session.close()


@app.post("/patients")
def create_patient():
    data = request.get_json(force=True)
    session = SessionLocal()
    try:
        patient = Patient(
            full_name=data["full_name"],
            date_of_birth=data["date_of_birth"],
            phone=data.get("phone"),
        )
        session.add(patient)
        session.commit()
        return jsonify(id=patient.id), 201
    finally:
        session.close()


@app.get("/appointments")
def list_appointments():
    session = SessionLocal()
    try:
        appts = session.query(Appointment).all()
        return jsonify([
            {
                "id": a.id,
                "patient_id": a.patient_id,
                "doctor_name": a.doctor_name,
                "scheduled_at": a.scheduled_at.isoformat(),
                "reason": a.reason,
            }
            for a in appts
        ])
    finally:
        session.close()


@app.post("/appointments")
def create_appointment():
    data = request.get_json(force=True)
    session = SessionLocal()
    try:
        appt = Appointment(
            patient_id=data["patient_id"],
            doctor_name=data["doctor_name"],
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]),
            reason=data.get("reason"),
        )
        session.add(appt)
        session.commit()
        return jsonify(id=appt.id), 201
    finally:
        session.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)