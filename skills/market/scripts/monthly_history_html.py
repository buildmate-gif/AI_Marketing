"""月次報告用の自己完結HTML。比較値は履歴CLIと同じ行データを使用する。"""
import html


def escape(value):
    return html.escape(str(value), quote=True)


def accessible_table(headers, rows):
    columns = "".join(f'<th scope="col">{escape(key)}</th>' for key in headers)
    body = "".join(
        "<tr>" + "".join(f'<td data-label="{escape(key)}">{escape(value)}</td>'
                         for key, value in zip(headers, row)) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{columns}</tr></thead><tbody>{body}</tbody></table>"


STYLE = """
:root{color-scheme:light;--ink:#1f2a44;--quiet:#505e69;--border:#d9d6cc;--paper:#fff;
--bg:#faf9f5;--navy:#202e47;--gold:#b99745}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,sans-serif;overflow-wrap:anywhere}
main,header>div{max-width:1080px;margin:auto;padding:0 clamp(16px,4vw,48px)}
header{background:var(--navy);color:var(--paper);padding:44px 0 36px;border-bottom:5px solid var(--gold)}
h1,h2,h3,p{margin:0}h1{font-size:clamp(28px,5vw,46px);letter-spacing:.03em;margin:.15em 0}
header p{color:#e3e7ef}h2{font-size:1.45rem;margin-bottom:14px}h3{font-size:1.05rem}
section{margin:36px 0}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px}
article,details,.table-wrap{background:var(--paper);border:1px solid var(--border);border-radius:10px}
article{padding:18px}.number{font-weight:700;font-size:1.65rem;line-height:1.35;margin:.35em 0}
.minor,dt{font-size:.875rem;color:var(--quiet)}dl{margin:14px 0 0}dd{margin:0 0 8px}
.status{display:inline-block;font-size:.8rem;border:1px solid #b5c5d9;border-radius:4px;
background:#edf2f8;padding:1px 7px;color:#24405e;margin-bottom:.6em}
.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:.91rem}
th,td{padding:11px 13px;border-bottom:1px solid var(--border);vertical-align:top}
th{background:#edf0f4}tbody tr:last-child td{border-bottom:none}summary{cursor:pointer;padding:14px;font-weight:600}
footer{margin:36px 0;color:var(--quiet);font-size:.875rem}
@media(max-width:700px){section{margin:26px 0}.table-wrap{border:0}
table,tbody,tr,td{display:block}table thead{position:absolute;clip-path:inset(50%);width:1px;height:1px;overflow:hidden}
tr{background:#fff;padding:10px 12px;border-bottom:1px solid var(--border)}
td{display:grid;grid-template-columns:5.5rem minmax(0,1fr);gap:8px;padding:3px 0;border:0}
td:before{content:attr(data-label);color:var(--quiet);font-size:.85em}}
@media print{body{background:#fff}main,header>div{max-width:none;padding:0}header{background:#fff;color:var(--ink);padding:12px 0}
header p{color:var(--quiet)}.cards{display:block}article{break-inside:avoid;margin:6px 0}
section{margin:12px 0}summary{display:none}details::details-content{display:block;content-visibility:visible}}
"""


def render_monthly(data, scores, actions, headers, measurements):
    entries = data["entries"]
    last = entries[-1]
    first_day = entries[0]["date"]
    last_day = last["date"]
    brand = data.get("brand_name") or data.get("url") or "対象案件"
    metric_cards = []
    for row in measurements:
        day, metric, value, source, period, basis, difference = row
        if day == last_day:
            metric_cards.append(f"""<article><h3>{escape(metric)}</h3>
<p class="number">{escape(value)}</p><p>前回比　{escape(difference)}</p>
<dl><dt>対象期間・出所</dt><dd>{escape(period)} ／ {escape(source)}</dd>
<dt>集計条件</dt><dd>{escape(basis)}</dd></dl></article>""")
    action_cards = []
    for action, day in actions:
        action_cards.append(f"""<article><span class="status">{escape(action["status"])}</span>
<h3>{escape(action["title"])}</h3><p class="minor">{escape(action["id"])} ／ 最終記録 {escape(day)}</p>
<dl><dt>確認根拠</dt><dd>{escape(action.get("evidence") or "未確認")}</dd>
<dt>追跡指標</dt><dd>{escape(action["metric"])}</dd></dl></article>""")
    metric_section = "".join(metric_cards) or "<p>成果指標は未計測です。</p>"
    action_section = "".join(action_cards) or "<p>施策IDの記録はありません。</p>"
    history = ""
    if measurements:
        history = f"""<section><details><summary>全測定日の成果指標と比較条件</summary>
<div class="table-wrap">{accessible_table(headers, measurements)}</div></details></section>"""
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>月次マーケティング報告 — {escape(brand)}</title><style>{STYLE}</style></head>
<body><header><div><p>{escape(brand)}</p><h1>月次マーケティング報告</h1>
<p>診断期間　{escape(first_day)} 〜 {escape(last_day)}　／　測定 {len(entries)} 回</p></div></header>
<main><section><h2>今回の成果指標</h2><div class="cards">{metric_section}</div></section>
<section><h2>施策の実施状況</h2><div class="cards">{action_section}</div></section>
<section><h2>診断スコアの推移</h2><div class="table-wrap">
{accessible_table(["測定日", "総合", "前回比", "実施メモ"], scores)}</div></section>{history}
<footer>対象URL　{escape(data.get("url") or "未記録")}</footer></main></body></html>
"""
