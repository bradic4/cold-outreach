"""Outlook OAuth2 Device Flow authenticator and token manager.

Enables programmatic sending via personal Outlook.com / Hotmail accounts using
Microsoft's required Modern Authentication (OAuth2 / XOAUTH2).
"""
import json
import os
import sys
import time
import ssl
import smtplib
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
    # If expires in less than 5 minutes, refresh
    if time.time() >= tok.get("expires_at", 0) - 300:
        if "refresh_token" in tok:
            try:
                tok = refresh_token(tok["refresh_token"])
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None
        else:
            return None
    return tok.get("access_token")


def start_device_flow():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "scope": SCOPE,
    }).encode("utf-8")
    req = urllib.request.Request(DEVICE_ENDPOINT, data=data)
    with urllib.request.urlopen(req) as resp:
        device_resp = json.loads(resp.read().decode("utf-8"))

    user_code = device_resp["user_code"]
    device_code = device_resp["device_code"]
    interval = device_resp.get("interval", 5)
    expires_in = device_resp.get("expires_in", 900)

    print("\n" + "=" * 60)
    print("AUTENTIFIKACIJA ZA OUTLOOK:")
    print("1. Otvori u browseru: https://www.microsoft.com/link")
    print(f"2. Unesi kod: {user_code}")
    print("3. Prijavi se sa ivan.bradic@outlook.com i potvrdi pristup.")
    print("=" * 60 + "\n")
    sys.stdout.flush()

    # Poll token endpoint
    start_time = time.time()
    poll_data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
    }).encode("utf-8")

    while time.time() - start_time < expires_in:
        time.sleep(interval)
        poll_req = urllib.request.Request(TOKEN_ENDPOINT, data=poll_data)
        try:
            with urllib.request.urlopen(poll_req) as resp:
                token_result = json.loads(resp.read().decode("utf-8"))
                token_result["expires_at"] = time.time() + token_result.get("expires_in", 3600)
                save_token(token_result)
                print("\n[USPEH] Token je uspesno sacuvan!")
                return token_result
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                err = err_json.get("error")
                if err == "authorization_pending":
                    # Still waiting for user
                    continue
                elif err == "slow_down":
                    interval += 5
                    continue
                else:
                    print(f"\n[GRESKA]: {err_json.get('error_description', err)}")
                    return None
            except Exception:
                print(f"\n[GRESKA HTTP {e.code}]: {err_body}")
                return None
    print("\n[ISTEKLO VREME] Nije potvrdjeno u roku od 15 minuta.")
    return None


def test_smtp_auth(username: str = "ivan.bradic@outlook.com"):
    access_token = get_valid_access_token()
    if not access_token:
        print("Nema validnog tokena.")
        return False
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    
    server = "smtp-mail.outlook.com"
    port = 587
    print(f"Povezujem se na {server}:{port}...")
    try:
        with smtplib.SMTP(server, port, timeout=20) as s:
            s.ehlo()
            s.starttls(context=ssl.create_default_context())
            s.ehlo()
            res = s.auth("XOAUTH2", lambda: auth_string)
            print(f"[SMTP USPESNO] Server odgovor: {res}")
            return True
    except Exception as e:
        print(f"[SMTP GRESKA]: {e}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Test stored token")
    args = parser.parse_args()

    if args.test:
        test_smtp_auth()
    else:
        tok = start_device_flow()
        if tok:
            test_smtp_auth()
