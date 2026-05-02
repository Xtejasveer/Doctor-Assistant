# 🏥 Doctor Assistant

An AI-powered appointment management system that uses an **agentic LLM architecture** with the **Model Context Protocol (MCP)** to let patients book appointments and doctors view reports — all through natural language conversations.

Built with **FastAPI + React + MCP + DeepSeek**, featuring automated email confirmations, Google Calendar integration, and Slack notifications.

## 🏗 Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  React Frontend │ ──────▶ │  FastAPI Server  │ ──────▶ │    AI Agent     │
│  (Vite + JSX)   │ ◀────── │  (REST API)      │ ◀────── │  (DeepSeek LLM) │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                 │
                                                          MCP Protocol
                                                                 │
                                                        ┌────────▼────────┐
                                                        │   MCP Server    │
                                                        │  (Tool Layer)   │
                                                        └────────┬────────┘
                                                                 │
                                    ┌────────────────────────────┼────────────────────────────┐
                                    │                            │                            │
                             ┌──────▼──────┐            ┌───────▼───────┐           ┌────────▼────────┐
                             │ PostgreSQL  │            │ Google        │           │  External APIs  │
                             │ Database    │            │ Calendar API  │           │  (SendGrid,     │
                             │             │            │               │           │   Slack)         │
                             └─────────────┘            └───────────────┘           └─────────────────┘
```

The system follows an **agentic loop** pattern:
1. User sends a natural language message via the React frontend
2. FastAPI backend forwards the message to the AI Agent
3. The Agent connects to the MCP Server to discover available tools
4. The Agent sends the message + tools to DeepSeek LLM (via OpenRouter)
5. If the LLM wants to call a tool, the Agent executes it via MCP and feeds the result back
6. This loop continues until the LLM produces a final text response
7. The response is returned to the user

---

## 👤 Features — Patient Side

### 💬 Natural Language Chat Interface
- Conversational chat UI where patients can type requests in plain English
- Markdown rendering with styled tables, lists, and bold text via `react-markdown`
- Auto-scrolling message feed with a "Thinking..." loading indicator
- Session-based conversation history so the AI remembers context within a chat

### 🔍 Check Doctor Availability
- Ask for available slots with any doctor on any date (e.g., *"Is Dr. Sharma available tomorrow?"*)
- The agent queries the database and returns available time slots as a clean numbered list
- Supports fuzzy doctor name matching (case-insensitive partial match)

### 📅 Book Appointments
- Book an appointment by simply conversing with the AI (e.g., *"Book the 10 AM slot with Dr. Patel"*)
- The agent collects all required info (doctor, date, time, patient name, email, reason) through conversation
- Automatically marks the slot as booked in the database and creates an appointment record
- Handles both 12-hour (AM/PM) and 24-hour time formats

### 🔄 Smart Auto-Rescheduling
- If a requested slot is unavailable, the agent automatically finds the **next available slot** using the `get_next_available_slot` tool
- Searches the same day first, then looks ahead up to 3 days
- Suggests the alternative slot and asks the patient to confirm before booking

### 📧 Email Confirmation (SendGrid)
- After every successful booking, a professionally styled **HTML confirmation email** is automatically sent to the patient's email address
- Includes appointment details: doctor name, date, time, and reason
- Powered by the SendGrid API

### 📆 Google Calendar Integration
- Every booked appointment is automatically added as a **Google Calendar event**
- Includes email and popup reminders (24 hours before and 30 minutes before)
- Returns a direct link to the calendar event

### 📜 Prompt History Logging
- Every patient message and agent response is logged to the `prompt_history` table in the database
- Stored with session ID, role, timestamp for traceability

---

## 🩺 Features — Doctor Side

### 📊 Appointment Reports & Summaries
- Doctors can ask for appointment summaries in natural language (e.g., *"How many patients do I have today?"*)
- The agent fetches appointment stats from the database and formats them into a clear report
- Shows patient names, appointment times, reasons, and statuses

### ⚡ Quick Report Buttons
- The doctor dashboard includes pre-built quick action buttons for common queries:
  - *"How many appointments do I have today?"*
  - *"Show me Dr. Ahuja's schedule for tomorrow"*
  - *"How many appointments does Dr. Sharma have today?"*
- One-click instant reports without typing

### 🔔 Slack Notifications
- Every time a doctor requests a report, a **formatted Slack notification** is automatically sent to a configured Slack channel via webhook
- The Slack message includes:
  - Doctor name and date
  - Total appointment count
  - Full patient list with times, reasons, and statuses
- Uses Slack Block Kit for rich formatting with headers, sections, and dividers

### 💬 Conversational Dashboard
- Full chat interface for doctors to interact with the AI naturally
- Maintains conversation history per session
- Markdown-rendered responses for clean report display

### 📜 Prompt History Logging
- Doctor interactions are also logged to the `prompt_history` table
- Tagged with `role: "doctor"` for differentiation from patient logs

---

## 🛠 Tech Stack

| Layer            | Technology                                                     |
| :--------------- | :------------------------------------------------------------- |
| **Frontend**     | React 19, Vite, Axios, react-markdown                          |
| **Backend**      | Python, FastAPI, Uvicorn                                       |
| **AI / LLM**     | DeepSeek Chat v3 (via OpenRouter API)                          |
| **Tool Protocol**| Model Context Protocol (MCP) — `mcp` Python SDK               |
| **Database**     | PostgreSQL + SQLAlchemy ORM                                    |
| **Email**        | SendGrid API                                                   |
| **Calendar**     | Google Calendar API (OAuth 2.0)                                |
| **Notifications**| Slack Incoming Webhooks                                        |
| **Pkg Manager**  | uv (Python), npm (Node.js)                                    |

---

## 📁 Project Structure

```
doctor-assistant/
├── backend/
│   ├── main.py              # FastAPI server with REST endpoints
│   ├── agent.py             # AI agent with agentic loop (LLM + MCP)
│   ├── mcp_server.py        # MCP tool server (5 tools exposed)
│   ├── database.py          # SQLAlchemy models & DB connection
│   ├── seed.py              # Database seeding script with sample data
│   ├── email_service.py     # SendGrid email confirmation service
│   ├── calendar_service.py  # Google Calendar event creation
│   └── notification.py      # Slack webhook notifications
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
├── pyproject.toml            # Python project config (uv)
├── requirements.txt          # Python dependencies (pip fallback)
└── uv.lock                  # Locked dependencies (uv)
```

---

## 🚀 Setup Guide

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and **npm**
- **PostgreSQL** (running locally or remote)
- API keys for:
  - [OpenRouter](https://openrouter.ai/) (for DeepSeek LLM access)
  - [SendGrid](https://sendgrid.com/) (for email confirmations)
  - [Slack Incoming Webhook](https://api.slack.com/messaging/webhooks) (for notifications)
  - [Google Cloud Console](https://console.cloud.google.com/) (for Calendar API)

---

### 1. Install uv

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager written in Rust. It replaces `pip`, `venv`, and `pyenv` in a single tool.

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation:**
```bash
uv --version
```

> [!TIP]
> uv will automatically manage Python versions for you. If Python 3.12 isn't installed, uv will download it when you sync the project.

---

### 2. Clone the Repository

```bash
git clone https://github.com/Xtejasveer/Doctor-Assistant.git
cd Doctor-Assistant
```

---

### 3. Set Up the Backend

```bash
# Create virtual environment and install all dependencies
uv sync
```

This single command will:
- Read `pyproject.toml` and `uv.lock`
- Create a `.venv` virtual environment
- Install all Python dependencies with exact locked versions

> [!NOTE]
> If you prefer using `pip` instead of `uv`, you can do:
> ```bash
> python -m venv .venv
> .venv\Scripts\activate    # Windows
> # source .venv/bin/activate  # macOS/Linux
> pip install -r requirements.txt
> ```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/doctor_assistant
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key
SENDGRID_API_KEY=SG.your-sendgrid-api-key
SENDGRID_FROM_EMAIL=your-verified-email@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

| Variable             | Description                                           |
| :------------------- | :---------------------------------------------------- |
| `DATABASE_URL`       | PostgreSQL connection string                          |
| `OPENROUTER_API_KEY` | API key from [openrouter.ai](https://openrouter.ai/)  |
| `SENDGRID_API_KEY`   | API key from [sendgrid.com](https://sendgrid.com/)    |
| `SENDGRID_FROM_EMAIL`| Verified sender email in SendGrid                     |
| `SLACK_WEBHOOK_URL`  | Slack incoming webhook URL for notifications          |

---

### 5. Set Up PostgreSQL

1. Make sure PostgreSQL is running on your machine
2. Create the database:

```sql
CREATE DATABASE doctor_assistant;
```

> The tables are auto-created when the backend starts (via SQLAlchemy's `create_all`).

---

### 6. Set Up Google Calendar (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Google Calendar API**
4. Create **OAuth 2.0 credentials** (Desktop application type)
5. Download the credentials JSON file and save it as `backend/credentials.json`
6. Run the calendar auth flow once:

```bash
cd backend
uv run python calendar_service.py
```

This will open a browser window for Google OAuth consent. After authorizing, a `token.pickle` file will be created for future use.

> [!NOTE]
> If you skip this step, appointments will still be booked — the calendar event creation will simply fail silently.

---

### 7. Seed the Database

Populate the database with sample doctors, availability slots, and appointments:

```bash
cd backend
uv run python seed.py
```

This creates:
- **4 Doctors**: Dr. Ahuja (General Physician), Dr. Sharma (Cardiologist), Dr. Patel (Dermatologist), Dr. Mehta (Neurologist)
- **Availability slots**: 6 slots per doctor per day for the next 5 days (09:00–16:30)
- **Sample appointments**: Pre-booked appointments for yesterday, today, and tomorrow

---

### 8. Set Up the Frontend

```bash
cd frontend
npm install
```

---

### 9. Run the Application

You need **two terminals** running simultaneously:

**Terminal 1 — Backend (FastAPI server):**
```bash
cd backend
uv run uvicorn main:app --reload
```

**Terminal 2 — Frontend (Vite dev server):**
```bash
cd frontend
npm run dev
```

Now open your browser at **http://localhost:5173** and you'll see the role selection screen!

---

## 📡 API Endpoints

| Method   | Endpoint                 | Description                            |
| :------- | :----------------------- | :------------------------------------- |
| `POST`   | `/chat`                  | Send a patient message to the AI agent |
| `POST`   | `/doctor/report`         | Send a doctor message to the AI agent  |
| `GET`    | `/history/{session_id}`  | Get prompt history for a session       |
| `DELETE` | `/chat/{session_id}`     | Clear conversation history for a session|
| `GET`    | `/health`                | Health check endpoint                  |

---

## 🔧 MCP Tools

The MCP server exposes 5 tools that the AI agent can call:

| Tool                     | Description                                                    |
| :----------------------- | :------------------------------------------------------------- |
| `check_availability`     | Check available time slots for a doctor on a given date        |
| `book_appointment`       | Book an appointment (marks slot, creates record, sends email, creates calendar event) |
| `get_appointment_stats`  | Get appointment stats for a doctor on a date (+ sends Slack notification) |
| `get_all_doctors`        | List all doctors with their specializations                    |
| `get_next_available_slot`| Find the next available slot when preferred time is unavailable|


