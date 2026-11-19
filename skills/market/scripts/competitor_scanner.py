#!/usr/bin/env python3
"""
Competitor Scanner — Utility script for AI Marketing Claude Code Skills
Scans competitor websites to extract positioning, pricing, features, and trust signals
for competitive analysis.
"""

import sys
import json
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser
from urllib.parse import urlparse


class CompetitorPageParser(HTMLParser):
    """Parse competitor page for positioning data."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.og_title = ""
        self.og_description = ""
        self.h1_tags = []
        self.h2_tags = []
        self.pricing_indicators = []
        self.social_links = []
        self.trust_signals = []
        self.ctas = []
        self.testimonial_count = 0
        self.logo_count = 0

        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_a = False
        self._in_button = False
        self._current_text = ""
        self._skip_tag = None
        self._all_text = []
        self._current_href = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in ("script", "style"):
            self._skip_tag = tag
        elif tag == "title":
            self._in_title = True
            self._current_text = ""
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
        elif tag == "h1":
            self._in_h1 = True
            self._current_text = ""
        elif tag == "h2":
            self._in_h2 = True
            self._current_text = ""
        elif tag == "a":
            self._in_a = True
            self._current_text = ""
            self._current_href = attrs_dict.get("href", "")
            # Social links
            social_platforms = {"twitter.com": "Twitter/X", "x.com": "Twitter/X",
                                "facebook.com": "Facebook", "linkedin.com": "LinkedIn",
                                "instagram.com": "Instagram", "youtube.com": "YouTube",
                                "tiktok.com": "TikTok", "github.com": "GitHub"}
            href = attrs_dict.get("href", "")
            for domain, name in social_platforms.items():
                if domain in href:
                    self.social_links.append({"platform": name, "url": href})
        elif tag == "button":
            self._in_button = True
            self._current_text = ""
        elif tag == "img":
            alt = attrs_dict.get("alt", "").lower()
            src = attrs_dict.get("src", "").lower()
            # Count customer logos
            if any(word in alt for word in ["logo", "client", "partner", "customer", "trusted"]):
                self.logo_count += 1
            if any(word in src for word in ["logo", "client", "partner"]):
                self.logo_count += 1

    def handle_endtag(self, tag):
        if tag == self._skip_tag:
            self._skip_tag = None
        elif tag == "title" and self._in_title:
            self._in_title = False
            self.title = self._current_text.strip()
        elif tag == "h1" and self._in_h1:
            self._in_h1 = False
            text = self._current_text.strip()
            if text:
                self.h1_tags.append(text)
        elif tag == "h2" and self._in_h2:
            self._in_h2 = False
            text = self._current_text.strip()
            if text:
                self.h2_tags.append(text)
        elif tag == "a" and self._in_a:
            self._in_a = False
            text = self._current_text.strip()
            cta_words = ["sign up", "get started", "try free", "start", "buy", "subscribe",
                         "join", "register", "download", "book", "demo", "contact", "pricing",
                         "問い合わせ", "問合せ", "資料請求", "見積", "予約", "購入", "カート", "相談"]
            if any(w in text.lower() for w in cta_words):
                self.ctas.append(text)
        elif tag == "button" and self._in_button:
            self._in_button = False
            text = self._current_text.strip()
            if text:
                self.ctas.append(text)

    def handle_data(self, data):
        if self._skip_tag:
            return
        if self._in_title or self._in_h1 or self._in_h2 or self._in_a or self._in_button:
            self._current_text += data
        self._all_text.append(data.strip())

        # Detect pricing indicators
        text_lower = data.lower().strip()
        pricing_patterns = [r"\$\d+", r"€\d+", r"£\d+", r"/month", r"/year", r"/mo",
                            r"per month", r"per year", r"annually", r"free plan",
                            r"free tier", r"free trial", r"enterprise", r"[¥￥]\s*[0-9０-９]",
                            r"[0-9０-９][0-9０-９,.，．]*\s*[万億]?円", r"月額|年額|料金プラン|無料体験"]
        for pattern in pricing_patterns:
            if re.search(pattern, text_lower):
                self.pricing_indicators.append(data.strip())
                break

        # Detect testimonials
        testimonial_words = ["testimonial", "review", "said about", "what our customers",
                             "customer stories", "case study", "success story", "お客様の声", "導入事例", "施工事例"]
        if any(w in text_lower for w in testimonial_words):
            self.testimonial_count += 1

    def get_results(self):
        full_text = " ".join(self._all_text)
        word_count = len(full_text.split())

        # Extract positioning
        positioning = self.og_description or self.meta_description or ""
        if self.h1_tags:
            positioning = self.h1_tags[0]

        return {
            "positioning": {
                "headline": self.h1_tags[0] if self.h1_tags else self.title,
                "tagline": self.meta_description,
                "og_title": self.og_title,
                "og_description": self.og_description,
                "key_sections": self.h2_tags[:10]
            },
            "pricing": {
                "has_pricing_info": len(self.pricing_indicators) > 0,
                "pricing_mentions": list(dict.fromkeys(self.pricing_indicators))[:10]
            },
            "trust": {
                "social_platforms": [s["platform"] for s in self.social_links],
                "social_link_count": len(self.social_links),
                "estimated_logo_count": self.logo_count,
                "has_testimonials": self.testimonial_count > 0
            },
            "ctas": list(dict.fromkeys(self.ctas))[:10],
            "content": {
                "word_count": word_count,
                "sections": len(self.h2_tags)
            }
        }


def fetch_page(url):
    """Fetch a webpage."""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except:
        return None


def scan_competitor(url):
    """Scan a competitor website."""
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")

    result = {
        "url": url,
        "domain": domain,
        "status": "success"
    }

    html = fetch_page(url)
    if not html:
        result["status"] = "error"
        result["message"] = "Could not fetch page"
        return result

    parser = CompetitorPageParser()
    try:
        parser.feed(html)
    except:
        result["status"] = "error"
        result["message"] = "Could not parse page"
        return result

    result["data"] = parser.get_results()

    # Try to fetch pricing page
    pricing_urls = [
        f"{parsed.scheme}://{parsed.netloc}/pricing",
        f"{parsed.scheme}://{parsed.netloc}/plans",
        f"{parsed.scheme}://{parsed.netloc}/price",
    ]

    for pricing_url in pricing_urls:
        pricing_html = fetch_page(pricing_url)
        if pricing_html:
            pricing_parser = CompetitorPageParser()
            try:
                pricing_parser.feed(pricing_html)
                pricing_data = pricing_parser.get_results()
                if not pricing_data["pricing"]["has_pricing_info"]:
                    continue
                result["pricing_page"] = {
                    "url": pricing_url,
                    "found": True,
                    "pricing_mentions": pricing_data["pricing"]["pricing_mentions"],
                    "sections": pricing_data["positioning"]["key_sections"]
                }
                break
            except (TypeError, ValueError):
                continue
    else:
        result["pricing_page"] = {"found": False}

    return result


def scan_multiple(urls):
    """Scan multiple competitor URLs."""
    results = []
    for url in urls:
        result = scan_competitor(url)
        results.append(result)
    return results


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 competitor_scanner.py <url1> [url2] [url3] ...",
            "example": "python3 competitor_scanner.py calendly.com acuityscheduling.com doodle.com",
            "description": "Scans competitor websites for positioning, pricing, and trust signals"
        }, indent=2))
        return

    urls = sys.argv[1:]
    if len(urls) == 1:
        result = scan_competitor(urls[0])
        print(json.dumps(result, indent=2, default=str))
    else:
        results = scan_multiple(urls)
        print(json.dumps({"competitors": results}, indent=2, default=str))


if __name__ == "__main__":
    main()
