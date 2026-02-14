import streamlit as st
import requests
import html

# --- CONFIGURATION ---
BACKEND_URL = "https://inboxintelligence.onrender.com"
st.set_page_config(page_title="Inbox Command Center", page_icon="⚡", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Global Dark Theme Tweaks */
    .stApp { background-color: #0E1117; }
    
    /* Metrics Box Styling */
    div[data-testid="stMetric"] {
        background-color: #262730;
        border: 1px solid #444;
        padding: 10px;
        border-radius: 8px;
    }
    
    /* Remove default expander styling for cleaner look */
    .streamlit-expanderHeader {
        background-color: #1E1E1E !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (FIXED ALIGNMENT) ---
with st.sidebar:
    st.title("⚡ Command Center")
    st.caption("v3.0 • AI-Powered Triage")
    
    st.markdown("---")
    
    # 1. Action Buttons (Aligned)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0;url={BACKEND_URL}/auth/login">', unsafe_allow_html=True)
    
    with col2:
        refresh_clicked = st.button("🔄 Sync", use_container_width=True)

    # 2. Refresh Logic (Toasts)
    if refresh_clicked:
        with st.spinner("Analyzing inbox..."):
            try:
                res = requests.get(f"{BACKEND_URL}/result", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "success":
                        st.session_state["data"] = data["categories"]
                        st.toast("Inbox successfully synced!", icon="✅")
                        st.rerun()
                    else:
                        st.warning("Please login first.")
                else:
                    st.error("Server Error.")
            except Exception:
                st.error("Backend offline.")

    st.markdown("---")
    
    # 3. Search Filter
    st.markdown("### 🔍 Filter")
    search_query = st.text_input("Search", placeholder="Sender or Subject...", label_visibility="collapsed")
    
    st.markdown("---")
    
    # 4. Footer Status
    if "data" in st.session_state:
        st.success("🟢 System Online")
    else:
        st.info("🟡 Waiting for Connection")

# --- MAIN DASHBOARD ---
if "data" not in st.session_state:
    st.markdown("## 👋 Welcome to Inbox Intelligence")
    st.info("Connect your Gmail account on the left to activate the Command Center.")
else:
    categories = st.session_state["data"]
    
    # 1. TOP METRICS
    c_urgent = len(categories.get("🚨 Action Required", []))
    c_apps = len(categories.get("⏳ Applications & Updates", []))
    c_uni = len(categories.get("🎓 University & Learning", []))
    c_promo = len(categories.get("🗑️ Promotions & Noise", []))
    
    st.markdown("### 📊 Inbox Health")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Action Items", c_urgent, delta="Do Now", delta_color="inverse")
    m2.metric("Applications", c_apps, delta="Waiting")
    m3.metric("University", c_uni)
    m4.metric("Promotions", c_promo)
    
    st.divider()

    # 2. TABS & LOGIC
    tabs = st.tabs(["🚨 Action Required", "⏳ Applications", "🎓 University", "🗑️ Promotions"])
    
    backend_keys = [
        "🚨 Action Required", 
        "⏳ Applications & Updates", 
        "🎓 University & Learning", 
        "🗑️ Promotions & Noise"
    ]

    for tab, key in zip(tabs, backend_keys):
        with tab:
            email_list = categories.get(key, [])
            
            # Search Logic
            if search_query:
                q = search_query.lower()
                email_list = [e for e in email_list if q in e['subject'].lower() or q in e['from'].lower()]
                if not email_list:
                    st.caption("No matches found.")

            if not email_list and not search_query:
                st.success("🎉 Nothing here! You're caught up.")
            
            # 3. RENDER CARDS
            for mail in email_list:
                sub = html.escape(mail.get("subject", "(No Subject)"))
                sender = html.escape(mail.get("from", "Unknown"))
                snippet = html.escape(mail.get("snippet", ""))
                count = mail.get("sender_count", 1)
                msg_id = mail.get("id", "")
                
                # Dynamic Icon
                if "Action" in key: icon = "🔴"
                elif "Applications" in key: icon = "🟠"
                elif "University" in key: icon = "🔵"
                else: icon = "📓"

                count_str = f"({count})" if count > 1 else ""

                # Clean Header String
                header_text = f"{icon} {sender} {count_str} | {sub}"
                
                with st.expander(header_text):
                    st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <span style="font-size: 1.2em; font-weight: bold; color: white;">{sub}</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <span style="background: #333; padding: 2px 8px; border-radius: 4px; color: #bbb; font-size: 0.8em;">From: {sender}</span>
                        <span style="background: #333; padding: 2px 8px; border-radius: 4px; color: #bbb; font-size: 0.8em;">{key}</span>
                    </div>
                    <div style="color: #ccc; font-style: italic; border-left: 2px solid #555; padding-left: 10px; margin-bottom: 15px;">
                        "{snippet}..."
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Native Buttons
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        if msg_id:
                            link = f"https://mail.google.com/mail/u/0/#inbox/{msg_id}"
                            st.link_button("↗ Open Gmail", link)
                        else:
                            st.button("View", key=f"btn_{msg_id}")