import streamlit as st
import os
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Traveling Panda | AI Travel Concierge",
    page_icon="🐼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Saved Plans Helper ───────────────────────────────────────────────────────
SAVED_PLANS_FILE = "e:/Antigravity/outputs/saved_plans.json"

def load_saved_plans():
    if os.path.exists(SAVED_PLANS_FILE):
        try:
            with open(SAVED_PLANS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_plan_entry(destination, answers, itinerary, gallery=None):
    plans = load_saved_plans()
    entry = {
        "id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "destination": destination,
        "date": datetime.datetime.now().strftime("%b %d, %Y"),
        "answers": answers,
        "itinerary": itinerary,
        "gallery": gallery or {}
    }
    plans.insert(0, entry)
    os.makedirs(os.path.dirname(SAVED_PLANS_FILE), exist_ok=True)
    with open(SAVED_PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, indent=2, ensure_ascii=False)

def delete_plan_entry(plan_id):
    plans = load_saved_plans()
    plans = [p for p in plans if p.get("id") != plan_id]
    os.makedirs(os.path.dirname(SAVED_PLANS_FILE), exist_ok=True)
    with open(SAVED_PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, indent=2, ensure_ascii=False)

def clear_all_plans():
    if os.path.exists(SAVED_PLANS_FILE):
        try:
            os.remove(SAVED_PLANS_FILE)
        except Exception:
            pass

# ─── Fresh Light & Airy Modern UI CSS ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    color: #0f172a;
}

/* Background */
.stApp {
    background-color: #f8fafc;
    background-image: 
        radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.06) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.06) 0px, transparent 50%);
}

/* Header Banner */
.fresh-hero-header {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.fresh-title-box {
    display: flex;
    align-items: center;
    gap: 16px;
}

.fresh-avatar-badge {
    width: 52px;
    height: 52px;
    background: linear-gradient(135deg, #10b981, #059669);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.25);
}

.fresh-main-text h1 {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
    letter-spacing: -0.4px;
}

.fresh-main-text p {
    font-size: 0.9rem;
    color: #64748b;
    margin: 2px 0 0 0;
}

.fresh-badge {
    background: #e6f4ea;
    color: #16a34a;
    border: 1px solid #b7ebc6;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

.new-chat-btn button {
    background: #0f172a !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 10px 16px !important;
    width: 100%;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
}

.new-chat-btn button:hover {
    background: #334155 !important;
}

.history-section-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin: 22px 0 12px 0;
}

.history-item button {
    background: #f8fafc !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    text-align: left !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    width: 100% !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

.history-item button:hover {
    background: #e2e8f0 !important;
    color: #0f172a !important;
}

/* Chat Messages */
.chat-panda-row {
    display: flex;
    gap: 14px;
    margin-bottom: 20px;
    align-items: flex-start;
}

.chat-user-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
}

.panda-avatar-box {
    width: 42px;
    height: 42px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.panda-bubble {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #10b981;
    border-radius: 4px 16px 16px 16px;
    padding: 16px 20px;
    color: #0f172a;
    font-size: 0.96rem;
    line-height: 1.6;
    max-width: 82%;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.user-bubble {
    background: linear-gradient(135deg, #10b981, #059669);
    border-radius: 16px 16px 4px 16px;
    padding: 14px 20px;
    color: #ffffff;
    font-size: 0.96rem;
    font-weight: 500;
    max-width: 75%;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.2);
}

/* Typing Form & Input Bar */
div[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 14px !important;
    padding: 8px 14px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
}

div[data-baseweb="input"] {
    background-color: transparent !important;
    border: none !important;
    color: #0f172a !important;
}

div[data-testid="stFormSubmitButton"] > button {
    background: #0f172a !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 9px 22px !important;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    background: #334155 !important;
}

/* Choice Chips Styling */
div[data-testid="column"] button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}

div[data-testid="column"] button:hover {
    background: #f1f5f9 !important;
    border-color: #10b981 !important;
    color: #059669 !important;
}

/* Itinerary Box */
.itinerary-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 28px;
    color: #0f172a;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

/* Metric Display Cards */
.metric-pill {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.metric-val {
    font-size: 1.1rem;
    font-weight: 700;
    color: #10b981;
}
.metric-lbl {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="stDownloadButton"] > button {
    background: #0f172a !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px 24px !important;
    font-size: 0.95rem !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="fresh-hero-header">
    <div class="fresh-title-box">
        <div class="fresh-avatar-badge">🐼</div>
        <div class="fresh-main-text">
            <h1>Traveling Panda Agent</h1>
            <p>Your Intelligent AI Travel Concierge & Custom Planner</p>
        </div>
    </div>
    <div class="fresh-badge">✨ Live Concierge</div>
</div>
""", unsafe_allow_html=True)

# ─── Session State Init ───────────────────────────────────────────────────────
if "chat_history"    not in st.session_state: st.session_state.chat_history    = []
if "answers"         not in st.session_state: st.session_state.answers         = {}
if "question_index"  not in st.session_state: st.session_state.question_index  = 0
if "phase"           not in st.session_state: st.session_state.phase           = "chat"   # chat | itinerary
if "itinerary"       not in st.session_state: st.session_state.itinerary       = None
if "gallery"         not in st.session_state: st.session_state.gallery         = {}
if "started"         not in st.session_state: st.session_state.started         = False

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("➕ New Plan", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    saved_plans = load_saved_plans()
    if saved_plans:
        st.markdown('<div class="history-section-title">Recent Plans</div>', unsafe_allow_html=True)
        for plan in saved_plans[:12]:
            dest_name = plan.get("destination", "Trip Plan").title()
            date_str  = plan.get("date", "")
            btn_label = f"🗺️ {dest_name} ({date_str})"
            
            c_plan, c_del = st.columns([5, 1])
            with c_plan:
                st.markdown('<div class="history-item">', unsafe_allow_html=True)
                if st.button(btn_label, key=f"plan_{plan['id']}", use_container_width=True):
                    st.session_state.answers   = plan.get("answers", {})
                    st.session_state.itinerary = plan.get("itinerary", "")
                    st.session_state.gallery   = plan.get("gallery", {})
                    st.session_state.phase     = "itinerary"
                    st.session_state.started   = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c_del:
                if st.button("🗑️", key=f"del_{plan['id']}", help="Delete this plan"):
                    delete_plan_entry(plan['id'])
                    st.rerun()

        if len(saved_plans) > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear All Plans", key="clear_all_plans_btn", use_container_width=True):
                clear_all_plans()
                st.rerun()
    else:
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-top: 18px; color: #334155; font-size: 0.86rem; line-height: 1.6;">
            <b style="color:#10b981; font-size:0.92rem;">✨ Welcome to Panda Planner!</b><br><br>
            📍 <b>Origin City Support</b><br>
            🗺️ <b>Direct Google Maps Links</b><br>
            📸 <b>Real Place & Hotel Photos</b><br>
            📝 <b>Word, PDF & JPG Exports</b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="color: #0f172a; font-size: 0.95rem; font-weight: 700; text-align: center; margin-top: 12px; letter-spacing: 0.5px;">Traveling Panda 🐼</div>', unsafe_allow_html=True)

# ─── Import Chat & Services ───────────────────────────────────────────────────
from backend.chat_agent import QUESTIONS, get_total_questions, generate_itinerary
from backend.image_service import fetch_trip_gallery
from backend.export_service import export_to_pdf, export_to_jpg, export_to_docx

TOTAL_Q = get_total_questions()

# ─── Helper: Render Chat History ──────────────────────────────────────────────
def render_chat():
    for msg in st.session_state.chat_history:
        if msg["role"] == "panda":
            clean_content = msg["content"].replace("When are you planning to travel, and for how long?", "What are your travel dates?")
            st.markdown(f"""
            <div class="chat-panda-row">
                <div class="panda-avatar-box">🐼</div>
                <div class="panda-bubble">{clean_content}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-user-row">
                <div class="user-bubble">{msg["content"]}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ─── PHASE 1: CHAT CONVERSATION WITH INTERACTIVE CHIPS ────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.phase == "chat":

    if not st.session_state.started:
        first_q = QUESTIONS[0]
        content = first_q["panda_func"]() if "panda_func" in first_q else first_q["panda"]
        st.session_state.chat_history.append({
            "role": "panda",
            "content": content
        })
        st.session_state.started = True

    render_chat()

    curr_idx = st.session_state.question_index

    # ── Interactive Quick Choice Chips for Questions ───────────────────────────
    if curr_idx < TOTAL_Q:
        current_q = QUESTIONS[curr_idx]
        q_key = current_q["key"]

        # 1. Destination Suggestions (Question 0)
        if q_key == "destination":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">💡 Popular Destinations:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            d_choices = [("🏖️ Goa Beaches", "Goa"), ("🛕 Ujjain & Omkareshwar", "Ujjain & Omkareshwar"),
                         ("🏔️ Ladakh Adventure", "Leh-Ladakh"), ("🌴 Kerala Backwaters", "Kerala")]
            for col, (label, val) in zip([c1, c2, c3, c4], d_choices):
                with col:
                    if st.button(label, key=f"chip_dest_{val}", use_container_width=True):
                        st.session_state.answers["destination"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[st.session_state.question_index]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 2. Origin City Suggestions (Question 1)
        elif q_key == "origin_city":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">📍 Select Starting City:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            o_choices = [("🏙️ Mumbai", "Mumbai"), ("🏛️ Delhi", "Delhi"), ("🌆 Ahmedabad", "Ahmedabad"), ("🌳 Bangalore", "Bangalore")]
            for col, (label, val) in zip([c1, c2, c3, c4], o_choices):
                with col:
                    if st.button(label, key=f"chip_orig_{val}", use_container_width=True):
                        st.session_state.answers["origin_city"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[st.session_state.question_index]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 3. Travel Dates Presets (Question 2)
        elif q_key == "travel_dates":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">📅 Select Travel Date Preset:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            date_choices = [
                ("🗓️ Nov 6 to Nov 16 (11 Days)", "Nov 6 to Nov 16 2026"),
                ("🏖️ Dec 20 to Dec 27 (8 Days)", "Dec 20 to Dec 27 2026"),
                ("🚀 Next Weekend (4 Days)", "Nov 14 to Nov 17 2026"),
                ("🎆 New Year (Dec 29 - Jan 3)", "Dec 29 2026 to Jan 3 2027")
            ]
            for col, (label, val) in zip([c1, c2, c3, c4], date_choices):
                with col:
                    if st.button(label, key=f"chip_dates_{val}", use_container_width=True):
                        st.session_state.answers["travel_dates"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[st.session_state.question_index]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 4. Travelers Suggestions (Question 3)
        elif q_key == "travelers":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">👥 Select Travelers:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            t_choices = [("👤 Solo", "Solo Traveler"), ("💑 Couple", "Couple"), ("👨‍👩‍👧‍👦 Family", "Family with kids"), ("👥 Friends Group", "Friends group of 4")]
            for col, (label, val) in zip([c1, c2, c3, c4], t_choices):
                with col:
                    if st.button(label, key=f"chip_trav_{val}", use_container_width=True):
                        st.session_state.answers["travelers"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[curr_idx + 1]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 5. Budget Suggestions (Question 4)
        elif q_key == "budget":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">💰 Select Budget Style:</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            b_choices = [("💡 Budget Friendly (₹10k-₹15k)", "Budget friendly ₹15,000"), ("⚖️ Moderate (₹25k-₹40k)", "Moderate ₹35,000"), ("🌟 Luxury (₹50k+)", "Luxury ₹60,000+")]
            for col, (label, val) in zip([c1, c2, c3], b_choices):
                with col:
                    if st.button(label, key=f"chip_budg_{val}", use_container_width=True):
                        st.session_state.answers["budget"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[curr_idx + 1]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 6. Stay Preference Suggestions (Question 5)
        elif q_key == "stay_preference":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">🏨 Select Stay Preference:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            s_choices = [("🏨 3-Star Hotel", "3-Star Hotel"), ("🏡 Resort & Spa", "Resort & Spa"), ("🎒 Hostel / Budget", "Hostel / Budget Stay"), ("🏠 Homestay", "Homestay")]
            for col, (label, val) in zip([c1, c2, c3, c4], s_choices):
                with col:
                    if st.button(label, key=f"chip_stay_{val}", use_container_width=True):
                        st.session_state.answers["stay_preference"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[curr_idx + 1]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 7. Interests Suggestions (Question 6)
        elif q_key == "interests":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">🎯 Select Main Activity / Vibe:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            i_choices = [("🏖️ Beaches & Water", "Beaches & Water Sports"), ("🛕 Temples & Pilgrimage", "Temples & History"),
                         ("🏔️ Mountains & Nature", "Mountains & Sightseeing"), ("🏄 Extreme Adventure", "Trekking & Extreme Adventure")]
            for col, (label, val) in zip([c1, c2, c3, c4], i_choices):
                with col:
                    if st.button(label, key=f"chip_int_{val}", use_container_width=True):
                        st.session_state.answers["interests"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        nxt = QUESTIONS[curr_idx + 1]
                        st.session_state.chat_history.append({"role": "panda", "content": nxt["panda"]})
                        st.rerun()

        # 8. Special Requirements Suggestions (Question 7)
        elif q_key == "special_requirements":
            st.markdown('<div style="color:#64748b; font-size:0.84rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin: 10px 0 8px 0;">🙏 Select Special Requirements:</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            req_choices = [("🌱 Pure Veg Food Only", "Pure Veg food only"), ("👴 Senior Citizen Friendly", "Senior citizen friendly"),
                           ("👶 Family with Kids", "Kids friendly"), ("🚫 No Special Requirements", "No special requirements")]
            for col, (label, val) in zip([c1, c2, c3, c4], req_choices):
                with col:
                    if st.button(label, key=f"chip_req_{val}", use_container_width=True):
                        st.session_state.answers["special_requirements"] = val
                        st.session_state.chat_history.append({"role": "user", "content": val})
                        st.session_state.question_index += 1
                        dest = st.session_state.answers.get('destination', 'your destination')
                        st.session_state.chat_history.append({
                            "role": "panda",
                            "content": f"Thank you! I have collected all your travel preferences.\n\n"
                                       f"Generating a comprehensive travel plan with real photos & Google Maps links for **{dest}** now... 🐼🗺️"
                        })
                        st.session_state.phase = "itinerary"
                        st.rerun()

        # Form Input Bar
        with st.form(key=f"chat_form_{curr_idx}", clear_on_submit=True):
            col_inp, col_btn = st.columns([5, 1])
            with col_inp:
                user_input = st.text_input(
                    "Your message:",
                    placeholder=current_q["placeholder"],
                    label_visibility="collapsed"
                )
            with col_btn:
                submitted = st.form_submit_button("Send ➤", use_container_width=True)

        # Auto-focus cursor
        import streamlit.components.v1 as components
        components.html("""
        <script>
            setTimeout(function() {
                const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                if (inputs.length > 0) {
                    const activeInput = inputs[inputs.length - 1];
                    activeInput.focus();
                }
            }, 150);
        </script>
        """, height=0)

        if submitted and user_input.strip():
            st.session_state.answers[q_key] = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
            st.session_state.question_index += 1

            if st.session_state.question_index < TOTAL_Q:
                next_q = QUESTIONS[st.session_state.question_index]
                next_content = next_q["panda_func"]() if "panda_func" in next_q else next_q["panda"]
                st.session_state.chat_history.append({"role": "panda", "content": next_content})
            else:
                dest = st.session_state.answers.get('destination', 'your destination')
                st.session_state.chat_history.append({
                    "role": "panda",
                    "content": f"Thank you! I have collected all your travel preferences.\n\n"
                               f"Generating a comprehensive travel plan with real photos & Google Maps links for **{dest}** now... 🐼🗺️"
                })
                st.session_state.phase = "itinerary"

            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ─── PHASE 2: TABBED MASTER ITINERARY VIEW ────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "itinerary":

    render_chat()

    dest = st.session_state.answers.get('destination', 'your destination')

    if st.session_state.itinerary is None:
        gemini_ok = bool(os.environ.get("GEMINI_API_KEY"))
        if not gemini_ok:
            st.error("Gemini API key is missing! Please check your `.env` file.")
        else:
            with st.spinner(f"Panda is generating your complete travel plan and fetching photos for **{dest}**..."):
                try:
                    itinerary = generate_itinerary(st.session_state.answers)
                    st.session_state.itinerary = itinerary

                    gallery = fetch_trip_gallery(dest, itinerary)
                    st.session_state.gallery = gallery

                    save_plan_entry(dest, st.session_state.answers, itinerary, gallery)
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {e}")
                    c_retry, c_new = st.columns([1, 1])
                    with c_retry:
                        if st.button("🔄 Retry Generating Plan", key="retry_gen_btn", use_container_width=True):
                            st.rerun()
                    with c_new:
                        if st.button("➕ Start New Plan", key="new_plan_err_btn", use_container_width=True):
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]
                            st.rerun()
    else:
        st.markdown("---")

        # Summary Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-lbl">Starting From</div>
                <div class="metric-val">{st.session_state.answers.get('origin_city', '-')}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-lbl">Destination</div>
                <div class="metric-val">{st.session_state.answers.get('destination', '-')}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-lbl">Dates & Duration</div>
                <div class="metric-val">{st.session_state.answers.get('travel_dates', '-')}</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-lbl">Budget</div>
                <div class="metric-val">{st.session_state.answers.get('budget', '-')}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabbed View (Fresh Modern Travel UI) ─────────────────────────────
        tab_plan, tab_hotels, tab_gallery, tab_export = st.tabs([
            "📅 Day-by-Day Master Plan",
            "🏨 Hotels & Stay Guide",
            "📸 Destination Photos",
            "📥 Download Options"
        ])

        gallery = st.session_state.gallery or {}

        # TAB 1: Day by Day Plan
        with tab_plan:
            st.markdown('<div class="itinerary-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.itinerary)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 2: Hotels & Stay Recommendations with Photos
        with tab_hotels:
            hotel_imgs = gallery.get("hotel_images", [])
            st.markdown("### 🏨 Suggested Hotel Recommendations & Photos")
            if hotel_imgs:
                cols_h = st.columns(min(3, len(hotel_imgs)))
                for idx, h_item in enumerate(hotel_imgs[:3]):
                    h_p = h_item.get("path") if isinstance(h_item, dict) else h_item
                    h_n = h_item.get("name", "Recommended Hotel") if isinstance(h_item, dict) else "Recommended Hotel"
                    if h_p and os.path.exists(h_p):
                        with cols_h[idx % len(cols_h)]:
                            st.image(h_p, use_container_width=True, caption=h_n)
            
            st.info("💡 All recommended hotels match your preferred budget and accommodation style. Click the Google Maps links in the Master Plan tab to view exact location pins!")

        # TAB 3: Destination Photo Gallery (All Attraction Spots across Days)
        with tab_gallery:
            dest_imgs = gallery.get("destination_images", [])
            st.markdown(f"### 📸 {dest.title()} Attraction Spots & Day Highlights ({len(dest_imgs)} Spots)")
            if dest_imgs:
                num_cols = min(3, len(dest_imgs))
                for i in range(0, len(dest_imgs), num_cols):
                    cols_g = st.columns(num_cols)
                    for j, item in enumerate(dest_imgs[i:i+num_cols]):
                        img_path = item.get("path") if isinstance(item, dict) else item
                        spot_name = item.get("name", f"Spot {i+j+1}") if isinstance(item, dict) else f"{dest.title()} Spot {i+j+1}"
                        if img_path and os.path.exists(img_path):
                            with cols_g[j]:
                                st.image(img_path, use_container_width=True, caption=spot_name)

        # TAB 4: Download Options (Word, PDF, JPG)
        with tab_export:
            st.markdown("### 📥 Download Travel Plan in Any Format")
            st.markdown("<br>", unsafe_allow_html=True)
            col_pdf, col_jpg, col_docx = st.columns(3)

            with col_pdf:
                try:
                    pdf_bytes = export_to_pdf(dest, st.session_state.answers, st.session_state.itinerary, gallery)
                    st.download_button(
                        "📕 Download PDF Guide (.pdf)",
                        data=pdf_bytes,
                        file_name=f"TravelingPanda_{dest.replace(' ','_')}_Guide.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF build error: {e}")

            with col_jpg:
                try:
                    jpg_bytes = export_to_jpg(dest, st.session_state.answers, st.session_state.itinerary, gallery)
                    st.download_button(
                        "🖼️ Download JPG Card (.jpg)",
                        data=jpg_bytes,
                        file_name=f"TravelingPanda_{dest.replace(' ','_')}_Card.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"JPG build error: {e}")

            with col_docx:
                try:
                    docx_bytes = export_to_docx(dest, st.session_state.answers, st.session_state.itinerary, gallery)
                    st.download_button(
                        "📝 Download Word Doc (.docx)",
                        data=docx_bytes,
                        file_name=f"TravelingPanda_{dest.replace(' ','_')}_Guide.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Word build error: {e}")
