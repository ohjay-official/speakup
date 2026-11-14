"""Build report/SpeakUp.docx in the Apart template layout from report/paper_final.md.

Needs pandoc and python-docx. The reference styles come from scripts/make_reference_docx.py (ref.docx in /tmp).
"""
import re
import subprocess

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

REF = "/tmp/speakup_ref.docx"
subprocess.run(["pandoc", "-o", REF, "--print-default-data-file", "reference.docx"], check=True)
subprocess.run(["python3", "scripts/make_reference_docx.py", REF], check=True)

md = open("report/paper_final.md").read()
title = re.search(r"^# (.+)$", md, re.M).group(1)
abstract = re.search(r"## Abstract\n\n(.+?)\n\n## 1\.", md, re.S).group(1).strip()
body = md[md.index("## 1. Introduction"):]
body = re.sub(r"\]\(report/(fig_\w+\.png)\)\{w=\d+\}", r"](report/\1){width=11.5cm}", body)
body = body.replace("## ", "# ").replace("\n### ", "\n## ")
body = body.replace("d′", "d⁠′")  # keep d and prime together
abstract = abstract.replace("d′", "d⁠′")
y = (f'---\ntitle: "{title.upper()}^[Research conducted at the AI x Epistemics Research Sprint, November 2026.]"\n'
     'author:\n  - "Faithful Adejoh"\n  - "Mechatronics Engineering, Bowen University, Nigeria"\n  - "With Apart Research"\n'
     f"abstract: |\n  {abstract}\n---\n\n")
open("/tmp/speakup_docx.md", "w").write(y + body)
subprocess.run(["pandoc", "/tmp/speakup_docx.md", "-o", "report/SpeakUp.docx", f"--reference-doc={REF}"], check=True)

d = Document("report/SpeakUp.docx")
# rules above the title and below the author block, as in the template
def rule(p, side):
    pPr = p._p.get_or_add_pPr()
    bd = pPr.find(qn("w:pBdr"))
    if bd is None:
        bd = OxmlElement("w:pBdr"); pPr.append(bd)
    e = OxmlElement(f"w:{side}")
    for k, v in (("val", "single"), ("sz", "12"), ("space", "8"), ("color", "000000")):
        e.set(qn("w:" + k), v)
    bd.append(e)
rule(d.paragraphs[0], "top")
for p in d.paragraphs[:6]:
    if p.text.strip() == "With Apart Research":
        rule(p, "bottom")
avail = Cm(21.59 - 5.08)
for t in d.tables:
    ncol = len(t.columns)
    lens = [max(18, max(len(r.cells[j].text) for r in t.rows)) ** 0.6 for j in range(ncol)]
    ws = [int(avail * l / sum(lens)) for l in lens]
    t.autofit = False
    tblW = t._tbl.tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW"); t._tbl.tblPr.append(tblW)
    tblW.set(qn("w:w"), str(int(sum(ws) / 635))); tblW.set(qn("w:type"), "dxa")
    for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), ws):
        gc.set(qn("w:w"), str(int(w / 635)))
    for r in t.rows:
        for j, c in enumerate(r.cells):
            c.width = ws[j]
            for para in c.paragraphs:
                para.paragraph_format.space_after = Pt(1)
                for run in para.runs:
                    run.font.size = Pt(8.5)
d.save("report/SpeakUp.docx")
print("wrote report/SpeakUp.docx")
