import argparse
import csv
import os
import sys
import yagmail

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(__file__))
from config import ROOT_DIR, get_email_credentials
from classes.Outreach import Outreach


def load_queue(path):
    if not os.path.exists(path): raise SystemExit(f"Queue not found: {path}")
    with open(path,encoding="utf-8",newline="") as f: return list(csv.DictReader(f))


def save_queue(path,rows):
    if not rows: return
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queue", default=os.path.join(ROOT_DIR, "data", "outreach_queue.csv"))
    args = p.parse_args()
    rows = load_queue(args.queue)
    creds = get_email_credentials()
    sender = Outreach()
    yag = None

    history_file = os.path.join(ROOT_DIR, ".mp", "sent_emails_history.txt")
    sent_history = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as hf:
            sent_history = {line.strip().lower() for line in hf if line.strip()}

    for row in rows:
        if row.get("status") not in ("ready", ""):
            continue
        email = row.get("email", "").strip().lower()
        domain = row.get("url", "").split("//")[-1].split("/")[0].replace("www.", "").strip().lower()
        if email in sent_history or domain in sent_history:
            print(f"\nSkipping already contacted lead: {row.get('company')} ({email})")
            row["status"] = "already_sent"
            save_queue(args.queue, rows)
            continue

        print("\n" + "=" * 70)
        print(f'{row.get("company")} | {row.get("url")}')
        contact_info = f"{row.get('contact_name')} <{row.get('email')}>" if row.get("contact_name") else row.get("email")
        print(f'Contact: {contact_info} ({row.get("role") or "unknown role"})')
        print(f'Perf {row.get("lighthouse_score")} | LCP {row.get("lcp_ms")}ms | TBT {row.get("tbt_ms")}ms')
        print(f'\nSubject: {row.get("subject")}\n\n{row.get("message")}\n')
        try:
            action = input("[S] Send  [K] Skip  [E] Edit  [B] Blacklist  [Q] Quit: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if action == "q":
            break
        if action == "k":
            row["status"] = "skipped"
            save_queue(args.queue, rows)
            continue
        if action == "b":
            row["status"] = "blacklisted"
            save_queue(args.queue, rows)
            continue
        if action == "e":
            try:
                row["subject"] = input("Subject: ").strip() or row["subject"]
                print("Enter one-line message (blank keeps current):")
                msg = input().strip()
                if msg:
                    row["message"] = msg
            except (EOFError, KeyboardInterrupt):
                break
            save_queue(args.queue, rows)
            continue
        if action != "s":
            continue
        email = row.get("email", "").strip()
        if not email or not sender.is_valid_mx(email):
            print("Invalid/missing MX; not sent.")
            row["status"] = "invalid_email"
            save_queue(args.queue, rows)
            continue
        try:
            confirm = input(f"Type SEND to confirm delivery to {email}: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if confirm != "SEND":
            continue
        if yag is None:
            yag = yagmail.SMTP(user=creds["username"], password=creds["password"], port=int(creds.get("smtp_port", 465)))
        try:
            yag.send(to=email, subject=row["subject"], contents=row["message"])
            row["status"] = "sent"
            print("Sent.")
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, "a", encoding="utf-8") as hf:
                hf.write(email.lower().strip() + "\n")
                if domain:
                    hf.write(domain + "\n")
            sent_history.add(email.lower().strip())
            if domain:
                sent_history.add(domain)
        except Exception as exc:
            row["status"] = "send_error"
            row["send_error"] = str(exc)
            print(f"Send failed: {exc}")
        save_queue(args.queue, rows)


if __name__=="__main__": main()
