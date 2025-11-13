# 📧 Agent Mail Automation System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## 🧩 Overview

**Agent Mail Automation System** is an intelligent email automation tool that monitors your mailbox in real time, classifies incoming emails using **GenAI (OpenAI)**, and generates AI-based response drafts for approval before sending.

It streamlines the process of managing and replying to emails, ensuring only relevant responses are automatically approved and sent.

---

## 🚀 Features

✅ **IMAP Mail Monitoring** — Continuously checks your inbox for new unseen emails.  
🤖 **AI-Based Classification** — Uses OpenAI to categorize mail as:  
   - `Work Related`  
   - `Personal`  
   - `General`  
   - `Spam`  
🧠 **Smart Response Generation** — Auto-generates reply content using an API for relevant emails.  
📩 **Approval Workflow** — Approver receives a mail to confirm the reply:  
   - Reply `"Yes"` → System sends the response to the sender.  
   - Reply `"No"` → Response is ignored.  
📂 **File Storage** — All generated responses and logs are saved locally.

---

## 🧠 Tech Stack

| Component | Description |
|------------|-------------|
| **Language** | Python |
| **AI Engine** | OpenAI (GenAI) |
| **Email Access** | IMAP |
| **Core Libraries** | `imaplib`, `email`, `openai`, `uuid`, `json`, `os` |
| **Storage** | Local file-based (in `/data` folder) |
| **Workflow** | Event-driven with approval control |

---

## 🗂️ Project Structure

```
agent_mail_automation/
│
├── main.py                      # Entry point for email monitoring
│
├── models/
│   └── mail_classification.py   # Classifies emails using OpenAI
│
├── utils/
│   ├── fetch_unseen_mail.py     # Fetches new unseen mails via IMAP
│   ├── request_mail_approval.py # Sends approval request to approver
│   ├── check_approval.py        # Checks for approval replies
│   └── send_response.py         # Sends approved responses
│
├── data/
│   └── responses/               # Stores generated response drafts
│
└── README.md                    # Project documentation
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/agent-mail-automation.git
cd agent-mail-automation
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment
Create a `.env` file in the root directory:

```
IMAP_HOST=imap.yourmail.com
IMAP_USER=your_email@example.com
IMAP_PASS=your_password
OPENAI_API_KEY=your_openai_api_key
APPROVER_EMAIL=approver@example.com
```

## 📬 Example Flow

1. A new mail arrives → fetched using IMAP.  
2. AI classifies it as **Work Related**.  
3. System generates a response draft and saves it.  
4. Approver receives an email with subject `[APPROVAL REQUIRED]`.  
5. Approver replies `"Yes"` → system sends the response to the sender.  
6. Approver replies `"No"` or doesn’t respond → ignored.

---

## 🔒 Notes & Best Practices

- Only **unseen** (`UNSEEN`) mails are processed.
- Processed mails can be marked as **seen** to prevent duplicates.
- Each mail is tagged with a **UUID** for tracking approvals.
- Approval replies are validated with regex for matching mail IDs.

---

## 🧭 Future Enhancements

- 🌐 Gmail / Outlook API Integration (FastAPI / Flask) 
- 📊 Tool calling (API Integaration)
- 🗃️ Database Support (PostgreSQL / SQLite)  
- 👥 Multi-level Approval Flow  
- 🧾 Logging & Analytics via Web UI  

