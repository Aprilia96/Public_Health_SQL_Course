#!/usr/bin/env python3
"""Build the single-PDF book edition of the course from content.txt."""
import re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily, stringWidth
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, Table, TableStyle, PageBreak, XPreformatted, KeepTogether,
    NextPageTemplate, Image)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.flowables import Flowable

class SectionMark(Flowable):
    """Invisible marker so nested module banners still register in TOC/outline."""
    def __init__(self, text):
        super().__init__(); self.text = text
        self.width = 0; self.height = 0
    def wrap(self, aw, ah): return (0, 0)
    def draw(self): pass

# ---------------- fonts ----------------
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DVS",  FD+"DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVSB", FD+"DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVSO", FD+"DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DVSBO",FD+"DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DVM",  FD+"DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DVMB", FD+"DejaVuSansMono-Bold.ttf"))
registerFontFamily("DVS", normal="DVS", bold="DVSB", italic="DVSO", boldItalic="DVSBO")
registerFontFamily("DVM", normal="DVM", bold="DVMB", italic="DVM", boldItalic="DVMB")

# ---------------- palette ----------------
INK   = colors.HexColor("#102329"); SOFT = colors.HexColor("#3d5560")
TEAL  = colors.HexColor("#0e7c86"); TEALD= colors.HexColor("#0a5d65")
NHS   = colors.HexColor("#005eb8"); NAVY = colors.HexColor("#0a3550")
CODEBG= colors.HexColor("#0d1f24"); CODEHD=colors.HexColor("#122a30")
CODEFG= colors.HexColor("#d8e8ec"); CODEDIM=colors.HexColor("#7fa4ad")
LINE  = colors.HexColor("#dbe5e3"); GREEN= colors.HexColor("#1e7a44")
AMBER = colors.HexColor("#b35a00"); PURP = colors.HexColor("#5b4b9e")
KEYBG = colors.HexColor("#e8f2f3"); KEYLN= colors.HexColor("#c9dfe1")
QBG   = colors.HexColor("#f7fafa")
NOTES = {"info": (colors.HexColor("#eef4fb"), NHS,   "NOTE"),
         "warn": (colors.HexColor("#fdf3e7"), AMBER, "TAKE CARE"),
         "ai":   (colors.HexColor("#f1eefa"), PURP,  "AI CORNER"),
         "study":(colors.HexColor("#edf6f0"), GREEN, "STUDY TIP")}

PAGE_W, PAGE_H = A4
ML, MR, MT, MB = 46, 46, 58, 54
USABLE = PAGE_W - ML - MR

# ---------------- styles ----------------
def S(name, **kw):
    d = dict(fontName="DVS", fontSize=9.6, leading=13.8, textColor=INK,
             spaceBefore=0, spaceAfter=6, alignment=TA_LEFT)
    d.update(kw); return ParagraphStyle(name, **d)

st_body   = S("body")
st_bullet = S("bullet", leftIndent=14, bulletIndent=3, spaceAfter=3, bulletFontName="DVS")
st_h3     = S("h3", fontName="DVSB", fontSize=11.2, leading=14, textColor=TEALD,
              spaceBefore=10, spaceAfter=5)
st_lesson = S("LessonTitle", fontName="DVSB", fontSize=14.5, leading=18,
              spaceBefore=0, spaceAfter=2)
st_eyebrow= S("eyebrow", fontName="DVSB", fontSize=7.2, textColor=TEAL,
              spaceAfter=3, leading=9)
st_modban = S("ModTitle", fontName="DVSB", fontSize=23, leading=28,
              textColor=colors.white, spaceAfter=0)
st_modkick= S("modkick", fontName="DVSB", fontSize=9, textColor=colors.HexColor("#9fe0e6"),
              spaceAfter=6, leading=11)
st_lab    = S("lab", fontName="DVSB", fontSize=7.2, leading=9, spaceAfter=4)
st_why    = S("why", fontName="DVSO", fontSize=8.8, leading=12.4, textColor=SOFT, spaceAfter=0)
st_opt    = S("opt", fontSize=9.2, leading=12.6, spaceAfter=2.5, leftIndent=13, bulletIndent=1)
st_opt_ok = ParagraphStyle("optok", parent=st_opt, bulletFontName="DVSB",
                           bulletColor=GREEN)
st_opt_no = ParagraphStyle("optno", parent=st_opt, bulletFontName="DVS",
                           bulletColor=colors.HexColor("#9db9bd"))
st_qtext  = S("qtext", fontName="DVSB", spaceAfter=5)
st_cell   = S("cell", fontSize=8.4, leading=11.2, spaceAfter=0)
st_cellh  = S("cellh", fontName="DVSB", fontSize=7.6, leading=10, spaceAfter=0,
              textColor=SOFT)
st_mono   = ParagraphStyle("mono", fontName="DVM", fontSize=7.8, leading=10.4,
              textColor=CODEFG)
st_chead  = S("chead", fontName="DVSB", fontSize=7.4, leading=9,
              textColor=colors.HexColor("#9fc0c7"), spaceAfter=0)
st_toc0 = ParagraphStyle("toc0", fontName="DVSB", fontSize=10.5, leading=17, textColor=INK)
st_toc1 = ParagraphStyle("toc1", fontName="DVS", fontSize=9, leading=13.6,
                         leftIndent=16, textColor=INK)

# ---------------- parse content ----------------
raw = open(os.path.join(BASE, "src", "content.txt"), encoding="utf-8").read()
raw = raw.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
raw = raw.replace("\u2728", "*")          # sparkles emoji not in DejaVu
lines = raw.split("\n")
i = 0
MODS, LESSONS = [], []
while i < len(lines) and lines[i].strip() != "#MODULES": i += 1
i += 1
while i < len(lines) and not lines[i].startswith("#LESSON "):
    m = re.match(r"^(\d+)\|(.+)$", lines[i])
    if m: MODS.append({"n": int(m.group(1)), "title": m.group(2).strip(), "lessons": []})
    i += 1
cur = None; block = None
def endb():
    global block
    if block is not None and cur is not None: cur["blocks"].append(block)
    block = None
for L in lines[i:]:
    lm = re.match(r"^#LESSON (\d+)\|(.+)$", L)
    if lm:
        endb()
        cur = {"n": len(LESSONS)+1, "mod": int(lm.group(1)),
               "title": lm.group(2).strip(), "blocks": []}
        LESSONS.append(cur)
        MODS[cur["mod"]-1]["lessons"].append(cur)
        continue
    if L.startswith("::"):
        endb()
        parts = L[2:].split("|")
        block = {"type": parts[0].strip(), "args": parts[1:], "lines": []}
        continue
    if block is not None: block["lines"].append(L)
endb()

# ---------------- inline markup ----------------
def xml(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def inline(s):
    s = xml(s)
    s = re.sub(r"`([^`]+)`",
        r'<font face="DVM" size="8.2" color="#0a4f57">\1</font>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<link href="\2" color="#005eb8"><u>\1</u></link>', s)
    return s

def para_flows(blines, body=st_body, bullet=st_bullet):
    out = []
    for chunk_line in blines:
        t = chunk_line.rstrip()
        if not t.strip(): continue
        if t.startswith("- "):
            out.append(Paragraph(inline(t[2:]), bullet, bulletText="\u2022"))
        else:
            out.append(Paragraph(inline(t), body))
    return out

# ---------------- code blocks ----------------
LANGNAME = {"sql":"SQL","sqltry":"SQL \u00b7 try it in the playground","r":"R",
            "text":"TEXT","bash":"SHELL","powershell":"POWERSHELL","python":"PYTHON",
            "yaml":"YAML"}
def wrap_code(line, maxw):
    if stringWidth(line, "DVM", 7.8) <= maxw: return [line]
    out, curl = [], ""
    for ch in line:
        if stringWidth(curl+ch, "DVM", 7.8) > maxw:
            out.append(curl); curl = "  \u21aa " + ch
        else: curl += ch
    if curl: out.append(curl)
    return out

def code_table(lang, label, code):
    maxw = USABLE - 18
    name = label if label else LANGNAME.get(lang, (lang or "code").upper())
    rows = [[Paragraph(xml(name.upper()), st_chead)]]
    styles = [("BACKGROUND",(0,0),(-1,0),CODEHD),
              ("BACKGROUND",(0,1),(-1,-1),CODEBG),
              ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
              ("TOPPADDING",(0,0),(-1,0),4),("BOTTOMPADDING",(0,0),(-1,0),4),
              ("TOPPADDING",(0,1),(-1,-1),0.6),("BOTTOMPADDING",(0,1),(-1,-1),0.6),
              ("VALIGN",(0,0),(-1,-1),"TOP")]
    body = code.strip("\n").split("\n")
    for ln in body:
        for piece in wrap_code(ln, maxw):
            dim = bool(re.match(r"^\s*(--|#)", ln)) and lang in ("sql","sqltry","r","bash","text","python","yaml")
            txt = '<font color="#7fa4ad">%s</font>' % xml(piece) if dim else xml(piece)
            rows.append([XPreformatted(txt, st_mono)])
    t = Table(rows, colWidths=[USABLE], repeatRows=1, style=TableStyle(styles))
    t.spaceBefore, t.spaceAfter = 7, 9
    return t

# ---------------- boxed helpers ----------------
def boxed(flows, bg, border, pad=9):
    t = Table([[flows]], colWidths=[USABLE],
        style=TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
            ("BOX",(0,0),(-1,-1),0.9,border),
            ("LEFTPADDING",(0,0),(-1,-1),pad),("RIGHTPADDING",(0,0),(-1,-1),pad),
            ("TOPPADDING",(0,0),(-1,-1),pad-2),("BOTTOMPADDING",(0,0),(-1,-1),pad-2),
            ("VALIGN",(0,0),(-1,-1),"TOP")]))
    t.spaceBefore, t.spaceAfter = 7, 9
    return t

# ---------------- block renderers ----------------
def r_p(b):    return para_flows(b["lines"])
def r_h(b):    return [Paragraph(inline(b["args"][0] if b["args"] else ""), st_h3)]
def r_code(b):
    lang = (b["args"][0] if b["args"] else "text").strip()
    label = b["args"][1] if len(b["args"]) > 1 else None
    return [code_table(lang, label, "\n".join(b["lines"]))]
def r_oscode(b):
    lang = (b["args"][0] if b["args"] else "text").strip()
    sec = {"win": [], "mac": [], "linux": []}; k = None
    for ln in b["lines"]:
        m = re.match(r"^@(win|mac|linux)\s*$", ln)
        if m: k = m.group(1); continue
        if k: sec[k].append(ln)
    out = []
    for k, lab in (("win","Windows"),("mac","macOS"),("linux","Linux")):
        out.append(code_table(lang, lab, "\n".join(sec[k])))
    return out
def r_quiz(b):
    q, opts, ok, why = "", [], -1, ""
    for ln in b["lines"]:
        if ln.startswith("Q "): q = ln[2:]
        elif ln.startswith("* "): ok = len(opts); opts.append(ln[2:])
        elif ln.startswith("- "): opts.append(ln[2:])
        elif ln.startswith("! "): why = ln[2:]
        elif ln.strip(): why += (" " if why else "") + ln.strip()
    inner = [Paragraph('<font color="#005eb8">QUICK CHECK</font>', st_lab),
             Paragraph(inline(q), st_qtext)]
    for ix, o in enumerate(opts):
        if ix == ok:
            inner.append(Paragraph('<b><font color="#1e7a44">%s</font></b>' % inline(o),
                                   st_opt_ok, bulletText="\u2713"))
        else:
            inner.append(Paragraph(inline(o), st_opt_no, bulletText="\u25cb"))
    inner.append(Spacer(1, 3))
    inner.append(Paragraph("<b>Why:</b> " + inline(why), st_why))
    return [boxed(inner, QBG, LINE)]
def r_ex(b):
    task, parts, cp = [], [], None
    for ln in b["lines"]:
        f = re.match(r"^~~~(\w*)\s*$", ln)
        if f: cp = {"lang": f.group(1) or "text", "lines": []}; parts.append(cp); continue
        (cp["lines"] if cp else task).append(ln)
    inner = [Paragraph('<font color="#0a5d65">EXERCISE</font>', st_lab)] + para_flows(task)
    out = [boxed(inner, colors.HexColor("#f2f8f8"), TEAL)]
    for pt in parts:
        out.append(code_table(pt["lang"],
            "Solution \u00b7 " + LANGNAME.get(pt["lang"], pt["lang"].upper()),
            "\n".join(pt["lines"])))
    return out
def r_key(b):
    inner = [Paragraph('<font color="#0a5d65">KEY POINTS</font>', st_lab)]
    for ln in b["lines"]:
        if ln.startswith("- "):
            inner.append(Paragraph(inline(ln[2:]), st_bullet, bulletText="\u2022"))
    return [boxed(inner, KEYBG, KEYLN)]
def r_note(b):
    typ = (b["args"][0] if b["args"] else "info").strip()
    bg, bc, deflab = NOTES.get(typ, NOTES["info"])
    lab = b["args"][1] if len(b["args"]) > 1 and b["args"][1] else deflab
    inner = [Paragraph('<font color="%s">%s</font>' % (bc.hexval().replace("0x","#"), xml(lab.upper())), st_lab)]
    inner += para_flows(b["lines"])
    return [boxed(inner, bg, bc)]
def r_table(b):
    rows = [ln.split("|") for ln in b["lines"] if ln.strip()]
    rows = [[c.replace("\u00a6", "|") for c in r] for r in rows]
    if not rows: return []
    ncol = max(len(r) for r in rows)
    rows = [r + [""]*(ncol-len(r)) for r in rows]
    weights = [max(len(rows[ri][ci]) for ri in range(len(rows))) for ci in range(ncol)]
    weights = [max(w, 8) for w in weights]
    tot = sum(weights)
    widths = [max(52, USABLE * w / tot) for w in weights]
    scale = USABLE / sum(widths)
    widths = [w*scale for w in widths]
    data = [[Paragraph(inline(c), st_cellh) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(inline(c), st_cell) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, style=TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#eaf1f0")),
        ("GRID",(0,0),(-1,-1),0.5,LINE),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("VALIGN",(0,0),(-1,-1),"TOP")]))
    t.spaceBefore, t.spaceAfter = 7, 9
    return [t]

RENDER = {"p": r_p, "h": r_h, "code": r_code, "oscode": r_oscode, "quiz": r_quiz,
          "ex": r_ex, "key": r_key, "note": r_note, "table": r_table}

# Image locations: lesson number -> (image filename, width_mm)
IMAGES = {
    2:  ("01_filesystem.png", 100),
    9:  ("09_database_schema.png", 110),
    12: ("12_sql_select.png", 110),
    25: ("25_joins.png", 120),
    46: ("46_r_structures.png", 110),
    56: ("56_ggplot_layers.png", 110),
    69: ("69_stats.png", 120),
    83: ("83_pipeline.png", 120),
    85: ("85_git_workflow.png", 120),
    101: ("capstone_a.png", 110),
    103: ("capstone_b.png", 110),
}

def image_path(name):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "images", name)

# ---------------- document template ----------------
class BookDoc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=ML, rightMargin=MR,
                         topMargin=MT, bottomMargin=MB, title="SQL & R for UK Public Health — from zero",
                         author="Code for Public Health UK", **kw)
        fr = Frame(ML, MB, USABLE, PAGE_H-MT-MB, id="f")
        self.addPageTemplates([
            PageTemplate(id="Front", frames=[fr], onPage=self.draw_front),
            PageTemplate(id="Body",  frames=[fr], onPage=self.draw_body)])
        self._section = ""
        self._bmk = 0
    def draw_front(self, canv, doc):
        canv.saveState()
        canv.setFont("DVS", 8); canv.setFillColor(SOFT)
        canv.drawCentredString(PAGE_W/2, 30, "\u2014 %d \u2014" % doc.page)
        canv.restoreState()
    def draw_body(self, canv, doc):
        canv.saveState()
        canv.setStrokeColor(LINE); canv.setLineWidth(0.7)
        canv.line(ML, PAGE_H-40, PAGE_W-MR, PAGE_H-40)
        canv.setFont("DVSO", 7.6); canv.setFillColor(SOFT)
        canv.drawString(ML, PAGE_H-36, "SQL & R for UK Public Health \u2014 from zero")
        canv.setFont("DVSB", 7.6)
        canv.drawRightString(PAGE_W-MR, PAGE_H-36, self._section[:70])
        canv.setFont("DVS", 8)
        canv.drawCentredString(PAGE_W/2, 30, "\u2014 %d \u2014" % doc.page)
        canv.restoreState()
    def afterFlowable(self, fl):
        if isinstance(fl, SectionMark):
            txt = fl.text
            self._section = txt
            key = "M" + txt.split("\u2014")[0].strip().split()[-1]
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(txt, key, level=0, closed=True)
            self.notify("TOCEntry", (0, txt, self.page, key))
            return
        if isinstance(fl, Paragraph):
            sn = fl.style.name
            if sn == "LessonTitle":
                txt = fl.getPlainText()
                key = "L" + txt.split(".", 1)[0].strip()
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(txt, key, level=1, closed=True)
                self.notify("TOCEntry", (1, txt, self.page, key))

# ---------------- build story ----------------
story = []
# ---- title page ----
story.append(Spacer(1, 120))
story.append(Paragraph('<font color="#0e7c86"><b>CODE FOR PUBLIC HEALTH UK</b></font>',
    S("tkick", fontName="DVSB", fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=14)))
story.append(Paragraph("SQL &amp; R for UK Public Health",
    S("t1", fontName="DVSB", fontSize=27, leading=33, alignment=TA_CENTER, spaceAfter=4)))
story.append(Paragraph("from zero to reproducible pipelines",
    S("t2", fontName="DVSO", fontSize=14, leading=19, alignment=TA_CENTER,
      textColor=SOFT, spaceAfter=26)))
story.append(Paragraph("%d lessons \u00b7 %d modules \u00b7 %d quick-check quizzes \u00b7 %d exercises with solutions"
    % (len(LESSONS), len(MODS),
       sum(1 for l in LESSONS for b in l["blocks"] if b["type"]=="quiz"),
       sum(1 for l in LESSONS for b in l["blocks"] if b["type"]=="ex")),
    S("t3", fontSize=10.5, alignment=TA_CENTER, textColor=SOFT, spaceAfter=60)))
about = ("This is the book edition of the interactive course. Quizzes here show the correct "
    "answer (marked \u2713) with its explanation, and every exercise is followed by its worked "
    "solution \u2014 attempt each one before reading on. Blocks labelled \u201cSQL \u00b7 try it in the "
    "playground\u201d refer to the live database built into the companion HTML edition; the queries "
    "are printed in full here so you can run them in any SQLite tool. "
    "All data mentioned in this course is fictional and computer-generated.")
story.append(boxed([Paragraph(about, S("ab", fontSize=9.4, leading=14, textColor=SOFT))],
    colors.HexColor("#f2f8f8"), KEYLN, pad=13))
story.append(Spacer(1, 170))
story.append(Paragraph("July 2026 \u00b7 companion to the interactive edition",
    S("t4", fontSize=8.6, alignment=TA_CENTER, textColor=SOFT)))
story.append(PageBreak())

# ---- table of contents ----
story.append(Paragraph("Contents", S("cth", fontName="DVSB", fontSize=17, leading=21, spaceAfter=12)))
toc = TableOfContents()
toc.levelStyles = [st_toc0, st_toc1]
toc.dotsMinLevel = 1
story.append(toc)
story.append(NextPageTemplate("Body"))
story.append(PageBreak())

# ---- modules & lessons ----
for M in MODS:
    story.append(SectionMark("Module %d \u2014 %s" % (M["n"], M["title"])))
    ban = Table([[ [Paragraph("MODULE %d" % M["n"], st_modkick),
                    Paragraph(xml("Module %d \u2014 %s" % (M["n"], M["title"])), st_modban)] ]],
        colWidths=[USABLE],
        style=TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
            ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),
            ("TOPPADDING",(0,0),(-1,-1),16),("BOTTOMPADDING",(0,0),(-1,-1),16)]))
    story.append(ban)
    story.append(Spacer(1, 12))
    story.append(Paragraph("In this module", st_h3))
    for l in M["lessons"]:
        story.append(Paragraph("<b>%d</b>&nbsp;&nbsp;%s" % (l["n"], xml(l["title"])),
            S("mlist", fontSize=9.2, leading=13, spaceAfter=1.5, leftIndent=6)))
    story.append(PageBreak())
    for l in M["lessons"]:
        head = [Paragraph("MODULE %d \u00b7 %s \u00b7 LESSON %d OF %d"
                    % (M["n"], xml(M["title"].upper()), l["n"], len(LESSONS)), st_eyebrow),
                Paragraph(xml("%d. %s" % (l["n"], l["title"])), st_lesson)]
        first = l["blocks"][0] if l["blocks"] else None
        firstf = RENDER.get(first["type"], lambda b: [])(first) if first else []
        lead = firstf[:1]
        rest_first = firstf[1:]
        story.append(KeepTogether(head + lead))
        story.extend(rest_first)
        for b in l["blocks"][1:]:
            story.extend(RENDER.get(b["type"], lambda b: [])(b))
        
        # Insert image if mapped to this lesson
        if l["n"] in IMAGES:
            imgfile, width = IMAGES[l["n"]]
            try:
                img = Image(image_path(imgfile), width=width*mm, height=None)
                img.spaceBefore, img.spaceAfter = 12, 8
                story.append(img)
            except Exception as e:
                pass  # silently skip if image not found
        
        story.append(Spacer(1, 4))
        rule = Table([[""]], colWidths=[USABLE], rowHeights=[1],
            style=TableStyle([("LINEBELOW",(0,0),(-1,-1),0.7,LINE)]))
        rule.spaceBefore, rule.spaceAfter = 6, 16
        story.append(rule)

doc = BookDoc(os.path.join(BASE, "course_book.pdf"))
doc.multiBuild(story)
print("PDF built.")
