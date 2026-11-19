#!/usr/bin/env python3
"""担当案件の診断、施策、成果指標を日付別に記録する。"""
import argparse
import datetime
import html
import json
import math
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit


STATUSES = {"予定", "進行中", "実施済", "未確認"}
DETAIL_FIELDS = ("source", "period", "unit", "basis")


def read_history(path):
    if not path.exists():
        return {"url": None, "entries": []}
    with path.open(encoding="utf-8") as stream:
        history = json.load(stream)
    if not isinstance(history, dict) or not isinstance(history.get("entries"), list):
        raise ValueError("履歴の entries を読み取れません")
    dates = set()
    for entry in history["entries"]:
        validate_day(entry["date"])
        if entry["overall"] is not None:
            validate_score(entry["overall"])
        if entry["date"] in dates:
            raise ValueError("履歴の日付が重複しています")
        dates.add(entry["date"])
    history["entries"].sort(key=lambda entry: entry["date"])
    return history


@contextmanager
def record_lock(path):
    # 置換される JSON 本体とは別のファイルをロックする。
    with path.with_name("." + path.name + ".lock").open("a+b") as stream:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def save_text(path, text):
    # 一時ファイルを閉じてから置換するため、読み手には完成した内容が見える。
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def validate_day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("測定日は YYYY-MM-DD 形式で指定してください")
    return datetime.date.fromisoformat(value)


def validate_score(value):
    if type(value) is not int or not 0 <= value <= 100:
        raise ValueError("スコアは0〜100の整数で指定してください")


def period_kind(period):
    if re.fullmatch(r"\d{4}-\d{2}", period):
        validate_day(period + "-01")
        return "月間"
    validate_day(period)
    return "時点"


def object_arg(raw, name):
    value = json.loads(raw)
    if not isinstance(value, dict) or any(not key.strip() for key in value):
        raise ValueError(f"{name} は名前をキーにしたJSONオブジェクトで指定してください")
    return value


def validate_action(action):
    for key in ("id", "title", "metric", "status"):
        if not isinstance(action.get(key), str) or not action[key].strip():
            raise ValueError(f"施策には {key} が必要です")
    if action["status"] not in STATUSES:
        raise ValueError(f"施策状況は {'／'.join(sorted(STATUSES))} から指定してください")
    if not isinstance(action.get("evidence", ""), str):
        raise ValueError("施策の確認根拠は文字列で指定してください")
    if action["status"] == "実施済" and not action.get("evidence", "").strip():
        raise ValueError("実施済の施策には公開ページや作業記録などの確認根拠が必要です")


def update_entry(entry, args):
    entry.update(date=args.date, overall=args.overall)
    if args.note is not None:
        entry["note"] = args.note
    if args.scores is not None:
        scores = object_arg(args.scores, "--scores")
        for value in scores.values():
            if value is not None:
                validate_score(value)
        entry.setdefault("scores", {}).update(scores)
    if args.metrics is not None:
        metrics = object_arg(args.metrics, "--metrics")
        for key, value in metrics.items():
            if value is not None and type(value) not in (int, float, str):
                raise ValueError(f"{key} の実測値には数値、従来形式の文字列、または null を指定してください")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"{key} の数値が有限ではありません")
        entry.setdefault("metrics", {}).update(metrics)
    if args.metric_details is not None:
        details = object_arg(args.metric_details, "--metric-details")
        for key, detail in details.items():
            if key not in entry.get("metrics", {}):
                raise ValueError(f"{key} の値は --metrics で指定してください（未計測は null）")
            if not isinstance(detail, dict) or not all(
                isinstance(detail.get(field), str) and detail[field].strip() for field in DETAIL_FIELDS
            ):
                raise ValueError(f"{key} の測定条件には source, period, unit, basis が必要です")
            period_kind(detail["period"])
        entry.setdefault("metric_details", {}).update(details)
    if args.actions is not None:
        actions = json.loads(args.actions)
        if not isinstance(actions, list) or not all(isinstance(a, dict) for a in actions):
            raise ValueError("--actions は施策の配列を指定してください")
        existing = {a["id"]: a for a in entry.get("actions", [])}
        incoming = set()
        for action in actions:
            validate_action(action)
            if action["id"] in incoming:
                raise ValueError("同じ施策IDが重複しています")
            incoming.add(action["id"])
            existing[action["id"]] = action
        entry["actions"] = list(existing.values())


def site_host(value):
    parts = urlsplit(value if "://" in value else "//" + value)
    if not parts.hostname or parts.username or parts.password:
        raise ValueError("案件の公開URLを指定してください")
    return re.sub(r"^www\.", "", parts.hostname).lower()


def apply_report(args):
    with Path(args.from_report).open(encoding="utf-8") as stream:
        report = json.load(stream)
    if not isinstance(report, dict) or not isinstance(report.get("url"), str):
        raise ValueError("入力レポートには対象URLが必要です")
    host = site_host(report["url"])
    if args.url and site_host(args.url) != host:
        raise ValueError("入力レポートのドメインと対象URLが異なります")
    args.url = args.url or report["url"]
    args.brand_name = report.get("brand_name")
    if not args.date:
        args.date = report.get("date")
        match = re.fullmatch(r"(\d{4})年(\d{1,2})月(\d{1,2})日", str(args.date))
        if match:
            args.date = datetime.date(*map(int, match.groups())).isoformat()
    if args.overall is None:
        args.overall = report.get("overall_score")
    if args.scores is None:
        categories = report.get("categories", {})
        if not isinstance(categories, dict) or not all(isinstance(item, dict) for item in categories.values()):
            raise ValueError("入力レポートのカテゴリは score を持つオブジェクトで指定してください")
        scores = {key: item.get("score") for key, item in categories.items()}
        args.scores = json.dumps(scores)
    if args.actions is None:
        actions = report.get("priority_actions", [])
        if not isinstance(actions, list) or not all(isinstance(action, dict) for action in actions):
            raise ValueError("入力レポートの priority_actions は施策配列を指定してください")
        keys = ("id", "title", "metric", "status", "evidence")
        args.actions = json.dumps([{key: action.get(key) for key in keys} for action in actions])


def score_change(before, after):
    if before is None or after is None:
        return "比較不可（未採点）"
    return signed(after - before)


def points(score):
    return "未採点" if score is None else f"{score}点"


def cmd_record(args):
    path = Path(args.path)
    if args.from_report:
        apply_report(args)
    elif args.overall is None:
        raise ValueError("--overall または --from-report を指定してください")
    validate_day(args.date)
    if args.overall is not None:
        validate_score(args.overall)
    path.parent.mkdir(parents=True, exist_ok=True)
    with record_lock(path):
        data = read_history(path)
        if args.url:
            host = site_host(args.url)
            if data.get("url") and site_host(data["url"]) != host:
                raise ValueError("記録先が別ドメインの履歴です。対象ドメインの保存先を指定してください")
            data["url"] = data.get("url") or args.url
        if isinstance(getattr(args, "brand_name", None), str) and args.brand_name.strip():
            data["brand_name"] = args.brand_name.strip()
        entries = data["entries"]
        entry = next((item for item in entries if item["date"] == args.date), None)
        if entry is None:
            entry = {"scores": {}, "note": ""}
            entries.append(entry)
        update_entry(entry, args)
        entries.sort(key=lambda item: item["date"])
        save_text(path, json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"記録しました：{args.date} 総合 {points(args.overall)}（全{len(entries)}回）")
    index = entries.index(entry)
    if index:
        previous = entries[index - 1]
        print(f"前回（{previous['date']}）比：{score_change(previous['overall'], args.overall)}")
    return 0


def cell(value):
    return html.escape(str(value), quote=False).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")


def table(headers, rows):
    print("| " + " | ".join(map(cell, headers)) + " |")
    print("|" + "---|" * len(headers))
    for row in rows:
        print("| " + " | ".join(map(cell, row)) + " |")
    print()


def signed(value):
    return f"{value:+.6g}"


def delta(previous, current, key):
    before = previous.get("metrics", {}).get(key)
    after = current.get("metrics", {}).get(key)
    if before is None or after is None:
        return "比較不可（未計測）"
    left = previous.get("metric_details", {}).get(key, {})
    right = current.get("metric_details", {}).get(key, {})
    if not left or not right:
        return "比較不可（条件未記録）"
    if any(left.get(field) != right.get(field) for field in ("source", "unit", "basis")):
        return "比較不可（条件変更）"
    period = right["period"]
    if period_kind(left["period"]) != period_kind(period) or left["period"] >= period:
        return "比較不可（対象期間を確認）"
    if type(before) not in (float, int) or type(after) not in (float, int):
        return "比較不可（数値未記録）"
    difference_unit = "ポイント" if right["unit"] in ("%", "％") else right["unit"]
    return signed(after - before) + difference_unit


def measurement_keys(entries):
    keys = {}
    for entry in entries:
        for key in entry.get("metrics", {}):
            keys[key] = True
        for action in entry.get("actions", []):
            keys[action["metric"]] = True
    return keys


def measurement_rows(entries, latest_only=False):
    keys = measurement_keys(entries)
    rows = []
    start = max(0, len(entries) - 2) if latest_only else 0
    for index in range(start, len(entries)):
        entry = entries[index]
        for key in keys:
            details = entry.get("metric_details", {}).get(key, {})
            value = entry.get("metrics", {}).get(key)
            unit = details.get("unit", "")
            change = delta(entries[index - 1], entry, key) if index and index > start else "—"
            rows.append([entry["date"], key, f"{value}{unit}" if value is not None else "未計測",
                         details.get("source", "出所未記録"), details.get("period", "期間未記録"),
                         details.get("basis", "条件未記録"), change])
    return rows


MEASUREMENT_HEADERS = ["測定日", "指標", "値", "出所", "対象期間", "集計条件", "前回比"]


def show_measurements(entries, latest_only=False):
    print("## 成果指標\n")
    rows = measurement_rows(entries, latest_only)
    if not rows:
        print("成果指標は未計測です。\n")
        return
    print("差分は表示した前回測定との比較です。計測条件を変更した指標には差分を付けません。\n")
    table(MEASUREMENT_HEADERS, rows)


def latest_actions(entries):
    latest = {}
    for entry in entries:
        for action in entry.get("actions", []):
            latest[action["id"]] = (action, entry["date"])
    return list(latest.values())


def show_actions(entries):
    print("## 優先施策の状況\n")
    latest = latest_actions(entries)
    if latest:
        table(["ID", "施策", "最終記録時の状況", "記録日", "確認根拠", "追跡指標"],
              ([a["id"], a["title"], a["status"], day, a.get("evidence") or "未確認", a["metric"]]
               for a, day in latest))
    else:
        print("施策IDの記録はありません。実施メモがあればスコア推移に表示します。\n")


def cmd_report(args):
    data = read_history(Path(args.path))
    entries = data["entries"]
    if not entries:
        raise ValueError("記録がありません。先に record を実行してください")
    if args.html:
        output = Path(args.html)
        if output.resolve() == Path(args.path).resolve() or output.suffix.lower() not in (".html", ".htm"):
            raise ValueError("履歴JSONとは別の .html ファイルを出力先に指定してください")
        from monthly_history_html import render_monthly
        comparisons = measurement_rows(entries)
        scores = [(e["date"], points(e["overall"]), score_change(entries[i-1]["overall"], e["overall"])
                   if i else "初回", e.get("note") or "—") for i, e in enumerate(entries)]
        report = render_monthly(data, scores, latest_actions(entries), MEASUREMENT_HEADERS, comparisons)
        output.parent.mkdir(parents=True, exist_ok=True)
        save_text(output, report)
    first, last = entries[0], entries[-1]
    print("# スコア推移レポート\n")
    print(f"**対象URL：** {cell(data.get('url') or '未記録')}\n")
    print(f"**測定回数：** {len(entries)} 回\n")
    print(f"**期間：** {first['date']} 〜 {last['date']}\n")
    if len(entries) > 1:
        print(f"**初回からの変化：{points(first['overall'])} → {points(last['overall'])}（{score_change(first['overall'], last['overall'])}）**\n")
    print("## 総合スコアの推移\n")
    table(["測定日", "総合", "前回比", "実施メモ"],
          ([e["date"], points(e["overall"]), score_change(entries[i - 1]["overall"], e["overall"]) if i else "—",
            e.get("note", "")] for i, e in enumerate(entries)))
    categories = sorted({key for e in entries for key in e.get("scores", {})})
    if categories:
        print("## カテゴリ別の推移\n")
        rows = []
        for key in categories:
            vals = [e.get("scores", {}).get(key) for e in entries]
            diff = signed(vals[-1] - vals[0]) if len(entries) > 1 and None not in (vals[0], vals[-1]) else "—"
            rows.append([key, *["—" if v is None else v for v in vals], diff])
        table(["カテゴリ", *[e["date"] for e in entries], "初回比"], rows)
    show_actions(entries)
    show_measurements(entries)
    print("## 総合スコアの推移（図）\n\n```")
    for entry in entries:
        score = entry["overall"]
        if score is None:
            print(f"{entry['date']}  未採点")
            continue
        print(f"{entry['date']}  {'█' * (score // 5)}{'░' * (20 - score // 5)} {score:3}")
    print("```")
    return 0


def cmd_diff(args):
    entries = read_history(Path(args.path))["entries"]
    if len(entries) < 2:
        raise ValueError("比較には2回以上の記録が必要です")
    previous, last = entries[-2:]
    print(f"{previous['date']} → {last['date']}\n")
    print(f"総合：{points(previous['overall'])} → {points(last['overall'])}（{score_change(previous['overall'], last['overall'])}）\n")
    for key in sorted(set(previous.get("scores", {})).intersection(last.get("scores", {}))):
        a, b = previous["scores"][key], last["scores"][key]
        if a is not None and b is not None:
            print(f"  {cell(key)}：{a} → {b}（{signed(b - a)}点）")
    print()
    show_actions(entries)
    show_measurements(entries, latest_only=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description="マーケティングスコアの定点観測")
    commands = parser.add_subparsers(dest="cmd", required=True)
    record = commands.add_parser("record", help="スコア、施策、実測値を記録")
    record.add_argument("path")
    record.add_argument("--url")
    record.add_argument("--from-report", help="案件の REPORT-DATA.json から診断と優先施策を取り込む")
    record.add_argument("--date", help="測定日 YYYY-MM-DD")
    record.add_argument("--overall", type=int, help="総合スコア 0〜100")
    record.add_argument("--scores", help="カテゴリ名とスコアのJSON")
    record.add_argument("--metrics", help="指標名と値のJSON（未計測は null）")
    record.add_argument("--metric-details", help="指標名と source, period, unit, basis のJSON")
    record.add_argument("--actions", help="id, title, status, metric, evidence を含む施策配列のJSON")
    record.add_argument("--note", help="この期間の実施メモ")
    record.set_defaults(func=cmd_record)
    for name, callback, help_text in (("report", cmd_report, "全期間のレポートを表示"),
                                       ("diff", cmd_diff, "直近2回を比較")):
        cmd = commands.add_parser(name, help=help_text)
        cmd.add_argument("path")
        if name == "report":
            cmd.add_argument("--html", metavar="PATH", help="共有用の月次レポートHTMLも保存")
        cmd.set_defaults(func=callback)
    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"エラー：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
