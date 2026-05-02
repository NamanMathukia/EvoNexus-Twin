import os
import sys
import streamlit as st
import json

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth import authorization_url_with_pkce, get_tokens, get_user_info, take_pkce_verifier
from utils import apply_custom_css

# --- 1. SET PAGE CONFIG FIRST ---
st.set_page_config(
    page_title="EvoNexus-Twin | Login",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
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
        # Added x-forwarded-proto so this works flawlessly if you deploy it behind HTTPS
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
# Protects against CookieController triggering a rerun mid-flight
if _oauth_code and not st.session_state["authenticated"]:
    if st.session_state.get("_oauth_last_success_code") == _oauth_code:
        st.query_params.clear()
        st.rerun()

    try:
        # Cache the single-use PKCE verifier in session state so it survives unexpected reruns
        if "pkce_verifier" not in st.session_state or st.session_state.get("current_oauth_state") != _oauth_state:
            st.session_state["pkce_verifier"] = take_pkce_verifier(_oauth_state) if _oauth_state else None
            st.session_state["current_oauth_state"] = _oauth_state
            
        pkce_verifier = st.session_state.get("pkce_verifier")
        
        if not _oauth_state:
            raise RuntimeError("Google did not return an OAuth `state` parameter.")
        if not pkce_verifier:
            raise RuntimeError("OAuth state expired or did not match a pending login.")

        # Exchange tokens
        tokens = get_tokens(
            _oauth_code,
            redirect_uri=get_runtime_redirect_uri(),
            code_verifier=pkce_verifier,
        )
        user_info = get_user_info(tokens["access_token"])
        
        st.session_state["authenticated"] = True
        st.session_state["user_info"] = user_info
        st.session_state["_oauth_last_success_code"] = _oauth_code
        
        # Flag that we need to save cookies on the next run
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

# --- 4. INITIALIZE COOKIES (Safe to do now) ---
from streamlit_cookies_controller import CookieController
controller = CookieController()

# Handle pending cookie save from successful login
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

# --- 5. RENDER UI ---
def login_page():
    st.markdown("""
    <div style="text-align:center; padding: 80px 0 20px 0;">
        <div style="font-size: 5rem;">🧬</div>
        <h1 style="font-size: 3.5rem; font-weight: 700; margin-top: 10px; background: linear-gradient(90deg, #3b82f6, #a78bfa, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            EvoNexus-Twin
        </h1>
        <p style="color:#94a3b8; font-size: 1.4rem; margin-top:10px;">
            Career Intelligence Engine
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin-top: 40px;'>", unsafe_allow_html=True)
        redirect_uri = get_runtime_redirect_uri()
        login_url = authorization_url_with_pkce(redirect_uri)
        
        st.markdown(f'''
        <a href="{login_url}" target="_self" style="text-decoration: none;">
            <div style="background-color: #1e293b; color: white; padding: 14px 24px; border: 1px solid #334155; border-radius: 8px; font-size: 18px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 12px; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                <img src="https://www.google.com/favicon.ico" width="24" height="24" alt="Google">
                Sign in with Google
            </div>
        </a>
        ''', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state["authenticated"]:
    pg = st.navigation([st.Page(login_page, title="Login", icon="🔒")])
    pg.run()
    st.stop()

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
    
    if needs_setup:
        setup_page = st.Page("views/0_🏠_Home.py", title="Setup Profile", icon="⚙️")
        pg = st.navigation([setup_page])
    else:
        home = st.Page("views/0_🏠_Home.py", title="Edit Profile", icon="⚙️")
        overview = st.Page("views/1_📊_Overview.py", title="Overview", icon="📊")
        risk_analysis = st.Page("views/2_🔍_Risk_Analysis.py", title="Risk Analysis", icon="🔍")
        career_roadmap = st.Page("views/3_🛣️_Career_Roadmap.py", title="Career Roadmap", icon="🛣️")
        placement_strategy = st.Page("views/4_💼_Placement_Strategy.py", title="Placement Strategy", icon="💼")
        
        pg = st.navigation({
            "Dashboard": [overview, risk_analysis, career_roadmap, placement_strategy],
            "Settings": [home]
        })
    
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0; border-bottom: 1px solid #334155; margin-bottom: 20px;">
            <div style="font-weight: bold; color: #e2e8f0; font-size: 1.1rem;">{st.session_state['user_info'].get('name', 'User')}</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">{st.session_state['user_info'].get('email', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", use_container_width=True):
            try:
                controller.remove('auth_email')
            except KeyError:
                pass
            try:
                controller.remove('auth_name')
            except KeyError:
                pass
            st.session_state["authenticated"] = False
            st.session_state["user_info"] = None
            st.session_state.pop("_oauth_last_success_code", None)
            st.rerun()

    pg.run()