#!/usr/bin/env python3
"""マーケティングスコアの定点観測を管理する。

スコアをJSONに追記し、前回・初回との差分を計算して推移表を返す。
継続支援の提案材料として使うため、出力はそのままレポートに貼れる形式にする。

使い方:
  # 記録する
  python3 track_history.py record MARKET-HISTORY.json \
      --url https://example.co.jp --date 2026-07-25 --overall 62 \
      --scores '{"コンテンツ・メッセージング": 68, "コンバージョン最適化": 52}' \
      --note "問い合わせフォームを5項目に削減"

  # 推移を出力する
  python3 track_history.py report MARKET-HISTORY.json

  # 直近2回の差分だけを出す
  python3 track_history.py diff MARKET-HISTORY.json
"""
import argparse
import json
import sys
from pathlib import Path


def load(path):
    p = Path(path)
    if not p.exists():
        return {"url": None, "entries": []}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_record(args):
    data = load(args.path)
    if data.get("url") and args.url and data["url"] != args.url:
        print(f"警告: 記録済みのURL（{data['url']}）と異なります: {args.url}", file=sys.stderr)
    if args.url:
        data["url"] = args.url

    try:
        scores = json.loads(args.scores) if args.scores else {}
    except json.JSONDecodeError as e:
        print(f"エラー: --scores のJSONが不正です: {e}", file=sys.stderr)
        return 1

    entry = {
        "date": args.date,
        "overall": args.overall,
        "scores": scores,
        "note": args.note or "",
    }
    if args.metrics:
        try:
            entry["metrics"] = json.loads(args.metrics)
        except json.JSONDecodeError as e:
            print(f"エラー: --metrics のJSONが不正です: {e}", file=sys.stderr)
            return 1

    # 同じ日付の記録があれば上書きする（測り直しに対応）
    data["entries"] = [e for e in data["entries"] if e["date"] != args.date]
    data["entries"].append(entry)
    data["entries"].sort(key=lambda e: e["date"])
    save(args.path, data)

    n = len(data["entries"])
    print(f"記録しました: {args.date} 総合 {args.overall}点（通算 {n} 回目）")
    if n >= 2:
        prev = data["entries"][-2]
        d = args.overall - prev["overall"]
        print(f"前回（{prev['date']}）比: {d:+d}点")
    return 0


def _arrow(d):
    if d > 0:
        return f"▲{d}"
    if d < 0:
        return f"▼{abs(d)}"
    return "→0"


def cmd_report(args):
    data = load(args.path)
    entries = data["entries"]
    if not entries:
        print("記録がありません。まず record を実行してください。", file=sys.stderr)
        return 1

    print(f"# スコア推移レポート\n")
    print(f"**対象URL：** {data.get('url', '（未記録）')}")
    print(f"**測定回数：** {len(entries)} 回")
    print(f"**期間：** {entries[0]['date']} 〜 {entries[-1]['date']}\n")

    first, last = entries[0], entries[-1]
    total = last["overall"] - first["overall"]
    print(f"**初回からの変化：{first['overall']}点 → {last['overall']}点（{_arrow(total)}点）**\n")

    # 総合スコアの推移
    print("## 総合スコアの推移\n")
    print("| 測定日 | 総合 | 前回比 | 実施した施策 |")
    print("|---|---|---|---|")
    for i, e in enumerate(entries):
        d = "—" if i == 0 else _arrow(e["overall"] - entries[i - 1]["overall"])
        print(f"| {e['date']} | {e['overall']}/100 | {d} | {e.get('note', '')} |")
    print()

    # カテゴリ別の推移
    keys = []
    for e in entries:
        for k in e.get("scores", {}):
            if k not in keys:
                keys.append(k)
    if keys:
        print("## カテゴリ別の推移\n")
        header = "| カテゴリ | " + " | ".join(e["date"] for e in entries) + " | 初回比 |"
        print(header)
        print("|---" * (len(entries) + 2) + "|")
        for k in keys:
            vals = [e.get("scores", {}).get(k) for e in entries]
            cells = [str(v) if v is not None else "—" for v in vals]
            fv = next((v for v in vals if v is not None), None)
            lv = next((v for v in reversed(vals) if v is not None), None)
            diff = _arrow(lv - fv) if (fv is not None and lv is not None) else "—"
            print(f"| {k} | " + " | ".join(cells) + f" | {diff} |")
        print()

    # 実測値の推移
    mkeys = []
    for e in entries:
        for k in e.get("metrics", {}):
            if k not in mkeys:
                mkeys.append(k)
    if mkeys:
        print("## 実測値の推移\n")
        print("| 指標 | " + " | ".join(e["date"] for e in entries) + " |")
        print("|---" * (len(entries) + 1) + "|")
        for k in mkeys:
            cells = [str(e.get("metrics", {}).get(k, "—")) for e in entries]
            print(f"| {k} | " + " | ".join(cells) + " |")
        print()

    # 簡易グラフ
    print("## 総合スコアの推移（図）\n```")
    for e in entries:
        bar = "█" * (e["overall"] // 5) + "░" * (20 - e["overall"] // 5)
        print(f"{e['date']}  {bar} {e['overall']:3}")
    print("```")
    return 0


def cmd_diff(args):
    data = load(args.path)
    entries = data["entries"]
    if len(entries) < 2:
        print("比較には2回以上の記録が必要です。", file=sys.stderr)
        return 1
    prev, last = entries[-2], entries[-1]
    print(f"{prev['date']} → {last['date']}")
    print(f"総合: {prev['overall']} → {last['overall']} ({_arrow(last['overall'] - prev['overall'])})")
    keys = set(prev.get("scores", {})) | set(last.get("scores", {}))
    for k in sorted(keys):
        a, b = prev.get("scores", {}).get(k), last.get("scores", {}).get(k)
        if a is None or b is None:
            continue
        print(f"  {k}: {a} → {b} ({_arrow(b - a)})")
    return 0


def main():
    ap = argparse.ArgumentParser(description="マーケティングスコアの定点観測")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="スコアを記録する")
    r.add_argument("path")
    r.add_argument("--url")
    r.add_argument("--date", required=True, help="YYYY-MM-DD")
    r.add_argument("--overall", type=int, required=True, help="総合スコア 0-100")
    r.add_argument("--scores", help='カテゴリ別スコアのJSON文字列')
    r.add_argument("--metrics", help='実測値のJSON文字列（問い合わせ数、順位など）')
    r.add_argument("--note", help="この期間に実施した施策")
    r.set_defaults(func=cmd_record)

    p = sub.add_parser("report", help="推移レポートを出力する")
    p.add_argument("path")
    p.set_defaults(func=cmd_report)

    d = sub.add_parser("diff", help="直近2回の差分を出力する")
    d.add_argument("path")
    d.set_defaults(func=cmd_diff)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
