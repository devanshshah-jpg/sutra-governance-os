import streamlit as st
from openai import OpenAI
import json
import time
import re

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="SUTRA OS: Presidential Command", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

# Initialize DeepSeek Client (Using OpenAI SDK format)
if "client" not in st.session_state:
    st.session_state.client = OpenAI(
        api_key="YOUR_DEEPSEEK_API_KEY", # Replace this tomorrow!
        base_url="https://api.deepseek.com"
    )

# Initialize System State
if "stage" not in st.session_state:
    st.session_state.stage = "init"
    st.session_state.logs = ["[SYS_INIT] SUTRA Governance OS Online.", "[HOOK] Core budget limits enforced."]
    st.session_state.bill_of_work = None

# --- HELPER FUNCTIONS ---
def log_event(message):
    t = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{t}] {message}")

def clean_json(raw_text):
    """Strips markdown formatting if the AI wraps the JSON in code blocks."""
    cleaned = re.sub(r'```json\s*', '', raw_text)
    cleaned = re.sub(r'```', '', cleaned)
    return cleaned.strip()

def call_deepseek(system_prompt, user_message):
    """Makes the API call to DeepSeek."""
    response = st.session_state.client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2 # Keep it analytical
    )
    return response.choices[0].message.content

# --- PROMPTS ---
CHIEF_OF_STAFF_PROMPT = """You are the Presidential Chief of Staff. 
The President has issued a decree. You must scope the project and estimate the cost.
You MUST output ONLY a valid JSON object. No other text.
Format required:
{
    "summary": "1 sentence description of the plan",
    "budget_billions": 150,
    "timeframe_years": 4,
    "departments": ["Defense", "Infrastructure"]
}"""

# --- UI DASHBOARD ---
st.title("🦅 EXECUTIVE COMMAND: SUTRA GOVERNANCE")
st.markdown("*" + "The unit of value is not a task. It’s the whole lifecycle." + "*")
st.write("---")

col_main, col_terminal = st.columns([2, 1])

# --- RIGHT COLUMN: THE SUTRA TELEMETRY (TERMINAL) ---
with col_terminal:
    st.markdown("### 📡 OS Telemetry (Local Hooks)")
    log_text = "<br>".join(st.session_state.logs[-20:]) 
    st.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
    
    if st.button("Clear Cache & Restart"):
        st.session_state.clear()
        st.rerun()

# --- LEFT COLUMN: FOUNDER/PRESIDENT UI ---
with col_main:
    
    # STAGE 1: THE VAGUE DECREE
    if st.session_state.stage == "init":
        st.markdown("### **THE PRESIDENTIAL DECREE (Vague Intent)**")
        decree = st.text_input("Enter a massive policy goal (e.g., 'Build a high-tech hospital in every city', 'Colonize the moon'):")
        
        if st.button("ISSUE DECREE", type="primary"):
            if decree:
                log_event(f"[USER] Decree issued: {decree}")
                log_event("[SUTRA_AGENT] Chief of Staff analyzing intent...")
                
                # 1. First AI Attempt
                raw_response = call_deepseek(CHIEF_OF_STAFF_PROMPT, decree)
                
                try:
                    plan = json.loads(clean_json(raw_response))
                    log_event(f"[SUTRA_AGENT] Proposed Budget: ${plan.get('budget_billions')}B")
                    
                    # 2. THE GOVERNANCE HOOK (The Magic)
                    # If the AI suggests a budget over $100B, the OS blocks it and forces a rewrite.
                    if plan.get("budget_billions", 0) > 100:
                        log_event("❌ [OS_HOOK_FATAL] Policy violation: Budget > $100B. Auto-rejecting plan.")
                        log_event("[SUTRA_AGENT] Revising plan to meet Phase 1 governance limits...")
                        
                        # Tell the AI to try again with strict limits
                        revision_prompt = f"Your previous plan cost ${plan.get('budget_billions')}B. This was REJECTED by system governance. Downscope this decree to a Phase 1 pilot program that costs exactly $50B or less. Return ONLY JSON."
                        raw_response_2 = call_deepseek(CHIEF_OF_STAFF_PROMPT, revision_prompt)
                        
                        plan = json.loads(clean_json(raw_response_2))
                        log_event(f"[OS_HOOK_PASS] Revised Phase 1 Budget accepted: ${plan.get('budget_billions')}B")
                    else:
                        log_event("✅ [OS_HOOK_PASS] Budget within limits.")
                    
                    # Save approved bill for display
                    st.session_state.bill_of_work = plan
                    st.session_state.stage = "review"
                    st.rerun()
                    
                except Exception as e:
                    log_event(f"❌ [SYS_ERROR] Agent failed to return valid JSON. Error: {e}")

    # STAGE 2: THE BILL OF WORK (APPROVAL)
    elif st.session_state.stage == "review":
        st.markdown("### **CHIEF OF STAFF: BILL OF WORK**")
        st.markdown("*Decisions stop dying in scroll-back. Review the exact cost before execution.*")
        
        bill = st.session_state.bill_of_work
        
        st.markdown(f"""
        <div class="bill-box">
            <h4>📋 Execution Blueprint</h4>
            <b>Plan:</b> {bill.get('summary')}<br><br>
            <b>💰 Estimated Cost:</b> ${bill.get('budget_billions')} Billion<br>
            <b>⏱️ Timeframe:</b> {bill.get('timeframe_years')} Years<br>
            <b>🏢 Departments Touched:</b> {', '.join(bill.get('departments', []))}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ APPROVE BILL & EXECUTE", use_container_width=True):
                log_event(f"[USER] Bill Approved. Routing to Operator for execution.")
                st.success("Execution Authorized. The Operator is now writing the code/legislation.")
                # You can reset or add a final stage here
        with col2:
            if st.button("❌ REJECT & SCRAP", use_container_width=True):
                log_event("[USER] Bill Rejected. Session terminated.")
                st.session_state.stage = "init"
                st.session_state.bill_of_work = None
                st.rerun()