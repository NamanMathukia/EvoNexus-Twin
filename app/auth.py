import os
import requests
import urllib.parse
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

# Streamlit's process cwd is not always the repo root; load env from known locations.
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_APP_DIR, ".."))
load_dotenv(os.path.join(_REPO_ROOT, ".env"))
load_dotenv(os.path.join(_APP_DIR, ".env"), override=True)
load_dotenv()


def _env(key: str, default: str = "") -> str:
    v = os.environ.get(key, default)
    return (v or default).strip()


GOOGLE_CLIENT_ID = _env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = _env("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = _env("REDIRECT_URI") or "http://localhost:8501"

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

def get_login_url(redirect_uri: str | None = None):
    effective_redirect_uri = (redirect_uri or REDIRECT_URI).strip()
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": effective_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"{AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
    return url

def get_tokens(code, redirect_uri: str | None = None):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise Exception(
            "Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET. "
            "Set them in a .env file at the project root or in app/, then restart Streamlit."
        )
    code = (code or "").strip()
    if not code:
        raise Exception("Empty authorization code from Google.")
    base_redirect_uri = (redirect_uri or REDIRECT_URI).strip()

    def _normalize_redirect_variants(uri: str) -> list[str]:
        """Generate common redirect URI variants (slash + localhost/127.0.0.1)."""
        uri = (uri or "").strip()
        if not uri:
            return []

        p = urlparse(uri)
        if not p.scheme or not p.netloc:
            return [uri]

        # Ensure path is either "" or "/"
        path_variants = []
        if p.path in ("", "/"):
            path_variants = ["", "/"]
        else:
            path_variants = [p.path]

        host = p.hostname or ""
        port = f":{p.port}" if p.port else ""
        host_variants = [host]
        if host == "localhost":
            host_variants.append("127.0.0.1")
        elif host == "127.0.0.1":
            host_variants.append("localhost")

        out: list[str] = []
        for hv in host_variants:
            netloc = f"{hv}{port}"
            for pv in path_variants:
                candidate = urlunparse((p.scheme, netloc, pv, "", "", ""))
                out.append(candidate)

        # Preserve order but unique
        seen = set()
        uniq = []
        for x in out:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
        return uniq

    redirect_candidates = _normalize_redirect_variants(base_redirect_uri) or [base_redirect_uri]

    last_status = None
    last_body = None
    tried: list[dict[str, str | int]] = []

    for effective_redirect_uri in redirect_candidates:
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": effective_redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.post(TOKEN_URL, data=data, timeout=15)
        last_status = response.status_code
        last_body = response.text
        tried.append({"redirect_uri": effective_redirect_uri, "status": response.status_code})
        if response.status_code == 200:
            return response.json()

    # No variant worked — raise a richer, safe error message.
    client_id_suffix = GOOGLE_CLIENT_ID[-8:] if GOOGLE_CLIENT_ID else ""
    raise Exception(
        "Failed to get tokens: "
        f"{last_body} "
        f"(tried_redirect_uris={tried}, client_id_endswith={client_id_suffix})"
    )

def get_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(USER_INFO_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get user info: {response.text}")
