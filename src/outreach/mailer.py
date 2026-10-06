"""Plain-text outreach mailer with clean headers and sender-domain deliverability checks.

Replaces yagmail for outreach: yagmail stamps Message-ID with "@yagmail" and
turns newlines into "<br>" (HTML), both of which look automated to spam filters.
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

FREEMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "live.com", "icloud.com", "proton.me", "protonmail.com", "aol.com",
}


def sender_domain(address: str) -> str:
    return address.rsplit("@", 1)[-1].strip().lower() if "@" in address else ""


def is_freemail(address: str) -> bool:
    return sender_domain(address) in FREEMAIL_DOMAINS


def build_message(sender: dict, from_addr: str, to_addr: str, subject: str, body: str) -> EmailMessage:
    """Build a plain-text message: real display name, real Message-ID, no HTML."""
    msg = EmailMessage()
    msg["From"] = formataddr((sender["full_name"], from_addr))
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=sender_domain(from_addr))
    if sender.get("reply_to"):
        msg["Reply-To"] = sender["reply_to"]
    msg["List-Unsubscribe"] = f"<mailto:{from_addr}?subject=unsubscribe>"
    msg.set_content(body.replace("\r\n", "\n"), charset="utf-8")
    return msg


def send_message(email_cfg: dict, msg: EmailMessage) -> None:
    server, port = email_cfg["smtp_server"], int(email_cfg.get("smtp_port", 465))
    if port == 465:
        with smtplib.SMTP_SSL(server, port, timeout=20, context=ssl.create_default_context()) as smtp:
            smtp.login(email_cfg["username"], email_cfg["password"])
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(server, port, timeout=20) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(email_cfg["username"], email_cfg["password"])
            smtp.send_message(msg)


def verify_mailbox_smtp(email: str, sender_addr: str = "ivanbradic46@gmail.com", timeout: int = 8) -> bool:
    """Check if the mailbox actually exists via SMTP RCPT TO probe.
    Returns True if 250 OK or server doesn't support RCPT probes.
    Returns False only on definitive rejection (500-554 User unknown / mailbox rejected).
    """
    if not email or "@" not in email:
        return False
    domain = email.split("@")[1].strip().lower()
    import dns.resolver

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    resolver.lifetime = 6
    try:
        answers = resolver.resolve(domain, "MX", tcp=True)
        mx_host = sorted(answers, key=lambda r: r.preference)[0].exchange.to_text()
        with smtplib.SMTP(mx_host, 25, timeout=timeout) as s:
            s.helo("gmail.com")
            s.mail(sender_addr)
            code, _ = s.rcpt(email)
            if 500 <= code <= 554:
                return False
            return True
    except Exception:
        # If server blocks port 25 or greylists, allow by default
        return True


def _txt_records(name: str) -> list:
    import dns.resolver

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    resolver.lifetime = 8
    try:
        answers = resolver.resolve(name, "TXT", tcp=True)
    except Exception:
        return []
    return ["".join(part.decode() for part in rdata.strings) for rdata in answers]


def check_domain_auth(domain: str, dkim_selector: str = "") -> dict:
    """Look up SPF, DKIM (needs selector) and DMARC for the sending domain."""
    spf = [t for t in _txt_records(domain) if t.lower().startswith("v=spf1")]
    dmarc = [t for t in _txt_records(f"_dmarc.{domain}") if t.lower().startswith("v=dmarc1")]
    dkim = []
    if dkim_selector:
        dkim = [t for t in _txt_records(f"{dkim_selector}._domainkey.{domain}") if "p=" in t]
    return {
        "spf": bool(spf),
        "dkim": bool(dkim) if dkim_selector else None,
        "dmarc": bool(dmarc),
        "dmarc_policy": next(
            (p.split("=")[1].strip() for t in dmarc for p in t.replace(" ", "").split(";") if p.lower().startswith("p=")),
            "",
        ),
    }


def send_gate_problems(sender: dict, from_addr: str, auth: dict | None = None) -> list:
    """Reasons sending must be refused. Empty list means OK to send."""
    problems = []
    if is_freemail(from_addr):
        if not sender.get("allow_freemail_sender"):
            problems.append(
                f"Sender {from_addr} is on a free-mail domain; use a dedicated domain address "
                "(set outreach_sender.allow_freemail_sender=true only to override)."
            )
        return problems

    if auth is not None:
        if not auth["spf"]:
            problems.append("SPF record missing for sender domain.")
        if auth["dkim"] is None:
            problems.append("outreach_sender.dkim_selector not set, DKIM cannot be verified.")
        elif not auth["dkim"]:
            problems.append("DKIM record not found for the configured selector.")
        if not auth["dmarc"]:
            problems.append("DMARC record missing for sender domain.")
    return problems
