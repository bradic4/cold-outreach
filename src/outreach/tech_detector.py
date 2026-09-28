import re


class TechDetector:
    """Detect common website technologies from fetched HTML."""

    SIGNALS = {
        "wordpress": ("/wp-content/", "/wp-includes/", "wp-json", 'generator" content="wordpress'),
        "elementor": ("elementor-element", "elementor-widget", "/plugins/elementor/"),
        "woocommerce": ("woocommerce", "wc-cart", "wc-block", "/plugins/woocommerce/"),
        "gtm": ("googletagmanager.com", "gtm-"),
        "meta_pixel": ("connect.facebook.net", "fbq("),
        "hotjar": ("hotjar.com", "hj("),
        "clarity": ("clarity.ms",),
    }

    @classmethod
    def detect(cls, html: str) -> dict:
        text = (html or "").lower()
        return {name: any(signal in text for signal in signals) for name, signals in cls.SIGNALS.items()}
