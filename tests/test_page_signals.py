"""HTMLから読み取れる範囲を検証する。業種・営業成果を推定するテストではない。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/market/scripts"))
import analyze_page
import competitor_scanner


class FakeHeaders:
    def get_content_charset(self):
        return "utf-8"


class FakeResponse:
    headers = FakeHeaders()

    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.body if size < 0 else self.body[:size]


class SafeFetchTest(unittest.TestCase):
    def test_response_size_limit(self):
        for module in (analyze_page, competitor_scanner):
            with self.subTest(module=module.__name__):
                with patch.object(module.urllib.request, "urlopen", return_value=FakeResponse("あ".encode())):
                    self.assertEqual(module.fetch_page("https://site.example/", max_bytes=3), "あ")
                with patch.object(module.urllib.request, "urlopen", return_value=FakeResponse(b"abcd")):
                    self.assertIsNone(module.fetch_page("https://site.example/", max_bytes=3))

    def test_sitemap_uses_its_own_limit(self):
        sitemap = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://site.example/</loc></url></urlset>'
        with patch.object(analyze_page, "fetch_page", return_value=sitemap) as fetch:
            result = analyze_page.fetch_sitemap("https://site.example/")
        fetch.assert_called_once_with("https://site.example/sitemap.xml", max_bytes=analyze_page.MAX_SITEMAP_BYTES)
        self.assertEqual(result["url_count"], 1)
        self.assertTrue(result["exists"])

    def test_sitemap_with_xml_declarations_is_not_parsed(self):
        for marker in ('<!DOCTYPE urlset [<!ENTITY a "b">]>', '<!doctype urlset>', '<!entity a "b">'):
            with self.subTest(marker=marker):
                with patch.object(analyze_page, "fetch_page", return_value=marker + "<urlset></urlset>"), \
                        patch.object(analyze_page.ElementTree, "fromstring") as parse:
                    result = analyze_page.fetch_sitemap("https://site.example/")
                parse.assert_not_called()
                self.assertFalse(result["exists"])


class PageSignalsTest(unittest.TestCase):
    def test_builder(self):
        page = """<title>青葉工務店</title><h1>地域の注文住宅</h1>
        <img alt="" src="divider.svg"><a href="works">施工事例</a>
        <a href="//other.example/area/home.example">来場予約</a>
        <script type="application/ld+json">"placeholder"</script><p>""" + "注文住宅" * 120 + "</p>"
        with patch.object(analyze_page, "fetch_page", return_value=page):
            data = analyze_page.analyze("https://home.example/")["analysis"]
        self.assertEqual(data["technical"]["internal_links"], 1)
        self.assertEqual(data["technical"]["external_links"], 1)
        self.assertEqual(data["seo"]["images_without_alt"], 0)
        self.assertGreaterEqual(data["content"]["japanese_char_count"], 480)
        self.assertFalse(data["sitemap"]["exists"])
        self.assertFalse(data["robots"]["exists"])
        self.assertEqual(data["conversion"]["cta_count"], 1)

    def test_javascript_redirect_is_unscored(self):
        page = '<title>公式通販</title><script>location.replace("/shop")</script>'
        with patch.object(analyze_page, "fetch_page", return_value=page):
            result = analyze_page.analyze("https://shop.example/")
        self.assertEqual(result["status"], "partial")
        self.assertIsNone(result["analysis"]["overall_score"])

    def test_shop(self):
        page = """<title>茶葉の通販</title><style>.ad {}</style><script>let ad = "月額999円";</script>
        <h1>春のお茶</h1><p>税込1,980円</p><a href="cart">カートに入れる</a>"""
        with patch.object(competitor_scanner, "fetch_page", side_effect=[page, "<h1>ページがありません</h1>", None, None]):
            data = competitor_scanner.scan_competitor("https://shop.example/")
        self.assertEqual(data["data"]["pricing"]["pricing_mentions"], ["税込1,980円"])
        self.assertEqual(data["data"]["ctas"], ["カートに入れる"])
        self.assertFalse(data["pricing_page"]["found"])


if __name__ == "__main__":
    unittest.main()
