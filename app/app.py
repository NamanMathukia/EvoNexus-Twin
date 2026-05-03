import os
import sys
import time
import streamlit as st
import json

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth import authorization_url_with_pkce, get_tokens, get_user_info, take_pkce_verifier
from utils import apply_custom_css, render_topbar

# --- 1. SET PAGE CONFIG FIRST ---
st.set_page_config(
    page_title="EvoNexus-Twin",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 2. INITIALIZE SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

def get_runtime_redirect_uri() -> str:
    """Build redirect URI from the active request host."""
    try:
        host = st.context.headers["host"]
        proto = st.context.headers.get("x-forwarded-proto", "http")
    except Exception:
        host = ""
        proto = "http"

    host = (host or "").strip()
    if host:
        return f"{proto}://{host}"
    return "http://localhost:8501"

apply_custom_css()

_oauth_code = (st.query_params.get("code") or "").strip()
_oauth_state = (st.query_params.get("state") or "").strip()

# --- 3. PROCESS OAUTH IMMEDIATELY ---
if _oauth_code and not st.session_state["authenticated"]:
    if st.session_state.get("_oauth_last_success_code") == _oauth_code:
        st.query_params.clear()
        st.rerun()

    try:
        if "pkce_verifier" not in st.session_state or st.session_state.get("current_oauth_state") != _oauth_state:
            st.session_state["pkce_verifier"] = take_pkce_verifier(_oauth_state) if _oauth_state else None
            st.session_state["current_oauth_state"] = _oauth_state

        pkce_verifier = st.session_state.get("pkce_verifier")

        if not _oauth_state:
            raise RuntimeError("Google did not return an OAuth `state` parameter.")
        if not pkce_verifier:
            raise RuntimeError("OAuth state expired or did not match a pending login.")

        tokens = get_tokens(
            _oauth_code,
            redirect_uri=get_runtime_redirect_uri(),
            code_verifier=pkce_verifier,
        )
        user_info = get_user_info(tokens["access_token"])

        st.session_state["authenticated"] = True
        st.session_state["user_info"] = user_info
        st.session_state["_oauth_last_success_code"] = _oauth_code
        st.session_state["_pending_cookie_save"] = True

        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Authentication failed: {e}")
        for key in ("code", "state", "scope", "authuser", "hd", "prompt"):
            try:
                del st.query_params[key]
            except KeyError:
                pass
        if st.button("Return to login"):
            st.rerun()
        st.stop()

# --- 4. INITIALIZE COOKIES ---
from streamlit_cookies_controller import CookieController
controller = CookieController()

if st.session_state.get("_pending_cookie_save"):
    user_info = st.session_state["user_info"]
    controller.set('auth_email', user_info.get("email", ""))
    controller.set('auth_name', user_info.get("name", ""))
    st.session_state.pop("_pending_cookie_save", None)

cookie_email = controller.get("auth_email")
cookie_name = controller.get("auth_name")

if cookie_email and not st.session_state["authenticated"] and not _oauth_code:
    st.session_state["authenticated"] = True
    st.session_state["user_info"] = {"email": cookie_email, "name": cookie_name or "User"}

# --- 5. RENDER LOGIN PAGE ---
def login_page():
    st.markdown("""
    <div style="min-height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 60px 20px;">
        <div style="text-align:center; max-width: 480px; width:100%;">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size: 3.2rem;
                font-weight: 800;
                letter-spacing: -0.02em;
                background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            ">EVONEXUS-TWIN</div>
            <p style="color:#475569; font-size:0.85rem; letter-spacing:0.18em; text-transform:uppercase; margin-bottom: 48px;">
                Career Intelligence Engine
            </p>
            <div style="
                background: rgba(15,23,42,0.7);
                border: 1px solid rgba(51,65,85,0.6);
                border-radius: 16px;
                padding: 36px 32px;
                backdrop-filter: blur(16px);
                box-shadow: 0 24px 60px rgba(0,0,0,0.5);
            ">
                <p style="color:#64748b; font-size:0.78rem; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:24px;">
                    Authenticate to continue
                </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        redirect_uri = get_runtime_redirect_uri()
        login_url = authorization_url_with_pkce(redirect_uri)
        st.markdown(f"""
        <a href="{login_url}" target="_self" style="text-decoration:none; display:block;">
            <div style="
                background: rgba(30,41,59,0.9);
                color: #e2e8f0;
                padding: 13px 24px;
                border: 1px solid rgba(59,130,246,0.35);
                border-radius: 10px;
                font-size: 0.9rem;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                transition: all 0.25s ease;
                letter-spacing: 0.04em;
                box-shadow: 0 0 20px rgba(59,130,246,0.12);
            "
            onmouseover="this.style.boxShadow='0 0 30px rgba(59,130,246,0.35)'; this.style.borderColor='rgba(59,130,246,0.6)'"
            onmouseout="this.style.boxShadow='0 0 20px rgba(59,130,246,0.12)'; this.style.borderColor='rgba(59,130,246,0.35)'"
            >
                <img src="https://www.google.com/favicon.ico" width="18" height="18" alt="G">
                Sign in with Google
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("</div></div></div>", unsafe_allow_html=True)

if not st.session_state["authenticated"]:
    pg = st.navigation([st.Page(login_page, title="Login", icon=None)])
    pg.run()
    st.stop()

# --- 6. SPLASH SCREEN (one-time per session, after login) ---
if "intro_played" not in st.session_state:
    st.markdown("""
    <style>
    @keyframes gridExpand {
        0%   { opacity: 0; transform: scale(0.85); }
        15%  { opacity: 1; }
        85%  { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(1.04); }
    }
    @keyframes wordmark {
        0%   { opacity: 0; letter-spacing: 0.6em; filter: blur(8px); }
        30%  { opacity: 1; letter-spacing: 0.12em; filter: blur(0); }
        75%  { opacity: 1; }
        100% { opacity: 0; }
    }
    @keyframes tagline {
        0%, 30% { opacity: 0; transform: translateY(10px); }
        50%     { opacity: 1; transform: translateY(0); }
        80%     { opacity: 1; }
        100%    { opacity: 0; }
    }
    @keyframes scanline {
        0%   { top: -10%; }
        100% { top: 110%; }
    }
    #ent-splash {
        position: fixed;
        inset: 0;
        z-index: 99999;
        background: #070b14;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    #ent-splash-grid {
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(59,130,246,0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59,130,246,0.07) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: gridExpand 2.6s ease forwards;
    }
    #ent-splash-scanline {
        position: absolute;
        left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.6), transparent);
        animation: scanline 2.5s linear forwards;
        pointer-events: none;
    }
    #ent-splash-wordmark {
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: clamp(2.2rem, 5vw, 4.5rem);
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: wordmark 2.5s cubic-bezier(0.16,1,0.3,1) forwards;
        position: relative; z-index: 2;
    }
    #ent-splash-tag {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.26em;
        text-transform: uppercase;
        color: #475569;
        margin-top: 14px;
        animation: tagline 2.5s ease forwards;
        position: relative; z-index: 2;
    }
    #ent-splash-ring {
        position: absolute;
        width: 320px; height: 320px;
        border-radius: 50%;
        border: 1px solid rgba(59,130,246,0.12);
        box-shadow: 0 0 60px rgba(59,130,246,0.08) inset;
        animation: gridExpand 2.6s ease forwards;
    }
    #ent-splash-ring2 {
        position: absolute;
        width: 520px; height: 520px;
        border-radius: 50%;
        border: 1px solid rgba(167,139,250,0.08);
        animation: gridExpand 2.6s ease 0.1s forwards;
    }
    </style>
    <div id="ent-splash">
        <div id="ent-splash-grid"></div>
        <div id="ent-splash-scanline"></div>
        <div id="ent-splash-ring2"></div>
        <div id="ent-splash-ring"></div>
        <div id="ent-splash-wordmark">EVONEXUS-TWIN</div>
        <div id="ent-splash-tag">Career Intelligence Engine</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.5)
    st.session_state["intro_played"] = True
    st.rerun()

# --- 7. AUTHENTICATED APP ---
def has_profile(email):
    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    if not os.path.exists(users_file):
        return False
    try:
        with open(users_file, "r") as f:
            users = json.load(f)
            return email in users
    except:
        return False

if st.session_state["authenticated"]:
    user_email = st.session_state["user_info"].get("email")
    needs_setup = not has_profile(user_email)

    # Render top bar and capture logout signal
    if render_topbar(st.session_state["user_info"], logout_key="main_logout"):
        controller.remove('auth_email')
        controller.remove('auth_name')
        st.session_state["authenticated"] = False
        st.session_state["user_info"] = None
        st.session_state.pop("_oauth_last_success_code", None)
        st.session_state.pop("intro_played", None)
        st.rerun()

    if needs_setup:
        setup_page = st.Page("views/0_🏠_Home.py", title="Setup Profile", icon=None)
        pg = st.navigation([setup_page])
    else:
        home             = st.Page("views/0_🏠_Home.py",            title="Edit Profile",       icon=None)
        overview         = st.Page("views/1_📊_Overview.py",         title="Overview",           icon=None)
        risk_analysis    = st.Page("views/2_🔍_Risk_Analysis.py",    title="Risk Analysis",      icon=None)
        career_roadmap   = st.Page("views/3_🛣️_Career_Roadmap.py",  title="Career Roadmap",     icon=None)
        placement_strategy = st.Page("views/4_💼_Placement_Strategy.py", title="Placement Strategy", icon=None)

        pg = st.navigation({
            "Dashboard": [overview, risk_analysis, career_roadmap, placement_strategy],
            "Settings":  [home]
        })

    pg.run()