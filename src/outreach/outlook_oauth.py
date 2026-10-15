"""Outlook OAuth2 token manager for modern authentication.

Supports personal Outlook.com / Hotmail accounts via OAuth2 device code flow and token refresh.
"""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"  # Thunderbird public client ID for Microsoft
SCOPE = "https://outlook.office.com/SMTP.Send offline_access"
DEVICE_ENDPOINT = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
TOKEN_ENDPOINT = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
TOKEN_PATH = Path(".mp/outlook_token.json")


def get_stored_token() -> dict | None:
    if TOKEN_PATH.exists():
        try:
            with open(TOKEN_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_token(token_data: dict) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)


def refresh_token(refresh_tok: str) -> dict:
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok,
        "scope": SCOPE,
    }).encode("utf-8")
    req = urllib.request.Request(TOKEN_ENDPOINT, data=data)
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read().decode("utf-8"))
        tokens["expires_at"] = time.time() + tokens.get("expires_in", 3600)
        save_token(tokens)
        return tokens


def get_valid_access_token() -> str | None:
    tok = get_stored_token()
    if not tok:
        return None
    # Refresh if expiring within 5 minutes
    if time.time() >= tok.get("expires_at", 0) - 300:
        if "refresh_token" in tok:
            try:
                tok = refresh_token(tok["refresh_token"])
            except Exception:
                return None
        else:
            return None
    return tok.get("access_token")
