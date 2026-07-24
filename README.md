# 🇮🇳 CM Executive Command: AI Governance Module

## 📌 Overview
This project is a specialized **Human-in-the-Loop (HITL) Governance OS** designed around the theme of a Chief Minister's State Secretariat. 

Built with the core philosophy of **Sutra OS**—*"The bill must arrive before the work"*—this application acts as an AI Chief of Staff. It intercepts executive policy decrees, scopes the fiscal impact in Crores, and forces out-of-band authorization gates before any execution can occur.

## ⚙️ Core Architecture & Enforcement Points
Rather than relying on unconstrained AI output, this system enforces strict fiscal discipline through three distinct governance tiers:

* **Tier 1 (Auto-Sanction):** Low-risk decrees under ₹500 Crores are surfaced and auto-approved.
* **Tier 2 (Inter-Ministerial Review):** Mid-tier decrees (up to ₹25,000 Crores) physically halt execution and trigger an out-of-band **Slack 2FA Webhook** for verification.
* **Tier 3 (PMO Override):** High-risk deficits exceeding ₹25,000 Crores lock down the system and force a secure **SMTP Email PIN challenge**.

## 🛡️ Key Features
* **Zero-Trust Pre-Flight Scanner:** A built-in source-code scanner that physically refuses to boot the UI if exposed API credentials are detected in the application tree.
* **Deterministic AI Execution:** API constraints (Temperature = 0.0) combined with regex sanitization guarantee consistent financial budgeting without LLM hallucination.
* **Local-First Telemetry:** Decisions do not die in scroll-back. Every execution writes to an immutable `audit_trail.jsonl` log and generates a tamper-proof PDF Executive Receipt.

## 🚀 Quick Start
1. Clone the repository:
   `git clone https://github.com/devanshshah-jpg/cm-executive-command.git`
2. Install the required dependencies:
   `pip install -r requirements.txt`
3. Configure your `.env` file with your secure API keys (DeepSeek, Slack Webhook, SMTP details).
4. Run the OS:
   `streamlit run app.py`

---
*Built to demonstrate strict AI fiscal control and approval gate mechanics.*
