#!/usr/bin/env python3
"""
Marketing Page Analyzer — Utility script for AI Marketing Claude Code Skills
Analyzes a webpage for marketing effectiveness: SEO elements, content structure,
trust signals, CTAs, social proof, and conversion optimization indicators.
"""

import sys
import json
import re
import urllib.request
import urllib.error
import ssl
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin


class MarketingPageParser(HTMLParser):
    """Parse HTML and extract marketing-relevant elements."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.meta_keywords = ""
        self.og_tags = {}
        self.headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        self.links = []
        self.images = []
        self.forms = []
        self.buttons = []
        self.scripts = []
        self.schema_data = []
        self.ctas = []
        self.social_links = []
        self.tracking_scripts = []

        # State tracking
        self._current_tag = None
        self._current_attrs = {}
        self._in_title = False
        self._in_heading = None
        self._in_button = False
        self._in_a = False
        self._current_text = ""
        self._in_script = False
        self._script_type = ""
        self._in_form = False
        self._current_form = {}
        self._form_fields = []
        self._text_content = []
        self._has_viewport = False
        self._canonical = ""
        self._robots_meta = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self._current_tag = tag
        self._current_attrs = attrs_dict

        if tag == "title":
            self._in_title = True
            self._current_text = ""

        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.meta_description = content
            elif name == "keywords":
                self.meta_keywords = content
            elif name == "viewport":
                self._has_viewport = True
            elif name == "robots":
                self._robots_meta = content
            elif prop.startswith("og:"):
                self.og_tags[prop] = content

        elif tag == "link":
            rel = attrs_dict.get("rel", "")
            if "canonical" in rel:
                self._canonical = attrs_dict.get("href", "")

        elif tag in self.headings:
            self._in_heading = tag
            self._current_text = ""

        elif tag == "a":
            self._in_a = True
            self._current_text = ""
            href = attrs_dict.get("href", "")
            self.links.append({"href": href, "text": "", "attrs": attrs_dict})
            # Check for social links
            social_platforms = ["twitter.com", "x.com", "facebook.com", "linkedin.com",
                                "instagram.com", "youtube.com", "tiktok.com", "github.com"]
            for platform in social_platforms:
                if platform in href:
                    self.social_links.append({"platform": platform.split(".")[0], "url": href})

        elif tag == "img":
            self.images.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", ""),
                "has_alt": "alt" in attrs_dict,
                "loading": attrs_dict.get("loading", "")
            })

        elif tag == "button":
            self._in_button = True
            self._current_text = ""

        elif tag == "form":
            self._in_form = True
            self._current_form = {
                "action": attrs_dict.get("action", ""),
                "method": attrs_dict.get("method", "GET").upper()
            }
            self._form_fields = []

        elif tag == "input" and self._in_form:
            self._form_fields.append({
                "type": attrs_dict.get("type", "text"),
                "name": attrs_dict.get("name", ""),
                "placeholder": attrs_dict.get("placeholder", ""),
                "required": "required" in attrs_dict
            })

        elif tag == "script":
            self._in_script = True
            self._script_type = attrs_dict.get("type", "")
            self._current_text = ""
            src = attrs_dict.get("src", "")
            if src:
                self.scripts.append(src)
                # Detect tracking scripts
                tracking_indicators = {
                    "gtag": "Google Analytics (gtag)",
                    "googletagmanager": "Google Tag Manager",
                    "google-analytics": "Google Analytics",
                    "analytics": "Analytics",
                    "fbevents": "Meta Pixel",
                    "facebook": "Meta/Facebook",
                    "snap.licdn": "LinkedIn Insight Tag",
                    "hotjar": "Hotjar",
                    "fullstory": "FullStory",
                    "mixpanel": "Mixpanel",
                    "amplitude": "Amplitude",
                    "segment": "Segment",
                    "hubspot": "HubSpot",
                    "intercom": "Intercom",
                    "crisp": "Crisp Chat",
                    "drift": "Drift",
                    "tiktok": "TikTok Pixel",
                    "clarity": "Microsoft Clarity"
                }
                src_lower = src.lower()
                for indicator, name in tracking_indicators.items():
                    if indicator in src_lower:
                        self.tracking_scripts.append(name)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = self._current_text.strip()

        elif tag in self.headings and self._in_heading == tag:
            text = self._current_text.strip()
            if text:
                self.headings[tag].append(text)
            self._in_heading = None

        elif tag == "a" and self._in_a:
            self._in_a = False
            text = self._current_text.strip()
            if self.links:
                self.links[-1]["text"] = text
            # Detect CTAs
            # 英語の汎用CTAキーワード
            cta_words_en = ["sign up", "get started", "try free", "start free", "buy now",
                            "subscribe", "join", "register", "download", "book", "schedule",
                            "request demo", "contact us", "learn more", "see pricing",
                            "start trial", "create account", "claim", "unlock"]
            # 日本語の汎用CTAキーワード
            cta_words_ja = [
                # 問い合わせ・相談系
                "お問い合わせ", "ご相談", "お気軽にご連絡", "資料請求", "お問合せ",
                "ご連絡ください", "今すぐ相談", "無料相談", "お気軽にどうぞ",
                # 予約・来場系（建設業界重要）
                "来場予約", "来場のご予約", "見学予約", "現地見学", "ショールーム予約",
                "モデルハウス", "見学会", "内覧会", "現場見学",
                # 見積もり・費用系（建設業界重要）
                "無料見積もり", "無料見積", "お見積り", "お見積もり", "見積依頼",
                "見積もり依頼", "費用を確認", "料金を見る",
                # 施工・実績系（建設業界特有）
                "施工事例を見る", "施工実績", "工事の流れ", "施工の流れ",
                "対応エリア", "対応エリアを確認", "工事エリア",
                # 資料・パンフレット
                "資料をダウンロード", "カタログ請求", "パンフレット", "資料を見る",
                # 汎用CTA
                "詳しくはこちら", "詳細はこちら", "もっと見る", "続きを読む",
                "今すぐ確認", "今すぐ申し込む", "無料で試す", "無料登録",
                "申し込む", "申込む", "購入する", "注文する",
                "始める", "スタート", "はじめる", "試してみる",
            ]
            cta_words = cta_words_en + cta_words_ja
            text_lower = text.lower()  # 英語の比較用（小文字化）
            matched = False
            # 英語キーワードは小文字比較
            for cta in cta_words_en:
                if cta in text_lower:
                    self.ctas.append({"text": text, "href": self.links[-1]["href"], "type": "link"})
                    matched = True
                    break
            # 日本語キーワードはそのまま比較（大文字小文字区別なし）
            if not matched:
                for cta in cta_words_ja:
                    if cta in text:
                        self.ctas.append({"text": text, "href": self.links[-1]["href"], "type": "link"})
                        break

        elif tag == "button" and self._in_button:
            self._in_button = False
            text = self._current_text.strip()
            if text:
                self.buttons.append(text)
                self.ctas.append({"text": text, "type": "button"})

        elif tag == "form" and self._in_form:
            self._in_form = False
            self._current_form["fields"] = self._form_fields
            self._current_form["field_count"] = len(self._form_fields)
            self.forms.append(self._current_form)

        elif tag == "script" and self._in_script:
            self._in_script = False
            script_content = self._current_text
            # Check for inline tracking
            if "gtag" in script_content or "dataLayer" in script_content:
                if "Google Analytics" not in self.tracking_scripts and "Google Tag Manager" not in self.tracking_scripts:
                    self.tracking_scripts.append("Google Analytics/GTM (inline)")
            if "fbq" in script_content:
                if "Meta Pixel" not in self.tracking_scripts:
                    self.tracking_scripts.append("Meta Pixel (inline)")
            # Check for JSON-LD schema
            if self._script_type == "application/ld+json":
                try:
                    schema = json.loads(script_content)
                    if isinstance(schema, list):
                        self.schema_data.extend(schema)
                    else:
                        self.schema_data.append(schema)
                except (json.JSONDecodeError, ValueError):
                    pass

    def handle_data(self, data):
        if self._in_title or self._in_heading or self._in_a or self._in_button or self._in_script:
            self._current_text += data
        self._text_content.append(data)

    def get_full_text(self):
        return " ".join(self._text_content)

    def get_results(self):
        """Compile all findings into a structured result."""
        # Count images without alt text
        images_without_alt = sum(1 for img in self.images if not img.get("has_alt") or not img.get("alt"))
        images_with_lazy = sum(1 for img in self.images if img.get("loading") == "lazy")

        # Analyze heading hierarchy
        heading_issues = []
        if not self.headings["h1"]:
            heading_issues.append("Missing H1 tag")
        elif len(self.headings["h1"]) > 1:
            heading_issues.append(f"Multiple H1 tags ({len(self.headings['h1'])})")
        if self.headings["h3"] and not self.headings["h2"]:
            heading_issues.append("H3 used without H2 (skipped level)")

        # Unique tracking tools
        tracking = list(set(self.tracking_scripts))

        # Full text for word count
        full_text = self.get_full_text()
        word_count = len(full_text.split())

        return {
            "seo": {
                "title": self.title,
                "title_length": len(self.title),
                "title_ok": 30 <= len(self.title) <= 60,
                "meta_description": self.meta_description,
                "meta_description_length": len(self.meta_description),
                "meta_description_ok": 120 <= len(self.meta_description) <= 160,
                "canonical": self._canonical,
                "robots_meta": self._robots_meta,
                "has_viewport": self._has_viewport,
                "og_tags": self.og_tags,
                "headings": {k: v for k, v in self.headings.items() if v},
                "heading_issues": heading_issues,
                "images_total": len(self.images),
                "images_without_alt": images_without_alt,
                "images_with_lazy_loading": images_with_lazy
            },
            "content": {
                "word_count": word_count,
                "headings_count": sum(len(v) for v in self.headings.values()),
                "h1": self.headings["h1"],
                "h2": self.headings["h2"]
            },
            "conversion": {
                "ctas": self.ctas[:20],
                "cta_count": len(self.ctas),
                "forms": self.forms,
                "form_count": len(self.forms),
                "buttons": self.buttons[:20]
            },
            "trust": {
                "social_links": self.social_links,
                "social_link_count": len(self.social_links)
            },
            "tracking": {
                "tools_detected": tracking,
                "tools_count": len(tracking),
                "schema_types": [s.get("@type", "Unknown") for s in self.schema_data],
                "schema_count": len(self.schema_data)
            },
            "technical": {
                "total_links": len(self.links),
                "internal_links": 0,  # Filled after URL analysis
                "external_links": 0,
                "scripts_count": len(self.scripts)
            }
        }


def fetch_page(url):
    """Fetch a webpage and return its HTML content."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=15, context=ctx)
        return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return None
    except Exception as e:
        return None


def fetch_robots_txt(url):
    """Fetch and parse robots.txt."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    content = fetch_page(robots_url)
    if content:
        has_sitemap = "sitemap:" in content.lower()
        return {"exists": True, "has_sitemap_reference": has_sitemap, "content_preview": content[:500]}
    return {"exists": False}


def fetch_sitemap(url):
    """Check if sitemap.xml exists."""
    parsed = urlparse(url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": "MarketingBot/1.0"})
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        content = response.read().decode("utf-8", errors="replace")
        # Count URLs in sitemap
        url_count = content.lower().count("<url>") or content.lower().count("<loc>")
        return {"exists": True, "url_count": url_count}
    except:
        return {"exists": False, "url_count": 0}


def analyze(url):
    """Run full marketing analysis on a URL."""
    results = {"url": url, "status": "success"}

    # Fetch and parse main page
    html = fetch_page(url)
    if not html:
        return {"url": url, "status": "error", "message": "Could not fetch page"}

    parser = MarketingPageParser()
    try:
        parser.feed(html)
    except Exception as e:
        return {"url": url, "status": "error", "message": f"Parse error: {str(e)}"}

    page_results = parser.get_results()

    # Count internal vs external links
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    internal = 0
    external = 0
    for link in parser.links:
        href = link.get("href", "")
        if href.startswith("/") or domain in href:
            internal += 1
        elif href.startswith("http"):
            external += 1
    page_results["technical"]["internal_links"] = internal
    page_results["technical"]["external_links"] = external

    # Check robots.txt and sitemap
    page_results["robots"] = fetch_robots_txt(url)
    page_results["sitemap"] = fetch_sitemap(url)

    # -------------------------------------------------------
    # マーケティングスコア算出（6カテゴリ加重平均）
    # READMEのウェイト仕様に準拠：
    #   コンテンツ・メッセージング  25%
    #   コンバージョン最適化        20%
    #   SEO・発見可能性             20%
    #   ブランド・信頼性            15%
    #   成長・戦略（計測基盤）      10%
    #   技術基盤                    10%
    # -------------------------------------------------------
    WEIGHTS = {
        "content":   0.25,
        "cta":       0.20,
        "seo":       0.20,
        "trust":     0.15,
        "tracking":  0.10,
        "technical": 0.10,
    }
    scores = {}
    seo = page_results["seo"]
    conv = page_results["conversion"]

    # --- コンテンツ・メッセージングスコア (0-10) ---
    content_score = 1  # 最低点
    content = page_results["content"]
    if content["word_count"] >= 500:
        content_score += 3
    elif content["word_count"] >= 300:
        content_score += 2
    elif content["word_count"] >= 100:
        content_score += 1
    if seo["headings"].get("h1"):
        content_score += 2
    h2_count = len(seo["headings"].get("h2", []))
    if h2_count >= 5:
        content_score += 2
    elif h2_count >= 3:
        content_score += 1
    if seo["og_tags"]:  # OGP設定（SNS拡散対応）
        content_score += 1
    if seo["images_total"] >= 5:  # 画像コンテンツの充実
        content_score += 1
    scores["content"] = min(10, content_score)

    # --- SEO・発見可能性スコア (0-10) ---
    seo_score = 10
    if not seo["title"]:
        seo_score -= 3
    elif not seo["title_ok"]:
        seo_score -= 1
    if not seo["meta_description"]:
        seo_score -= 3
    elif not seo["meta_description_ok"]:
        seo_score -= 1
    if not seo["headings"].get("h1"):
        seo_score -= 2
    if seo["images_without_alt"] > 0:
        seo_score -= min(2, seo["images_without_alt"])
    if seo["heading_issues"]:
        seo_score -= 1
    if not seo["has_viewport"]:
        seo_score -= 1
    if page_results["robots"].get("exists"):
        seo_score = min(10, seo_score + 1)
    if page_results["sitemap"].get("exists"):
        seo_score = min(10, seo_score + 1)
    scores["seo"] = max(0, seo_score)

    # --- コンバージョン最適化スコア (0-10) ---
    cta_score = 2
    if conv["cta_count"] == 0:
        cta_score = 1
    elif conv["cta_count"] >= 2:
        cta_score = 6
    if conv["cta_count"] >= 4:
        cta_score = 7
    if conv["cta_count"] >= 6:
        cta_score = 8
    # 文字数10文字超のCTA（説明的な訴求文）はポイント加算
    value_ctas = [c for c in conv["ctas"] if len(c.get("text", "")) > 10]
    if value_ctas:
        cta_score = min(10, cta_score + 1)
    # フォームがあればさらに加算
    if conv["form_count"] >= 1:
        cta_score = min(10, cta_score + 1)
    scores["cta"] = cta_score

    # --- ブランド・信頼性スコア (0-10) ---
    trust_score = 4
    social_count = page_results["trust"]["social_link_count"]
    if social_count >= 3:
        trust_score += 2
    elif social_count >= 1:
        trust_score += 1
    schema_count = page_results["tracking"]["schema_count"]
    if schema_count >= 2:
        trust_score += 2
    elif schema_count >= 1:
        trust_score += 1
    if seo["canonical"]:  # canonical設定は信頼性・技術品質の指標
        trust_score += 1
    scores["trust"] = min(10, trust_score)

    # --- 成長・戦略（計測基盤）スコア (0-10) ---
    track_score = 2
    tools = page_results["tracking"]["tools_count"]
    if tools >= 3:
        track_score = 9
    elif tools >= 2:
        track_score = 7
    elif tools >= 1:
        track_score = 5
    scores["tracking"] = track_score

    # --- 技術基盤スコア (0-10) ---
    tech_score = 5
    if seo["has_viewport"]:
        tech_score += 1
    tech = page_results["technical"]
    if tech["internal_links"] >= 5:
        tech_score += 1
    if seo["images_with_lazy_loading"] > 0:
        tech_score += 1
    if page_results["robots"].get("exists"):
        tech_score += 1
    if page_results["sitemap"].get("exists"):
        tech_score += 1
    scores["technical"] = min(10, tech_score)

    # --- 加重平均で総合スコア算出（0-100点） ---
    overall = sum(scores[cat] * WEIGHTS[cat] for cat in WEIGHTS) * 10
    page_results["scores"] = scores
    page_results["weights"] = WEIGHTS
    page_results["overall_score"] = round(overall, 1)

    results["analysis"] = page_results
    return results


def main():
    if len(sys.argv) < 2:
        # Demo mode
        print(json.dumps({
            "usage": "python3 analyze_page.py <url>",
            "example": "python3 analyze_page.py https://calendly.com",
            "description": "Analyzes a webpage for marketing effectiveness"
        }, indent=2))
        return

    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url

    results = analyze(url)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
