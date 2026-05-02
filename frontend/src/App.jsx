// frontend/src/App.jsx

import { useState } from "react"
import PatientChat from "./PatientChat"
import DoctorDashboard from "./DoctorDashboard"

export default function App() {
  const [role, setRole] = useState(null) // "patient" or "doctor"

  // Role selection screen
  if (!role) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h1 style={styles.title}>🏥 Doctor Assistant</h1>
          <p style={styles.subtitle}>Please select your role to continue</p>
          <div style={styles.buttonGroup}>
            <button
              style={styles.patientBtn}
              onClick={() => setRole("patient")}
            >
              👤 I am a Patient
            </button>
            <button
              style={styles.doctorBtn}
              onClick={() => setRole("doctor")}
            >
              🩺 I am a Doctor
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Back button */}
      <button style={styles.backBtn} onClick={() => setRole(null)}>
        ← Back
      </button>

      {role === "patient" ? <PatientChat /> : <DoctorDashboard />}
    </div>
  )
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
  },
  card: {
    background: "white",
    borderRadius: "16px",
    padding: "48px",
    textAlign: "center",
    boxShadow: "0 4px 24px rgba(0,0,0,0.1)",
    width: "400px",
  },
  title: {
    fontSize: "28px",
    marginBottom: "8px",
    color: "#1a1a2e",
  },
  subtitle: {
    color: "#666",
    marginBottom: "32px",
    fontSize: "15px",
  },
  buttonGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  patientBtn: {
    padding: "14px",
    fontSize: "16px",
    backgroundColor: "#2c7be5",
    color: "white",
    border: "none",
    borderRadius: "8px",
    transition: "background 0.2s",
  },
  doctorBtn: {
    padding: "14px",
    fontSize: "16px",
    backgroundColor: "#00b894",
    color: "white",
    border: "none",
    borderRadius: "8px",
    transition: "background 0.2s",
  },
  backBtn: {
    position: "fixed",
    top: "16px",
    left: "16px",
    padding: "8px 16px",
    backgroundColor: "#eee",
    border: "none",
    borderRadius: "8px",
    fontSize: "14px",
    zIndex: 100,
  }
}