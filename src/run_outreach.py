"""
Outreach-only launcher for MoneyPrinter V2.
Skips YouTube/Twitter/TTS/Ollama dependencies — runs only the Outreach module.

Usage:
    python src/run_outreach.py
"""

import os
import sys

# Fix Windows console encoding for emoji/unicode characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Make sure src/ modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from config import ROOT_DIR, assert_folder_structure
from status import info, success, error, warning
from classes.Outreach import Outreach
from termcolor import colored


def main():
    print(colored("""
 $$\\      $$\\  $$$$$$\\  $$\\   $$\\ $$$$$$$$\\ $$\\     $$\\ 
 $$$\\    $$$ |$$  __$$\\ $$$\\  $$ |$$  _____|\\$$\\   $$  |
 $$$$\\  $$$$ |$$ /  $$ |$$$$\\ $$ |$$ |       \\$$\\ $$  / 
 $$\\$$\\$$ $$ |$$ |  $$ |$$ $$\\$$ |$$$$$\\      \\$$$$  /  
 $$ \\$$$  $$ |$$ |  $$ |$$ \\$$$$ |$$  __|      \\$$  /   
 $$ |\\$  /$$ |$$ |  $$ |$$ |\\$$$ |$$ |          $$ |    
 $$ | \\_/ $$ | $$$$$$  |$$ | \\$$ |$$$$$$$$\\     $$ |    
 \\__|     \\__| \\______/ \\__|  \\__|\\________|    \\__|    
                                                         
        MoneyPrinter V2 — OUTREACH MODE
    """, "green"))

    # Setup folder structure
    assert_folder_structure()

    info("Starting Outreach...\n")

    # Show current config
    from config import (
        get_google_maps_scraper_niche,
        get_outreach_message_subject,
        get_outreach_message_body_file,
        get_email_credentials,
    )

    niche = get_google_maps_scraper_niche()
    subject = get_outreach_message_subject()
    body_file = get_outreach_message_body_file()
    email_creds = get_email_credentials()

    print(colored("============ OUTREACH CONFIG ============", "cyan"))
    print(colored(f"  Niche:         {niche}", "cyan"))
    print(colored(f"  Email Subject: {subject}", "cyan"))
    print(colored(f"  Email Body:    {body_file}", "cyan"))
    print(colored(f"  SMTP Server:   {email_creds['smtp_server']}", "cyan"))
    print(colored(f"  SMTP User:     {email_creds['username']}", "cyan"))
    print(colored("=========================================\n", "cyan"))

    # Validate config before running
    problems = []
    if not niche or niche.strip() == "":
        problems.append("google_maps_scraper_niche is empty in config.json")
    if email_creds["username"] == "TVOJ_EMAIL@gmail.com" or not email_creds["username"]:
        problems.append("email.username is not set in config.json")
    if email_creds["password"] == "TVOJ_APP_PASSWORD" or not email_creds["password"]:
        problems.append("email.password is not set in config.json")
    if not os.path.exists(os.path.join(ROOT_DIR, body_file)):
        problems.append(f"Email body file '{body_file}' not found in project root")

    if problems:
        error("Config problems found:")
        for p in problems:
            print(colored(f"  ❌ {p}", "red"))
        print()
        error("Fix these in config.json and try again.")
        sys.exit(1)

    targets_file = os.path.join(ROOT_DIR, "targets.txt")
    manual_targets = []
    if os.path.exists(targets_file):
        with open(targets_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    manual_targets.append(line)

    if manual_targets:
        success(f"Pronađeno {len(manual_targets)} stavki u targets.txt za direktno slanje!\n")
        import yagmail
        import requests
        import re

        yag = yagmail.SMTP(
            user=email_creds["username"],
            password=email_creds["password"],
            port=465
        )

        with open(os.path.join(ROOT_DIR, body_file), "r", encoding="utf-8") as f:
            raw_body = f.read()

        for idx, target in enumerate(manual_targets, 1):
            try:
                receiver_email = ""
                company_name = "biznis"

                if "@" in target and not target.startswith("http"):
                    receiver_email = target
                else:
                    info(f"[{idx}/{len(manual_targets)}] Tražim email na sajtu: {target}")
                    r = requests.get(target, verify=False, timeout=10)
                    if r.status_code == 200:
                        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
                        found = re.findall(email_pattern, r.text)
                        if found:
                            receiver_email = found[0]

                if not receiver_email:
                    warning(f" => Email nije pronađen za {target}. Preskačem...")
                    continue

                subject = subject.replace("{{COMPANY_NAME}}", company_name)
                body = raw_body.replace("{{COMPANY_NAME}}", company_name)

                info(f" => Šaljem mejl na {receiver_email}...")
                yag.send(to=receiver_email, subject=subject, contents=body)
                success(f" => Uspešno poslato na {receiver_email}")
            except Exception as err:
                error(f" => Greška za {target}: {err}")

        success("\nDirektno slanje iz targets.txt završeno!")
        return

    try:
        outreach = Outreach()
        outreach.start()
    except Exception as e:
        error(f"Outreach failed: {e}")
        sys.exit(1)

    success("\nOutreach process completed!")


if __name__ == "__main__":
    main()
