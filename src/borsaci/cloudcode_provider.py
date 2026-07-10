"""Cloud Code Assist API provider for Google Gemini with OAuth.

This module implements the same authentication approach used by OpenClaw/OpenCode:
1. Uses Google's internal Cloud Code Assist API (cloudcode-pa.googleapis.com)
2. Works with cloud-platform scope (no generative-language scope needed)
3. Uses wrapped request format: {project, model, request: {...}}

This bypasses the public Gemini API limitations and allows OAuth authentication.
"""

import asyncio
import json
from typing import Optional, Any, AsyncIterator
from dataclasses import dataclass
import aiohttp

from .config import get_config_manager, GoogleOAuthCredential
from .oauth import refresh_access_token, resolve_oauth_credentials


# Cloud Code Assist API endpoints (in order of preference)
CLOUDCODE_ENDPOINTS = [
    "https://cloudcode-pa.googleapis.com/v1internal",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com/v1internal",
    "https://daily-cloudcode-pa.sandbox.googleapis.com/v1internal",
]

# Default endpoint
DEFAULT_ENDPOINT = CLOUDCODE_ENDPOINTS[0]


@dataclass
class CloudCodeProject:
    """Project info from Cloud Code Assist API."""
    project_id: str
    display_name: Optional[str] = None


class CloudCodeClient:
    """
    Client for Google's Cloud Code Assist API.

    This is the internal API used by Gemini CLI, VS Code Gemini extension, etc.
    It accepts OAuth tokens with cloud-platform scope.
    """

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._project: Optional[CloudCodeProject] = None
        self._endpoint = DEFAULT_ENDPOINT

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _get_access_token(self) -> str:
        """Get current access token, refreshing if needed."""
        cm = get_config_manager()

        # Check if token expired
        if cm.is_google_token_expired():
            cred = cm.get_google_oauth()
            if not cred or not cred.refresh_token:
                raise Exception("Google OAuth token expired. Run 'login google' to re-authenticate.")

            # Refresh token
            source, client_id, client_secret = resolve_oauth_credentials()
            new_cred = await refresh_access_token(
                refresh_token=cred.refresh_token,
                client_id=client_id,
                client_secret=client_secret,
            )
            cm.save_google_oauth(
                GoogleOAuthCredential(
                    access_token=new_cred.access_token,
                    refresh_token=new_cred.refresh_token,
                    expires_at=new_cred.expires_at,
                    email=cred.email,
                ),
                source=source,
            )

        cred = cm.get_google_oauth()
        if not cred:
            raise Exception("No Google OAuth credentials. Run 'login google' first.")
        return cred.access_token

    def _get_headers(self, access_token: str) -> dict:
        """Get request headers for Cloud Code API."""
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "borsaci/0.3.0",
            "X-Goog-Api-Client": "borsaci/0.3.0",
            "Client-Metadata": "ideType=IDE_UNSPECIFIED,platform=PLATFORM_UNSPECIFIED,pluginType=GEMINI",
        }

    async def load_code_assist(self) -> CloudCodeProject:
        """
        Load or create Cloud Code Assist project.

        This is required before making API calls - it provisions a managed GCP project.
        """
        if self._project:
            return self._project

        access_token = await self._get_access_token()
        session = await self._get_session()

        url = f"{self._endpoint}:loadCodeAssist"
        headers = self._get_headers(access_token)

        payload = {
            "metadata": {
                "ideType": "IDE_UNSPECIFIED",
                "platform": "PLATFORM_UNSPECIFIED",
                "pluginType": "GEMINI",
            }
        }

        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"loadCodeAssist failed ({resp.status}): {text}")

            data = await resp.json()

            # Extract project ID from response (OpenClaw pattern)
            # Cloud Code API returns project ID in different fields depending on endpoint
            project_id = (
                data.get("projectId")
                or data.get("cloudaicompanionProject")  # Main field from loadCodeAssist
                or data.get("project", {}).get("projectId")
                or data.get("managedProject", {}).get("projectId")
            )

            if not project_id:
                # Account not onboarded yet - provision a managed project
                project_id = await self._onboard_user(payload["metadata"])

            if not project_id:
                raise Exception(f"No project ID in response: {data}")

            self._project = CloudCodeProject(
                project_id=project_id,
                display_name=data.get("displayName"),
            )
            return self._project

    async def _onboard_user(self, metadata: dict) -> Optional[str]:
        """
        Call onboardUser to provision a managed Code Assist project.

        Required for accounts that have never used Gemini CLI / Code Assist.
        The endpoint is a long-running operation; polled by re-posting until done.
        """
        access_token = await self._get_access_token()
        session = await self._get_session()
        url = f"{self._endpoint}:onboardUser"
        headers = self._get_headers(access_token)
        payload = {"tierId": "free-tier", "metadata": metadata}

        for _ in range(10):
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"onboardUser failed ({resp.status}): {text}")
                data = await resp.json()
                if data.get("done"):
                    project = (data.get("response") or {}).get("cloudaicompanionProject") or {}
                    return project.get("id")
            await asyncio.sleep(2)
        return None

    async def generate_content(
        self,
        model: str,
        contents: list[dict],
        generation_config: Optional[dict] = None,
        system_instruction: Optional[dict] = None,
        tools: Optional[list[dict]] = None,
    ) -> dict:
        """
        Generate content using Cloud Code Assist API.

        Args:
            model: Model name (e.g., "gemini-2.0-flash")
            contents: List of content parts
            generation_config: Optional generation configuration
            system_instruction: Optional system instruction
            tools: Optional list of function declarations for tool calling

        Returns:
            API response dict
        """
        # Ensure we have a project
        project = await self.load_code_assist()

        access_token = await self._get_access_token()
        session = await self._get_session()

        url = f"{self._endpoint}:generateContent"
        headers = self._get_headers(access_token)

        # Build the wrapped request
        request_body = {
            "contents": contents,
        }
        if generation_config:
            request_body["generationConfig"] = generation_config
        if system_instruction:
            request_body["systemInstruction"] = system_instruction
        if tools:
            request_body["tools"] = tools

        payload = {
            "project": project.project_id,
            "model": model,
            "request": request_body,
        }

        # Retry logic for rate limiting (429 errors)
        max_retries = 8
        for attempt in range(max_retries):
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 429:
                    # Rate limited - wait and retry
                    text = await resp.text()
                    try:
                        import json as json_module
                        error_data = json_module.loads(text)
                        # Extract retry delay from response
                        details = error_data.get("error", {}).get("details", [])
                        retry_delay = 1.0  # Default 1 second
                        for detail in details:
                            if "retryDelay" in detail:
                                delay_str = detail["retryDelay"]
                                # Parse "0.594357549s" format
                                retry_delay = float(delay_str.rstrip("s"))
                                break
                    except:
                        retry_delay = 1.0

                    # Advertised retryDelay is often shorter than the real
                    # throttle window on free tier - enforce exponential floor
                    retry_delay = min(max(retry_delay, 2.0 * (2 ** attempt)), 45.0)

                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay + 0.1)  # Add small buffer
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} retries")

                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"generateContent failed ({resp.status}): {text}")

                return await resp.json()

    async def stream_generate_content(
        self,
        model: str,
        contents: list[dict],
        generation_config: Optional[dict] = None,
        system_instruction: Optional[dict] = None,
    ) -> AsyncIterator[dict]:
        """
        Stream generate content using Cloud Code Assist API.

        Args:
            model: Model name (e.g., "gemini-2.0-flash")
            contents: List of content parts
            generation_config: Optional generation configuration
            system_instruction: Optional system instruction

        Yields:
            Streamed response chunks
        """
        # Ensure we have a project
        project = await self.load_code_assist()

        access_token = await self._get_access_token()
        session = await self._get_session()

        url = f"{self._endpoint}:streamGenerateContent?alt=sse"
        headers = self._get_headers(access_token)

        # Build the wrapped request
        request_body = {
            "contents": contents,
        }
        if generation_config:
            request_body["generationConfig"] = generation_config
        if system_instruction:
            request_body["systemInstruction"] = system_instruction

        payload = {
            "project": project.project_id,
            "model": model,
            "request": request_body,
        }

        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"streamGenerateContent failed ({resp.status}): {text}")

            # Parse SSE stream
            async for line in resp.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data and data != '[DONE]':
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            pass

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


# Singleton instance
_cloudcode_client: Optional[CloudCodeClient] = None


def get_cloudcode_client() -> CloudCodeClient:
    """Get singleton CloudCodeClient instance."""
    global _cloudcode_client
    if _cloudcode_client is None:
        _cloudcode_client = CloudCodeClient()
    return _cloudcode_client


async def test_cloudcode_api():
    """Test the Cloud Code API connection."""
    client = get_cloudcode_client()

    try:
        # Load project
        project = await client.load_code_assist()
        print(f"✅ Project loaded: {project.project_id}")

        # Test generate content
        response = await client.generate_content(
            model="gemini-2.0-flash",
            contents=[{
                "role": "user",
                "parts": [{"text": "Say hello in Turkish in one sentence."}]
            }],
        )

        # Extract text from response
        text = response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print(f"✅ Response: {text}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    finally:
        await client.close()
