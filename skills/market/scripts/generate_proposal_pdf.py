#!/usr/bin/env python3
"""CLIENT-PROPOSAL.md をHTMLとPDFに変換する（提案書専用の簡易変換）。

配色・書体は hiro-html-design 準拠（generate_report_html.py と同じPALETTEを流用）。
冒頭の内部向け注記ブロック（送付前に削除する指示）は、変換時に自動で除外する。

HTMLファイルは中間生成物ではなく、共有用の成果物として常に残す。
（先方にPDFが開けない場合の代替、ブラウザでの手早い確認用など）

使い方:
  python3 generate_proposal_pdf.py <ドメイン>/CLIENT-PROPOSAL.md <ドメイン>/CLIENT-PROPOSAL.pdf

  → 同じフォルダに CLIENT-PROPOSAL.html と CLIENT-PROPOSAL.pdf の両方を出力する
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

PALETTE = {
    "bg": "#FCFBF7", "paper": "#ffffff", "text": "#1F2A44", "gray": "#5A6478",
    "brand": "#1F2A44", "accent": "#B99745", "blue": "#2563EB",
    "blueLight": "#EFF4FF", "border": "#E8E4DA", "highlight": "#FDF8EC",
}

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def find_chrome():
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def strip_admin_note(md: str) -> str:
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith(">"):
            while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ""):
                if lines[i].strip() == "" and (i + 1 >= len(lines) or not lines[i + 1].startswith(">")):
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def render_table(rows):
    header, _, *body = rows
    cells_h = [c.strip() for c in header.strip("|").split("|")]
    out = ['<table><thead><tr>']
    out += [f"<th>{inline(c)}</th>" for c in cells_h]
    out.append("</tr></thead><tbody>")
    for r in body:
        cells = [c.strip() for c in r.strip("|").split("|")]
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def md_to_html_body(md: str) -> str:
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "---":
            out.append("<hr/>")
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append(f"<pre>{html.escape(chr(10).join(code))}</pre>")
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1)) + 1
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            out.append(render_table(table_lines))
            continue

        if re.match(r"^-\s+", stripped):
            items = []
            while i < n and re.match(r"^-\s+", lines[i].strip()):
                items.append(re.sub(r"^-\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(it)}</li>" for it in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline(it)}</li>" for it in items) + "</ol>")
            continue

        if stripped == "":
            i += 1
            continue

        out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    return "\n".join(out)


CSS = f"""
:root {{
{chr(10).join(f'  --hiro-{k}: {v};' for k, v in PALETTE.items())}
}}
* {{ box-sizing: border-box; }}
body {{
  background: var(--hiro-bg);
  color: var(--hiro-text);
  font-family: 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  line-height: 1.85;
  max-width: 860px;
  margin: 0 auto;
  padding: 56px 48px 80px;
  font-size: 14.5px;
}}
h1 {{ font-size: 26px; font-weight: 700; color: var(--hiro-brand); margin: 0 0 4px; }}
h2 {{
  font-size: 20px; font-weight: 700; color: var(--hiro-brand);
  border-left: 4px solid var(--hiro-accent); padding-left: 12px;
  margin: 40px 0 18px; page-break-before: auto;
}}
h3 {{
  font-size: 15.5px; font-weight: 700; color: var(--hiro-brand);
  border-bottom: 1px solid var(--hiro-border); padding-bottom: 6px;
  margin: 26px 0 12px;
}}
p {{ margin: 10px 0; }}
strong {{ color: var(--hiro-brand); }}
hr {{ border: none; border-top: 1px solid var(--hiro-border); margin: 28px 0; }}
ul, ol {{ padding-left: 22px; margin: 10px 0; }}
li {{ margin: 5px 0; }}
code {{ background: var(--hiro-highlight); padding: 1px 5px; border-radius: 3px; font-size: 13px; }}
pre {{
  background: var(--hiro-code, #1E293B); color: #E2E8F0; padding: 16px 20px;
  border-radius: 8px; font-size: 12.5px; overflow-x: auto; white-space: pre-wrap;
  line-height: 1.7;
}}
table {{ width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px; }}
th {{
  text-align: left; padding: 9px 12px; background: var(--hiro-paper);
  border-bottom: 2px solid var(--hiro-brand); color: var(--hiro-gray); font-weight: 500;
}}
td {{ padding: 9px 12px; border-bottom: 1px solid var(--hiro-border); }}
tr:last-child td {{ border-bottom: none; }}
@media print {{
  body {{ padding: 24px 8px; }}
  h2 {{ page-break-after: avoid; }}
  table, pre {{ page-break-inside: avoid; }}
}}
"""


def build_html(md_path: Path) -> str:
    raw = md_path.read_text(encoding="utf-8")
    cleaned = strip_admin_note(raw)
    body = md_to_html_body(cleaned)
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>マーケティング戦略 ご提案書</title>
<style>{CSS}</style></head><body>{body}</body></html>"""


def to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if not chrome:
        print("Chrome が見つかりません。HTMLはブラウザで開き、"
              "「印刷 → PDFとして保存」で変換してください。", file=sys.stderr)
        return False
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--virtual-time-budget=8000",
           f"--print-to-pdf={Path(pdf_path).resolve()}",
           Path(html_path).resolve().as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not Path(pdf_path).exists():
        print(f"PDF変換に失敗しました。\n{r.stderr[:400]}", file=sys.stderr)
        return False
    return True


def main():
    if len(sys.argv) < 3:
        print("使い方: python3 generate_proposal_pdf.py 入力.md 出力.pdf", file=sys.stderr)
        return 1
    md_path, pdf_path = Path(sys.argv[1]), Path(sys.argv[2])
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(build_html(md_path), encoding="utf-8")
    print(f"HTMLを出力しました: {html_path}（共有用に保持）")

    if to_pdf(html_path, pdf_path):
        size = Path(pdf_path).stat().st_size
        print(f"PDFを出力しました: {pdf_path}（{size:,} バイト）")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
