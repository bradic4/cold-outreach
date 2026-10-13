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

        if any(w in text for w in ("auto servis", "autoservis", "mehanic", "vulkanizer", "auto repair", "garage")):
            return "auto servisa i radionica" if lang == "sr" else "auto repair workshops"
        if any(w in text for w in ("knjigovod", "racunovod", "bilans", "accountant", "accounting")):
            return "knjigovodstvenih i računovodstvenih agencija" if lang == "sr" else "accounting firms"
        if any(w in text for w in ("namestaj", "kuhinj", "kitchen", "joinery", "furniture", "woodcraft", "carpentry", "wardrobe", "cabinet")):
            return "firmi za izradu nameštaja po meri" if lang == "sr" else "bespoke kitchen and joinery companies"
        if any(w in text for w in ("stamparij", "print", "štamp")):
            return "štamparija i grafičkih studija" if lang == "sr" else "printing and graphics studios"
        if any(w in text for w in ("stolarij", "pvc", "alu stolarij", "window", "conservator", "glazing", "doors")):
            return "firmi za proizvodnju i ugradnju stolarije" if lang == "sr" else "window and door specialists"
        if any(w in text for w in ("architect", "arhitekt", "enterijer", "interior", "dizajn enterijera")):
            return "arhitektonskih i dizajnerskih studija" if lang == "sr" else "architecture and interior design studios"
        if any(w in text for w in ("solicitor", "lawyer", "attorney", "law", "advokat", "pravn")):
            return "advokatskih kancelarija" if lang == "sr" else "law firms"
        if any(w in text for w in ("nekretnin", "estate", "property", "stanov", "real estate", "agencija za nekretnine", "apartman", "novogradn")):
            return "agencija za nekretnine i investitora" if lang == "sr" else "estate agencies"
        if any(w in text for w in ("montazn", "brvnar", "kuce", "gradjev", "drvenekuce", "home builder", "construction", "renovation", "roofing")):
            return "proizvođača i graditelja kuća" if lang == "sr" else "home builders and specialist contractors"
        if any(w in text for w in ("dental", "dentist", "stomatolog", "klinik", "clinic", "ordinacij", "hirurg", "estetsk", "medic")):
            return "privatnih klinika i ordinacija" if lang == "sr" else "private clinics"
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
        lines = []
        lines.append("Pozdrav," if lang == "sr" else "Best,")
        lines.append(sender["full_name"])
        portfolio = sender.get("portfolio_url", "").strip().replace("https://", "").replace("http://", "").rstrip("/")
        if portfolio:
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

            # A/B testing on subject line
            ab_variant = (row.get("ab_variant") or "").upper().strip()
            if ab_variant not in ("A", "B"):
                key = str(row.get("email") or row.get("url") or "")
                ab_variant = "A" if (sum(ord(c) for c in key) % 2 == 0) else "B"

            if ab_variant == "A":
                subject = f"Prezentacija za {company} - curenje konverzija i posetilaca na sajtu"
            else:
                subject = "Kratka sugestija za vaš sajt"

            is_studio = any(w in biz_type for w in ("studij", "dizajn", "arhitekt"))
            target_entity = "vašeg studija" if is_studio else "vaše firme"
            showcase_item = "projekte" if is_studio else "ponudu i usluge"

            p1 = (
                f"Pogledao sam sajt {target_entity} i primetio nekoliko stvari koje bi mogle da se unaprede, "
                "posebno kada ga potencijalni klijenti otvaraju sa telefona."
            )
            p2 = (
                f"Kod {biz_type} sajt često predstavlja prvi kontakt sa budućim klijentom. "
                f"Zato je važno da brzo prikaže {showcase_item} i omogući posetiocima da lako stupe u kontakt."
            )
            p3 = (
                "Bavim se optimizacijom web sajtova i imam nekoliko konkretnih predloga kako biste mogli da poboljšate korisničko iskustvo i povećate šanse za nove upite.\n\n"
                "Mogu da vam pošaljem kratku besplatnu analizu sa 3 stvari koje bih prvo promenio.\n\n"
                "Da li biste želeli da je pogledate?"
            )
            paragraphs = [greeting, p1, p2, p3, cls.signature(sender, lang="sr")]
        else:
            greeting = f"Hi {first_name}," if first_name else "Hi,"

            ab_variant = (row.get("ab_variant") or "").upper().strip()
            if ab_variant not in ("A", "B"):
                key = str(row.get("email") or row.get("url") or "")
                ab_variant = "A" if (sum(ord(c) for c in key) % 2 == 0) else "B"

            if ab_variant == "A":
                subject = f"Quick question about {company}'s website"
            else:
                subject = "Quick suggestion for your website"

            p1 = (
                "I had a look at your company's website and noticed a few things that could be improved, "
                "especially when potential clients open it on their mobile phone."
            )
            p2 = (
                f"For {biz_type}, the website is usually the first point of contact with a future client. "
                "That's why it's important that it quickly showcases your work and services and makes it effortless for visitors to get in touch."
            )
            p3 = (
                "I specialize in website optimization and have a few specific ideas on how you could improve the mobile experience and increase enquiries.\n\n"
                "I can send over a short free breakdown with the 3 things I'd change first.\n\n"
                "Would you like to take a look at it?"
            )
            paragraphs = [greeting, p1, p2, p3, cls.signature(sender, lang="en")]

        return subject, "\n\n".join(paragraphs)

