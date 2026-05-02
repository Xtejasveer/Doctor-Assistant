
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")


def send_appointment_confirmation(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    date: str,
    time: str,
    reason: str = "General checkup"
):
    """Send appointment confirmation email to patient"""
    
    subject = f"Appointment Confirmed with {doctor_name}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c7be5;">Appointment Confirmation</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>Your appointment has been successfully booked. Here are your details:</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Doctor</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{doctor_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Date</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{date}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Time</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{time}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6;"><strong>Reason</strong></td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{reason}</td>
                </tr>
            </table>
            
            <p>Please arrive 10 minutes before your appointment time.</p>
            <p>If you need to reschedule, please contact us as soon as possible.</p>
            
            <br>
            <p>Best regards,</p>
            <p><strong>Doctor Assistant Team</strong></p>
        </body>
    </html>
    """
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=patient_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[Email] Confirmation sent to {patient_email} — Status: {response.status_code}")
        return {"success": True, "message": f"Confirmation email sent to {patient_email}"}
    except Exception as e:
        print(f"[Email] Failed to send email: {e}")
        return {"success": False, "error": str(e)}