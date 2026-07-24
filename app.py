import streamlit as st
from openai import OpenAI
import json
import time
import re
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import base64
import requests
from fpdf import FPDF
from dotenv import load_dotenv

# Load environment variables from the hidden .env file
load_dotenv()

# --- SECRETS & CREDENTIALS (Loaded securely) ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GMAIL_ADDRESS = "devshahnirja@gmail.com"
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD") 
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="SUTRA OS: CM Secretariat Command", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .terminal-box {
        background-color: #000000;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #333;
        height: 400px;
        overflow-y: auto;
        font-size: 0.85em;
    }
    .bill-box { background-color: #1a202c; padding: 20px; border-left: 5px solid #d69e2e; border-radius: 5px; margin-bottom: 20px;}
    .stTextInput label p, .stNumberInput label p {
        color: #ffffff !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- TRUE SECURITY GUARDRAIL HOOK (SOURCE SCANNER) ---
def run_security_preflight():
    # 1. Check if keys even exist in the environment
    if not all([DEEPSEEK_API_KEY, GMAIL_APP_PASSWORD, SLACK_WEBHOOK_URL]):
        return False, "Missing credentials in .env file. The system cannot boot."
    
    # 2. Source Code Scanner: Check if the user hardcoded keys directly into this python file
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        # Regex hunts for someone defining a variable and assigning it a raw API string
        if re.search(r'DEEPSEEK_API_KEY\s*=\s*["\']sk-[a-zA-Z0-9]+["\']', source_code):
            return False, "CRITICAL: Hardcoded DeepSeek API key detected in source code. Move to .env file immediately."
        if re.search(r'GMAIL_APP_PASSWORD\s*=\s*["\'][a-zA-Z\s]{10,}["\']', source_code):
            return False, "CRITICAL: Hardcoded Gmail password detected in source code."
        if re.search(r'SLACK_WEBHOOK_URL\s*=\s*["\']https://hooks\.slack\.com.+["\']', source_code):
            return False, "CRITICAL: Hardcoded Slack webhook detected in source code."
            
    except Exception as e:
        return False, f"Pre-flight file scan failed: {e}"

    return True, "Environment secured. Zero hardcoded secrets detected in source tree."

# --- SYSTEM STATE INITIALIZATION ---
if "stage" not in st.session_state:
    st.session_state.stage = "setup" 
    st.session_state.logs = ["[SYS_INIT] SUTRA Governance OS (India Module) Online.", "[HOOK] State fiscal limits enforced.", "[TELEMETRY] Local JSONL logger active."]
    st.session_state.bill_of_work = None
    st.session_state.pending_plan = None
    st.session_state.auto_download_triggered = False
    st.session_state.treasury_balance = 0
    st.session_state.approved_bills = []
    st.session_state.slack_pin = None

# --- TERMINAL TELEMETRY SETUP ---
col_main, col_terminal = st.columns([2, 1])

with col_terminal:
    st.markdown("### 📡 OS Telemetry (Local Hooks)")
    terminal_placeholder = st.empty() 
    
    if st.button("Clear Cache & Restart OS"):
        st.session_state.clear()
        st.rerun()

def update_terminal(new_log=None):
    if new_log:
        t = time.strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{t}] {new_log}")
    log_text = "<br>".join(st.session_state.logs[-20:])
    terminal_placeholder.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)

update_terminal()

# --- PRE-FLIGHT EXECUTION ---
is_secure, security_msg = run_security_preflight()

if not is_secure:
    with col_main:
        st.error("🚨 **FATAL SECURITY HALT**")
        st.warning("The OS cannot boot. Architecture policy violation detected.")
        st.code(security_msg, language="bash")
        st.info("Fix: Remove hardcoded strings from app.py and rely strictly on the .env file.")
        
    if f"❌ [FATAL_SECURITY_HALT] {security_msg}" not in st.session_state.logs:
        update_terminal(f"❌ [FATAL_SECURITY_HALT] {security_msg}")
    st.stop() 

# --- SAFE BOOT: INITIALIZE AI CLIENT ---
if "client" not in st.session_state:
    try:
        st.session_state.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        if "[SYS_SECURITY] Environment verified." not in st.session_state.logs:
            update_terminal("[SYS_SECURITY] Environment verified.")
    except Exception as e:
        st.error(f"Failed to connect: {e}")

# --- SIDEBAR: STATE DEVELOPMENT FUND & AUDIT LEDGER ---
with st.sidebar:
    st.header("🏛️ STATE DEVELOPMENT FUND")
    if st.session_state.stage == "setup":
        st.info("Awaiting financial allocation...")
    else:
        st.metric(label="Available State Treasury", value=f"₹{st.session_state.treasury_balance:,.2f} Cr")
        st.divider()
        st.markdown("### 📜 Secretariat Master Ledger")
        if not st.session_state.approved_bills:
            st.write("No state decrees executed yet.")
        else:
            ledger_text = "SUTRA OS - STATE FISCAL AUDIT LEDGER\n"
            ledger_text += "="*45 + "\n\n"
            for idx, bill in enumerate(st.session_state.approved_bills):
                ledger_text += f"[{idx+1}] {bill.get('summary')}\n"
                ledger_text += f"    Allocation: ₹{bill.get('budget_crores')} Cr | Depts: {', '.join(bill.get('departments', []))}\n\n"
            
            st.download_button(
                label="📥 DOWNLOAD AUDIT LEDGER (.TXT)",
                data=ledger_text,
                file_name=f"STATE_LEDGER_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True
            )

# --- HELPER FUNCTIONS ---
def write_audit_log(event_type, details):
    log_entry = {"timestamp": datetime.now().isoformat(), "event": event_type, "details": details}
    with open("audit_trail.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def clean_json(raw_text):
    cleaned = re.sub(r'```json\s*', '', raw_text)
    return re.sub(r'```', '', cleaned).strip()

def call_deepseek(system_prompt, user_message):
    try:
        response = st.session_state.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            temperature=0.0,
            seed=42
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API_ERROR: {str(e)}"

def send_slack_alert(webhook_url, message_text, is_refill=False):
    if not webhook_url: return False, "No webhook URL configured."
    header_text = "🚨 UNION CABINET / e-OFFICE REFILL REQUEST" if is_refill else "⚠️ NIC e-OFFICE INTER-MINISTERIAL ALERT"
    payload = {
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": header_text, "emoji": True}},
            {"type": "section", "text": {"type": "mrkdwn", "text": message_text}}
        ]
    }
    try:
        res = requests.post(webhook_url, json=payload)
        return (True, "Success") if res.status_code == 200 else (False, f"HTTP {res.status_code}")
    except Exception as e: return False, str(e)

def send_auth_email(manager_email, subject, body_text):
    secure_pin = str(random.randint(100000, 999999))
    msg = MIMEMultipart()
    msg['From'] = "SUTRA GOVERNANCE OS (PMO PORTAL)"
    msg['To'] = manager_email
    msg['Subject'] = subject
    
    full_body = f"[SECURE PMO TRANSMISSION]\n\n{body_text}\n\nUNION CABINET AUTHORIZATION PIN: {secure_pin}"
    msg.attach(MIMEText(full_body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, manager_email, msg.as_string())
        server.quit()
        return secure_pin, True
    except Exception as e:
        return str(e), False

def generate_executive_brief_pdf(plan, auth_pin="N/A"):
    class PDF(FPDF):
        def header(self):
            self.set_font("Courier", 'B', 16)
            self.cell(0, 10, "GOVERNMENT OF INDIA - SUTRA OS", border=0, ln=1, align="C")
            self.set_font("Courier", 'I', 10)
            self.cell(0, 10, "STATE SECRETARIAT - OFFICIAL CABINET BRIEFING", border=0, ln=1, align="C")
            self.line(10, 30, 200, 30)
            self.ln(10)
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    pdf.cell(0, 6, txt=f"TIMESTAMP    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", ln=1)
    pdf.cell(0, 6, txt=f"AUTH PIN USED: {auth_pin}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="POLICY DECREE BLUEPRINT", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, txt=f"Summary: {plan.get('summary', 'N/A')}\nAllocation: INR {plan.get('budget_crores', 0)} Crores\nTimeframe: {plan.get('timeframe_years', 0)} Years\nDepartments Mobilized: {', '.join(plan.get('departments', []))}")
    return bytes(pdf.output())

# --- COMMAND INTERFACE LOGIC ---
with col_main:
    st.title("🇮🇳 CM EXECUTIVE COMMAND: SUTRA GOVERNANCE")
    st.markdown("*" + "Good governance is measured by last-mile delivery and absolute fiscal transparency." + "*")
    st.write("---")

    # --- STAGE: INITIAL SETUP ---
    if st.session_state.stage == "setup":
        st.markdown("### **ALLOCATE STATE DEVELOPMENT FUND**")
        st.info("Define the initial State Treasury capital in Crores for this administrative cycle.")
        
        start_budget = st.number_input("Starting Treasury Budget (in ₹ Crores):", min_value=100, max_value=100000, value=10000, step=500)
        
        if st.button("INITIALIZE SECRETARIAT OS", type="primary"):
            st.session_state.treasury_balance = float(start_budget)
            st.session_state.stage = "init"
            update_terminal(f"[SYS] State Development Fund initialized with ₹{start_budget:,.2f} Cr.")
            write_audit_log("SYS_BOOT", f"Treasury initialized with ₹{start_budget:,.2f} Cr.")
            st.rerun()
    

    # --- STAGE: DECREE INPUT ---
    elif st.session_state.stage == "init":
        st.markdown("### **STATE CABINET POLICY DECREE**")
        decree = st.text_input("Enter a state policy goal:")
        
        # UI ADDITION: Quick Launch Idea Box
        with st.expander("💡 Quick Access: Sample Cabinet Decrees"):
            st.markdown("""
            * **Tier 1 (Auto-Approve):** `Deploy digital learning kiosks and solar panels in 50 rural government schools.`
            * **Tier 2 (NIC e-Office Alert):** `Upgrade the state's entire public transit fleet to autonomous electric vehicles and build 500 charging stations.`
            * **Tier 3 (PMO Override):** `Construct a high-speed underground bullet train network connecting all major state districts.`
            * **Easter Egg:** `Build a state-funded Willy Wonka Chocolate Factory with a real chocolate river and import Oompa Loompas.`
            """)
        
        CHIEF_OF_STAFF_PROMPT = """You are the Principal Secretary to the Chief Minister. 
The Chief Minister has issued a policy decree. You must scope the project and estimate the cost in Indian Rupees (INR) in CRORES.

CRITICAL INSTRUCTIONS FOR COST ESTIMATION:
1. Perform a structured, educated estimate based on realistic government infrastructure and public policy benchmarks in India.
2. Consider standard unit economics (e.g., land acquisition, material costs, labor, state-wide deployment scales, and technology infrastructure).
3. BE DETERMINISTIC & CONSISTENT: For the same input decree, always apply the exact same formula and arrive at the exact same budget. Do not randomize or drastically fluctuate the numbers across identical requests.

You MUST output ONLY a valid JSON object. No markdown formatting. No other text.
Format required:
{
    "summary": "1 sentence description of the plan",
    "budget_crores": 150,
    "timeframe_years": 4,
    "departments": ["Public Works Department", "Finance"]
}"""
        if st.button("ISSUE DECREE", type="primary"):
            if decree:
                update_terminal(f"[USER] Decree issued: {decree}")
                update_terminal("[PRINCIPAL_SECRETARY] Scoping state fiscal impact...")
                
                raw_response = call_deepseek(CHIEF_OF_STAFF_PROMPT, decree)
                if raw_response.startswith("API_ERROR:"):
                    update_terminal(f"❌ [SYS_FATAL] {raw_response}")
                else:
                    try:
                        plan = json.loads(clean_json(raw_response))
                        budget = float(plan.get("budget_crores", 0))
                        update_terminal(f"[PRINCIPAL_SECRETARY] Estimated Outlay: ₹{budget} Cr")
                        write_audit_log("DECREE_SCOPED", f"Target: {decree} | Estimated Cost: ₹{budget} Cr")
                        
                        if budget > st.session_state.treasury_balance:
                            update_terminal(f"❌ [TREASURY_HALT] Insufficient funds. Need ₹{budget} Cr, only have ₹{st.session_state.treasury_balance} Cr.")
                            st.session_state.pending_plan = plan
                            st.session_state.stage = "deficit"
                            st.rerun()
                        
                        elif budget > 25000:
                            update_terminal("⚠️ [HOOK_ESCALATION] High Fiscal Risk (> ₹25,000 Cr). PMO Cabinet Override required.")
                            st.session_state.pending_plan = plan
                            st.session_state.stage = "tier3_confirm"
                            st.rerun()
                        elif budget >= 500 and budget <= 25000:
                            update_terminal("⚠️ [HOOK_ESCALATION] Mid-Tier Fiscal Limit Reached. Dispatching NIC e-Office PIN challenge...")
                            
                            gen_slack_pin = str(random.randint(1000, 9999))
                            slack_msg = f"*Policy Decree:* {plan.get('summary')}\n*Outlay:* ₹{budget} Cr\n\n*NIC Verification PIN:* `{gen_slack_pin}`\n_Provide this code to the CM Secretariat terminal to authorize execution._"
                            
                            success, msg = send_slack_alert(SLACK_WEBHOOK_URL, slack_msg)
                            if success: 
                                update_terminal("✅ [NIC_PORTAL] Challenge PIN broadcasted successfully.")
                                
                            st.session_state.slack_pin = gen_slack_pin
                            st.session_state.pending_plan = plan
                            st.session_state.stage = "tier2_slack"
                            st.rerun()
                        else:
                            update_terminal("✅ [OS_HOOK_PASS] Outlay within standard state discretionary limits (< ₹500 Cr).")
                            st.session_state.bill_of_work = plan
                            st.session_state.stage = "review"
                            st.rerun()
                    except Exception as e:
                        update_terminal(f"❌ [SYS_ERROR] JSON Failed: {raw_response}")

    # --- STAGE: TREASURY DEFICIT ---
    elif st.session_state.stage == "deficit":
        st.markdown("### **🛑 STATE DEVELOPMENT FUND DEPLETED**")
        plan = st.session_state.pending_plan
        budget = float(plan.get("budget_crores", 0))
        shortfall = budget - st.session_state.treasury_balance
        
        st.error(f"This policy requires **₹{budget:,.2f} Crores**, but the State Treasury only has **₹{st.session_state.treasury_balance:,.2f} Crores** remaining (Deficit Shortfall: ₹{shortfall:,.2f} Cr).")
        
        # DYNAMIC FIX: Asking for the exact shortfall
        st.info(f"Request a Central Grant / Special Assistance Capital Injection of ₹{shortfall:,.2f} Crores from the Union Ministry of Finance.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 REQUEST CENTRAL GRANT (EMAIL)", use_container_width=True, type="primary"):
                update_terminal("[SYS] Dispatching Central Assistance request to Union Finance Ministry...")
                # DYNAMIC FIX: Email text uses shortfall
                gen_pin, success = send_auth_email("devshahnirja@gmail.com", "⚠️ URGENT: Central Grant Allocation Required", f"State Secretariat requires an emergency capital injection of ₹{shortfall:,.2f} Crores to fund policy decree:\n\nDecree: {plan.get('summary')}")
                if success:
                    st.session_state.auth_pin = gen_pin
                    st.session_state.stage = "refill_auth"
                    update_terminal("[SYS] Union Ministry authorization email sent.")
                    st.rerun()
        with col2:
            if st.button("💬 ALERT NIC e-OFFICE", use_container_width=True):
                # DYNAMIC FIX: Slack text uses shortfall
                send_slack_alert(SLACK_WEBHOOK_URL, f"State Treasury halted due to insufficient funds for policy:\n*Decree:* {plan.get('summary')}\n\n*Required:* ₹{budget:,.2f} Cr | *Shortfall:* ₹{shortfall:,.2f} Cr\n\n*Action Required:* Authorize ₹{shortfall:,.2f} Cr Grant.", is_refill=True)
                update_terminal("[SYS] Central Grant challenge logged on NIC e-Office.")
        with col3:
            if st.button("❌ SCRAP DECREE", use_container_width=True):
                st.session_state.stage = "init"
                st.session_state.pending_plan = None
                st.rerun()

    # --- STAGE: REFILL AUTHORIZATION ---
    elif st.session_state.stage == "refill_auth":
        # DYNAMIC FIX: Calculate the shortfall at the top of the auth screen
        budget = float(st.session_state.pending_plan.get("budget_crores", 0))
        shortfall = budget - st.session_state.treasury_balance
        
        st.markdown("### **💰 CENTRAL ASSISTANCE INJECTION AUTHORIZATION**")
        st.warning(f"Enter the 6-digit Union Finance Ministry PIN sent to your email to authorize a ₹{shortfall:,.2f} Crore state capital credit.")
        user_pin = st.text_input("Enter 6-Digit PIN:", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("AUTHORIZE STATE CREDIT", type="primary", use_container_width=True):
                if user_pin == st.session_state.auth_pin:
                    # DYNAMIC FIX: Add the exact shortfall to the treasury
                    st.session_state.treasury_balance += shortfall
                    update_terminal(f"✅ [CREDIT SUCCESS] ₹{shortfall:,.2f} Cr Central Grant credited to State Treasury.")
                    
                    if budget > st.session_state.treasury_balance:
                        st.session_state.stage = "deficit"
                    elif budget > 25000:
                        st.session_state.stage = "tier3_confirm"
                    elif budget >= 500 and budget <= 25000:
                        gen_slack_pin = str(random.randint(1000, 9999))
                        slack_msg = f"*Policy Decree:* {st.session_state.pending_plan.get('summary')}\n*Outlay:* ₹{budget} Cr\n\n*NIC Verification PIN:* `{gen_slack_pin}`\n_Provide this code to the CM Secretariat terminal to authorize execution._"
                        success, msg = send_slack_alert(SLACK_WEBHOOK_URL, slack_msg)
                        st.session_state.slack_pin = gen_slack_pin
                        st.session_state.stage = "tier2_slack"
                    else:
                        st.session_state.stage = "review"
                    st.rerun()
                else:
                    st.error("Invalid Union PIN.")
        with col2:
            if st.button("❌ CANCEL REQUEST", use_container_width=True):
                update_terminal("❌ [OPERATION_CANCELLED] Grant request aborted.")
                st.session_state.stage = "init"
                st.session_state.pending_plan = None
                st.rerun()

    # --- STAGE: TIER 2 SLACK ---
    elif st.session_state.stage == "tier2_slack":
        st.markdown("### **⚠️ MID-TIER POLICY REVIEW (TIER 2 - ₹500 Cr to ₹25,000 Cr)**")
        st.warning(f"This policy requires ₹{st.session_state.pending_plan.get('budget_crores')} Crores. A verification PIN has been dispatched to the NIC e-Office channel.")
        
        user_slack_pin = st.text_input("Enter 4-Digit NIC Verification PIN:", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("VERIFY NIC PIN", type="primary", use_container_width=True):
                if user_slack_pin == st.session_state.slack_pin:
                    st.session_state.bill_of_work = st.session_state.pending_plan
                    st.session_state.auth_pin = st.session_state.slack_pin
                    st.session_state.stage = "review"
                    update_terminal("✅ [AUTH_SUCCESS] NIC e-Office Verification accepted.")
                    st.rerun()
                else:
                    st.error("Invalid NIC PIN.")
                    update_terminal("❌ [AUTH_FAIL] Incorrect NIC PIN entered.")
        with col2:
            if st.button("❌ ABORT POLICY", use_container_width=True):
                update_terminal("❌ [OPERATION_CANCELLED] Policy aborted.")
                st.session_state.stage = "init"
                st.session_state.pending_plan = None
                st.session_state.slack_pin = None
                st.rerun()

    # --- STAGE: TIER 3 EMAIL CONFIRM ---
    elif st.session_state.stage == "tier3_confirm":
        st.markdown("### **🛑 HIGH-RISK FISCAL LIMIT EXCEEDED (TIER 3 - > ₹25,000 Cr)**")
        plan = st.session_state.pending_plan
        st.error(f"Outlay: ₹{plan.get('budget_crores')} Crores exceeds state autonomous limits. PMO Union Cabinet override required.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📧 REQUEST PMO CABINET OVERRIDE", type="primary", use_container_width=True):
                update_terminal("[SYS] Transmitting secure cabinet file to PMO...")
                gen_pin, success = send_auth_email("devshahnirja@gmail.com", "⚠️ ACTION REQUIRED: PMO Union Cabinet Policy Override", f"Policy Decree: {plan.get('summary')}\nOutlay: ₹{plan.get('budget_crores')} Cr")
                if success:
                    st.session_state.auth_pin = gen_pin
                    st.session_state.stage = "tier3_auth"
                    update_terminal("[SYS] PMO authorization dispatch complete.")
                    st.rerun()
        with col2:
            if st.button("❌ CANCEL OPERATION", use_container_width=True):
                update_terminal("❌ [OPERATION_CANCELLED] Cabinet escalation dropped.")
                st.session_state.stage = "init"
                st.session_state.pending_plan = None
                st.rerun()

    # --- STAGE: TIER 3 EMAIL AUTH ---
    elif st.session_state.stage == "tier3_auth":
        st.markdown("### **🛑 PMO CABINET OVERRIDE REQUIRED**")
        st.warning("Secure file transmitted! Check your email for the 6-digit PMO Cabinet PIN.")
        user_pin = st.text_input("Enter 6-Digit PMO PIN:", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("VERIFY PMO PIN", type="primary", use_container_width=True):
                if user_pin == st.session_state.auth_pin:
                    st.session_state.bill_of_work = st.session_state.pending_plan
                    st.session_state.stage = "review"
                    update_terminal("✅ [AUTH_SUCCESS] PMO Cabinet Override accepted.")
                    st.rerun()
                else: 
                    st.error("Invalid PMO PIN.")
        with col2:
            if st.button("❌ CANCEL OPERATION", use_container_width=True):
                update_terminal("❌ [AUTH_CANCELLED] Operation aborted by user.")
                st.session_state.stage = "init"
                st.session_state.pending_plan = None
                st.rerun()

    # --- STAGE: FINAL REVIEW ---
    elif st.session_state.stage == "review":
        st.markdown("### **PRINCIPAL SECRETARY: FINAL BILL OF WORK**")
        bill = st.session_state.bill_of_work
        st.markdown(f"<div class='bill-box'><b>{bill.get('summary')}</b><br>Outlay: ₹{bill.get('budget_crores')} Cr | Timeframe: {bill.get('timeframe_years')} Yrs</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ SANCTION & DEDUCT FROM TREASURY", use_container_width=True):
                st.session_state.treasury_balance -= float(bill.get('budget_crores', 0))
                st.session_state.approved_bills.append(bill)
                
                update_terminal("[USER] Policy sanctioned. Treasury deducted.")
                write_audit_log("FUNDS_DISBURSED", f"Sanctioned: {bill.get('summary')} | Outlay: ₹{bill.get('budget_crores')} Cr")
                st.session_state.stage = "approved"
                st.session_state.auto_download_triggered = False
                st.rerun()
        with col2:
            if st.button("❌ SCRAP BILL", use_container_width=True):
                update_terminal("[USER] Policy Sanction Rejected.")
                st.session_state.stage = "init"
                st.session_state.bill_of_work = None
                st.rerun()

    # --- STAGE: APPROVED & PDF ---
    elif st.session_state.stage == "approved":
        st.markdown("### **✅ POLICY SANCTION AUTHORIZED**")
        st.success("State Treasury updated. Official Secretariat Briefing downloading automatically.")
        
        bill = st.session_state.bill_of_work
        if not st.session_state.auto_download_triggered:
            pdf_bytes = generate_executive_brief_pdf(bill, st.session_state.get("auth_pin", "AUTO-APPROVED"))
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            file_name = f"SECRETARIAT_BRIEF_{int(time.time())}.pdf"
            
            st.components.v1.html(f"<script>const a=document.createElement('a');a.href='data:application/pdf;base64,{b64_pdf}';a.download='{file_name}';a.click();</script>", height=0)
            st.session_state.auto_download_triggered = True 
            st.download_button("📄 MANUAL DOWNLOAD", data=pdf_bytes, file_name=file_name, mime="application/pdf")

        if st.button("🔄 RETURN TO SECRETARIAT TERMINAL", type="primary"):
            st.session_state.stage = "init"
            st.session_state.bill_of_work = None
            st.session_state.pending_plan = None
            st.session_state.auto_download_triggered = False
            st.rerun()