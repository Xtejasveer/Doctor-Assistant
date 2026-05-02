// frontend/src/PatientChat.jsx

import { useState, useRef, useEffect } from "react"
import axios from "axios"
import ReactMarkdown from "react-markdown"

const SESSION_ID = "patient_" + Math.random().toString(36).substr(2, 9)

export default function PatientChat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi! I'm your appointment assistant 👋 I can help you book appointments with our doctors. What would you like to do?"
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  // Auto scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput("")

    // Add user message to chat
    setMessages(prev => [...prev, { role: "user", content: userMessage }])
    setLoading(true)

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        session_id: SESSION_ID,
        message: userMessage,
        role: "patient"
      })

      // Add agent response to chat
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

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.headerTitle}>👤 Patient Chat</h2>
        <p style={styles.headerSub}>Book and manage your appointments</p>
      </div>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.messageBubble,
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.role === "user" ? "#2c7be5" : "white",
              color: msg.role === "user" ? "white" : "#333",
            }}
          >
            <ReactMarkdown
  components={{
    p: ({node, ...props}) => <p style={{margin: "4px 0"}} {...props} />,
    ul: ({node, ...props}) => <ul style={{paddingLeft: "20px", margin: "8px 0"}} {...props} />,
    ol: ({node, ...props}) => <ol style={{paddingLeft: "20px", margin: "8px 0"}} {...props} />,
    li: ({node, ...props}) => <li style={{margin: "4px 0"}} {...props} />,
    strong: ({node, ...props}) => <strong style={{fontWeight: "600"}} {...props} />,
    table: ({node, ...props}) => (
      <table style={{
        borderCollapse: "collapse",
        width: "100%",
        margin: "8px 0",
        fontSize: "14px"
      }} {...props} />
    ),
    th: ({node, ...props}) => (
      <th style={{
        border: "1px solid #ddd",
        padding: "8px 12px",
        backgroundColor: "#2c7be5",
        color: "white",
        textAlign: "left"
      }} {...props} />
    ),
    td: ({node, ...props}) => (
      <td style={{
        border: "1px solid #ddd",
        padding: "8px 12px",
        backgroundColor: "white",
        color: "#333"
      }} {...props} />
    ),
    tr: ({node, ...props}) => (
      <tr style={{
        borderBottom: "1px solid #ddd"
      }} {...props} />
    ),
  }}
>
  {msg.content}
</ReactMarkdown>
          </div>
        ))}

        {loading && (
          <div style={{ ...styles.messageBubble, alignSelf: "flex-start", backgroundColor: "white" }}>
            <span>Thinking...</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        <textarea
          style={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button
          style={{
            ...styles.sendBtn,
            opacity: loading ? 0.6 : 1
          }}
          onClick={sendMessage}
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
    backgroundColor: "#2c7be5",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "15px",
    fontWeight: "600",
  }
}