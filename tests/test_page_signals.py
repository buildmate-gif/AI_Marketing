"""HTMLから読み取れる範囲を検証する。業種・営業成果を推定するテストではない。"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/market/scripts"))
import analyze_page
import competitor_scanner


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
