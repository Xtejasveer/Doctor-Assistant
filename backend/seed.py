
from database import engine, Base, SessionLocal, Doctor, Availability, Appointment
from datetime import date, timedelta

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
db.query(Appointment).delete()
db.query(Availability).delete()
db.query(Doctor).delete()
db.commit()

# --- Add Doctors ---
doctors = [
    Doctor(name="Dr. Ahuja", specialization="General Physician", email="ahuja@clinic.com"),
    Doctor(name="Dr. Sharma", specialization="Cardiologist", email="sharma@clinic.com"),
    Doctor(name="Dr. Patel", specialization="Dermatologist", email="patel@clinic.com"),
    Doctor(name="Dr. Mehta", specialization="Neurologist", email="mehta@clinic.com"),
]
db.add_all(doctors)
db.commit()

# --- Add Availability Slots ---
today = date.today()
times = [
    ("09:00", "09:30"),
    ("10:00", "10:30"),
    ("11:00", "11:30"),
    ("14:00", "14:30"),
    ("15:00", "15:30"),
    ("16:00", "16:30"),
]

for i in range(5):  # next 5 days
    day = today + timedelta(days=i)
    for doc in db.query(Doctor).all():
        for start, end in times:
            slot = Availability(
                doctor_id=doc.id,
                date=str(day),
                start_time=start,
                end_time=end,
                is_booked=False
            )
            db.add(slot)

db.commit()

# --- Add Real Appointments ---
# Get doctor ids
ahuja = db.query(Doctor).filter(Doctor.name == "Dr. Ahuja").first()
sharma = db.query(Doctor).filter(Doctor.name == "Dr. Sharma").first()
patel = db.query(Doctor).filter(Doctor.name == "Dr. Patel").first()
mehta = db.query(Doctor).filter(Doctor.name == "Dr. Mehta").first()

yesterday = str(today - timedelta(days=1))
today_str = str(today)
tomorrow_str = str(today + timedelta(days=1))

appointments = [
    # Yesterday's appointments
    Appointment(doctor_id=ahuja.id, patient_name="Rahul Verma", patient_email="rahul@gmail.com", date=yesterday, start_time="09:00", reason="Fever and cold", status="completed"),
    Appointment(doctor_id=ahuja.id, patient_name="Priya Singh", patient_email="priya@gmail.com", date=yesterday, start_time="10:00", reason="General checkup", status="completed"),
    Appointment(doctor_id=ahuja.id, patient_name="Amit Sharma", patient_email="amit@gmail.com", date=yesterday, start_time="11:00", reason="Headache", status="completed"),
    Appointment(doctor_id=sharma.id, patient_name="Sunita Patel", patient_email="sunita@gmail.com", date=yesterday, start_time="09:00", reason="Chest pain", status="completed"),
    Appointment(doctor_id=sharma.id, patient_name="Vikram Mehta", patient_email="vikram@gmail.com", date=yesterday, start_time="10:00", reason="Blood pressure checkup", status="completed"),

    # Today's appointments
    Appointment(doctor_id=ahuja.id, patient_name="Neha Gupta", patient_email="neha@gmail.com", date=today_str, start_time="09:00", reason="Fever", status="confirmed"),
    Appointment(doctor_id=ahuja.id, patient_name="Rajesh Kumar", patient_email="rajesh@gmail.com", date=today_str, start_time="10:00", reason="Diabetes followup", status="confirmed"),
    Appointment(doctor_id=ahuja.id, patient_name="Pooja Agarwal", patient_email="pooja@gmail.com", date=today_str, start_time="11:00", reason="Fever and body ache", status="confirmed"),
    Appointment(doctor_id=sharma.id, patient_name="Deepak Joshi", patient_email="deepak@gmail.com", date=today_str, start_time="09:00", reason="Heart palpitations", status="confirmed"),
    Appointment(doctor_id=sharma.id, patient_name="Kavita Nair", patient_email="kavita@gmail.com", date=today_str, start_time="10:00", reason="ECG followup", status="confirmed"),
    Appointment(doctor_id=patel.id, patient_name="Arjun Reddy", patient_email="arjun@gmail.com", date=today_str, start_time="09:00", reason="Skin rash", status="confirmed"),
    Appointment(doctor_id=patel.id, patient_name="Meera Iyer", patient_email="meera@gmail.com", date=today_str, start_time="10:00", reason="Acne treatment", status="confirmed"),
    Appointment(doctor_id=mehta.id, patient_name="Suresh Babu", patient_email="suresh@gmail.com", date=today_str, start_time="09:00", reason="Migraine", status="confirmed"),

    # Tomorrow's appointments
    Appointment(doctor_id=ahuja.id, patient_name="Ananya Das", patient_email="ananya@gmail.com", date=tomorrow_str, start_time="09:00", reason="General checkup", status="confirmed"),
    Appointment(doctor_id=ahuja.id, patient_name="Karan Malhotra", patient_email="karan@gmail.com", date=tomorrow_str, start_time="10:00", reason="Fever", status="confirmed"),
    Appointment(doctor_id=sharma.id, patient_name="Divya Krishnan", patient_email="divya@gmail.com", date=tomorrow_str, start_time="09:00", reason="Cholesterol checkup", status="confirmed"),
    Appointment(doctor_id=patel.id, patient_name="Rohan Saxena", patient_email="rohan@gmail.com", date=tomorrow_str, start_time="11:00", reason="Eczema treatment", status="confirmed"),
]

db.add_all(appointments)

# Mark corresponding availability slots as booked
for appt in appointments:
    slot = db.query(Availability).filter(
        Availability.doctor_id == appt.doctor_id,
        Availability.date == appt.date,
        Availability.start_time == appt.start_time
    ).first()
    if slot:
        slot.is_booked = True

db.commit()
db.close()
print("Database seeded successfully with real data!")