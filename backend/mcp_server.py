# Here we are building a MCP server and will define custom tools for our LLM to interact with.

from mcp.server.fastmcp import FastMCP
from database import SessionLocal, Doctor, Availability, Appointment
from email_service import send_appointment_confirmation
from notification import send_doctor_report_slack
from datetime import datetime
from calendar_service import create_calendar_event

mcp = FastMCP("Doctor Assistant")

@mcp.tool()
def check_availability(doctor_name: str, date: str) -> dict:
    """Check available slots for a doctor on a given date"""
    db = SessionLocal()
    
    doctor = db.query(Doctor).filter(
        Doctor.name.ilike(f"%{doctor_name}%")
    ).first()
    
    if not doctor:
        return {"error": f"Doctor {doctor_name} not found"}
    
    slots = db.query(Availability).filter(
        Availability.doctor_id == doctor.id,
        Availability.date == date,
        Availability.is_booked == False
    ).all()
    
    db.close()
    
    if not slots:
        return {"message": f"No available slots for {doctor.name} on {date}"}
    
    return {
        "doctor": doctor.name,
        "date": date,
        "available_slots": [
            {"id": s.id, "start": s.start_time, "end": s.end_time}
            for s in slots
        ]
    }


@mcp.tool()
def book_appointment(doctor_name: str, date: str, start_time: str,
                     patient_name: str, patient_email: str, reason: str = "General checkup") -> dict:
    """Book an appointment for a patient with a doctor"""
    
    # Fix time format
    from datetime import datetime
    try:
        if "AM" in start_time.upper() or "PM" in start_time.upper():
            parsed = datetime.strptime(start_time.strip(), "%I:%M %p")
            start_time = parsed.strftime("%H:%M")
    except:
        start_time = start_time.strip()

    db = SessionLocal()
    doctor_name_actual = None
    end_time = None
    
    try:
        # Find doctor
        doctor = db.query(Doctor).filter(
            Doctor.name.ilike(f"%{doctor_name}%")
        ).first()

        if not doctor:
            return {"error": f"Doctor {doctor_name} not found"}

        doctor_name_actual = doctor.name
        doctor_id = doctor.id

        # Find slot
        slot = db.query(Availability).filter(
            Availability.doctor_id == doctor_id,
            Availability.date == date,
            Availability.start_time == start_time,
            Availability.is_booked == False
        ).first()

        if not slot:
            return {"error": f"Slot {start_time} is not available"}
        
        end_time = slot.end_time

        # Mark slot as booked
        slot.is_booked = True
        db.flush()

        # Create appointment
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_name=patient_name,
            patient_email=patient_email,
            date=date,
            start_time=start_time,
            reason=reason,
            status="confirmed"
        )
        db.add(appointment)
        db.commit()
        

    except Exception as e:
        db.rollback()
        return {"error": f"Booking failed: {str(e)}"}
    finally:
        db.close()
    calendar_result = create_calendar_event(
        doctor_name=doctor_name_actual,
        patient_name=patient_name,
        date=date,
        start_time=start_time,
        end_time=end_time,
        reason=reason
    )

    # Send email AFTER session is closed
    send_appointment_confirmation(
        patient_email=patient_email,
        patient_name=patient_name,
        doctor_name=doctor_name_actual,
        date=date,
        time=start_time,
        reason=reason
    )

    return {
        "success": True,
        "message": f"Appointment booked with {doctor_name_actual} on {date} at {start_time}. Confirmation email sent.",
        "patient": patient_name,
        "doctor": doctor_name_actual,
        "date": date,
        "time": start_time,
        "calendar_event": calendar_result.get("event_link")
    }

@mcp.tool()
def get_appointment_stats(doctor_name: str, date: str) -> dict:
    """Get appointment statistics for a doctor on a given date"""
    db = SessionLocal()
    
    doctor = db.query(Doctor).filter(
        Doctor.name.ilike(f"%{doctor_name}%")
    ).first()
    
    if not doctor:
        db.close()
        return {"error": f"Doctor {doctor_name} not found"}
    
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date == date
    ).all()
    
    db.close()
    patients = [
        {
            "name": a.patient_name,
            "time": a.start_time,
            "reason": a.reason,
            "status": a.status
        }
        for a in appointments
    ]

    send_doctor_report_slack(
        doctor_name=doctor.name,
        date=date,
        total_appointments=len(appointments),
        patients=patients
    )
    
    return {
    "doctor": doctor.name,
    "date": date,
    "total_appointments": len(appointments),
    "patients": [
        {
            "name": a.patient_name,
            "time": a.start_time,
            "reason": a.reason,
            "status": a.status
        }
        for a in appointments
    ]
}


@mcp.tool()
def get_all_doctors() -> dict:
    """Get list of all available doctors"""
    db = SessionLocal()
    doctors = db.query(Doctor).all()
    db.close()
    
    return {
        "doctors": [
            {"id": d.id, "name": d.name, "specialization": d.specialization}
            for d in doctors
        ]
    }
@mcp.tool()
def get_next_available_slot(doctor_name: str, date: str, preferred_time: str) -> dict:
    """Get the next available slot for a doctor when preferred slot is unavailable"""
    db = SessionLocal()
    
    doctor = db.query(Doctor).filter(
        Doctor.name.ilike(f"%{doctor_name}%")
    ).first()
    
    if not doctor:
        db.close()
        return {"error": f"Doctor {doctor_name} not found"}
    
    # Get all available slots from that date onwards
    from datetime import datetime, timedelta
    
    # First check remaining slots on same day
    same_day_slots = db.query(Availability).filter(
        Availability.doctor_id == doctor.id,
        Availability.date == date,
        Availability.is_booked == False,
        Availability.start_time > preferred_time
    ).order_by(Availability.start_time).all()
    
    if same_day_slots:
        next_slot = same_day_slots[0]
        db.close()
        return {
            "doctor": doctor.name,
            "date": date,
            "next_available": {
                "date": next_slot.date,
                "start": next_slot.start_time,
                "end": next_slot.end_time
            },
            "message": f"Next available slot is on {next_slot.date} at {next_slot.start_time}"
        }
    
    # If no slots on same day, check next 3 days
    for i in range(1, 4):
        next_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
        next_day_slots = db.query(Availability).filter(
            Availability.doctor_id == doctor.id,
            Availability.date == next_date,
            Availability.is_booked == False
        ).order_by(Availability.start_time).all()
        
        if next_day_slots:
            next_slot = next_day_slots[0]
            db.close()
            return {
                "doctor": doctor.name,
                "date": next_date,
                "next_available": {
                    "date": next_slot.date,
                    "start": next_slot.start_time,
                    "end": next_slot.end_time
                },
                "message": f"Next available slot is on {next_slot.date} at {next_slot.start_time}"
            }
    
    db.close()
    return {"message": f"No available slots found for {doctor.name} in the next 3 days"}

# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")