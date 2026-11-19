"""定点観測の通常CLIと履歴の保全を確認する。"""
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/market/scripts/track_history.py"


class HistoryCliTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.history = Path(temp.name) / "MARKET-HISTORY.json"

    def cli(self, command, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), command, str(self.history), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return result.stdout

    def record(self, day, score, *args, ok=True):
        return self.cli("record", "--date", day, "--overall", str(score), *args, ok=ok)

    def test_legacy_backfill_retry_and_validation(self):
        original = {"url": "https://example.jp", "entries": [
            {"date": "2026-11-19", "scores": {"SEO": 65}, "overall": 62, "metrics": {"問合せ": 4}, "note": "導線確認"}
        ]}
        self.history.write_text(json.dumps(original))
        self.record("2026-09-19", 60)
        output = self.record("2026-10-19", 63, "--url", "https://www.example.jp/")
        self.assertIn("2026-09-19）比：+3", output)
        self.record("2026-11-19", 64, "--metrics", '{"受注":null}')
        last = json.loads(self.history.read_text())["entries"][-1]
        self.assertEqual(last["metrics"], {"問合せ": 4, "受注": None})
        self.assertEqual(last["note"], "導線確認")
        self.assertEqual(last["scores"]["SEO"], 65)
        self.assertIn("出所未記録", self.cli("report"))
        before = self.history.read_bytes()
        self.record("2026-11-19", 63, "--url", "https://other.example", ok=False)
        self.record("2026-02-30", 63, ok=False)
        self.record("2026-11-19", 101, ok=False)
        self.record("2026-11-19", 64, "--metrics", "[]", ok=False)
        self.record("2026-11-19", 64, "--actions", '[{"id":"A01"}]', ok=False)
        self.assertEqual(self.history.read_bytes(), before)

    def test_monthly_action_and_kpi(self):
        action = {"id": "A01", "title": "フォームの見直し", "status": "予定", "metric": "問合せ", "evidence": "監査記録"}
        for month, value, status in [(9, 0, "予定"), (10, 3, "実施済"), (11, 5, "実施済")]:
            action.update(status=status, evidence="公開記録" if month > 9 else "監査記録")
            detail = {"source": "顧客台帳", "period": f"2026-{month:02}", "unit": "件",
                      "basis": "重複除外" if month < 11 else "重複含む"}
            self.record(f"2026-{month:02}-30", 60 + month, "--metrics", json.dumps({"問合せ": value, "受注": None}),
                        "--metric-details", json.dumps({"問合せ": detail}), "--actions", json.dumps([action]))
            if month == 10:
                diff = self.cli("diff")
                for term in ("A01", "実施済", "2026-10", "+3件", "0件", "比較不可（未計測）"):
                    self.assertIn(term, diff)
        self.assertIn("比較不可（条件変更）", self.cli("diff"))
        self.assertIn("+3件", self.cli("report"))
        self.record("2026-12-01", 68, "--metrics", '{"問合せ":7}')
        self.assertIn("比較不可（条件未記録）", self.cli("diff"))

    def test_report_import_and_unscored_followup(self):
        report_path = self.history.parent / "REPORT-DATA.json"
        report = {"url": "https://shop.example/", "date": "2026年10月19日", "overall_score": None,
                  "categories": {"SEO": {"score": None}},
                  "priority_actions": [{"id": "S01", "title": "在庫表示を追加", "status": "予定",
                                        "metric": "注文数", "evidence": "商品ページを確認", "baseline": 18}]}
        report_path.write_text(json.dumps(report))
        self.cli("record", "--from-report", str(report_path))
        report.update(date="2026-11-19", overall_score=0)
        report["categories"]["SEO"]["score"] = 0
        report_path.write_text(json.dumps(report))
        self.cli("record", "--from-report", str(report_path), "--metrics", '{"注文数":0}')
        text = self.cli("report")
        for term in ("未採点", "0点", "比較不可（未採点）", "注文数", "未計測", "S01"):
            self.assertIn(term, text)
        self.assertIn("未採点 → 0点", self.cli("diff"))
        entries = json.loads(self.history.read_text())["entries"]
        self.assertNotIn("metrics", entries[0])
        self.assertEqual(entries[-1]["metrics"], {"注文数": 0})
        self.cli("record", "--from-report", str(report_path), "--url", "https://other.example", ok=False)

    def test_html_markdown_match_and_escape(self):
        output = self.history.parent / "report.html"
        detail = {"source": "台帳<script>", "period": "2026-09", "basis": "全相談", "unit": "%"}
        for month, score in [(9, 30), (10, 40)]:
            detail["period"] = f"2026-{month:02}"
            self.record(f"2026-{month:02}-19", 60, "--metrics", json.dumps({"相談完了率": score, "受注": None}),
                        "--metric-details", json.dumps({"相談完了率": detail}), "--note", "<img src=x>")
        markdown = self.cli("report", "--html", str(output))
        webpage = output.read_text()
        for value in ("+10ポイント", "未計測", "台帳&lt;script&gt;", "&lt;img src=x&gt;"):
            self.assertIn(value, markdown)
            self.assertIn(value, webpage)
        self.assertNotIn("<script>", webpage)
        self.assertNotIn("<img src=x>", webpage)
        before = self.history.read_bytes()
        self.cli("report", "--html", str(self.history), ok=False)
        self.assertEqual(self.history.read_bytes(), before)

    def test_parallel_writes_and_damaged_file(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda i: self.record(f"2026-10-{i:02}", 61), range(1, 11)))
        entries = json.loads(self.history.read_text())["entries"]
        self.assertEqual(len(entries), 10)
        self.history.write_text('{"entries":')
        self.record("2026-11-19", 61, ok=False)
        self.assertEqual(self.history.read_text(), '{"entries":')


if __name__ == "__main__":
    unittest.main()
