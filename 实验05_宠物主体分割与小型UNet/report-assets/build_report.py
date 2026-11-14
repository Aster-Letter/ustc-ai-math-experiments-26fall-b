"""从独立report.md生成中文PDF；保留原始课程报告模板。"""
import re
from pathlib import Path
from html import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, Preformatted, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('Song', 'C:/Windows/Fonts/simsun.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hei', 'C:/Windows/Fonts/simhei.ttf'))
pdfmetrics.registerFontFamily('Song', normal='Song', bold='Hei', italic='Song', boldItalic='Hei')
NAVY = colors.HexColor('#193953')
TEAL = colors.HexColor('#167b83')
styles = {
    'body': ParagraphStyle('body', fontName='Song', fontSize=10.2, leading=15.8,
                           spaceAfter=8, wordWrap='CJK', textColor=colors.HexColor('#202c36')),
    'h1': ParagraphStyle('h1', fontName='Hei', fontSize=23, leading=30,
                         textColor=NAVY, spaceAfter=12),
    'h2': ParagraphStyle('h2', fontName='Hei', fontSize=15, leading=21,
                         textColor=NAVY, spaceBefore=9, spaceAfter=9, keepWithNext=True),
    'h3': ParagraphStyle('h3', fontName='Hei', fontSize=11.5, leading=17,
                         textColor=TEAL, spaceBefore=5, spaceAfter=7, keepWithNext=True),
    'cell': ParagraphStyle('cell', fontName='Song', fontSize=9, leading=13, wordWrap='CJK'),
    'th': ParagraphStyle('th', fontName='Hei', fontSize=9, leading=13,
                         textColor=colors.white, wordWrap='CJK'),
    'caption': ParagraphStyle('caption', fontName='Song', fontSize=8.6, leading=12,
                              textColor=colors.HexColor('#526575'), alignment=TA_CENTER,
                              spaceAfter=7),
    'code': ParagraphStyle('code', fontName='Courier', fontSize=8.1, leading=11,
                           backColor=colors.HexColor('#f2f5f7'), borderPadding=8,
                           spaceBefore=4, spaceAfter=10),
}

def inline(text):
    text = escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<font color="#167b83">\1</font>', text)

def footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor('#ccd8df'))
    canvas.line(45, h-35, w-45, h-35)
    canvas.setFont('Song', 8)
    canvas.setFillColor(colors.HexColor('#526575'))
    canvas.drawString(45, h-26, '实验05  /  宠物主体分割')
    canvas.drawRightString(w-45, 25, f'{doc.page}')
    canvas.restoreState()

def build():
    doc = SimpleDocTemplate(str(ROOT / 'report.pdf'), pagesize=A4,
                            leftMargin=45, rightMargin=45, topMargin=48, bottomMargin=43,
                            title='实验05：宠物主体分割', author='实验报告',
                            subject='基础编解码器、BN改进与小型U-Net的实测对照')
    lines = (ROOT / 'report.md').read_text(encoding='utf-8').splitlines()
    story, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
            i += 1
        elif line.startswith('```'):
            i += 1
            block = []
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i])
                i += 1
            story.append(Preformatted('\n'.join(block), styles['code']))
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+', c) for c in row):
                    rows.append(row)
                i += 1
            n = len(rows[0])
            weights = {2: [1,3.4], 3:[1,1.6,1.6], 4:[1.15,1.5,1.7,.75],
                       5:[1.1,1.3,1.8,1.3,.65], 6:[1.65,.85,.75,1,1,.85]}[n]
            if rows[0][0] == '原始值':
                weights = [.7, 1.4, 1.1, .8, 1.5]
            widths = [doc.width * x / sum(weights) for x in weights]
            data = [[Paragraph(inline(c), styles['th' if r == 0 else 'cell'])
                     for c in row] for r, row in enumerate(rows)]
            table = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), NAVY),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f5f7')]),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LINEBELOW', (0,0), (-1,0), .5, NAVY),
                ('LINEBELOW', (0,-1), (-1,-1), .5, colors.HexColor('#ccd8df')),
            ]))
            story.extend([table, Spacer(1,10)])
        elif line.startswith('!['):
            match = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
            title, path = match.groups()
            img = Image(str(ROOT / path))
            scale = min(doc.width/img.imageWidth, 210/img.imageHeight)
            img.drawWidth, img.drawHeight = img.imageWidth*scale, img.imageHeight*scale
            story.append(KeepTogether([img, Paragraph(inline(title), styles['caption'])]))
            i += 1
        else:
            match = re.match(r'^(#{1,3}) (.*)$', line)
            if match:
                story.append(Paragraph(inline(match[2]), styles['h'+str(len(match[1]))]))
            else:
                story.append(Paragraph(inline(line), styles['body']))
            i += 1
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

if __name__ == '__main__':
    build()
