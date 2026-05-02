import os
import sys
import streamlit as st

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth import get_login_url, get_tokens, get_user_info
from utils import apply_custom_css

import json
from streamlit_cookies_controller import CookieController

# Initialize cookie controller
controller = CookieController()


def get_runtime_redirect_uri() -> str:
    """Build redirect URI from the active request host to avoid host mismatches."""
    try:
        host = st.context.headers["host"]
    except Exception:
        host = ""

    host = (host or "").strip()
    if host:
        return f"http://{host}"
    return "http://localhost:8501"

# Page config must be the first st command
st.set_page_config(
    page_title="EvoNexus-Twin | Login",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()

# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# Attempt to restore auth from cookie
cookie_email = controller.get('auth_email')
cookie_name = controller.get('auth_name')

if cookie_email and not st.session_state["authenticated"]:
    st.session_state["authenticated"] = True
    st.session_state["user_info"] = {"email": cookie_email, "name": cookie_name or "User"}

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
        login_url = get_login_url(redirect_uri=redirect_uri)
        
        # We use standard HTML for a sleek button
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
    # Check if we are returning from Google Auth
    if "code" in st.query_params:
        try:
            code = st.query_params["code"]
            redirect_uri = get_runtime_redirect_uri()
            tokens = get_tokens(code, redirect_uri=redirect_uri)
            user_info = get_user_info(tokens["access_token"])
            
            st.session_state["authenticated"] = True
            st.session_state["user_info"] = user_info
            
            # Save to cookies
            controller.set('auth_email', user_info.get("email", ""))
            controller.set('auth_name', user_info.get("name", ""))
            
            # Clear query params so refresh doesn't fail with used code
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            # Remove OAuth params so reload does not replay an already-used/expired code.
            for key in ("code", "scope", "authuser", "hd", "prompt"):
                try:
                    del st.query_params[key]
                except KeyError:
                    pass
            st.caption(
                "If this persists: in Google Cloud Console, under APIs & Services → Credentials, "
                "the authorized redirect URI must match `REDIRECT_URI` exactly "
                "(including `localhost` vs `127.0.0.1` and no trailing slash unless you registered one). "
                "Sign in again from the login page."
            )
            st.caption(f"Current callback URI used by app: `{get_runtime_redirect_uri()}`")
            if st.button("Return to login"):
                st.rerun()
            st.stop()
    else:
        # Define and run the login page only
        pg = st.navigation([st.Page(login_page, title="Login", icon="🔒")])
        pg.run()
        st.stop()

# Helper to check if user profile exists
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

# If authenticated, show the dashboard
if st.session_state["authenticated"]:
    user_email = st.session_state["user_info"].get("email")
    needs_setup = not has_profile(user_email)
    
    if needs_setup:
        # User MUST setup profile first
        setup_page = st.Page("views/0_🏠_Home.py", title="Setup Profile", icon="⚙️")
        pg = st.navigation([setup_page])
    else:
        # Define full dashboard pages
        home = st.Page("views/0_🏠_Home.py", title="Edit Profile", icon="⚙️")
        overview = st.Page("views/1_📊_Overview.py", title="Overview", icon="📊")
        risk_analysis = st.Page("views/2_🔍_Risk_Analysis.py", title="Risk Analysis", icon="🔍")
        career_roadmap = st.Page("views/3_🛣️_Career_Roadmap.py", title="Career Roadmap", icon="🛣️")
        placement_strategy = st.Page("views/4_💼_Placement_Strategy.py", title="Placement Strategy", icon="💼")
        
        pg = st.navigation({
            "Dashboard": [overview, risk_analysis, career_roadmap, placement_strategy],
            "Settings": [home]
        })
    
    # Sidebar user profile & logout
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0; border-bottom: 1px solid #334155; margin-bottom: 20px;">
            <div style="font-weight: bold; color: #e2e8f0; font-size: 1.1rem;">{st.session_state['user_info'].get('name', 'User')}</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">{st.session_state['user_info'].get('email', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", use_container_width=True):
            controller.remove('auth_email')
            controller.remove('auth_name')
            st.session_state["authenticated"] = False
            st.session_state["user_info"] = None
            st.rerun()

    # Run the navigation
    pg.run()
