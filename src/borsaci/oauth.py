"""Google Gemini OAuth with PKCE flow (OpenClaw google-gemini-cli-auth pattern)"""

import secrets
import hashlib
import base64
import asyncio
import shutil
import re
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
import webbrowser
from pathlib import Path
from typing import Optional, Tuple, Iterator
from dataclasses import dataclass

import aiohttp

# OAuth Config (OpenClaw uses port 8085, we use 8086)
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
REDIRECT_URI = "http://localhost:8086/oauth2callback"
CALLBACK_PORT = 8086

# Scopes for Gemini API access
# NOTE: Using cloud-platform scope for Vertex AI compatibility
# The generative-language scope is not registered for Gemini CLI OAuth client
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "openid",
    "email",
]


def should_use_manual_oauth_flow() -> bool:
    """
    OpenClaw pattern: WSL2 veya remote ortamda browser açılamaz.
    Bu durumda manual URL paste mode kullanılır.

    Returns:
        True if manual mode should be used (WSL2, SSH, headless)
    """
    # WSL2 detection
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    return True
        except Exception:
            pass

    # SSH session detection
    if os.getenv("SSH_CLIENT") or os.getenv("SSH_TTY"):
        return True

    # No display (headless Linux)
    if sys.platform.startswith("linux") and not os.getenv("DISPLAY"):
        return True

    return False


def extract_from_gemini_cli() -> Optional[Tuple[str, Optional[str]]]:
    """
    Extract OAuth client ID/secret from installed Gemini CLI.
    OpenClaw pattern - no need for user to set up Google Cloud project.

    Returns:
        Tuple of (client_id, client_secret) or None if not found
    """
    gemini_path = shutil.which("gemini")
    if not gemini_path:
        return None

    try:
        gemini_dir = Path(gemini_path).resolve().parent.parent

        # Search paths for oauth2.js (OpenClaw pattern)
        search_paths = [
            gemini_dir / "node_modules/@google/gemini-cli-core/dist/src/code_assist/oauth2.js",
            gemini_dir / "node_modules/@google/gemini-cli-core/dist/code_assist/oauth2.js",
            gemini_dir / "lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/oauth2.js",
        ]

        for oauth_js in search_paths:
            result = _extract_credentials_from_file(oauth_js)
            if result:
                return result

        # Modern Gemini CLI ships as bundled chunks (bundle/*.js) with named
        # OAUTH_CLIENT_ID / OAUTH_CLIENT_SECRET constants
        bundle_dir = gemini_dir / "bundle"
        if bundle_dir.exists():
            for chunk in sorted(bundle_dir.glob("*.js")):
                result = _extract_credentials_from_bundle(chunk)
                if result:
                    return result

        # Recursive search as fallback (max 10 levels deep - OpenClaw pattern)
        for oauth_js in _find_oauth_files(gemini_dir, max_depth=10):
            result = _extract_credentials_from_file(oauth_js)
            if result:
                return result

    except Exception:
        pass

    return None


def _extract_credentials_from_file(file_path: Path) -> Optional[Tuple[str, Optional[str]]]:
    """
    Extract client ID/secret from oauth2.js file using regex.

    Args:
        file_path: Path to oauth2.js file

    Returns:
        Tuple of (client_id, client_secret) or None
    """
    if not file_path.exists():
        return None
    try:
        content = file_path.read_text()
        # Pattern: xxx.apps.googleusercontent.com
        client_id_match = re.search(r'(\d+-[a-z0-9]+\.apps\.googleusercontent\.com)', content)
        # Pattern: GOCSPX-xxx
        client_secret_match = re.search(r'(GOCSPX-[A-Za-z0-9_-]+)', content)
        if client_id_match:
            client_id = client_id_match.group(1)
            client_secret = client_secret_match.group(1) if client_secret_match else None
            return (client_id, client_secret)
    except Exception:
        pass
    return None


def _extract_credentials_from_bundle(file_path: Path) -> Optional[Tuple[str, Optional[str]]]:
    """
    Extract OAuth client ID/secret from a bundled Gemini CLI chunk file
    using the named constants (OAUTH_CLIENT_ID / OAUTH_CLIENT_SECRET).
    """
    if not file_path.exists():
        return None
    try:
        content = file_path.read_text(errors="ignore")
        id_match = re.search(r'OAUTH_CLIENT_ID\s*=\s*["\']([^"\']+)["\']', content)
        if not id_match:
            return None
        secret_match = re.search(r'OAUTH_CLIENT_SECRET\s*=\s*["\']([^"\']+)["\']', content)
        return (id_match.group(1), secret_match.group(1) if secret_match else None)
    except Exception:
        pass
    return None


def _find_oauth_files(start_dir: Path, max_depth: int = 10) -> Iterator[Path]:
    """
    Recursive search for oauth2.js files.

    Args:
        start_dir: Directory to start search
        max_depth: Maximum recursion depth

    Yields:
        Paths to oauth2.js files
    """
    try:
        for root, dirs, files in os.walk(start_dir):
            depth = len(Path(root).relative_to(start_dir).parts)
            if depth > max_depth:
                dirs.clear()  # Stop descending
                continue
            if "oauth2.js" in files:
                yield Path(root) / "oauth2.js"
    except Exception:
        pass


def get_antigravity_credentials() -> Tuple[str, str]:
    """
    Return built-in Antigravity credentials (OpenClaw pattern).
    Base64-encoded in source, decoded at runtime.

    Returns:
        Tuple of (client_id, client_secret)
    """
    # OpenClaw google-antigravity-auth credentials (base64 encoded)
    CLIENT_ID_B64 = "MTA3MTAwNjA2MDU5MS10bWhzc2luMmgyMWxjcmUyMzV2dG9sb2poNGc0MDNlcC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbQ=="
    CLIENT_SECRET_B64 = "R09DU1BYLUs1OEZXUjQ4NkxkTEoxbUxCOHNYQzR6NnFEQWY="

    client_id = base64.b64decode(CLIENT_ID_B64).decode()
    client_secret = base64.b64decode(CLIENT_SECRET_B64).decode()

    return (client_id, client_secret)


def resolve_oauth_credentials() -> Tuple[str, str, Optional[str]]:
    """
    Resolve OAuth client credentials with priority (OpenClaw pattern):
    1. Extract from installed Gemini CLI (automatic)
    2. Use built-in Antigravity credentials (fallback)

    Returns:
        Tuple of (source, client_id, client_secret)
        source = "gemini-cli" or "antigravity"

    Note:
        NO env variable support - only these two methods.
    """
    # 1. Try Gemini CLI first
    creds = extract_from_gemini_cli()
    if creds:
        client_id, client_secret = creds
        return ("gemini-cli", client_id, client_secret)

    # 2. Fallback: Antigravity built-in credentials
    client_id, client_secret = get_antigravity_credentials()
    return ("antigravity", client_id, client_secret)


@dataclass
class GoogleCredentials:
    """Container for Google OAuth credentials"""
    access_token: str
    refresh_token: str
    expires_at: int  # Unix timestamp (ms)
    email: Optional[str] = None


def extract_tokens_from_gemini_cli() -> Optional[GoogleCredentials]:
    """
    Extract existing OAuth tokens from Gemini CLI's credential file.

    Gemini CLI stores tokens in ~/.gemini/oauth_creds.json.
    If user is already logged in via Gemini CLI, we can reuse those tokens
    without requiring a new browser login.

    Returns:
        GoogleCredentials if valid tokens found, None otherwise
    """
    import json

    token_file = Path.home() / ".gemini" / "oauth_creds.json"

    if not token_file.exists():
        return None

    try:
        with open(token_file) as f:
            data = json.load(f)

        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        expiry_date = data.get("expiry_date")  # Unix timestamp in ms

        if not access_token or not refresh_token:
            return None

        # Extract email from id_token if present
        email = None
        id_token = data.get("id_token")
        if id_token:
            try:
                # Decode JWT payload (middle part)
                import json as json_mod
                payload = id_token.split(".")[1]
                # Add padding if needed
                payload += "=" * (4 - len(payload) % 4)
                decoded = base64.urlsafe_b64decode(payload)
                claims = json_mod.loads(decoded)
                email = claims.get("email")
            except Exception:
                pass

        return GoogleCredentials(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expiry_date or 0,
            email=email,
        )

    except Exception:
        return None


def generate_pkce() -> Tuple[str, str]:
    """
    Generate PKCE verifier and challenge for OAuth flow.

    Returns:
        Tuple of (verifier, challenge)
    """
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")
    return verifier, challenge


def build_auth_url(client_id: str, challenge: str, state: str) -> str:
    """
    Build Google OAuth authorization URL.

    Args:
        client_id: Google OAuth client ID
        challenge: PKCE challenge
        state: CSRF protection state

    Returns:
        Full authorization URL
    """
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback on localhost"""
    code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None

    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        parsed = urlparse(self.path)
        if parsed.path == "/oauth2callback":
            params = parse_qs(parsed.query)
            OAuthCallbackHandler.code = params.get("code", [None])[0]
            OAuthCallbackHandler.state = params.get("state", [None])[0]
            OAuthCallbackHandler.error = params.get("error", [None])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            response = """
            <html>
            <head><title>BorsaCI OAuth</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h2>OAuth tamamlandı!</h2>
                <p>Bu pencereyi kapatabilirsiniz ve terminale dönebilirsiniz.</p>
            </body>
            </html>
            """
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass


async def wait_for_callback(expected_state: str, timeout: int = 300) -> str:
    """
    Start callback server and wait for OAuth response.

    Args:
        expected_state: Expected state parameter for CSRF protection
        timeout: Timeout in seconds

    Returns:
        Authorization code

    Raises:
        Exception: On OAuth error or timeout
    """
    # Reset handler state
    OAuthCallbackHandler.code = None
    OAuthCallbackHandler.state = None
    OAuthCallbackHandler.error = None

    server = HTTPServer(("localhost", CALLBACK_PORT), OAuthCallbackHandler)
    server.timeout = timeout

    # Run server in thread to not block
    def serve():
        server.handle_request()

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, serve)

    if OAuthCallbackHandler.error:
        raise Exception(f"OAuth error: {OAuthCallbackHandler.error}")

    if OAuthCallbackHandler.state != expected_state:
        raise Exception("OAuth state mismatch (CSRF protection)")

    if not OAuthCallbackHandler.code:
        raise Exception("No authorization code received")

    return OAuthCallbackHandler.code


async def exchange_code_for_tokens(
    code: str,
    verifier: str,
    client_id: str,
    client_secret: Optional[str] = None,
) -> GoogleCredentials:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: Authorization code from OAuth callback
        verifier: PKCE verifier
        client_id: Google OAuth client ID
        client_secret: Optional client secret

    Returns:
        GoogleCredentials with tokens

    Raises:
        Exception: On token exchange failure
    """
    data = {
        "client_id": client_id,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret

    async with aiohttp.ClientSession() as session:
        async with session.post(GOOGLE_TOKEN_URL, data=data) as resp:
            result = await resp.json()

            if "error" in result:
                error_desc = result.get("error_description", result["error"])
                raise Exception(f"Token exchange failed: {error_desc}")

            # Get user email
            email = None
            try:
                headers = {"Authorization": f"Bearer {result['access_token']}"}
                async with session.get(GOOGLE_USERINFO_URL, headers=headers) as user_resp:
                    user_info = await user_resp.json()
                    email = user_info.get("email")
            except Exception:
                pass

            import time
            # Calculate expiry with 5 minute safety margin
            expires_at = int(time.time() * 1000) + (result["expires_in"] * 1000) - (5 * 60 * 1000)

            return GoogleCredentials(
                access_token=result["access_token"],
                refresh_token=result.get("refresh_token", ""),
                expires_at=expires_at,
                email=email,
            )


async def refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: Optional[str] = None,
) -> GoogleCredentials:
    """
    Refresh expired access token using refresh token.

    Args:
        refresh_token: Google OAuth refresh token
        client_id: Google OAuth client ID
        client_secret: Optional client secret

    Returns:
        GoogleCredentials with new access token

    Raises:
        Exception: On token refresh failure
    """
    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    if client_secret:
        data["client_secret"] = client_secret

    async with aiohttp.ClientSession() as session:
        async with session.post(GOOGLE_TOKEN_URL, data=data) as resp:
            result = await resp.json()

            if "error" in result:
                error_desc = result.get("error_description", result["error"])
                raise Exception(f"Token refresh failed: {error_desc}")

            import time
            expires_at = int(time.time() * 1000) + (result["expires_in"] * 1000) - (5 * 60 * 1000)

            return GoogleCredentials(
                access_token=result["access_token"],
                refresh_token=result.get("refresh_token", refresh_token),
                expires_at=expires_at,
            )


async def login_google_oauth(
    client_id: str,
    client_secret: Optional[str] = None,
    force_manual: bool = False,
) -> GoogleCredentials:
    """
    Complete Google OAuth flow with auto-detection for WSL2/remote.

    Args:
        client_id: Google OAuth client ID
        client_secret: Optional client secret
        force_manual: Force manual mode (for testing)

    Returns:
        GoogleCredentials with tokens

    Raises:
        Exception: On OAuth failure
    """
    verifier, challenge = generate_pkce()
    state = secrets.token_urlsafe(16)
    auth_url = build_auth_url(client_id, challenge, state)

    # Auto-detect if manual mode needed (OpenClaw pattern)
    use_manual = force_manual or should_use_manual_oauth_flow()

    if use_manual:
        print(f"\n🔗 Bu URL'yi tarayıcınızda açın:\n")
        print(f"  {auth_url}\n")
        print("Google'da giriş yaptıktan sonra yönlendirildiğiniz URL'yi buraya yapıştırın.")
        print("(URL http://localhost:8086/oauth2callback?code=... formatında olacak)\n")

        callback_url = input("Redirect URL: ").strip()

        parsed = urlparse(callback_url)
        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        returned_state = params.get("state", [None])[0]

        if returned_state != state:
            raise Exception("OAuth state mismatch (CSRF protection)")
        if not code:
            raise Exception("URL'de authorization code bulunamadı")
    else:
        # Browser mode with localhost callback
        try:
            webbrowser.open(auth_url)
            print("🌐 Tarayıcınızda Google giriş sayfası açıldı...")
            print("Giriş yaptıktan sonra otomatik olarak devam edilecek.\n")
        except Exception as e:
            # Fallback to manual if browser fails
            print(f"⚠️  Browser açılamadı: {e}")
            print(f"\n🔗 Bu URL'yi tarayıcınızda açın:\n")
            print(f"  {auth_url}\n")
            print("Google'da giriş yaptıktan sonra yönlendirildiğiniz URL'yi buraya yapıştırın.\n")

            callback_url = input("Redirect URL: ").strip()

            parsed = urlparse(callback_url)
            params = parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            returned_state = params.get("state", [None])[0]

            if returned_state != state:
                raise Exception("OAuth state mismatch (CSRF protection)")
            if not code:
                raise Exception("URL'de authorization code bulunamadı")

            return await exchange_code_for_tokens(code, verifier, client_id, client_secret)

        code = await wait_for_callback(state)

    return await exchange_code_for_tokens(code, verifier, client_id, client_secret)
