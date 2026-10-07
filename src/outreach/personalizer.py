import html
import re


class Personalizer:
    @staticmethod
    def detect_language(row: dict) -> str:
        """Infer target language ('sr' or 'en') from row, url, or domain TLD."""
        explicit = (row.get("language") or row.get("lang") or "").lower()
        if explicit in ("sr", "bs", "hr", "srb", "balkan"):
            return "sr"
        if explicit in ("en", "eng"):
            return "en"
        query = str(row.get("query") or "").lower()
        if any(w in query for w in ("srbij", "beograd", "novi sad", "nis", "zlatibor", "stanov", "kuc", "ordinacij", "hirurgij", "apartman")):
            return "sr"
        url = (row.get("url") or "").lower()
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        tld = domain.split(".")[-1]
        if tld in ("rs", "ba", "me", "hr", "srb", "si", "mk"):
            return "sr"
        return "en"

    @staticmethod
    def infer_business_type(row: dict, lang: str = "en") -> str:
        """Infer business category for the copy."""
        text = " ".join([
            str(row.get("company_name") or ""),
            str(row.get("company") or ""),
            str(row.get("url") or ""),
            str(row.get("query") or ""),
            str(row.get("role") or ""),
        ]).lower()

        if any(w in text for w in ("architect", "arhitekt", "enterijer", "interior", "dizajn enterijera")):
            return "arhitektonskih i dizajnerskih studija" if lang == "sr" else "an architecture or design studio"
        if any(w in text for w in ("solicitor", "lawyer", "attorney", "law", "advokat", "pravn")):
            return "advokatskih kancelarija" if lang == "sr" else "a law firm"
        if any(w in text for w in ("nekretnin", "estate", "property", "stanov", "real estate", "agencija za nekretnine", "apartman", "novogradn")):
            return "agencija za nekretnine i investitora" if lang == "sr" else "an estate agency"
        if any(w in text for w in ("montazn", "brvnar", "kuce", "gradjev", "drvenekuce")):
            return "proizvođača i graditelja kuća" if lang == "sr" else "a home builder"
        if any(w in text for w in ("dental", "dentist", "stomatolog", "klinik", "clinic", "ordinacij", "hirurg", "estetsk", "medic")):
            return "privatnih klinika i ordinacija" if lang == "sr" else "a private clinic"
        return "uslužnih firmi" if lang == "sr" else "service businesses"

    @staticmethod
    def finding(row: dict, lang: str = "en") -> tuple[str, str, str]:
        """Return (subject_finding, cause_description, fix_sentence)."""
        lcp_ms = float(row.get("lcp_ms") or 0)
        sec = round(lcp_ms / 1000, 1) if lcp_ms > 0 else 5.2
        sec_str = f"{sec:.1f}"
        sec_str_sr = sec_str.replace(".", ",")

        primary = row.get("primary_issue") or ""
        savings_kb = float(row.get("estimated_savings_kb") or row.get("transfer_kb") or 1600)
        savings_mb = round(savings_kb / 1024, 1)
        savings_mb_str = f"{savings_mb:.1f}"
        savings_mb_sr = savings_mb_str.replace(".", ",")

        if primary == "image_delivery" or float(row.get("images") or 0) >= 15:
            if lang == "sr":
                return (
                    f"sajt se na telefonu učitava {sec_str_sr} sekundi",
                    f"neoptimizovanih slika (oko {savings_mb_sr} MB nepotrebnog tereta)",
                    "Kompresija tih slika i prelazak na modernije formate bi najverovatnije spustili učitavanje ispod 3 sekunde.",
                )
            return (
                f"homepage takes about {sec_str}s on mobile",
                f"an uncompressed {savings_mb_str} MB of image weight",
                "Compressing those images and serving modern formats would likely bring it under 3 seconds.",
            )

        if primary == "render_blocking":
            if lang == "sr":
                return (
                    f"skripte usporavaju prikaz na telefonu ({sec_str_sr}s)",
                    "skripti i stilova koji blokiraju početno renderovanje ekrana",
                    "Odlaganje tih skripti i optimizacija učitavanja bi najverovatnije spustili učitavanje ispod 3 sekunde.",
                )
            return (
                f"scripts delay mobile display ({sec_str}s)",
                "render-blocking scripts and styles that delay the initial display",
                "Deferring non-critical scripts and streamlining CSS would likely bring it under 3 seconds.",
            )

        if primary == "unused_javascript":
            if lang == "sr":
                return (
                    f"skripte usporavaju mobilni prikaz ({sec_str_sr}s)",
                    "koda i eksternih skripti koje se nepotrebno učitavaju pre nego što je stranica spremna",
                    "Odlaganje tih skripti i njihovo učitavanje po potrebi bi najverovatnije spustilo učitavanje ispod 3 sekunde.",
                )
            return (
                f"scripts delay mobile usability ({sec_str}s)",
                "unused JavaScript and third-party scripts loading before the page is usable",
                "Deferring those scripts and loading them only when needed would likely bring it under 3 seconds.",
            )

        # Fallback based on overall heavy transfer
        if lang == "sr":
            return (
                f"sajt se na telefonu učitava {sec_str_sr} sekundi",
                f"velike težine stranice (oko {savings_mb_sr} MB) koja usporava telefon",
                "Optimizacija najtežih resursa i keširanja bi najverovatnije spustila učitavanje ispod 3 sekunde.",
            )
        return (
            f"homepage takes about {sec_str}s on mobile",
            f"heavy page assets ({savings_mb_str} MB) delaying mobile rendering",
            "Compressing the heaviest assets and tuning browser caching would likely bring it under 3 seconds.",
        )

    @staticmethod
    def sender_missing(sender):
        """Return the config keys that must be set before any email is sent."""
        required = ("full_name", "portfolio_url", "proof_result")
        return [key for key in required if not (sender.get(key) or "").strip()]

    @staticmethod
    def signature(sender, lang: str = "en"):
        lines = [sender["full_name"]]
        if lang == "sr":
            title = sender.get("title_sr") or "Web Developer & Conversion Specialist"
            proof = sender.get("proof_result_sr") or "Ubrzan mobilni sajt sa 5,1s na 3,5s (54% manja stranica)"
        else:
            title = sender.get("title") or "Web performance & WordPress developer"
            proof = sender.get("proof_result") or "Cut a client's mobile load from 5.1s to 3.5s"
        lines.append(title)

        portfolio = sender.get("portfolio_url", "").strip()
        if portfolio and proof:
            lines.append(f"{portfolio} · {proof}")
        elif portfolio:
            lines.append(portfolio)
        return "\n".join(lines)

    @classmethod
    def draft(cls, row, sender=None):
        if sender is None:
            try:
                from config import get_outreach_sender_config
            except ImportError:
                from src.config import get_outreach_sender_config
            sender = get_outreach_sender_config()

        company = html.unescape(
            row.get("company_name")
            or row.get("company")
            or row.get("url", "").split("//")[-1].split("/")[0].replace("www.", "")
        )
        url = row.get("url", "")
        domain = url.split("//")[-1].split("/")[0].replace("www.", "") or company
        first_name = (row.get("first_name") or "").strip()
        generic_first_names = {
            "stanovi", "stan", "nekretnine", "agencija", "prodaja", "izdavanje",
            "office", "info", "kontakt", "upit", "podrska", "admin", "mail", "posao",
            "novisad", "beograd", "nis", "kragujevac", "subotica", "mostar"
        }
        if (
            len(first_name) <= 1
            or first_name.lower() == company.lower()
            or "doo" in first_name.lower()
            or first_name.lower() in generic_first_names
            or any(
                company.lower().startswith(first_name.lower() + sfx)
                for sfx in (" nekretnine", " doo", " d.o.o.", " agency", " ltd")
            )
        ):
            first_name = ""

        lang = cls.detect_language(row)
        finding_subj, cause, fix = cls.finding(row, lang=lang)
        biz_type = cls.infer_business_type(row, lang=lang)

        lcp_ms = float(row.get("lcp_ms") or 0)
        sec = round(lcp_ms / 1000, 1) if lcp_ms > 0 else 5.2
        sec_str = f"{sec:.1f}"
        sec_str_sr = sec_str.replace(".", ",")

        if lang == "sr":
            greeting = f"Zdravo {first_name}," if first_name else "Zdravo,"
            subject = f"{company} – {finding_subj} (curenje upita)"
            p1 = (
                f"Pogledao sam {domain} na telefonu: početna stranica postane upotrebljiva "
                f"tek posle oko {sec_str_sr} sekundi, uglavnom zbog {cause}."
            )
            p2 = (
                f"Kod {biz_type} većina ljudi ponudu gleda sa telefona. "
                "Problem sa sporim učitavanjem je što posetioci odustanu, pa upiti i pozivi bukvalno cure pre nego što uopšte vide vašu ponudu."
            )
            p3 = (
                f"{fix} Mogu da vam pošaljem kratku analizu sa 3 konkretne stvari koje možete odmah popraviti, "
                "bez ikakvih obaveza. Vredi li da vam pošaljem?"
            )
            paragraphs = [greeting, p1, f"{p2}\n\n{p3}", cls.signature(sender, lang="sr")]
        else:
            greeting = f"Hi {first_name}," if first_name else "Hi,"
            subject = f"{company} – {finding_subj}"
            p1 = (
                f"I ran {domain} through PageSpeed on mobile: the homepage takes about "
                f"{sec_str} seconds to become usable, mostly because of {cause}."
            )
            p2 = (
                f"For {biz_type} that's usually where enquiries get lost, "
                f"since most people check on their phone first. {fix}"
            )
            p3 = (
                "I can send you a short list of the 3 fixes I'd make first, "
                "no strings attached. Want me to?"
            )
            paragraphs = [greeting, p1, f"{p2}\n\n{p3}", cls.signature(sender, lang="en")]

        return subject, "\n\n".join(paragraphs)

