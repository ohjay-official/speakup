"""Render report/paper_final.md to report/SpeakUp.pdf with reportlab.

Supports: # title, ## / ### headings, paragraphs, **bold**, *italic*, `code`,
pipe tables, numbered and bulleted lists, and ![caption](path) images.
"""
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, ListFlowable, ListItem, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

src = sys.argv[1] if len(sys.argv) > 1 else "report/paper_final.md"
dst = sys.argv[2] if len(sys.argv) > 2 else "report/SpeakUp.pdf"

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
_L = "/usr/share/fonts/truetype/liberation/LiberationSerif-"
for _n, _f in (("Serif", "Regular"), ("Serif-Bold", "Bold"), ("Serif-Italic", "Italic"), ("Serif-BoldItalic", "BoldItalic")):
    pdfmetrics.registerFont(TTFont(_n, _L + _f + ".ttf"))
addMapping("Serif", 0, 0, "Serif"); addMapping("Serif", 1, 0, "Serif-Bold")
addMapping("Serif", 0, 1, "Serif-Italic"); addMapping("Serif", 1, 1, "Serif-BoldItalic")

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Serif", fontSize=10, leading=13,
                      alignment=TA_JUSTIFY, spaceAfter=5)
small = ParagraphStyle("s", parent=body, fontSize=8, leading=10, alignment=0, spaceAfter=0)
cap = ParagraphStyle("c", parent=body, fontSize=8.5, leading=10.5, textColor=colors.HexColor("#52514e"))
h1 = ParagraphStyle("h1", parent=body, fontName="Serif-Bold", fontSize=16, leading=19, alignment=1, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=body, keepWithNext=1, fontName="Serif-Bold", fontSize=12, leading=15, spaceBefore=8, spaceAfter=4,
                    alignment=0)
h3 = ParagraphStyle("h3", parent=body, keepWithNext=1, fontName="Serif-Bold", fontSize=10.5, leading=13, spaceBefore=4, alignment=0)
author = ParagraphStyle("a", parent=body, alignment=1, fontSize=10)


def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)
    return t


def table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    data = [[Paragraph(("<b>%s</b>" if i == 0 else "%s") % inline(c), small) for c in r] for i, r in enumerate(rows)]
    # widths in proportion to each column's longest cell (square root, so long text columns get more but not all)
    ncol = max(len(r) for r in rows)
    avail = A4[0] - 4 * cm
    wts = [max(18, max(len(r[j]) if j < len(r) else 0 for r in rows)) ** 0.6 for j in range(ncol)]
    widths = [avail * w / sum(wts) for w in wts]
    t = Table(data, repeatRows=1, hAlign="LEFT", colWidths=widths)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
                           ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                           ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
    return t


story = []
lines = open(src).read().split("\n")
i = 0
para = []


def flush():
    global para
    if para:
        story.append(Paragraph(inline(" ".join(para)), body))
        para = []


first_h1 = True
while i < len(lines):
    l = lines[i]
    if l.startswith("# "):
        flush()
        story.append(Paragraph(inline(l[2:]), h1))
    elif l.startswith("## "):
        flush()
        story.append(Paragraph(inline(l[3:]), h2))
    elif l.startswith("### "):
        flush()
        story.append(Paragraph(inline(l[4:]), h3))
    elif l.startswith("|"):
        flush()
        tl = []
        while i < len(lines) and lines[i].startswith("|"):
            tl.append(lines[i])
            i += 1
        story.append(table(tl))
        story.append(Spacer(1, 5))
        continue
    elif m := re.match(r"!\[(.*)\]\((.+?)\)(?:\{w=([\d.]+)\})?", l):
        flush()
        w = float(m.group(3) or 16) * cm
        img = Image(m.group(2))
        img.drawHeight = img.drawHeight * w / img.drawWidth
        img.drawWidth = w
        story.append(KeepTogether([img, Paragraph(inline(m.group(1)), cap)]))
    elif re.match(r"^(\d+\.|-) ", l):
        flush()
        items = []
        num = l[0].isdigit()
        while i < len(lines) and re.match(r"^(\d+\.|-) ", lines[i]):
            txt = re.sub(r"^(\d+\.|-) ", "", lines[i])
            i += 1
            while i < len(lines) and lines[i].startswith("   ") and lines[i].strip():
                txt += " " + lines[i].strip()
                i += 1
            items.append(ListItem(Paragraph(inline(txt), body), leftIndent=12))
        story.append(ListFlowable(items, bulletType="1" if num else "bullet", leftIndent=12, bulletFontSize=9))
        continue
    elif l.strip() == "":
        flush()
    elif l.startswith("**Faithful") or l.strip() == "With Apart Research":
        flush()
        story.append(Paragraph(inline(l), author))
    else:
        para.append(l.strip())
    i += 1
flush()


def foot(c, d):
    c.saveState()
    c.setFont("Serif", 8)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, str(d.page))
    c.restoreState()


doc = SimpleDocTemplate(dst, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm,
                        bottomMargin=2 * cm, title="SpeakUp", author="Faithful Adejoh")
doc.build(story, onFirstPage=foot, onLaterPages=foot)
print("wrote", dst)
