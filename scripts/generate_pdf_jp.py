import json
import sys
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, String, Group, Circle, Rect
from reportlab.graphics.charts.barcharts import HorizontalBarChart

# ---------------------------------------------------------
# 1. トラスト・ブルー：カラーパレット＆フォント定義
# ---------------------------------------------------------
# どの環境でも文字化けしない標準日本語フォントを登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
FONT_NAME = 'HeiseiKakuGo-W5'

# トラスト・ブルーの配色設定
NAVY = colors.HexColor("#1B2A4A")       # 権威と信頼のネイビー（見出し）
BLUE = colors.HexColor("#2D5BFF")       # 鮮やかなブルー（アクセント）
LIGHT_BG = colors.HexColor("#F5F7FA")   # 清潔感のあるライトグレー（背景）
TEXT_COLOR = colors.HexColor("#2C3E50") # 視認性の高いダークグレー（本文）
BORDER = colors.HexColor("#E0E6ED")     # 境界線

# スコア用ステータスカラー
COLOR_A = colors.HexColor("#00C853") # 優秀 (80-100)
COLOR_B = colors.HexColor("#2D5BFF") # 良好 (60-79)
COLOR_C = colors.HexColor("#FFB300") # 要改善 (40-59)
COLOR_D = colors.HexColor("#FF1744") # 致命的 (0-39)

def get_score_color(score):
    if score >= 80: return COLOR_A
    if score >= 60: return COLOR_B
    if score >= 40: return COLOR_C
    return COLOR_D

def get_grade(score):
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"

# ---------------------------------------------------------
# 2. スタイルシート定義
# ---------------------------------------------------------
def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='TrustTitle',
        fontName=FONT_NAME,
        fontSize=24,
        textColor=NAVY,
        spaceAfter=20,
        leading=30
    ))
    
    styles.add(ParagraphStyle(
        name='TrustHeading',
        fontName=FONT_NAME,
        fontSize=16,
        textColor=NAVY,
        spaceAfter=15,
        spaceBefore=20,
        leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='TrustBody',
        fontName=FONT_NAME,
        fontSize=10,
        textColor=TEXT_COLOR,
        leading=16,
        spaceAfter=10
    ))
    
    return styles

# ---------------------------------------------------------
# 3. 描画コンポーネント
# ---------------------------------------------------------
def create_score_gauge(score):
    """表紙の円形スコアゲージを描画"""
    d = Drawing(200, 200)
    color = get_score_color(score)
    
    # 外枠
    d.add(Circle(100, 100, 90, fillColor=None, strokeColor=BORDER, strokeWidth=10))
    # スコア枠（簡易的な円で表現）
    d.add(Circle(100, 100, 90, fillColor=None, strokeColor=color, strokeWidth=10))
    
    # 中央のテキスト
    d.add(String(100, 110, str(score), fontName=FONT_NAME, fontSize=48, fillColor=NAVY, textAnchor='middle'))
    d.add(String(100, 80, "/ 100", fontName=FONT_NAME, fontSize=16, fillColor=TEXT_COLOR, textAnchor='middle'))
    d.add(String(100, 50, f"GRADE: {get_grade(score)}", fontName=FONT_NAME, fontSize=14, fillColor=color, textAnchor='middle'))
    
    return d

def create_bar_chart(categories):
    """2ページ目のカテゴリ別スコア棒グラフ"""
    d = Drawing(400, 200)
    chart = HorizontalBarChart()
    chart.x = 50
    chart.y = 20
    chart.height = 160
    chart.width = 300
    
    names = list(categories.keys())
    scores = [categories[k]['score'] for k in names]
    
    chart.data = [scores]
    chart.categoryAxis.categoryNames = names
    chart.categoryAxis.labels.fontName = FONT_NAME
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 25
    chart.valueAxis.labels.fontName = FONT_NAME
    
    # バーの配色
    for i, score in enumerate(scores):
        chart.bars[0][i].fillColor = get_score_color(score)
    
    d.add(chart)
    return d

# ---------------------------------------------------------
# 4. メインPDF生成ロジック
# ---------------------------------------------------------
def generate_pdf(data, output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = create_styles()
    story = []

    # --- ページ1：表紙 & サマリー ---
    story.append(Paragraph("マーケティング監査レポート", styles['TrustTitle']))
    story.append(Paragraph(f"対象URL: {data.get('url', 'N/A')} | 発行日: {data.get('date', 'N/A')}", styles['TrustBody']))
    story.append(Spacer(1, 1*cm))
    
    # ゲージを中央に配置
    story.append(create_score_gauge(data.get('overall_score', 0)))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("エグゼクティブ・サマリー", styles['TrustHeading']))
    story.append(Paragraph(data.get('executive_summary', ''), styles['TrustBody']))
    story.append(PageBreak())

    # --- ページ2：スコア内訳 ---
    story.append(Paragraph("評価スコア内訳", styles['TrustTitle']))
    cats = data.get('categories', {})
    if cats:
        story.append(create_bar_chart(cats))
        story.append(Spacer(1, 1*cm))
        
        # テーブルデータの作成
        table_data = [["カテゴリ", "スコア", "重み"]]
        for name, info in cats.items():
            table_data.append([name, f"{info['score']}/100", info['weight']])
            
        t = Table(table_data, colWidths=[8*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
    story.append(PageBreak())

    # --- ページ3：主要課題 ---
    story.append(Paragraph("主要課題", styles['TrustTitle']))
    findings = data.get('findings', [])
    if findings:
        table_data = [["重要度", "課題内容"]]
        for f in findings:
            table_data.append([f.get('severity', ''), f.get('finding', '')])
            
        t = Table(table_data, colWidths=[3*cm, 13*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
    story.append(PageBreak())

    # --- ページ4：アクションプラン ---
    story.append(Paragraph("優先度別アクションプラン", styles['TrustTitle']))
    
    sections = [
        ("クイックウィン (今週中)", data.get('quick_wins', [])),
        ("中期施策 (1〜3ヶ月)", data.get('medium_term', [])),
        ("戦略施策 (3〜6ヶ月)", data.get('strategic', []))
    ]
    
    for title, items in sections:
        if items:
            story.append(Paragraph(title, styles['TrustHeading']))
            for i, item in enumerate(items, 1):
                story.append(Paragraph(f"{i}. {item}", styles['TrustBody']))
            story.append(Spacer(1, 0.5*cm))

    # --- PDF生成実行 ---
    doc.build(story)
    print(f"PDFを出力しました: {output_filename}")

# ---------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------
if __name__ == "__main__":
    # 引数からJSONと出力先を取得（デフォルトのモックデータも用意）
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        output_pdf = sys.argv[2] if len(sys.argv) > 2 else "MARKETING-REPORT-output.pdf"
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("テストデータでPDFを生成します...")
        data = {
            "url": "https://example.com",
            "date": "2026年3月6日",
            "overall_score": 75,
            "executive_summary": "トラスト・ブルーのデザインを適用したサマリーです。洗練されたレイアウトで出力されています。",
            "categories": {
                "コンテンツ&メッセージ": {"score": 82, "weight": "25%"},
                "コンバージョン最適化": {"score": 54, "weight": "20%"}
            },
            "findings": [{"severity": "致命的", "finding": "コンバージョンボタンが目立たない"}],
            "quick_wins": ["ボタンの色をブルーにする"]
        }
        output_pdf = "MARKETING-REPORT-sample.pdf"
        
    generate_pdf(data, output_pdf)