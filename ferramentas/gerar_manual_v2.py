#!/usr/bin/env python3
"""Gera Paragon50_Manual_v2.pdf: parte I (nova, atualizada) + esquema (4 folhas) + parte II (manual v1, secoes 6-9 e anexos, inalteradas).
Uso: python3 manual_v2.py <esquema_pdf> <manual_v1_pdf> <saida_pdf>"""
import sys, io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from pypdf import PdfReader, PdfWriter, Transformation

ESQ, V1, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', FD + 'DejaVuSans.ttf')); pdfmetrics.registerFont(TTFont('DV-B', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVM', FD + 'DejaVuSansMono.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DV', normal='DV', bold='DV-B', italic='DV', boldItalic='DV-B')

AZ = colors.HexColor('#1f4e79')
st = dict(
    body=ParagraphStyle('body', fontName='DV', fontSize=9, leading=12.6, spaceAfter=4),
    small=ParagraphStyle('small', fontName='DV', fontSize=7.6, leading=9.6),
    cell=ParagraphStyle('cell', fontName='DV', fontSize=7.8, leading=9.8),
    cellb=ParagraphStyle('cellb', fontName='DV-B', fontSize=7.8, leading=9.8, textColor=colors.white),
    h1=ParagraphStyle('h1', fontName='DV-B', fontSize=15, leading=19, spaceBefore=6, spaceAfter=8, textColor=AZ),
    h2=ParagraphStyle('h2', fontName='DV-B', fontSize=11, leading=14, spaceBefore=8, spaceAfter=4, textColor=AZ),
    h3=ParagraphStyle('h3', fontName='DV-B', fontSize=9.2, leading=12, spaceBefore=5, spaceAfter=2),
    mono=ParagraphStyle('mono', fontName='DVM', fontSize=6.3, leading=8.2),
    capa1=ParagraphStyle('capa1', fontName='DV-B', fontSize=26, leading=32, textColor=AZ, alignment=TA_LEFT),
    capa2=ParagraphStyle('capa2', fontName='DV', fontSize=13, leading=18, textColor=colors.HexColor('#333')),
    nota=ParagraphStyle('nota', fontName='DV', fontSize=8.2, leading=11, backColor=colors.HexColor('#fff8dc'), borderColor=colors.HexColor('#d9c26b'), borderWidth=0.6, borderPadding=4, spaceBefore=4, spaceAfter=8),
)
def P(t, s='body'): return Paragraph(t, st[s])
def H1(t): return P(t, 'h1')
def H2(t): return P(t, 'h2')
def H3(t): return P(t, 'h3')
def bullets(items): return [Paragraph('&bull;&nbsp;' + i, ParagraphStyle('b', parent=st['body'], leftIndent=10, firstLineIndent=-8, spaceAfter=2)) for i in items]
def tbl(rows, widths, head=True, zebra=True, fs=None):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), st['cellb'] if (head and i == 0) else st['cell']) for c in r])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    sty = [('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b0b0b0')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3),
           ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]
    if head: sty.append(('BACKGROUND', (0, 0), (-1, 0), AZ))
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if i % 2 == 0: sty.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f2f6fb')))
    t.setStyle(TableStyle(sty)); return t
def code(t): return Preformatted(t, st['mono'], dedent=0)

# ---------------------------------------------------------------- documento
def pagina(c, d):
    pass
doc = BaseDocTemplate('/tmp/_m.pdf', pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
                      title='PARAGON 50 - Manual da placa CPU 68000 (v2)', author='Tabajara Labs / Claude')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')], onPage=pagina)])
S = []

# ---- capa
S += [Spacer(1, 40 * mm), P('PARAGON 50', 'capa1'), P('Manual da placa CPU 68000', 'capa1'), Spacer(1, 6 * mm),
      P('Uso standalone como computador 68K: hardware, esquema, mapas de memória e de E/S, conectores, software (ROM v2.1), integração com a RepRapDiscount Smart Controller, interposer e gabinete 3D', 'capa2'),
      Spacer(1, 14 * mm), P('<b>Versão 2</b> &mdash; 12 de novembro de 2026', 'capa2'), P('Tabajara Labs &mdash; tabalabs.com.br', 'capa2'), Spacer(1, 10 * mm),
      P('Placa CPU do laser cirúrgico PARAGON 50 (Heraeus Surgical / LaserSonics), FAB NO. 8094-8001-01 REV E, reaproveitada como computador 68000 independente do laser.', 'body'),
      Spacer(1, 30 * mm),
      P('<b>Legenda de confiança:</b> [C] confirmado no código &middot; [M] medido na placa (multímetro / osciloscópio / programa de teste) &middot; [I] inferido &middot; [?] ainda a confirmar na placa.', 'nota'),
      P('<b>Como este manual está organizado.</b> A <b>Parte I</b> (seções 1 a 12) é nova e reflete o estado atual da placa, incluindo tudo o que foi medido e modificado desde a versão 1. As quatro folhas do <b>esquema</b> estão na seção 4. A <b>Parte II</b> reproduz, sem alterações, as seções 6 a 9 e os anexos do manual v1 (engenharia reversa do firmware original do laser), que continuam válidos como documentação do firmware de fábrica.', 'body'), PageBreak()]

# ---- histórico + sumário
S += [H1('Histórico de versões'),
      tbl([['Versão', 'Data', 'Conteúdo'],
           ['v1', '07/11/2026', 'Manual de engenharia reversa (27 páginas): análise das ROMs HI/LO, mapa de memória e de E/S deduzidos do firmware, arquitetura do firmware do laser, guia de diagnóstico, anexos de código.'],
           ['v2', '12/11/2026', 'Esta versão. Atualiza o hardware (RAM de 128 KB, ROM 27C512, clock, serial), traz o mapa de endereços medido, a pinagem de J1/J2/J4, o esquema funcional em 4 folhas, a ROM v2.1 com monitor, EhBASIC, CP/M-68K e periféricos, a integração com a RepRapDiscount, o projeto do interposer e o estado do gabinete 3D. As seções 6 a 9 e os anexos do v1 foram mantidos na Parte II.']],
          [18, 24, 130]), Spacer(1, 6 * mm),
      H1('Sumário'),
      tbl([['Seção', 'Título'],
           ['1', 'Visão geral e estado atual do projeto'], ['2', 'O que mudou em relação ao manual v1 (errata)'], ['3', 'Hardware atual da placa'], ['4', 'Esquema funcional (folhas 1 a 4)'],
           ['5', 'Mapa de memória e de E/S'], ['6', 'Conectores e pinagens (J1, J2, J4, TB1)'], ['7', 'Software: ROM v2.1, monitor, EhBASIC, CP/M-68K, periféricos, ferramentas'],
           ['8', 'Integração com a RepRapDiscount Smart Controller'], ['9', 'Expansão: RAM e interposer com CPLD'], ['10', 'Gabinete impresso em 3D'],
           ['11', 'Procedimentos de teste e diagnóstico atualizados'], ['12', 'Pendências e próximos passos'], ['13', 'Arquivos do projeto'],
           ['Parte II', 'Manual v1: arquitetura do firmware do laser, descritivo funcional, diagnóstico, anexos A-C, resumo final']], [22, 150]), PageBreak()]

# ---- 1
S += [H1('1. Visão geral e estado atual do projeto'),
      P('A placa é a CPU do laser de CO<sub>2</sub> cirúrgico PARAGON 50 (Heraeus Surgical). O laser foi declarado obsoleto e sucateado; a placa não volta mais a ele (os dumps das ROMs e das NVRAMs originais estão guardados). Ela foi reaproveitada como <b>computador 68000 standalone</b>: monitor com assembler/disassembler/depurador, EhBASIC, CP/M-68K e Tetris numa ROM única de 128 KB, RAM de 128 KB, serial a 57600 bps e, em andamento, cartão SD, LCD 20x4 e buzzer pela placa RepRapDiscount Smart Controller ligada a J1/J2.'),
      P('Resumo técnico: MC68000P10 (10 MHz nominal, módulo oscilador de 8 MHz); 2 EPROMs 27C512 (128 KB, $F80000-$F9FFFF); 2 SRAMs KM681000BLP-5 em adaptadores 28&rarr;32 (128 KB, $000000-$01FFFF); DUART MC68681P com cristal próprio de 3,6864 MHz; Intel 8254 e DAC8212 do laser (não usados no uso standalone); 16 saídas e 16 entradas digitais TTL em J1/J2; decodificação por lógica discreta (sem PAL/GAL).'),
      H2('Estado do projeto'),
      tbl([['Item', 'Estado', 'Observação'],
           ['Dump das ROMs e NVRAMs originais', 'Feito', 'rom_original/ (HI e LO, 32 KB cada). Bateria das DS1230Y (código 9528) esgotada de longa data.'],
           ['Engenharia reversa e disassembly do firmware do laser', 'Feito', 'Paragon50_firmware.asm (~16,7 mil linhas) e manual v1 (Parte II).'],
           ['Monitor v2 / v2.1 (assembler, disassembler, depurador)', 'Feito', 'Módulo estendido em C (ext.c, asm.c, dis.c) + monitor.asm; ROM v2.1 de 128 KB gravada em 27C512.'],
           ['EhBASIC, CP/M-68K, Tetris na ROM', 'Feito', 'CP/M com discos A: e B: (512 KB) servidos pela ponte no PC. Menu BASIC/MONITOR no boot.'],
           ['RAM de 128 KB (2 x KM681000)', 'Feito, funcionando', 'Troca das DS1230Y por adaptadores 28&rarr;32; nenhuma lógica nova. Plano de 256 KB abandonado ($20000-$3FFFF é E/S).'],
           ['Mapa de endereços', 'Medido', 'Varredura de 256 blocos de 64 KB em 10/11/2026 (seção 5).'],
           ['Saídas de J1/J2 ($020018)', 'Medido', '16 bits localizados com osciloscópio (seção 6).'],
           ['Saídas $020020 e E/S de 8 bits ($040xxx)', 'Parcial', 'Só $020020 bit 7 &rarr; J1-48 localizado; o resto do roteamento falta medir.'],
           ['Entradas de J1', 'Parcial', 'B0-B6 e A3 localizados em 12/11/2026; B7 provável em J1-36 [?]; J2 sem entradas conhecidas.'],
           ['Serial J4', 'Fechado', 'Pinagem completa (seção 6.3); 57600 bps adotado.'],
           ['SD + LCD + buzzer (RepRapDiscount)', 'Programa pronto; teste na placa pendente', 'Comando @ da ROM (G F8F000). Falta montar a placa de ligação J1/J2 &harr; EXP1/EXP2.'],
           ['Interposer CPLD EPM7128S', 'Projeto pronto, não construído', 'Verilog e modelo Python em cpld/; RAM 1 MB, TMS9118, LCD/SD, teclado PS/2 (seção 9).'],
           ['Gabinete 3D em cunha', 'Em andamento', 'Placa de teste v5 pronta para imprimir; gabinete v3 (laterais com cintura, cantos arredondados) a fazer (seção 10).'],
           ['Publicação no GitHub', 'Pendente', 'O usuário autorizou publicar tudo, inclusive dumps/disassembly; falta conectar o GitHub e escolher nome/licença.']],
          [52, 30, 90]), PageBreak()]

# ---- 2
S += [H1('2. O que mudou em relação ao manual v1 (errata)'),
      P('O manual v1 foi escrito só com fotos e as ROMs. Depois de medir a placa, várias afirmações mudaram. Esta tabela substitui as seções 1 a 5 do v1 onde houver conflito; as seções 6 a 9 do v1 (firmware do laser) continuam corretas.'),
      tbl([['Assunto', 'Manual v1', 'Situação atual'],
           ['RAM', '2 x DS1230Y-200 (NVRAM 32K x 8), 64 KB retentivos em $000000-$00FFFF', '2 x KM681000BLP-5 (128K x 8, usadas pela metade) em adaptadores 28&rarr;32, 128 KB <b>voláteis</b> em $000000-$01FFFF. Sem bateria.'],
           ['ROM', '2 x 27C256, 64 KB, $F80000-$F8FFFF', '2 x 27C512, 128 KB, $F80000-$F9FFFF. Os pinos 27, 26 e 1 das EPROMs (A14, A13, A15 da 27C512) vêm de A15, A14 e A16 do 68000 pelo 74LS14 U26 [M].'],
           ['Clock', 'Oscilador XO-43B 8,000 MHz (inferido da foto)', 'Módulo oscilador de 8 MHz confirmado; a CPU é P10 (10 MHz). Overclock a 12 MHz considerado.'],
           ['Serial', '9600 bps nos dois canais (firmware do laser)', 'Monitor, BASIC e CP/M em <b>57600 bps</b>, 8N1. 38400 funciona, 115200 não (cristal de 3,6864 MHz do 68681). Drivers 1488/1489 mantidos.'],
           ['Decodificação', 'RAM A23..A16 = 0, I/O por A17/A18 [I]', 'Só A17 e A18 na parte baixa; A16 e A19-A23 ignorados, tudo se repete a cada $80000 até $F7FFFF [M]. Sem PAL/GAL.'],
           ['Bloco $060000-$07FFFF', 'não citado', 'Sem /DTACK: a CPU trava e o watchdog reinicia [M]. Nunca escrever/ler ali sem hardware próprio.'],
           ['/BERR', 'não citado', '/BERR em Vcc: não há timeout de barramento; endereço sem /DTACK = travamento.'],
           ['Watchdog JP6', 'jumper permite inibir', 'JP6 <b>não instalado</b>: o watchdog está ativo; programas longos devem chamar STROBE ($F8082A).'],
           ['J4', '"fita para painel/serial"', 'IDC de 20 pinos só com a serial dos canais A e B (seção 6.3). A DB9 J111 fica na outra placa (Display Interface PCB), não montada.'],
           ['J1/J2', 'sinais do laser (interlocks, chaves, sensores) [V]', 'Mapa medido: 16 saídas TTL sem drivers e entradas via 74LS240 (seção 6). Os drivers de potência (ULN) ficavam na outra placa.'],
           ['Entradas $020028/$020030', 'XOR $FF34 e $1BD3 no firmware do laser', 'Hardware: 74LS240 inversores com pull-up de 4,7 k; aterrar o pino faz o bit subir. SW2 (DIP de 8) ocupa os bits 8-15 da porta B.'],
           ['Mapa de memória livre', 'RAM em $0-$FFFF', 'RAM em $0-$1FFFF; $2000-RAMEND é a RAM de usuário (vetores e pilha do monitor abaixo).']],
          [28, 62, 82]), PageBreak()]

# ---- 3
S += [H1('3. Hardware atual da placa'),
      H2('3.1 CPU e clock'),
      P('MC68000P10 em DIP-64 (no soquete), 10 MHz nominal, alimentada por módulo oscilador de 8 MHz. Pinos úteis: A16=44, A17=45, A18=46, A19=47, A20=48, A21=50, A22=51, A23=52; /AS=6, /UDS=7, /LDS=8, R/W=9, /DTACK=10, CLK=15, /RESET=18; Vcc=14 e 49, GND=16 e 53. O DIP-64 permite o <b>interposer</b> com CPLD no soquete (seção 9). Os 8 MHz geram 1 ciclo de barramento de 4 clocks sem wait states nas EPROMs de 150 ns e na SRAM de 55 ns.'),
      H2('3.2 Memória'),
      P('<b>ROM:</b> duas EPROMs 27C512 (128 KB) com etiqueta de fábrica "HI ROM U8" e a gêmea LO em U7. HI fornece os bytes pares (D8-D15) e LO os ímpares (D0-D7). As EPROMs originais eram -15 (150 ns); podem ser trocadas por flash de 100/120 ns. Os pinos A14, A13 e A15 da 27C512 passam por inversores do 74LS14 U26 vindos de A15, A14 e A16 do 68000, o que explica a ordem embaralhada dos dumps originais (endereço_ROM = $F80000 + (offset XOR $C000)). A imagem lógica de 128 KB é gerada por mkrom21.py.'),
      P('<b>RAM:</b> duas KM681000BLP-5 (55 ns, DIP-32) em adaptadores 28&rarr;32 nos soquetes originais das DS1230Y (U13 = D0-D7, U14 = D8-D15). O /CE vem do U4 Y4 (pino 11) como antes; A16 da CPU (pino 44) vai ao pino 31 (A15) das duas KM; o pino 2 (A16 da KM) vai a GND; CS2 (pino 30) em Vcc; /WE vem de U28 (pino 3 byte baixo, pino 11 byte alto); 100 nF em cada KM. Detalhes na folha 2 do esquema. O teste do monitor: <font face="DVM">P 3010 77</font>, <font face="DVM">D 13010</font> deve ler 00 (sem espelho) e <font face="DVM">Z</font> deve passar de $2000 a $1FFFE.'),
      H2('3.3 Serial (MC68681P)'),
      P('DUART MC68681P em $FA0000 (registradores nos endereços ímpares, D0-D7), cristal próprio de 3,6864 MHz, canais A e B com drivers DS1488 (TX) e MC1489 (RX) alimentados com +/-12 V, saindo em J4. OP2 faz o strobe do watchdog (DS1232), IP3 é entrada de segurança do firmware do laser, IRQ com vetor $1F. A velocidade é padronizada em 57600 bps para monitor, BASIC, CP/M e ponte do PC (porta COM9).'),
      H2('3.4 Decodificação, DTACK, reset'),
      P('Decodificação com dois 74LS138 (U4 para os blocos de 128 KB, U6 para o sub-bloco de E/S), portas 74LS11/74LS14/74LS74 e U19 (A19-A23); não há PAL/GAL. Cada janela de E/S gera o próprio /DTACK; $060000-$07FFFF não gera. O DS1232 faz o reset (~150 ms) e o watchdog; JP6 (inibe) não está instalado. Reset manual em SW1.'),
      H2('3.5 Entradas e saídas'),
      P('Saídas: 2 x 74LS273 em $020018 (16 bits, push-pull, J1/J2) e 2 x 74LS273 em $020020 (bits 0-7 por 74LS06 U41/U47 em coletor aberto <b>invertido</b>; bits 8-15 diretos, parte indo ao AD7501 U38). Entradas: 4 x 74LS240 (U42+U48 = porta B em $020028, U44+U37 = porta A em $020030) com pull-up de 4,7 k, <b>invertidas</b>; o DIP SW2 está nos bits 8-15 da porta B (U48). Além disso há E/S de 8 bits em $040180, $04018A (saídas) e $040194, $04019C (entradas). Todos os níveis são TTL/CMOS 0-4,3 V sem proteção: use buffers/resistores se ligar algo externo.'),
      H2('3.6 Alimentação'),
      P('TB1: GND, +12 V, -12 V. O +5 V dos CIs vem de outra entrada [?]. J1 não tem Vcc utilizável; o painel RepRapDiscount deve ser alimentado por fonte externa de 5 V com GND comum (J1-1/2/9/50 são GND).'),
      H2('3.7 Circuitos integrados identificados'),
      tbl([['Ref.', 'CI', 'Função'],
           ['U4', '74LS138', 'blocos de 128 KB: Y4 RAM (pino 11), Y5 E/S 16 bits (pino 10), Y7 sem DTACK (pino 7) [M/I]'],
           ['U6', '74LS138', 'sub-decodificação de $0200xx; Y3 (pino 12) = clock de $020020 [M]'],
           ['U7 / U8', '27C512', 'ROM LO (ímpares) / HI (pares)'],
           ['U13 / U14', 'KM681000BLP-5 em adaptador', 'RAM D0-D7 / D8-D15 (antes DS1230Y)'],
           ['U10', '74LS14', 'clock dos latches $020020; inversores livres [M]'],
           ['U26', '74LS14', 'inversores de A15, A14, A16 para a ROM'],
           ['U28', '(porta)', '/WE da RAM (byte baixo no pino 3, alto no pino 11)'],
           ['U19', '(porta, a identificar)', 'entradas pinos 2-6 = A19-A23 [M]'],
           ['U34 / U35', '74LS74 / 74LS11', 'lógica de DTACK/overlay [?], com portas livres'],
           ['U36 / U43', 'MC1489 / DS1488', 'RX / TX RS-232 dos canais A e B (J4)'],
           ['U37, U42, U44, U48', '74LS240', 'entradas: porta A (U44, U37) e porta B (U42, U48 com SW2)'],
           ['U39, U45', '74LS273', 'saídas $020018 (J1/J2)'],
           ['U40, U46', '74LS273', 'saídas $020020 (U40 bits 8-15, U46 bits 0-7)'],
           ['U41, U47', '74LS06', 'inversores de coletor aberto de U46 (e alguns de U40)'],
           ['U38', 'AD7501', 'chave analógica comandada por $020020 bits 12-15'],
           ['-', 'MC68681P, Intel 8254, DAC8212 + AD584, CD4051 + OP07, DS1232', 'DUART, temporizador, DAC, medida analógica, reset/watchdog (referências na placa a anotar)']],
          [24, 46, 102]), PageBreak()]

# ---- 4: intro + 4 folhas (placeholders substituídos depois)
S += [H1('4. Esquema funcional (folhas 1 a 4)'),
      P('Não existe esquemático original da placa. As quatro folhas a seguir (A3 reduzidas para A4, em vetor) foram reconstruídas das fotos, do firmware e das medições. O conteúdo marcado com [?] ainda precisa ser confirmado com o multímetro.'),
      tbl([['Folha', 'Conteúdo'],
           ['1', 'Diagrama funcional do sistema: CPU, barramento, ROM, RAM, DUART, 8254, DAC, decodificador, latches, entradas, conectores, clock/reset e periféricos externos.'],
           ['2', 'Decodificação de endereços (U4/U6), mapa de blocos, ligação dos endereços da ROM, adaptador da RAM 28&rarr;32, /DTACK e reset.'],
           ['3', 'Portas de E/S: tabela dos 16 bits de $020018 (pino e frequência medida), de $020020, das entradas, caminho de dados e serviços da ROM ($F80800...).'],
           ['4', 'Conectores J1 e J2 (todos os 100 pinos desenhados), J4 (serial) e ligação da RepRapDiscount Smart Controller (EXP1/EXP2).']], [18, 154]),
      P('ESQUEMA_FOLHA_1'), PageBreak(), P('ESQUEMA_FOLHA_2'), PageBreak(), P('ESQUEMA_FOLHA_3'), PageBreak(), P('ESQUEMA_FOLHA_4'), PageBreak()]

# ---- 5
S += [H1('5. Mapa de memória e de E/S'),
      H2('5.1 Mapa de endereços (medido em 10/11/2026)'),
      P('Varredura por leitura de 256 blocos de 64 KB. O decodificador só usa A17 e A18 na parte baixa; A16 e A19-A23 são ignorados, então tudo se repete de $080000 em $080000 até $F7FFFF. Como não há /BERR, um endereço sem /DTACK trava a CPU até o watchdog reiniciar.'),
      tbl([['Faixa', 'Uso', 'Observação'],
           ['$000000-$01FFFF', 'RAM 128 KB (KM681000 x 2)', 'vetores, pilha e dados do monitor em baixo; RAM de usuário de $2000 a RAMEND ($1FFFF)'],
           ['$020000-$03FFFF', 'E/S de 16 bits (laser)', 'entradas, DACs, 8254, latches; espelhado a cada 64 KB'],
           ['$040000-$05FFFF', 'E/S de 8 bits', 'lê $FF se nada ligado ($040180, $04018A, $040194, $04019C)'],
           ['$060000-$07FFFF', '<b>SEM /DTACK</b>', 'a CPU trava e o watchdog reinicia. Livre para expansão: o dispositivo novo precisa gerar /DTACK'],
           ['$080000-$F7FFFF', 'repete a parte baixa', 'a cada $80000 (A19-A23 ignorados)'],
           ['$F80000-$F9FFFF', 'ROM 128 KB (27C512 x 2)', 'com a 27C256 antiga (64 KB) a imagem se espelhava em $F90000; agora ocupa os 128 KB'],
           ['$FA0000-$FBFFFF', 'MC68681 DUART', 'espelhado em $FB0000; ler $FA0000 com D consome caracteres do receptor'],
           ['$FC0000-$FDFFFF', 'vazio', 'responde com DTACK sem dispositivo (devolve lixo do último ciclo, ex.: $6100)'],
           ['$FE0000-$FFFFFF', 'lê $FF', '']],
          [32, 42, 98]),
      H2('5.2 Mapa de E/S'),
      tbl([['Endereço', 'Nome', 'Acesso', 'Descrição'],
           ['$020000', 'IN_WORD_0', 'L', 'leitura de 16 bits usada em rotinas de teste do laser'],
           ['$02000A / $02000C', 'DAC_A / DAC_B', 'E', 'DAC8212 12 bits: A = pedido x 4095 / 5000, B = pedido x 4095 / 125000'],
           ['$020010-$020016', '8254', 'L/E', 'controle em $020010, contadores 2, 1, 0 em $020012/14/16 (A1/A0 invertidos)'],
           ['$020018', 'saídas A', 'E (16 b)', '<b>só escrita</b>: bits 0-7 em J1, bits 8-15 em J2 (seção 6); manter cópia-sombra em RAM (o monitor usa LSH = $2F40)'],
           ['$020020', 'saídas B', 'E (16 b)', 'bits 0-7 invertidos/coletor aberto (74LS06); bit 7 em J1-48; bits 12-15 vão ao AD7501'],
           ['$020028', 'entradas B', 'L (16 b)', 'U42 + U48 (SW2 nos bits 8-15); aterrar o pino = bit 1; B0=J1-7, B1=J1-35, B2=J1-33, B3=J1-31, B4=J1-27, B5=J1-25, B6=J1-23'],
           ['$020030', 'entradas A', 'L (16 b)', 'U44 + U37; A3=J1-4; demais bits a localizar'],
           ['$040180 / $04018A', 'saídas 8 b', 'E', 'latches de 8 bits (laser) [?]'],
           ['$040194 / $04019C', 'entradas 8 b', 'L', 'entradas de 8 bits (laser) [?]'],
           ['$FA0000-$FA001F', 'MC68681', 'L/E', 'registro n em $FA0000 + 2n + 1 (ver Parte II, tabela do v1)']], [30, 24, 20, 98]),
      P('Observação: o firmware do laser fazia XOR $FF34 em $020028 e XOR $1BD3 em $020030 porque cada bit era ativo em nível baixo/alto conforme o sensor; no uso standalone basta lembrar que o 74LS240 <b>inverte</b> e que o pull-up de 4,7 k mantém o bit em 0 com o pino aberto.', 'nota'),
      H2('5.3 Serviços da ROM (tabela de saltos a partir de $F80800)'),
      tbl([['Endereço', 'Nome', 'Função'],
           ['$F80800', 'PUTC', 'envia o caractere de D0 à serial'], ['$F80806', 'GETC', 'espera uma tecla e devolve em D0'], ['$F8080C', 'PUTS', 'imprime texto terminado em 0 apontado por A1'],
           ['$F80812', 'HEXB', 'imprime D0.B em hexa'], ['$F80818', 'HEXW', 'imprime D0.W em hexa'], ['$F8081E', 'HEXL', 'imprime D0.L em hexa'], ['$F80824', 'CRLF', 'nova linha'],
           ['$F8082A', 'STROBE', 'pulsa o watchdog (OP2 do 68681)'], ['$F80830', 'GETHEX', 'lê número hexa da linha (A1) para D0'], ['$F80836', 'GETLINE', 'lê uma linha para o buffer em $0500']], [28, 28, 116]),
      H2('5.4 Variáveis do monitor v2.1'),
      tbl([['Endereço', 'Conteúdo'],
           ['$00040C (long)', 'RAMEND: último byte da RAM detectada ($0000FFFF com 64 KB, $0001FFFF com 128 KB)'],
           ['$000430', 'marca "RAM1" ($52414D31) = RAMEND válido; área $000410-$00042F usada na sondagem'],
           ['$000500', 'buffer de linha (GETLINE)'],
           ['$002F40 / $002F42 ...', 'copia-sombra do latch, calibração do buzzer, estado do SD (perif.asm)']], [40, 132]), PageBreak()]

# ---- 6
S += [H1('6. Conectores e pinagens'),
      H2('6.1 J1 (IDC 50 pinos)'),
      P('Pinos ímpares na coluna da esquerda, pares na da direita (pino 1 e 2 na mesma linha). Todas as saídas são TTL push-pull de 0 a ~4,3 V (frequências do teste com contador no DSO-X 2002A: bit 0 = 108 kHz, cada bit seguinte na metade).'),
      tbl([['Pino', 'Sinal', 'Pino', 'Sinal'],
           ['J1-28', 'saída $020018 bit 0 (SCK)', 'J1-7', 'entrada B0 ($020028)'],
           ['J1-26', 'saída $020018 bit 1 (MOSI)', 'J1-35', 'entrada B1'],
           ['J1-24', 'saída $020018 bit 2 (CS do SD)', 'J1-33', 'entrada B2'],
           ['J1-20', 'saída $020018 bit 3 (LCD_E)', 'J1-31', 'entrada B3'],
           ['J1-18', 'saída $020018 bit 4 (LCD_RS)', 'J1-27', 'entrada B4'],
           ['J1-15', 'saída $020018 bit 5 (LCD_D4)', 'J1-25', 'entrada B5'],
           ['J1-14', 'saída $020018 bit 6 (LCD_D5)', 'J1-23', 'entrada B6'],
           ['J1-10', 'saída $020018 bit 7 (LCD_D6)', 'J1-36 [?]', 'entrada B7 (número ilegível na folha; provável 36)'],
           ['J1-48', 'saída $020020 bit 7 (coletor aberto, invertida, U47 pino 8; precisa de pull-up)', 'J1-4', 'entrada A3 ($020030)'],
           ['J1-1, 2, 9, 50', 'GND', 'J1-13, J1-17', 'apenas ruído acoplado de J1-15; sem sinal'],
           ['J1-29', 'sem resposta (riscado na folha)', 'outros', 'sem sinal nos testes; muitos estão em Vcc (não identificados)']], [26, 62, 26, 58]),
      H2('6.2 J2 (IDC 50 pinos)'),
      tbl([['Pino', 'Bit de $020018', 'Frequência', 'Pino', 'Bit de $020018', 'Frequência'],
           ['J2-47', 'bit 8 (LCD_D7)', '422 Hz', 'J2-28', 'bit 12', '26 Hz'], ['J2-40', 'bit 9 (BUZZER)', '211 Hz', 'J2-27', 'bit 13', '13 Hz'],
           ['J2-37', 'bit 10', '105 Hz', 'J2-24', 'bit 14', '6 Hz'], ['J2-30', 'bit 11', '52 Hz', 'J2-23', 'bit 15', '~3 Hz']], [20, 32, 28, 20, 32, 28]),
      P('Nos demais pinos de J2 nada respondeu nos testes (muitos estão em Vcc). Ainda não foram localizadas as entradas dos demais bits das portas A e B, nem as saídas $020020 bits 0-6 e 8-11 e as portas de 8 bits. Programas como entradas_bip e o comando J do monitor servem para isso (aterrar o pino com 330 &Omega; e ver o bit mudar).'),
      H2('6.3 J4 (IDC 20 pinos): serial'),
      P('Fechado em 11/11/2026. O conector é grande só para não ser confundido com os demais da placa display. A coluna "DE-9" mostra a ligação a um DB9 fêmea no papel de DCE, para usar cabo direto ao PC.'),
      tbl([['J4', 'Sinal', 'CI / pino', 'DE-9 fêmea'],
           ['1, 2, 12, 13', 'GND', '-', '5'], ['3', 'RX canal A', 'U36 pino 1', '3 (A)'], ['4', 'RX canal B', 'U36 pino 13', '3 (B)'],
           ['5', 'TX canal A', 'U43 pino 11', '2 (A)'], ['6', 'TX canal B', 'U43 pino 6', '2 (B)'], ['7', 'CTS canal A', 'U36 pino 4', '7 (A)'], ['8', 'CTS canal B', '(U36 pino 10)', '7 (B)'],
           ['9', 'RTS canal B', 'U43 pino 3', '8 (B)'], ['11', 'RTS canal A', 'U43 pino 8', '8 (A)'], ['15', 'interligado ao pino 11', '-', '-'], ['10, 14, 16-20', 'sem conexão (medido na placa toda)', '-', '-']], [26, 52, 44, 30]),
      P('Terminal: 57600 bps, 8N1, sem controle de fluxo. O canal usado pelo monitor é o que responde na COM9 do PC (teste de 10/11: o texto indica qual canal está naquele fio).', 'small'),
      H2('6.4 TB1, SW1, SW2, JP6'),
      tbl([['Item', 'Função'], ['TB1', 'GND, +12 V, -12 V (drivers RS-232 e op-amps)'], ['SW1', 'botão RESET'], ['SW2', 'DIP de 8 chaves, lido nos bits 8-15 da porta B ($020028, U48)'],
           ['JP6', 'WATCHDOG INHIBIT: não instalado (watchdog ativo)'], ['A/D GROUND JUMPER', 'aterramento do conversor analógico (laser), sem uso no standalone'], ['TP1-TP5', 'pontos de teste']], [40, 132]), PageBreak()]

# ---- 7
S += [H1('7. Software'),
      H2('7.1 ROM v2.1 (27C512)'),
      P('Gravar PARAGON512_HI.bin na U8 e PARAGON512_LO.bin na U7. PARAGON512_F80000.bin é a imagem lógica de 128 KB ($F80000-$F9FFFF) para conferência. CRC-32 dos arquivos (com o programa de periféricos): HI A4128F08, LO 422CD135. A ROM contém o monitor v2.1, o EhBASIC, o CP/M-68K, o Tetris e o programa de periféricos em $F8F000. A primeira v2.1 sondava $2FFE0 e $3FFE0 (E/S) e <b>não deve ser usada</b> (CRC HI 143810AA).'),
      tbl([['Novidade da v2.1', 'Descrição'],
           ['Tela limpa no reset', 'envia ESC [ 2 J e ESC [ H antes do menu'],
           ['Detecção da RAM', 'blocos de 64 KB só em $0-$1FFFF, assinatura em $xFFE0, restaura o conteúdo; RAMEND em $40C, marca "RAM1" em $430; comando I mostra'],
           ['Comando Q', 'mapa de memória por leitura (não grava; não lê o bloco sem DTACK nem o DUART)'],
           ['Comando J', 'monitor das entradas: imprime cada bit que muda em $020030/$020028'],
           ['Comando @ (ou G F8F000)', 'SD (SPI) + buzzer passivo + LCD 20x4 da RepRapDiscount'],
           ['X (depurador)', 'trata erro de endereço (vetor 3) e de barramento (vetor 2) sem travar; PC salvo pode estar até 10 bytes além'],
           ['Teste de RAM Z', 'passada final grava endereço XOR bits altos: detecta espelhamento de 64 KB'],
           ['CP/M-68K e EhBASIC', 'usam a RAM detectada: TPA $2F00 até RAMEND (116 KB com 128 KB); BASIC com 122366 bytes livres (emulador)']], [44, 128]),
      H2('7.2 Comandos do monitor (números em hexadecimal)'),
      code("""MEMORIA     D [ini [fim]] dump       P [ini [byte...]] grava   E [end] edita      F [ini [fim [byte]]] preenche
            M [ini [fim [dest]]] copia   V compara   S [ini [fim [byte...]]] procura   Z teste de RAM
            Y checksum/CRC-16/CRC-32     = [expr] calculadora
PROGRAMAS   L carrega S-record (S19/S28/S37)   W [ini [fim]] despeja S-records   G [end] executa (JSR)
DESASSEMB.  U [ini [fim]] desassembla   A [end | -] assembla linha a linha (rotulos, sintaxe Motorola)
DEPURACAO   R [reg [valor]]   N [qtd] passo   O [qtd] passo sem entrar em JSR/BSR
            K [end | -end | -] breakpoints (ate 8, RAM $2000-RAMEND)   X [end] executa sob o depurador
SISTEMA     B EhBASIC   C CP/M-68K   T Tetris   I informacoes   Q mapa de memoria   J monitor de entradas
            @ SD + buzzer + LCD   ? [comando] ajuda detalhada (ex.: ? A, ? ASM, ? DEBUG)"""),
      P('Convenção de ajuda (pedido do usuário): textos sempre verbosos, sem abreviar (início, fim, bloco...), no formato "D [início [fim]]   descrição". A memória protegida contra escrita pelos comandos P, F, E, A, K e Z vai de $2000 até RAMEND. O X coloca a pilha em $FEFC (RAM de 64 KB) e exige STROBE periódico se o watchdog estiver ativo.', 'small'),
      H2('7.3 EhBASIC, CP/M-68K e Tetris'),
      P('<b>EhBASIC</b> (Lee Davison) portado para a placa: comando B do monitor; usa RAMEND+1 como topo. <b>CP/M-68K</b>: BDOS/CCP/BIOS ficam na ROM em $F88000; na RAM ficam os dados ($2000-$30FF) e a TPA ($3100...). Os discos A: e B: de 512 KB são arquivos A.dsk/B.dsk servidos pela ponte do PC. O CP/M tenta passar a serial a 57600 bps e volta a 9600 sozinho se a velocidade não fechar; Ctrl+R na ponte força 9600. Programas de usuário em formato .68K absoluto a partir de $4000. <b>Tetris</b> de terminal (prioridade mais baixa; só seria cortado se faltasse espaço); se o clock do 68000 subir, rever as constantes de atraso.'),
      H2('7.4 Programas de teste e periféricos'),
      tbl([['Programa', 'Função'],
           ['programas/entradas.asm, entradas_bip.asm', 'mostra as entradas $020028/$020030 e apita quando uma muda; usado para localizar os pinos de J1'],
           ['programas/sd.asm', 'driver SPI do cartão SD por bit-banging no latch $020018 (inicialização, leitura de setor, SDHC)'],
           ['programas/perif.asm', 'SD + buzzer + LCD 20x4 (HD44780, 4 bits): comandos I (inicializa SD), R (lê setor), B (escala de notas), A (tom 440 Hz), K (calibra buzzer), L (teste do LCD), Q (sai)']], [62, 110]),
      P('Todos carregam com L e executam com G 2000 (ou pelo comando @ da ROM). O latch $020018 é só de escrita: os drivers mantêm a cópia-sombra LSH ($2F40) e alteram só os bits que usam.', 'small'),
      H2('7.5 Ponte serial no PC (COM9)'),
      bullets(['Instalar uma vez: <font face="DVM">py -3 -m pip install pyserial</font>. Fechar o RealTerm (a porta só abre num programa).', 'Dois cliques em ponte.bat (ou <font face="DVM">py -3 ferramentas\\paragon_bridge.py --port COM9</font>): a janela funciona como terminal, tudo é gravado em serial.log com hora.',
               'Pasta envio\\: um arquivo .s19 é carregado (comando L); se o nome terminar em _run, executa também (G). Um .txt vira uma linha de comando por linha; "#wait 60" aumenta o tempo de espera.',
               'A ponte serve os discos do CP/M (disco\\A.dsk e B.dsk). osc\\ponte_osc.py faz o mesmo para o osciloscópio (capturas em osc\\capturas).']),
      H2('7.6 Ferramentas de build'),
      tbl([['Arquivo', 'Uso'],
           ['ferramentas/m68kasm.py, asm68k.py', 'assembler 68000 em Python (usado para monitor.asm, perif.asm, programas)'],
           ['ferramentas/build.py, build_mon.py, srec.py', 'monta o monitor e gera S-records'],
           ['fontes_monitor_v2.1/ (ext.c, asm.c, dis.c, ext_a.s, monitor.asm, perif.asm, mkrom21.py, cpm/bios.c, ehbasic/eh_rom.asm)', 'monitor v2.1: núcleo em assembly + módulo estendido em C; mkrom21.py gera HI/LO/F80000'],
           ['fontes_monitor_v2.1/boardtest.py', 'teste automatizado no emulador (modelo da placa: E/S em $20000, sem /DTACK em $60000)'],
           ['fonte/Paragon50_firmware.asm', 'disassembly comentado do firmware do laser (~16,7 mil linhas)']], [68, 104]), PageBreak()]

# ---- 8
S += [H1('8. Integração com a RepRapDiscount Smart Controller'),
      P('Decisão do usuário: cartão SD e buzzer passivo são fundamentais, o LCD 20x4 "sempre serve", o encoder é dispensável. A placa RepRapDiscount (kit RAMPS) fica fora do gabinete, ligada por cabo a uma placa de interligação entre J1/J2 e os conectores EXP1/EXP2. A ordem dos pinos abaixo é a padrão de memória (RAMPS): <b>confirmar na serigrafia antes de ligar</b>.'),
      tbl([['EXP', 'Sinal', 'Paragon', 'Direção'],
           ['EXP2-2', 'SCK', 'J1-28 (bit 0 de $020018)', 'saída'], ['EXP2-6', 'MOSI', 'J1-26 (bit 1)', 'saída'], ['EXP2-4', 'SD_CS', 'J1-24 (bit 2)', 'saída'],
           ['EXP1-3', 'LCD_EN', 'J1-20 (bit 3)', 'saída'], ['EXP1-4', 'LCD_RS', 'J1-18 (bit 4)', 'saída'], ['EXP1-5', 'LCD_D4', 'J1-15 (bit 5)', 'saída'], ['EXP1-6', 'LCD_D5', 'J1-14 (bit 6)', 'saída'],
           ['EXP1-7', 'LCD_D6', 'J1-10 (bit 7)', 'saída'], ['EXP1-8', 'LCD_D7', 'J2-47 (bit 8)', 'saída (fio em J2)'], ['EXP1-1', 'BEEPER', 'J2-40 (bit 9)', 'saída (fio em J2)'],
           ['EXP2-1', 'MISO', 'J1-7 (B0 de $020028)', 'entrada'], ['EXP1-2', 'BTN_ENC', 'J1-31 (B3)', 'entrada'], ['EXP2-3', 'BTN_EN1', 'J1-33 (B2)', 'entrada'], ['EXP2-5', 'BTN_EN2', 'J1-35 (B1)', 'entrada'],
           ['EXP2-7', 'SD_DETECT', 'J1-27 (B4)', 'entrada, opcional'], ['EXP1-9 e EXP2-9', 'GND', 'J1-9 + GND da fonte', '-'], ['EXP1-10', '+5 V', 'fonte externa de 5 V (J1 não tem Vcc)', '-'], ['EXP2-8 (KILL), EXP2-10', '-', 'sem ligação', '-']],
          [28, 26, 80, 38]),
      bullets(['Livres em J1 para expansão: J1-23 (B6), J1-25 (B5), J1-36 (B7) [?], J1-4 (A3).',
               'O MISO do cartão é 3,3 V: o 74LS240 aceita (VIH = 2 V). O SD fica a 3,3 V no módulo do controlador (conversor de nível 4050 no próprio controlador).',
               'O SPI é por software (bit-banging) no latch de 16 bits, a ~dezenas de kHz: suficiente para ler setores no monitor/CP/M, não para velocidade.',
               'O buzzer é passivo: o programa gera o tom (440 Hz de teste, escala de notas, calibração K) pelo bit 9.']),
      H1('9. Expansão: RAM e interposer com CPLD'),
      H2('9.1 RAM'),
      P('Feito: 128 KB em $000000-$01FFFF (seção 3.2). O plano de 256 KB (Y4 AND Y5) foi abandonado porque $020000-$03FFFF é E/S do laser; a RAM de 1 MB contígua por modificação da decodificação foi substituída pela proposta do interposer. Futuro: $060000-$07FFFF está livre mas precisa de /DTACK próprio (origem a rastrear em U35, U1, U33); o CP/M-68K aceita várias regiões de memória.'),
      H2('9.2 Interposer EPM7128S (projeto, não construído)'),
      P('O 68000 vai num soquete em cima do interposer (placa perfurada) e um macho torneado "back to back" encaixa no soquete da placa. Quase todos os 64 pinos passam direto; só /AS (6), /UDS (7), /LDS (8) e /DTACK (10) são cortados e passam pelo CPLD (EPM7128SLC84-15, Quartus 13.0sp1, USB-Blaster), que bloqueia o ciclo da placa original nas janelas novas.'),
      tbl([['Faixa', 'Função', 'Observação'],
           ['$000000-$07FFFF', 'placa original', 'inalterado (RAM de 128 KB, E/S)'],
           ['$100000-$1FFFFF', 'SRAM nova, 1 MB (2 x 512K x 8)', 'sem wait state, palavra, bytes alto e baixo'],
           ['$200000-$2FFFFF', 'registradores do CPLD', 'periférico de 8 bits, endereços ímpares, espelhado a cada 16 bytes'],
           ['$300000-$3FFFFF', 'TMS9118 (módulo próprio com 2 RAMs, cristal, NTSC)', '$300001 dado, $300003 registrador/status (MODE = A1)'],
           ['$F80000-$FFFFFF', 'ROM e DUART', 'inalterado']], [34, 62, 76]),
      tbl([['Registrador', 'Endereço', 'Conteúdo'],
           ['0', '$200001', 'b3..0 = D4..D7 do LCD; b4 = RS; b5 = E; b6 = BEEP'], ['1', '$200003', 'b0 = CS do SD (1 = desselecionado); b1 = velocidade SPI (0 = 250 kHz, 1 = 2 MHz)'],
           ['2', '$200005', 'escrita: inicia transferência SPI de 8 bits; leitura: último byte recebido'], ['3', '$200007', 'b0 = BUSY (SPI); b1 = cartão presente'],
           ['4', '$200009', 'b0 = ENC_A, b1 = ENC_B, b2 = botão, b3 = KILL, b4 = INT do VDP'], ['5 / 6', '$20000B / $20000D', '$5A (identificação) / $01 (versão)']], [26, 34, 112]),
      P('Arquivos: cpld/paragon_x.v (Verilog), cpld/model.py e test_model.py (modelo de teste em Python). Falta mandar o arquivo .pin do Quartus para gerar a tabela de fiação. Teclado PS/2 e a decodificação associada ficam para o interposer. Pinos do CPLD: 29 entradas + 8 do barramento + 19 saídas = 48 de 68 do PLCC-84.', 'small'), PageBreak()]

# ---- 10
S += [H1('10. Gabinete impresso em 3D'),
      P('Objetivo: caixa em cunha (painel superior inclinado, como a do TEC-1), impressa em 3D, com <b>J1 e J2 virados para a frente (lado baixo)</b>. A placa fica <b>em cima da tampa</b>, num rebaixo de 1,2 mm, e é aparafusada nela; a RepRapDiscount fica fora, ligada por cabo. A mesa da impressora tem 300 mm ou mais. O usuário tem um croqui de uma caixa comercial (duas cascas: casca superior com bisel e painel, mais a base) e quer a mesma forma, ampliada para caber a placa.'),
      H2('10.1 Dimensões da placa'),
      tbl([['Medida', 'Valor', 'Fonte / estado'],
           ['Comprimento maior ("largura")', '274 mm', 'confirmado pelo teste: encaixou perfeito na tampa_v1'],
           ['Lado menor ("comprimento")', '~142,6 mm (provisório)', 'a estimativa inicial de 147 mm e a correção de 144,8 mm erraram; o teste da v3 (rebaixo de 145,6 mm) deixou 3 mm de folga atrás com a placa encostada na frente: 145,6 - 3,0 = 142,6 [?]. Confirmar com a placa de teste v5 e com paquímetro.'],
           ['Folga em volta do rebaixo', '0,4 mm', 'parâmetro FOLGA'],
           ['Conectores J1/J2', 'sobressaem ~7 mm da borda da frente', 'entalhes na margem frontal ($u$ 42-129 e 142-218 mm)'],
           ['Furos de fixação', '5 furos M3', 'tabela abaixo']], [46, 38, 88]),
      tbl([['Furo', 'Projeto antigo (u; v) mm', 'Corrigido na placa de teste v5 (u; v) mm', 'Deslocamento medido nas fotos (Δu; Δv)'],
           ['1', '33,8; 5,6', '31,7; 6,0', '-2,1; 0,0'], ['2', '36,7; 107,0', '32,5; 107,1', '-4,2; -0,3'], ['3', '141,0; 58,0', '137,3; 59,0', '-3,7; +0,6'],
           ['4', '241,5; 4,7', '240,9; 6,8', '-0,6; +1,7'], ['5', '243,0; 102,0', '241,4; 104,0', '-1,6; +3,7 (leitura ruim)']], [14, 44, 62, 52]),
      P('u = distância ao longo do lado de 274 mm a partir do canto esquerdo da frente; v = distância a partir da borda da frente (lado de J1/J2). Método: em cada boss da placa de teste v3 o furo impresso é o projeto e o ponto de caneta marca o furo real da PCB; medida com a régua da foto (~6 px/mm). Incerteza de cada valor: ±0,5 a 1 mm. Em u o desvio médio é -2,4 mm (e os vãos 1&rarr;4 e 2&rarr;5 saíram ~1,5 a 2,5 mm maiores que o projeto); em v a placa estava encostada na frente, então o desvio é real. Os furos impressos saíram com 2,4 a 2,9 mm (projeto de 3,4 mm): a v4/v5 usa 4,0 mm. Conferir os valores com paquímetro antes de fixar o gabinete.', 'small'),
      H2('10.2 Placas de teste (calibre do rebaixo e dos furos)'),
      tbl([['Versão', 'Mudança', 'Arquivo'],
           ['v1', 'chapa maciça de 4,5 mm (malha com defeito: furos saíam como rasgos); arquivo perdido', '-'],
           ['v2', 'malha fechada, grade vazada no meio (economiza plástico); W = 147', 'placa_teste_v2.stl/.py'],
           ['v3', 'W = 144,8 (correção após o teste da tampa_v1); impressa e medida', 'placa_teste_v3.stl/.py'],
           ['v4', 'metade da espessura (2,25 mm; apoio e nervuras de 1,05 mm), furos de 4,0 mm, furos reposicionados; W = 144,8', 'placa_teste_v4.stl/.py'],
           ['v5', 'igual à v4 com W = 142,6 mm; ~21 g de PLA. <b>Próxima a imprimir</b>', 'placa_teste_v5.stl/.py']], [18, 110, 44]),
      H2('10.3 Gabinete: v1 e v2'),
      P('<b>v1</b>: bandeja aberta com paredes de topo inclinado + tampa-moldura plana, 281 x 149 x 62 mm; foi muito diferente do croqui e a malha (CSG) tem arestas sem par; não usar para novas impressões. <b>v2</b>: refeito conforme o croqui: duas cascas (tampa com bisel de 9 mm + base), frente a 10°, topo a 15°, junção inclinada (z = 12 + 24,2/184 · y), paredes da base a 25° (frente) e 15° (fundo), painel rebaixado 1,2 mm, janela com apoio de 2 mm, colunas de parafuso inclinadas 15° e 4 pilares verticais de união; externo 292,0 x 155,1 mm, altura 32,9 mm na frente e 73,5 mm no fundo. A tampa imprime de cabeça para baixo; os 11,8 mm do topo plano do croqui foram removidos (precisariam de suporte). O croqui original mede 268 x 184 x 77,5 mm; o usuário escolheu ampliar o croqui para acomodar a placa.'),
      H2('10.4 Feedback do usuário e v3 planejada'),
      bullets(['As laterais não são retas: abrem para fora na metade de baixo e fecham na de cima; a "linha de cintura" (onde as duas metades se encontram) tem a maior seção. Inclinação típica a usar: 4-5° (fotos de frente/fundo na altura da cintura, vista de cima e close do canto com régua permitem acertar).',
               'As arestas e os cantos são arredondados, não vivos: raio de ~6-8 mm.',
               'A largura da cintura deve crescer para ~296 mm; o bisel fica mais estreito no fundo porque a inclinação é relativa ao plano inclinado da junção.',
               'Usar W = 142,6 mm (provisório) e a tabela de furos corrigida; manter versionamento (gabinete_v3, base_v3, tampa_v3) e o CHANGELOG_gabinete.txt.']),
      P('Arquivos em gabinete/: base_v1/v2.stl, tampa_v1/v2.stl, montagem_v1/v2.stl, gabarito_furos_v1.stl, gabinete_v1.py/gabinete_v2.py, placa_teste_v2..v5, previas e perfil_gabinete_v2_vs_croqui.png; obsoletos_sem_versao/ guarda os arquivos antigos sem versão no nome. Regra: todo arquivo gerado leva _vN e nada é sobrescrito.', 'small'), PageBreak()]

# ---- 11
S += [H1('11. Procedimentos de teste e diagnóstico atualizados'),
      P('Trate a placa como parte de um laser de alta tensão apenas se algum dia voltar ao equipamento: no uso standalone trabalhe só com +5 V e +/-12 V em bancada, com J1/J2 sem nada ligado além do que o projeto prevê. Sequência sugerida (complementa o guia do v1, Parte II):'),
      tbl([['#', 'Verificação', 'Como / esperado', 'Se falhar'],
           ['1', 'Alimentação', '+5 V nos CIs (CPU pinos 14 e 49), +12 V e -12 V em TB1', 'sem +/-12 V os drivers RS-232 e os op-amps não operam'],
           ['2', 'Clock', '8 MHz no pino 15 da CPU', 'sem clock a CPU não executa'],
           ['3', 'Reset', 'DS1232: /RESET sobe ~150 ms após a alimentação', 'oscilando = watchdog disparando (JP6 não instalado)'],
           ['4', 'Boot', 'no terminal (57600 8N1) aparece a tela limpa e o menu BASIC/MONITOR', 'testar EPROMs HI/LO trocadas; checar U26 (74LS14) e os pinos 27, 26 e 1 da ROM'],
           ['5', 'RAM', 'comando I: RAM 128 KB ($000000-$01FFFF); Q: mapa; Z: teste completo', 'I mostra 64 KB: A16/A15 ou /CS1 do adaptador errados; bytes trocados: inverter U13/U14; espelho em $13010: A16 não chegou ao pino 31'],
           ['6', 'Serial', 'monitor responde a 57600; em dúvida usar 38400 ou 9600', '115200 não funciona (cristal de 3,6864 MHz)'],
           ['7', 'E/S', 'comando J mostra os bits que mudam ao aterrar um pino de J1 por 330 &Omega;', 'conferir pull-up de 4,7 k e o 74LS240 do bit'],
           ['8', 'Saídas', 'osciloscópio em J1-28: contador a 108 kHz (programa de teste)', 'U39/U45 (273), clock de U6 Y3'],
           ['9', 'Periféricos', 'comando @: banner no LCD, apito do buzzer, "I" inicializa o SD', 'conferir a ordem EXP1/EXP2 e a alimentação de 5 V externa']], [8, 24, 70, 70]),
      P('Cuidados: nunca escrever em $020000-$07FFFF sem saber o que há ali; $060000-$07FFFF trava a CPU; o latch $020018 é só de escrita; leituras no DUART ($FA0000) consomem caracteres do receptor; o watchdog reinicia a placa se o programa do usuário demorar sem chamar STROBE ($F8082A).', 'nota'),
      H1('12. Pendências e próximos passos'),
      tbl([['Item', 'Detalhe'],
           ['Gabinete', 'imprimir a placa de teste v5; medir com paquímetro o lado menor e a folga; fechar W e os furos; gabinete v3 (laterais com cintura, raio 6-8 mm), fotos do gabinete do croqui se o usuário encontrar.'],
           ['Periféricos', 'montar a placa de interligação J1/J2 &harr; EXP1/EXP2 e testar o comando @ (SD, LCD, buzzer) na placa real; só depois decidir sobre encoder.'],
           ['Mapa de E/S', 'localizar as demais entradas (portas A e B), as saídas $020020 (bits 0-6 e 8-11), as portas de 8 bits em $040xxx; confirmar B7 em J1-36; anotar referências de U19, U28, U34, U35, U1, U33 e do 68000.'],
           ['ROM / monitor', 'validar a ROM v2.1 na placa real (comandos I, Q, J, X com erro de endereço/barramento); rever X/Z/F para o novo mapa; atrasos do Tetris se o clock subir; testar EPROM/flash mais rápida ou clock de 12 MHz.'],
           ['Interposer', 'gerar o .pin no Quartus, montar o interposer em placa perfurada, RAM 1 MB, TMS9118, teclado PS/2.'],
           ['Serial', 'avaliar MAX232 se for desejado 115200 bps (o limite é o cristal do 68681).'],
           ['GitHub', 'conectar o GitHub, escolher nome do repositório e licença; publicar todo o material (dumps e disassembly incluídos) com publicação automatizada.'],
           ['Documentação', 'este manual e o esquema são versionados (v2 / v1); atualizar a cada novo resultado.']], [30, 142]), PageBreak()]

# ---- 13
S += [H1('13. Arquivos do projeto'),
      P('Pasta de trabalho no PC: Documents\\Claude\\Paragon50\\ (cada sessão/conversa com seu diretório).'),
      code("""Paragon50/
  fotos/  fotos_display/     fotos da placa CPU (frente, verso, soquetes) e da placa Display Interface
  rom_original/              Paragon_50_HI.BIN, Paragon_50_LO.BIN (dumps do laser)
  rom/ROM_V2.1_27C512/       PARAGON512_HI/LO/F80000.bin + LEIA-ME (gravar HI na U8 e LO na U7)
  rom/ROM_V2_27C512/, rom/Arquivo/   versoes anteriores e testes (serial, CP/M, DIAG)
  fonte/                     monitor.asm, Paragon50_firmware.asm (disassembly comentado do laser)
  fontes_monitor_v2.1/       ext.c asm.c dis.c ext_a.s monitor.asm perif.asm mkrom21.py boardtest.py cpm/ ehbasic/
  programas/                 entradas*.asm, sd.asm, perif.asm (+ .s19, listagens _P.txt)
  ferramentas/               m68kasm.py asm68k.py build*.py srec.py paragon_bridge.py
  osc/                       ponte_osc.py e capturas do DSO-X
  envio/enviados/            historico de tudo que foi enviado a placa pela ponte
  cpld/                      paragon_x.v, model.py, test_model.py (interposer)
  disco/                     A.dsk, B.dsk (CP/M)
  gabinete/                  STL e scripts do gabinete e das placas de teste (+ CHANGELOG_gabinete.txt)
  docs/                      Mapa_enderecos.txt, Mapa_J1_J2_porta_020018.txt, Mapa_entradas_J1.txt, J4_pinagem_serial.txt,
                             Ligacao_RRD_Smart_Controller_J1.txt, Paragon50_Esquema_v1.pdf, Paragon50_Manual_v2.pdf,
                             PDFs de medicao e projeto (RAM128K, interposer, J1/J2, rastreio, adesivos de CI)
  docs/arquivo/              versoes antigas de PDFs, incluindo Paragon50_Manual_v1.pdf
  ponte.bat  serial.log  LEIA-ME.txt  LEIA-ME_PONTE.txt  MONITOR_V2_MANUAL.txt  TODO_monitor_v2.1.txt"""),
      Spacer(1, 6 * mm),
      P('Este manual foi gerado por gerar_manual_v2.py a partir do esquema (gerar_esquema_v1.py) e do manual v1; os scripts ficam em ferramentas/ para regenerar a cada atualização.', 'small'), PageBreak()]
S += [Spacer(1, 80 * mm), P('PARTE II', 'capa1'), Spacer(1, 6 * mm), P('Manual v1 (07/11/2026): engenharia reversa do firmware do laser', 'capa2'), Spacer(1, 8 * mm),
      P('As páginas seguintes reproduzem, sem alterações, as seções 6 a 9 e os anexos A, B e C do manual v1 (arquitetura do firmware, máquina de estados, interrupção, serial, exceções, descritivo funcional, guia de diagnóstico, rotinas comentadas, tabela de funções, textos do display e resumo final). Os mapas de memória e de E/S, a lista de CIs e as conclusões de hardware das seções 1 a 5 do v1 foram substituídos pela Parte I; onde houver divergência vale a Parte I (ver seção 2, errata). A numeração das páginas desta parte é a original do v1.', 'body'), ]
def _flat(x):
    for e in x:
        if isinstance(e, list): yield from _flat(e)
        else: yield e
doc.build(list(_flat(S)))

# ---------------------------------------------------------------- pós-processamento com pypdf
base = PdfReader('/tmp/_m.pdf'); esq = PdfReader(ESQ); v1 = PdfReader(V1)
w = PdfWriter()
n_part1 = len(base.pages)
idx_ph = {}
for i, pg in enumerate(base.pages):
    t = pg.extract_text() or ''
    for k in range(1, 5):
        if f'ESQUEMA_FOLHA_{k}' in t: idx_ph[i] = k - 1
a4l = (842.0, 595.0)
for i, pg in enumerate(base.pages):
    if i in idx_ph:
        src = esq.pages[idx_ph[i]]; sw, sh = float(src.mediabox.width), float(src.mediabox.height)
        k = min((a4l[0] - 20) / sw, (a4l[1] - 36) / sh)
        newp = w.add_blank_page(width=a4l[0], height=a4l[1])
        newp.merge_transformed_page(src, Transformation().scale(k).translate((a4l[0] - sw * k) / 2, 22))
    else:
        w.add_page(pg)
# páginas da parte II: 6..26 (seção 6 em diante) do v1
for i in range(6, len(v1.pages)): w.add_page(v1.pages[i])
total = len(w.pages)
# numeração de página nas páginas da parte I (inclui divisória da parte II)
def numerar(i, pg, ate):
    wd, ht = float(pg.mediabox.width), float(pg.mediabox.height)
    buf = io.BytesIO(); c = rl_canvas.Canvas(buf, pagesize=(wd, ht)); c.setFont('DV', 7.5); c.setFillColor(colors.HexColor('#555555'))
    c.drawString(18 * mm if wd < 600 else 20, 10 if wd >= 600 else 11 * mm, 'PARAGON 50 - Manual v2 - Tabajara Labs')
    c.drawRightString(wd - (18 * mm if wd < 600 else 20), 10 if wd >= 600 else 11 * mm, f'pág. {i + 1} / {total}')
    c.save(); buf.seek(0); pg.merge_page(PdfReader(buf).pages[0])
for i in range(n_part1):
    if i > 0: numerar(i, w.pages[i], n_part1)
w.add_metadata({'/Title': 'PARAGON 50 - Manual da placa CPU 68000 (v2)', '/Author': 'Tabajara Labs / Claude'})
w.write(OUT)
print('paginas:', total, 'parte I:', n_part1)
