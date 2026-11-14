from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
d=Document('ref.docx')
S={s.name:s for s in d.styles}
def setf(name,size=None,bold=None,italic=None,align=None,before=None,after=None):
    s=S[name]; f=s.font; f.color.rgb=RGBColor(0,0,0)
    rpr=s.element.get_or_add_rPr(); rf=rpr.find(W+'rFonts')
    if rf is None: rf=OxmlElement('w:rFonts'); rpr.insert(0,rf)
    for a in ('asciiTheme','hAnsiTheme','cstheme','eastAsiaTheme'): rf.attrib.pop(W+a,None)
    for a in ('ascii','hAnsi','cs','eastAsia'): rf.set(W+a,'Times New Roman')
    if size: f.size=Pt(size)
    if bold is not None: f.bold=bold
    if italic is not None: f.italic=italic
    if not hasattr(s,'paragraph_format'): return
    pf=s.paragraph_format
    if align is not None: pf.alignment=align
    if before is not None: pf.space_before=Pt(before)
    if after is not None: pf.space_after=Pt(after)
J=WD_ALIGN_PARAGRAPH.JUSTIFY; C=WD_ALIGN_PARAGRAPH.CENTER
for n in ('Compact','Block Text','Hyperlink','Caption','Bibliography','Verbatim Char'): setf(n)
S['Hyperlink'].font.color.rgb=RGBColor(0x1a,0x4f,0x9c)
setf('Normal',11); setf('Body Text',11,align=J,before=0,after=5); setf('First Paragraph',11,align=J,before=0,after=5); setf('Compact',10.5,after=2)
setf('Footnote Text',8.5)
setf('Heading 1',13,True,False,before=12,after=4); setf('Heading 2',11.5,True,False,before=8,after=3); setf('Heading 3',11,True,False,before=6,after=2)
setf('Title',15,True,False,align=C,before=0,after=8); setf('Author',11,align=C,after=2); setf('Abstract Title',11.5,True,align=C,before=10,after=4); setf('Abstract',11,italic=True,align=J,after=6)
setf('Image Caption',9.5,False,True,after=8); setf('Table Caption',9.5,False,True,after=8)
for n in ('Heading 1','Heading 2','Heading 3','Abstract Title'): S[n].paragraph_format.keep_with_next=True
sec=d.sections[0]; sec.page_width=Cm(21.59); sec.page_height=Cm(27.94)
for m in ('left_margin','right_margin','top_margin','bottom_margin'): setattr(sec,m,Cm(2.54))
d.save('ref.docx'); print('ok')
