// frontend/src/DoctorDashboard.jsx

import { useState } from "react"
import axios from "axios"
import ReactMarkdown from "react-markdown"

const SESSION_ID = "doctor_" + Math.random().toString(36).substr(2, 9)

export default function DoctorDashboard() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello Doctor! 👨‍⚕️ I can help you get reports on your appointments. You can ask me things like:\n\n- *How many appointments do I have today?*\n- *How many patients visited yesterday?*\n- *Show me Dr. Ahuja's schedule for tomorrow*"
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const sendMessage = async (messageToSend) => {
    const userMessage = messageToSend || input.trim()
    if (!userMessage || loading) return

    setInput("")
    setMessages(prev => [...prev, { role: "user", content: userMessage }])
    setLoading(true)

    try {
      const response = await axios.post("http://localhost:8000/doctor/report", {
        session_id: SESSION_ID,
        message: userMessage,
        role: "doctor"
      })

      setMessages(prev => [...prev, {
        role: "assistant",
        content: response.data.response
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, something went wrong. Please try again."
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Quick report buttons
  const quickReports = [
    "How many appointments do I have today?",
    "Show me Dr. Ahuja's schedule for tomorrow",
    "How many appointments does Dr. Sharma have today?",
  ]

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.headerTitle}>🩺 Doctor Dashboard</h2>
        <p style={styles.headerSub}>View appointment summaries and reports</p>
      </div>

      {/* Quick Report Buttons */}
      <div style={styles.quickBtns}>
        {quickReports.map((q, i) => (
          <button
            key={i}
            style={styles.quickBtn}
            onClick={() => sendMessage(q)}
            disabled={loading}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.messageBubble,
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.role === "user" ? "#00b894" : "white",
              color: msg.role === "user" ? "white" : "#333",
            }}
          >
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        ))}

        {loading && (
          <div style={{ ...styles.messageBubble, alignSelf: "flex-start", backgroundColor: "white" }}>
            <span>Generating report...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        <textarea
          style={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask for a report... (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button
          style={{
            ...styles.sendBtn,
            opacity: loading ? 0.6 : 1
          }}
          onClick={() => sendMessage()}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    maxWidth: "800px",
    margin: "0 auto",
    padding: "16px",
  },
  header: {
    textAlign: "center",
    padding: "16px 0",
    marginBottom: "8px",
  },
  headerTitle: {
    fontSize: "22px",
    color: "#1a1a2e",
  },
  headerSub: {
    color: "#666",
    fontSize: "14px",
  },
  quickBtns: {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
    marginBottom: "12px",
  },
  quickBtn: {
    padding: "8px 12px",
    backgroundColor: "#f0f4f8",
    border: "1px solid #ddd",
    borderRadius: "20px",
    fontSize: "13px",
    color: "#333",
    whiteSpace: "nowrap",
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    padding: "16px 0",
  },
  messageBubble: {
    maxWidth: "70%",
    padding: "12px 16px",
    borderRadius: "12px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
    lineHeight: "1.5",
    fontSize: "15px",
  },
  inputArea: {
    display: "flex",
    gap: "8px",
    padding: "12px 0",
    borderTop: "1px solid #eee",
  },
  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "15px",
    resize: "none",
    outline: "none",
    fontFamily: "inherit",
  },
  sendBtn: {
    padding: "0 24px",
    backgroundColor: "#00b894",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "15px",
    fontWeight: "600",
  }
}