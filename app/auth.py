import base64
import hashlib
import json
import os
import pathlib
import secrets
import time
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

_PKCE_PENDING: dict[str, tuple[float, str]] = {}
_PKCE_PENDING_TTL_S = 15 * 60
_PKCE_DISK_DIR = pathlib.Path(_REPO_ROOT) / ".oauth_pkce_pending"


def _disk_path_for_state(oauth_state: str) -> pathlib.Path:
    h = hashlib.sha256(oauth_state.encode("utf-8")).hexdigest()
    return _PKCE_DISK_DIR / f"{h}.json"


def _prune_pkce_disk() -> None:
    if not _PKCE_DISK_DIR.is_dir():
        return
    cutoff = time.time() - _PKCE_PENDING_TTL_S
    for path in _PKCE_DISK_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if float(data.get("saved_at", 0)) < cutoff:
                path.unlink(missing_ok=True)
        except (OSError, ValueError, TypeError):
            path.unlink(missing_ok=True)


def _write_pkce_disk(oauth_state: str, code_verifier: str) -> None:
    """Persist verifier so redirects survive Streamlit reloads / process reuse."""
    _PKCE_DISK_DIR.mkdir(parents=True, exist_ok=True)
    _prune_pkce_disk()
    payload = {"saved_at": time.time(), "state": oauth_state, "verifier": code_verifier}
    dest = _disk_path_for_state(oauth_state)
    dest.write_text(json.dumps(payload), encoding="utf-8")


def _read_pop_pkce_disk(oauth_state: str) -> str | None:
    path = _disk_path_for_state(oauth_state)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        path.unlink(missing_ok=True)
    except (OSError, ValueError, TypeError):
        path.unlink(missing_ok=True)
        return None
    if data.get("state") != oauth_state:
        return None
    saved = float(data.get("saved_at", 0))
    if time.time() - saved > _PKCE_PENDING_TTL_S:
        return None
    v = data.get("verifier")
    return str(v) if isinstance(v, str) and v else None


def _prune_pkce_pending() -> None:
    now = time.time()
    dead = [
        k
        for k, (ts, _) in _PKCE_PENDING.items()
        if now - ts > _PKCE_PENDING_TTL_S
    ]
    for k in dead:
        del _PKCE_PENDING[k]


def remember_pkce_verifier(oauth_state: str, code_verifier: str) -> None:
    """Bind PKCE verifier to OAuth `state` (returned verbatim by Google after login)."""
    _prune_pkce_pending()
    key = oauth_state.strip()
    _PKCE_PENDING[key] = (time.time(), code_verifier)
    _write_pkce_disk(key, code_verifier)


def take_pkce_verifier(oauth_state: str) -> str | None:
    """Consume PKCE verifier for this `state` (one-shot)."""
    key = (oauth_state or "").strip()
    if not key:
        return None
    disk_v = _read_pop_pkce_disk(key)
    if disk_v:
        _PKCE_PENDING.pop(key, None)
        return disk_v
    _prune_pkce_pending()
    tup = _PKCE_PENDING.pop(key, None)
    if not tup:
        return None
    ts, verifier = tup
    if time.time() - ts > _PKCE_PENDING_TTL_S:
        return None
    return verifier


def authorization_url_with_pkce(redirect_uri: str) -> str:
    """Build Google authorize URL including PKCE + `state`, and stash verifier server-side."""
    verifier, challenge = generate_pkce_pair()
    oauth_state = secrets.token_urlsafe(24)
    remember_pkce_verifier(oauth_state, verifier)
    return get_login_url(
        redirect_uri=redirect_uri,
        pkce_challenge=challenge,
        state=oauth_state,
    )


def generate_pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge_s256) for Google's PKCE OAuth flow."""
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def get_login_url(
    redirect_uri: str | None = None,
    *,
    pkce_challenge: str | None = None,
    state: str | None = None,
):
    effective_redirect_uri = (redirect_uri or REDIRECT_URI).strip()
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": effective_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    if pkce_challenge:
        params["code_challenge"] = pkce_challenge
        params["code_challenge_method"] = "S256"
    if state:
        params["state"] = state
    url = f"{AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
    return url


def get_tokens(code, redirect_uri: str | None = None, code_verifier: str | None = None):
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

    verifier = (code_verifier or "").strip() or None

    def token_payload(
        *,
        eff_redirect: str,
        send_client_secret: bool,
        send_code_verifier: bool,
    ) -> dict:
        p: dict = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": eff_redirect,
            "grant_type": "authorization_code",
        }
        if send_client_secret and GOOGLE_CLIENT_SECRET:
            p["client_secret"] = GOOGLE_CLIENT_SECRET
        if send_code_verifier and verifier:
            p["code_verifier"] = verifier
        return p

    # Web client (confidential): client_secret only. Desktop / PKCE-required: code_verifier, often no secret.
    last_status = None
    last_body = None
    tried: list[dict[str, str | int | bool]] = []

    for effective_redirect_uri in redirect_candidates:
        if verifier:
            attempt_specs = [
                (True, True),  # PKCE + client_secret (works for many Web configs)
                (False, True),  # PKCE only (Desktop / public-style)
            ]
        else:
            attempt_specs = [(True, False)]

        seen_payload_keys: set[str] = set()
        for send_secret, send_verifier in attempt_specs:
            if send_verifier and not verifier:
                continue
            if send_secret and not GOOGLE_CLIENT_SECRET:
                continue
            data = token_payload(
                eff_redirect=effective_redirect_uri,
                send_client_secret=send_secret,
                send_code_verifier=send_verifier,
            )
            sig = repr(sorted(data.items()))
            if sig in seen_payload_keys:
                continue
            seen_payload_keys.add(sig)

            response = requests.post(TOKEN_URL, data=data, timeout=15)
            last_status = response.status_code
            last_body = response.text
            tried.append(
                {
                    "redirect_uri": effective_redirect_uri,
                    "status": response.status_code,
                    "client_secret_sent": send_secret,
                    "code_verifier_sent": send_verifier and verifier is not None,
                }
            )
            if response.status_code == 200:
                return response.json()

    # No variant worked — raise a richer, safe error message.
    client_id_suffix = GOOGLE_CLIENT_ID[-8:] if GOOGLE_CLIENT_ID else ""
    raise Exception(
        "Failed to get tokens: "
        f"{last_body} "
        f"(tried={tried}, client_id_endswith={client_id_suffix})"
    )

def get_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(USER_INFO_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get user info: {response.text}")
