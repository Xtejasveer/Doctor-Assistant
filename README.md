# 🏥 Doctor Assistant

An AI-powered appointment management system that uses an **agentic LLM architecture** with the **Model Context Protocol (MCP)** to let patients book appointments and doctors view reports — all through natural language conversations.

Built with **FastAPI + React + MCP + GPT-4o**, featuring automated email confirmations, Google Calendar integration, and Slack notifications.

---

## 🏗 MCP Architecture

```
┌─────────────────┐         ┌─────────────────┐           ┌─────────────────┐
│  React Frontend │ ──────▶ │  FastAPI Server │ ──────▶  │    AI Agent     │
│  (Vite + JSX)   │ ◀────── │  (REST API)     │ ◀──────  │  (GPT-4o LLM)   │
└─────────────────┘         └─────────────────┘           └────────┬────────┘
                                                                   │
                                                            MCP Protocol (stdio)
                                                                   │
                                                          ┌────────▼────────┐
                                                          │   MCP Server    │
                                                          │  (mcp_server.py)│
                                                          └────────┬────────┘
                                                                   │
                                ┌──────────────────────────────────┼──────────────────────────────────┐
                                │                                  │                                  │
                       ┌────────▼────────┐               ┌────────▼────────┐               ┌─────────▼────────┐
                       │     Tools       │               │   Resources     │               │     Prompts      │
                       │ (5 MCP tools)   │               │ (2 MCP resources)│              │ (2 MCP prompts)  │
                       └────────┬────────┘               └────────┬────────┘               └──────────────────┘
                                │                                 │
             ┌──────────────────┼──────────────────┐              │
             │                  │                  │              │
    ┌────────▼──────┐  ┌────────▼──────┐  ┌───────▼──────┐        │
    │  PostgreSQL   │  │Google Calendar│  │  SendGrid +  │  ◀─────┘
    │  Database     │  │     API       │  │    Slack     │
    └───────────────┘  └───────────────┘  └──────────────┘
```

### MCP Primitives Implemented

This project implements all 3 MCP primitives as required:

#### 🔧 Tools (Actions the LLM can invoke)
Tools allow the LLM to perform actions. The LLM decides which tool to call and when — no hardcoded routing.

| Tool | Description |
|---|---|
| `check_availability` | Check available time slots for a doctor on a given date |
| `book_appointment` | Book an appointment, create calendar event, send email |
| `get_appointment_stats` | Get appointment stats for a doctor, send Slack report |
| `get_all_doctors` | List all doctors with specializations |
| `get_next_available_slot` | Find next available slot for auto-rescheduling |

#### 📦 Resources (Data the LLM can read)
Resources are read-only data sources the LLM reads as background context before deciding what to do.

| Resource URI | Description |
|---|---|
| `doctors://all` | List of all doctors in the system |
| `appointments://today` | All appointments scheduled for today |

#### 📝 Prompts (Reusable templates)
Prompts are pre-built templates for common user tasks.

| Prompt | Description |
|---|---|
| `book_appointment_prompt` | Template for booking an appointment with a doctor |
| `doctor_report_prompt` | Template for generating a doctor appointment report |

---

### How the Agentic Loop Works

1. User sends a natural language message via React frontend
2. FastAPI forwards the message to the AI Agent (`agent.py`)
3. Agent connects to MCP Server via stdio protocol
4. Agent calls `session.list_tools()` to **dynamically discover** available tools at runtime
5. Agent sends message + tools to GPT-4o via OpenRouter
6. If LLM wants to call a tool, Agent executes it via MCP and feeds result back
7. Loop continues until LLM produces a final text response
8. Response is returned to the user

> **Important:** The LLM drives all workflow decisions. The backend never hardcodes "if user says X, call tool Y". The LLM decides which tools to call and in what order based on the user's natural language input.

---

## ✅ Integration Status

All integrations in this project are **real and fully functional** — no mocks or simulated responses anywhere.

| Integration | Type | Status | Details |
|---|---|---|---|
| PostgreSQL | Database |  Real | Stores doctors, availability, appointments, prompt history |
| Google Calendar API | External API |  Real | Creates actual calendar events on booking |
| SendGrid | Email Service |  Real | Sends actual HTML confirmation emails to patients |
| Slack Webhooks | Notification |  Real | Sends formatted reports to Slack channel |
| OpenRouter GPT-4o | LLM |  Real | Actual AI model calls with tool calling |
| MCP Protocol | Architecture |  Real | Proper client-server communication via stdio |

---

## 🧪 Testing the MCP Architecture

To verify the full MCP architecture is working correctly, run the dedicated test file:

```bash
cd backend
python test_mcp.py
```

This test independently verifies:
- MCP Client connects to MCP Server
- Tools are dynamically discovered at runtime via `tools/list`
- Resources are discovered via `resources/list`
- Prompts are discovered via `prompts/list`
- Tool execution works via MCP protocol
- Resource reading works via MCP protocol
- Prompt retrieval works via MCP protocol

Expected output:
```
============================================================
MCP ARCHITECTURE TEST
Testing: Client → Server → Tool/Resource/Prompt
============================================================

 MCP Client connected to MCP Server successfully
 5 tools discovered at runtime
 2 resources discovered
 2 prompts discovered
 Tool execution via MCP protocol working
 Resource reading via MCP protocol working
 Prompt retrieval via MCP protocol working
============================================================
All MCP primitives (Tool/Resource/Prompt) are
properly implemented and accessible via MCP protocol.
============================================================
```

---

## 👤 Features — Patient Side

### 💬 Natural Language Chat Interface
- Conversational chat UI where patients can type requests in plain English
- Markdown rendering with styled lists and bold text via `react-markdown`
- Auto-scrolling message feed with a "Thinking..." loading indicator
- Session-based conversation history so the AI remembers context within a chat

### 🔍 Check Doctor Availability
- Ask for available slots with any doctor on any date
- The agent queries the database and returns available time slots as a clean numbered list
- Supports fuzzy doctor name matching (case-insensitive partial match)

### 📅 Book Appointments
- Book an appointment by simply conversing with the AI
- The agent collects all required info through conversation
- Automatically marks the slot as booked in the database
- Handles both 12-hour (AM/PM) and 24-hour time formats

### 🔄 Smart Auto-Rescheduling
- If a requested slot is unavailable, the agent automatically finds the next available slot
- Searches the same day first, then looks ahead up to 3 days
- Suggests the alternative and asks the patient to confirm before booking

### 🛡 Edge Case Handling
- **Duplicate booking prevention** — detects if same patient already has an appointment with same doctor on same date
- **Slot validation** — verifies slot exists before booking, suggests alternatives if not
- **Date format validation** — validates date format before any database queries
- **Time format handling** — converts AM/PM to 24-hour format automatically

### 📧 Email Confirmation (SendGrid)
- After every successful booking, a professionally styled HTML confirmation email is sent
- Includes appointment details: doctor name, date, time, and reason

### 📆 Google Calendar Integration
- Every booked appointment is automatically added as a Google Calendar event
- Includes email and popup reminders
- Returns a direct link to the calendar event

### 📜 Prompt History Logging
- Every patient message and agent response is logged to the `prompt_history` table
- Stored with session ID, role, and timestamp

---

## 🩺 Features — Doctor Side

### 📊 Appointment Reports & Summaries
- Doctors can ask for appointment summaries in natural language
- The agent fetches real appointment data from the database
- Shows patient names, appointment times, reasons, and statuses

### ⚡ Quick Report Buttons
- Pre-built quick action buttons for common queries:
  - *"How many appointments do I have today?"*
  - *"Show me Dr. Ahuja's schedule for tomorrow"*
  - *"How many appointments does Dr. Sharma have today?"*

### 🔔 Slack Notifications
- Every doctor report automatically sends a formatted Slack notification
- Uses Slack Block Kit for rich formatting with headers, sections, and dividers

### 📜 Prompt History Logging
- Doctor interactions logged to `prompt_history` table
- Tagged with `role: "doctor"` for differentiation from patient logs

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite, Axios, react-markdown |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI / LLM** | GPT-4o (via OpenRouter API) |
| **Tool Protocol** | Model Context Protocol (MCP) — `mcp` Python SDK |
| **Database** | PostgreSQL + SQLAlchemy ORM |
| **Email** | SendGrid API |
| **Calendar** | Google Calendar API (OAuth 2.0) |
| **Notifications** | Slack Incoming Webhooks |
| **Pkg Manager** | uv (Python), npm (Node.js) |

---

## 📁 Project Structure

```
doctor-assistant/
├── backend/
│   ├── main.py              # FastAPI server with REST endpoints
│   ├── agent.py             # AI agent with agentic loop (LLM + MCP client)
│   ├── mcp_server.py        # MCP server (Tools + Resources + Prompts)
│   ├── database.py          # SQLAlchemy models & DB connection
│   ├── seed.py              # Database seeding script with sample data
│   ├── email_service.py     # SendGrid email confirmation service
│   ├── calendar_service.py  # Google Calendar event creation
│   ├── notification.py      # Slack webhook notifications
│   └── test_mcp.py          # MCP architecture test file
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Role selection (Patient / Doctor)
│   │   ├── PatientChat.jsx   # Patient chat interface
│   │   ├── DoctorDashboard.jsx # Doctor report dashboard
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env                      # Environment variables (not committed)
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

---

## 🚀 Setup Guide

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and **npm**
- **PostgreSQL**
- API keys for OpenRouter, SendGrid, Slack, Google Cloud

---

### 1. Clone the Repository

```bash
git clone https://github.com/Xtejasveer/Doctor-Assistant.git
cd Doctor-Assistant
```

---

### 2. Set Up the Backend

```bash
uv sync
```

---

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` folder:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/doctor_assistant
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SENDGRID_FROM_EMAIL=your-verified-email@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

### 4. Set Up PostgreSQL

```sql
CREATE DATABASE doctor_assistant;
```

---

### 5. Set Up Google Calendar

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project and enable the **Google Calendar API**
3. Create **OAuth 2.0 credentials** (Desktop application type)
4. Download credentials JSON and save as `backend/credentials.json`
5. Run the auth flow once:

```bash
cd backend
python calendar_service.py
```

---

### 6. Seed the Database

```bash
cd backend
python seed.py
```

Creates 4 doctors, availability slots for 5 days, and sample appointments.

---

### 7. Set Up the Frontend

```bash
cd frontend
npm install
```

---

### 8. Run the Application

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

### 9. Test MCP Architecture

```bash
cd backend
python test_mcp.py
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a patient message to the AI agent |
| `POST` | `/doctor/report` | Send a doctor message to the AI agent |
| `GET` | `/history/{session_id}` | Get prompt history for a session |
| `DELETE` | `/chat/{session_id}` | Clear conversation history |
| `GET` | `/health` | Health check endpoint |

---

## 💬 Sample Prompts

### Patient Prompts

```
What doctors are available?
```
```
I want to book an appointment with Dr. Ahuja tomorrow morning
```
```
Book the 10 AM slot, my name is John Doe and my email is john@gmail.com
```
```
I want to book the 9 AM slot with Dr. Ahuja tomorrow
```
*(If 9 AM is taken, agent auto-suggests next available slot)*

### Doctor Prompts

```
How many appointments do I have today?
```
```
How many patients visited yesterday?
```
```
How many patients with fever today?
```
```
Show me Dr. Ahuja's schedule for tomorrow
```

---

## 🔁 Multi-turn Conversation Example

```
Patient: "I want to check Dr. Ahuja's availability for tomorrow"
Agent:   "Here are the available slots:
          1. 9:00 AM - 9:30 AM
          2. 10:00 AM - 10:30 AM ..."

Patient: "Book the 10 AM slot"
Agent:   "What is your name and email?"

Patient: "John Doe, john@gmail.com"
Agent:   "Appointment booked! Confirmation email sent to john@gmail.com"
```

The agent maintains full context across all turns using session-based conversation history stored server-side.

---

## ⚠️ Important Notes

- `credentials.json` and `token.pickle` are not committed to the repo
- `.env` is not committed to the repo
- Database must be seeded before first use with `python seed.py`
- Google Calendar events are created in the authenticated user's calendar
- MCP server communicates via stdio protocol — it does not run as a separate HTTP server
