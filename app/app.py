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
    page_title="EvoNexus-Twin | Career Intelligence",
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

# Save cookies if login just succeeded
if st.session_state.get("_pending_cookie_save"):
    uinfo = st.session_state["user_info"]
    controller.set('auth_email', uinfo.get("email", ""))
    controller.set('auth_name', uinfo.get("name", ""))
    st.session_state.pop("_pending_cookie_save", None)

# Persistent check for cookies to avoid flicker on refresh
if not st.session_state["authenticated"]:
    c_email = controller.get("auth_email")
    c_name = controller.get("auth_name")
    if c_email:
        st.session_state["authenticated"] = True
        st.session_state["user_info"] = {"email": c_email, "name": c_name or "User"}
        st.rerun()

# --- 5. RENDER LOGIN PAGE ---
def login_page():
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 60px 20px;">
        <div style="text-align:center; max-width: 440px; width:100%;">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size: 3rem;
                font-weight: 800;
                letter-spacing: -0.04em;
                background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0px;
                line-height: 1;
            ">EVONEXUS</div>
            <p style="color:#475569; font-size:0.7rem; letter-spacing:0.3em; text-transform:uppercase; margin-bottom: 30px; font-weight: 600;">
                Intelligence Engine
            </p>
            <div style="
                background: rgba(15,23,42,0.6);
                border: 1px solid rgba(51,65,85,0.4);
                border-radius: 24px;
                padding: 30px;
                backdrop-filter: blur(20px);
                box-shadow: 0 20px 50px rgba(0,0,0,0.4);
            ">
                <p style="color:#94a3b8; font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:24px; font-weight:500;">
                    Secure Authentication Required
                </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        redirect_uri = get_runtime_redirect_uri()
        login_url = authorization_url_with_pkce(redirect_uri)
        st.markdown(f"""
        <a href="{login_url}" target="_self" style="text-decoration:none; display:block;">
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));
                color: #f8fafc;
                padding: 12px 20px;
                border: 1px solid rgba(59,130,246,0.3);
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                transition: all 0.3s ease;
                letter-spacing: 0.02em;
                text-transform: uppercase;
            "
            onmouseover="this.style.background='rgba(59, 130, 246, 0.25)'; this.style.borderColor='rgba(59,130,246,0.6)'"
            onmouseout="this.style.background='rgba(59, 130, 246, 0.15)'; this.style.borderColor='rgba(59,130,246,0.3)'"
            >
                <img src="https://www.google.com/favicon.ico" width="16" height="16" alt="G">
                Sign in with Google
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("</div></div></div>", unsafe_allow_html=True)

if not st.session_state["authenticated"]:
    # If we haven't confirmed no-cookie after a brief wait, show login
    if not _oauth_code:
        # Give CookieController a frame to load
        if "cookie_wait" not in st.session_state:
            st.session_state["cookie_wait"] = True
            time.sleep(0.1)
            st.rerun()
            
        pg = st.navigation([st.Page(login_page, title="Login", icon=None)])
        pg.run()
        st.stop()
    else:
        st.info("Verifying session...")
        st.stop()

# --- 6. SPLASH SCREEN ---
if "intro_played" not in st.session_state:
    st.markdown("""
    <style>
    @keyframes gridPulse {
        0%   { opacity: 0; transform: perspective(500px) rotateX(60deg) translateY(0); }
        50%  { opacity: 0.5; }
        100% { opacity: 0; transform: perspective(500px) rotateX(60deg) translateY(-50px); }
    }
    @keyframes logoDraw {
        0%   { opacity: 0; filter: blur(10px); transform: scale(0.9); letter-spacing: 1em; }
        40%  { opacity: 1; filter: blur(0); transform: scale(1); letter-spacing: 0.1em; }
        80%  { opacity: 1; }
        100% { opacity: 0; transform: scale(1.05); }
    }
    @keyframes neonGlow {
        0%, 100% { text-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
        50%      { text-shadow: 0 0 40px rgba(59, 130, 246, 0.8), 0 0 60px rgba(167, 139, 250, 0.4); }
    }
    #ent-splash {
        position: fixed; inset: 0; z-index: 99999;
        background: #070b14;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        overflow: hidden;
    }
    #ent-splash-grid {
        position: absolute; bottom: 0; width: 200%; height: 100%;
        background-image: 
            linear-gradient(rgba(59,130,246,0.2) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59,130,246,0.2) 1px, transparent 1px);
        background-size: 60px 60px;
        animation: gridPulse 2.5s linear forwards;
        transform: perspective(500px) rotateX(60deg);
        mask-image: linear-gradient(to top, black, transparent);
    }
    #ent-splash-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 5rem; font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: logoDraw 2.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards, neonGlow 2s ease-in-out infinite;
        position: relative; z-index: 2;
    }
    </style>
    <div id="ent-splash">
        <div id="ent-splash-grid"></div>
        <div id="ent-splash-title">EVONEXUS</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.5)
    st.session_state["intro_played"] = True
    st.rerun()

# --- 7. AUTHENTICATED APP ---
def get_user_profile(email):
    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    if not os.path.exists(users_file):
        return None
    try:
        with open(users_file, "r") as f:
            return json.load(f).get(email)
    except:
        return None

# Restore profile results
user_email = st.session_state["user_info"].get("email")
profile = get_user_profile(user_email)
needs_setup = profile is None

if not needs_setup and "result" not in st.session_state:
    from src.predict import predict_full
    with st.spinner("Restoring intelligence state..."):
        try:
            st.session_state.result = predict_full(profile)
            st.session_state.sample = profile
        except:
            needs_setup = True

# Header/TopBar logic
if render_topbar(st.session_state["user_info"], logout_key="main_logout"):
    controller.remove('auth_email')
    controller.remove('auth_name')
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = None
    st.session_state.pop("intro_played", None)
    st.query_params.clear()
    st.rerun()

if needs_setup:
    pg = st.navigation([st.Page("views/0_Home.py", title="Setup Profile")])
else:
    nav = st.query_params.get("nav", "Overview")
    pages = {
        "Overview":           st.Page("views/1_Overview.py"),
        "Risk-Analysis":      st.Page("views/2_Risk_Analysis.py"),
        "Career-Roadmap":     st.Page("views/3_Career_Roadmap.py"),
        "Placement-Strategy": st.Page("views/4_Placement_Strategy.py"),
        "Profile":            st.Page("views/0_Home.py")
    }
    pg = st.navigation([pages.get(nav, pages["Overview"])])

pg.run()