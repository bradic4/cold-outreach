import argparse
import csv
import os
import sys
import yagmail

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
    p=argparse.ArgumentParser(); p.add_argument("--queue",default=os.path.join(ROOT_DIR,"data","outreach_queue.csv"))
    args=p.parse_args(); rows=load_queue(args.queue)
    creds=get_email_credentials(); sender=Outreach(); yag=None
    for row in rows:
        if row.get("status") not in ("ready",""): continue
        print("\n"+"="*70)
        print(f'{row.get("company")} | {row.get("url")}')
        print(f'Contact: {row.get("email")} ({row.get("role") or "unknown role"})')
        print(f'Perf {row.get("lighthouse_score")} | LCP {row.get("lcp_ms")}ms | TBT {row.get("tbt_ms")}ms')
        print(f'\nSubject: {row.get("subject")}\n\n{row.get("message")}\n')
        action=input("[S] Send  [K] Skip  [E] Edit  [B] Blacklist  [Q] Quit: ").strip().lower()
        if action=="q": break
        if action=="k": row["status"]="skipped"; save_queue(args.queue,rows); continue
        if action=="b": row["status"]="blacklisted"; save_queue(args.queue,rows); continue
        if action=="e":
            row["subject"]=input("Subject: ").strip() or row["subject"]
            print("Enter one-line message (blank keeps current):")
            msg=input().strip()
            if msg: row["message"]=msg
            save_queue(args.queue,rows); continue
        if action!="s": continue
        email=row.get("email","").strip()
        if not email or not sender.is_valid_mx(email):
            print("Invalid/missing MX; not sent."); row["status"]="invalid_email"; save_queue(args.queue,rows); continue
        confirm=input(f"Type SEND to confirm delivery to {email}: ").strip()
        if confirm!="SEND": continue
        if yag is None:
            yag=yagmail.SMTP(user=creds["username"],password=creds["password"],port=int(creds.get("smtp_port",465)))
        try:
            yag.send(to=email,subject=row["subject"],contents=row["message"])
            row["status"]="sent"; print("Sent.")
        except Exception as exc:
            row["status"]="send_error"; row["send_error"]=str(exc); print(f"Send failed: {exc}")
        save_queue(args.queue,rows)


if __name__=="__main__": main()
