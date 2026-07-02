"""
MedAppoint - Patient Appointment Management API
"""
import os
from datetime import datetime

from flask import Flask, jsonify, request, redirect
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


@app.get("/appointments/new")
def new_appointment_form():
    session = SessionLocal()
    try:
        patients = session.query(Patient).all()
    finally:
        session.close()

    if not patients:
        return "<p>No patients exist yet. Create one via POST /patients first.</p>", 200

    options = "".join(f'<option value="{p.id}">{p.full_name} (id {p.id})</option>' for p in patients)
    return f"""
    <!doctype html>
    <html>
    <head><title>Book an Appointment - MedAppoint</title></head>
    <body style="font-family: sans-serif; max-width: 480px; margin: 40px auto;">
      <h2>Book an Appointment</h2>
      <form method="POST" action="/appointments">
        <label>Patient</label><br>
        <select name="patient_id" required>{options}</select><br><br>
        <label>Doctor</label><br>
        <input type="text" name="doctor_name" required><br><br>
        <label>Date &amp; time</label><br>
        <input type="datetime-local" name="scheduled_at" required><br><br>
        <label>Reason</label><br>
        <input type="text" name="reason"><br><br>
        <button type="submit">Book</button>
      </form>
    </body>
    </html>
    """


@app.post("/appointments")
def create_appointment():
    data = request.get_json(silent=True) or request.form
    session = SessionLocal()
    try:
        appt = Appointment(
            patient_id=int(data["patient_id"]),
            doctor_name=data["doctor_name"],
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]),
            reason=data.get("reason"),
        )
        session.add(appt)
        session.commit()
        if request.form:
            return f"""
            <p>Appointment #{appt.id} booked with {appt.doctor_name}.</p>
            <p><a href="/appointments/new">Book another</a></p>
            """, 201
        return jsonify(id=appt.id), 201
    finally:
        session.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)