# -*- coding: utf-8 -*-
import json, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak,
                                Image, Preformatted, KeepTogether, NextPageTemplate, CondPageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents
F='/usr/share/fonts/truetype/dejavu/'
for n,f in (('Sans','DejaVuSans.ttf'),('Sans-B','DejaVuSans-Bold.ttf'),('Sans-I','DejaVuSans-Oblique.ttf'),('Sans-BI','DejaVuSans-BoldOblique.ttf'),
            ('Serif','DejaVuSerif.ttf'),('Serif-B','DejaVuSerif-Bold.ttf'),('Mono','DejaVuSansMono.ttf'),('Mono-B','DejaVuSansMono-Bold.ttf'),
            ('Cond','DejaVuSansCondensed.ttf'),('Cond-B','DejaVuSansCondensed-Bold.ttf')):
    pdfmetrics.registerFont(TTFont(n,F+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Sans-B',italic='Sans-I',boldItalic='Sans-BI')
pdfmetrics.registerFontFamily('Mono',normal='Mono',bold='Mono-B',italic='Mono',boldItalic='Mono-B')
AZUL=colors.HexColor('#12355b'); LARA=colors.HexColor('#d9731a'); CINZA=colors.HexColor('#eef1f5'); CINZA2=colors.HexColor('#c9d1dc')
TXT=colors.HexColor('#1d2733'); VERDE=colors.HexColor('#2f7d4f'); VERM=colors.HexColor('#b3362d'); CODEBG=colors.HexColor('#f3f5f8')
VERSAO='2.0'; DATA='15 de novembro de 2026'
ROMVER='retrato do projeto em 15/11/2026 (stub v3.2s · monitor v3.5a)'
W,H=A4; LM=RM=20*mm; TM=24*mm; BM=20*mm
S={}
S['body']=ParagraphStyle('body',fontName='Sans',fontSize=9.4,leading=14,textColor=TXT,alignment=TA_JUSTIFY,spaceAfter=5)
S['bodyl']=ParagraphStyle('bodyl',parent=S['body'],alignment=TA_LEFT)
S['h1']=ParagraphStyle('h1',fontName='Serif-B',fontSize=23,leading=28,textColor=AZUL,spaceBefore=0,spaceAfter=10)
S['h2']=ParagraphStyle('h2',keepWithNext=1,fontName='Sans-B',fontSize=13.2,leading=17,textColor=AZUL,spaceBefore=13,spaceAfter=5)
S['h3']=ParagraphStyle('h3',keepWithNext=1,fontName='Sans-B',fontSize=10.4,leading=14,textColor=LARA,spaceBefore=8,spaceAfter=3)
S['cell']=ParagraphStyle('cell',fontName='Sans',fontSize=8.4,leading=11.2,textColor=TXT)
S['cellb']=ParagraphStyle('cellb',parent=S['cell'],fontName='Sans-B')
S['cellh']=ParagraphStyle('cellh',parent=S['cell'],fontName='Sans-B',textColor=colors.white)
S['cellm']=ParagraphStyle('cellm',parent=S['cell'],fontName='Mono',fontSize=7.9,leading=10.6)
S['cap']=ParagraphStyle('cap',fontName='Sans-I',fontSize=8.2,leading=11,textColor=colors.HexColor('#566475'),alignment=TA_CENTER,spaceBefore=3,spaceAfter=9)
S['bul']=ParagraphStyle('bul',parent=S['body'],leftIndent=12,bulletIndent=2,spaceAfter=2.5,alignment=TA_LEFT)
S['code']=ParagraphStyle('code',fontName='Mono',fontSize=7.3,leading=9.6,textColor=colors.HexColor('#142033'))
S['toc1']=ParagraphStyle('toc1',fontName='Sans-B',fontSize=10.2,leading=17,textColor=AZUL,leftIndent=0)
S['toc2']=ParagraphStyle('toc2',fontName='Sans',fontSize=8.8,leading=13,textColor=TXT,leftIndent=14)
def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def P(t,st='body'): return Paragraph(t,S[st])
class Heading(Paragraph): pass
story=[]
def h1(t):
    story.append(NextPageTemplate('corpo')); story.append(PageBreak()) if False else None
    story.append(CondPageBreak(60*mm)) if False else None
    story.append(PageBreak()); p=Heading(t,S['h1']); p._lvl=0; story.append(p)
    story.append(LineRule())
def h2(t): p=Heading(t,S['h2']); p._lvl=1; story.append(p)
def h3(t): story.append(Paragraph(t,S['h3']))
def para(t): story.append(P(t))
def bullets(items): 
    for it in items: story.append(Paragraph(it,S['bul'],bulletText='•'))
def sp(h=4): story.append(Spacer(1,h))
class LineRule(Flowable):
    def wrap(self,aw,ah): self.w=aw; return aw,5
    def draw(self):
        c=self.canv; c.setStrokeColor(LARA); c.setLineWidth(2.2); c.line(0,2,38*mm,2); c.setStrokeColor(CINZA2); c.setLineWidth(.8); c.line(38*mm,2,self.w,2)
def code(txt,title=None):
    txt=txt.rstrip('\n').expandtabs(4)
    pre=Preformatted(txt,S['code'])
    rows=[[pre]]
    if title: rows.insert(0,[Paragraph(title,ParagraphStyle('ct',fontName='Sans-B',fontSize=7.4,textColor=colors.white))])
    t=Table(rows,colWidths=[W-LM-RM])
    st=[('BACKGROUND',(0,-1),(-1,-1),CODEBG),('BOX',(0,0),(-1,-1),.6,CINZA2),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBEFORE',(0,0),(0,-1),2.4,AZUL)]
    if title: st+= [('BACKGROUND',(0,0),(-1,0),AZUL),('TOPPADDING',(0,0),(-1,0),3),('BOTTOMPADDING',(0,0),(-1,0),3)]
    t.setStyle(TableStyle(st)); t.hAlign='LEFT'
    if len(txt.split('\n'))<45: story.append(KeepTogether([t,Spacer(1,6)]))
    else: story.append(t); story.append(Spacer(1,6))
def callout(kind,txt):
    cor={'aviso':VERM,'dica':VERDE,'nota':AZUL,'cuidado':LARA}[kind]; rot={'aviso':'ATENÇÃO','dica':'DICA','nota':'NOTA','cuidado':'CUIDADO'}[kind]
    p=Paragraph('<font name="Sans-B" color="#%s">%s</font>&nbsp;&nbsp;%s'%(cor.hexval()[2:],rot,txt),ParagraphStyle('co',parent=S['bodyl'],fontSize=8.9,leading=13,spaceAfter=0))
    t=Table([[p]],colWidths=[W-LM-RM]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f7f8fa')),('LINEBEFORE',(0,0),(0,-1),3.4,cor),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(KeepTogether([t,Spacer(1,7)]))
def tabela(rows,widths,header=True,mono_cols=(),zebra=True,fs=None):
    data=[]
    for i,r in enumerate(rows):
        line=[]
        for j,c in enumerate(r):
            if isinstance(c,str):
                st='cellh' if (header and i==0) else ('cellm' if j in mono_cols else 'cell')
                line.append(Paragraph(c,S[st]))
            else: line.append(c)
        data.append(line)
    tw=W-LM-RM; cw=[tw*w/sum(widths) for w in widths]
    t=Table(data,colWidths=cw,repeatRows=1 if header else 0)
    st=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),3.2),('BOTTOMPADDING',(0,0),(-1,-1),3.6),('LINEBELOW',(0,0),(-1,-1),.4,CINZA2),('BOX',(0,0),(-1,-1),.6,CINZA2)]
    if header: st+=[('BACKGROUND',(0,0),(-1,0),AZUL)]
    if zebra:
        for i in range(1 if header else 0,len(rows)):
            if (i%2)==0: st.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#f5f7fa')))
    t.setStyle(TableStyle(st)); story.append(t); story.append(Spacer(1,8))
FIGN=[0]
def figura(path,larg,legenda):
    import re; FIGN[0]+=1; legenda=re.sub(r'^Figura \d+ — ','Figura %d — '%FIGN[0],legenda)
    from PIL import Image as PI
    w,h=PI.open(path).size; im=Image(path,width=larg,height=larg*h/w); im.hAlign='CENTER'
    story.append(KeepTogether([im,Paragraph(legenda,S['cap'])]))

# ---------------- documento ----------------
class Doc(BaseDocTemplate):
    def afterFlowable(self,fl):
        if isinstance(fl,Heading):
            txt=fl.getPlainText(); lvl=fl._lvl; import hashlib; key='k'+hashlib.md5(txt.encode()).hexdigest()[:10]
            self._n+=1; self.canv.bookmarkPage(key); self.canv.addOutlineEntry(txt,key,level=lvl,closed=(lvl>0))
            self.notify('TOCEntry',(lvl,txt,self.page,key))
            if lvl==0: self.capmap[self.page]=txt
def capa(c,doc):
    c.saveState(); c.setFillColor(AZUL); c.rect(0,0,W,H,fill=1,stroke=0)
    # padrao de trilhas
    c.setStrokeColor(colors.HexColor('#1d4a7c')); c.setLineWidth(1.2)
    import random; random.seed(7)
    for i in range(26):
        y=H*0.08+i*13*mm*0.55; x0=random.choice([0,20,40])*mm
        c.line(x0,y,x0+60*mm+random.random()*70*mm,y)
        c.line(x0+60*mm,y,x0+60*mm+10*mm,y+10*mm)
    c.setFillColor(LARA); c.rect(0,H*0.455,W,5*mm,fill=1,stroke=0)
    # glow + laser
    lw=84*mm; lh=lw*1600/618; lx=W-lw-10*mm; ly=28*mm
    for r,al in [(125-i*5,0.012) for i in range(18)]:
        c.setFillColor(colors.white); c.setFillAlpha(al); c.circle(lx+lw/2,ly+lh*0.45,r*mm,fill=1,stroke=0)
    c.setFillAlpha(1)
    c.drawImage('img/laser_recorte.png',lx,ly,width=lw,height=lh,mask='auto')
    c.setFillColor(colors.white); c.setFont('Serif-B',45); c.drawString(24*mm,H*0.29,'PARAGON 50')
    c.setFont('Sans',15); c.drawString(24*mm,H*0.29-13*mm,'Do laser sucateado ao computador 68000')
    c.setFont('Sans',11.5); c.setFillColor(colors.HexColor('#c8d8ea'))
    c.drawString(24*mm,H*0.29-23*mm,'A história de um projeto, do primeiro')
    c.drawString(24*mm,H*0.29-36*mm,'CP/M-68K e Forth'); c.drawString(24*mm,H*0.29-29.5*mm,'dump de ROM ao monitor v3.5a, com BASIC,')
    c.setFillColor(colors.white); c.setFont('Sans-B',10.5); c.drawString(24*mm,H*0.455-12*mm,'Edição %s  ·  %s'%(VERSAO,DATA))
    c.setFont('Sans',9.2); c.setFillColor(colors.HexColor('#c8d8ea')); c.drawString(24*mm,H*0.455-18*mm,'%s'%ROMVER)
    c.setFont('Serif-B',12); c.setFillColor(colors.white); c.drawString(24*mm,26*mm,'Tabajara Labs'); c.setFont('Sans',8.5); c.setFillColor(colors.HexColor('#c8d8ea'))
    c.drawString(24*mm,20.5*mm,'SBC Paragon 50 DIY'); c.restoreState()
def capatual(doc):
    if doc.page<3: return 'Sumário'
    ks=[k for k in sorted(doc.capmap) if k<=doc.page]
    return doc.capmap[ks[-1]] if ks else ''
def corpo(c,doc):
    c.saveState()
    c.setFillColor(AZUL); c.rect(0,H-13*mm,W,13*mm,fill=1,stroke=0); c.setFillColor(LARA); c.rect(0,H-14.4*mm,W,1.4*mm,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont('Serif-B',10.5); c.drawString(LM,H-8.4*mm,'PARAGON 50'); c.setFont('Sans',8.4); c.drawRightString(W-RM,H-8.2*mm,capatual(doc))
    c.setStrokeColor(CINZA2); c.setLineWidth(.6); c.line(LM,13*mm,W-RM,13*mm)
    c.setFillColor(colors.HexColor('#566475')); c.setFont('Sans',7.6); c.drawString(LM,8.6*mm,'Mini-livro · edição %s · Tabajara Labs'%VERSAO)
    c.setFont('Sans-B',8.6); c.setFillColor(AZUL); c.drawRightString(W-RM,8.4*mm,str(doc.page)); c.restoreState()
doc=Doc('LIVRO_PARAGON50_v2.pdf',pagesize=A4,leftMargin=LM,rightMargin=RM,topMargin=TM,bottomMargin=BM,
        title='PARAGON 50 — Do laser sucateado ao computador 68000',author='Tabajara Labs',subject='Computador 68000 baseado na placa do laser Paragon 50')
doc._n=0; doc.cap=''; doc.capmap={}
fr=Frame(LM,BM,W-LM-RM,H-TM-BM,id='f',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates([PageTemplate(id='capa',frames=[Frame(0,0,W,H,id='c')],onPage=capa),PageTemplate(id='corpo',frames=[fr],onPage=corpo)])
HLP=json.load(open('helps.json')); PINS=json.load(open('pins.json'))
exec(open('conteudo_livro_v2.py',encoding='utf-8').read())
doc.multiBuild(story)
print('ok')
