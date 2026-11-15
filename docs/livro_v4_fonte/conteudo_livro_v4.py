# -*- coding: utf-8 -*-
story.append(NextPageTemplate('corpo')); story.append(PageBreak())
story.append(Paragraph('Sumário',S['h1'])); story.append(LineRule()); story.append(Spacer(1,8))
toc=TableOfContents(); toc.levelStyles=[S['toc1'],S['toc2']]; toc.dotsMinLevel=0; story.append(toc)

def quadro(titulo,txt):
    p=[Paragraph('<font name="Sans-B" color="#d9731a">%s</font>'%titulo,ParagraphStyle('q1',parent=S['bodyl'],fontSize=9,spaceAfter=3)),Paragraph(txt,ParagraphStyle('q2',parent=S['bodyl'],fontSize=8.9,leading=13,spaceAfter=0))]
    t=Table([[p]],colWidths=[W-LM-RM]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fdf3e8')),('BOX',(0,0),(-1,-1),.6,LARA),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(KeepTogether([t,Spacer(1,8)]))

def _caixa(rot,titulo,txt,cor,bg,hdr):
    t1=Paragraph('<font name="Sans-B" color="white">%s</font>&nbsp;&nbsp;<font name="Sans" color="#dfe8f3">%s</font>'%(rot,titulo),ParagraphStyle('bh',parent=S['bodyl'],fontSize=8.3,leading=11,spaceAfter=0))
    t2=Paragraph(txt,ParagraphStyle('bb',parent=S['bodyl'],fontSize=8.7,leading=12.6,spaceAfter=0))
    t=Table([[t1],[t2]],colWidths=[W-LM-RM]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),hdr),('BACKGROUND',(0,1),(-1,1),bg),('BOX',(0,0),(-1,-1),.6,cor),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,0),3.5),('BOTTOMPADDING',(0,0),(-1,0),3.5),('TOPPADDING',(0,1),(-1,1),6),('BOTTOMPADDING',(0,1),(-1,1),7)]))
    story.append(KeepTogether([t,Spacer(1,8)]))
def saber(titulo,txt): _caixa('PARA SABER MAIS',titulo,txt,colors.HexColor('#3b7bb8'),colors.HexColor('#eef5fb'),colors.HexColor('#3b7bb8'))
def esp(titulo,txt): _caixa('EXPLICAÇÃO PARA ESPECIALISTAS',titulo,txt,colors.HexColor('#2b3440'),colors.HexColor('#f1f3f6'),colors.HexColor('#2b3440'))
def licao(txt): callout('dica','<b>Lição:</b> '+txt)

# ---------- Prefácio ----------
h1('Prefácio')
para('Este livro conta uma história curta e intensa: como a placa de controle de um laser cirúrgico, jogada fora junto com o resto do equipamento, virou um computador 68000 de verdade — com monitor, BASIC, CP/M, Forth, cartão SD, relógio, e um bootloader que impede a placa de “morrer” (<i>brickar</i>) por causa de uma gravação errada.')
para('Os personagens são dois. <b>Alexandre</b>, do Tabajara Labs, com a bancada, o ferro de solda, o osciloscópio e as ideias — muitas das melhores decisões do projeto foram dele. E <b>Claude</b>, o assistente de IA que escreveu o firmware, os emuladores, os testes e os documentos, e que, por uma ponte serial, operava a placa diretamente na bancada enquanto Alexandre dizia onde encostar a ponta de prova.')
para('Não é um manual (esse é o <i>Manual de Referência</i>, que acompanha este livro). Aqui interessa o <b>caminho</b>: por que cada decisão foi tomada, o que deu errado, o que aprendemos, e como o método de trabalho — pequeno passo, medir, testar no emulador, só depois gravar — salvou o projeto mais de uma vez. Cada capítulo termina com uma <b>lição</b>, porque a gente aprende muito mais com os erros do que com os acertos.')
quadro('Como ler','Quem quer só a história pode ler os capítulos 1 a 8 em sequência. Os quadros laranja explicam, em linguagem simples, os conceitos técnicos que aparecem (o que é um disassembly, o que é bit-bang, o que é um CRC...). O capítulo 11 descreve o método de trabalho, e o 12 aponta os próximos passos.')

# ---------- 1 ----------
h1('1. Um laser no lixo')
para('O ponto de partida foi um laser cirúrgico <b>PARAGON 50</b>, da Heraeus Surgical. O equipamento foi declarado obsoleto e sucateado; da carcaça, Alexandre salvou a placa da CPU. Antes de mexer em qualquer coisa, ele fez o que todo preservador de eletrônica faz: leu e guardou o conteúdo das memórias — os dois chips de ROM (<font name="Mono">Paragon_50_HI.BIN</font> e <font name="Mono">Paragon_50_LO.BIN</font>) e as NVRAMs Dallas — e fotografou a placa pelos dois lados.')
figura('img/laser_inteiro.jpg',72*mm,'Figura 0 — O laser PARAGON 50 completo: coluna com o braço óptico, painel de controle “Laserscope” (com a barra vermelha) e o gabinete com a placa CPU lá dentro.')
figura('img/laser_painel.jpg',95*mm,'Figura 0 — O painel de controle do laser: botões de potência (watts), modo contínuo/pulsado/único e repetição. Os controles do painel eram, provavelmente, lidos pelas entradas digitais da placa — parte do que o comando J ajudou a mapear.')
figura('img/foto_frente.jpg',150*mm,'Figura 1 — A placa CPU do PARAGON 50: 68000 (canto superior direito), 68681 DUART (à direita), SRAMs Dallas com bateria embutida, conversor D/A, buzina de teste e os conectores J1 e J2 na borda inferior.')
para('A placa deixou de ter um laser para comandar, mas continuava sendo um computador completo: um <b>Motorola 68000</b>, memória, uma porta serial, entradas e saídas digitais, conversores analógicos. Faltava só um programa novo. A pergunta que abriu o projeto foi: “dá para reaproveitar isso como um micro 68000 standalone?”.')
h2('O primeiro pedido: entender o que existe')
para('Antes de escrever código novo, era preciso entender o código antigo. O primeiro pedido foi um <b>disassembly comentado</b> das duas ROMs, um descritivo do funcionamento da placa, o mapa de endereços e das principais portas de E/S, e um manual. O resultado foi o arquivo <font name="Mono">Paragon50_firmware.asm</font> e os documentos de mapa de endereços — a base de tudo que veio depois.')
quadro('O que é um disassembly?','As ROMs guardam números (o código de máquina). O <i>disassembler</i> transforma esses números de volta em instruções legíveis (<font name="Mono">move.l d0,(a0)+</font>, <font name="Mono">bra.s loop</font>...). Depois, descobrir <i>o que</i> cada trecho faz — e dar nomes aos endereços — é um trabalho de detetive chamado <b>engenharia reversa</b>. É como aprender uma língua morta lendo textos antigos: dá trabalho, mas cada palavra descoberta ajuda a entender as próximas.')
para('A decisão central veio logo: <b>a placa não voltaria ao laser</b>. Isso liberou tudo — todos os recursos do hardware poderiam ser reaproveitados, e o firmware original servia apenas como fonte de informação (por exemplo, de como o conversor A/D era disparado).')
figura('img/foto_nvram.jpg',150*mm,'Figura 2 — Detalhe: as duas NVRAMs Dallas DS1230Y (SRAM de 32 KB com bateria) e a ROM. O conteúdo das NVRAMs foi lido e arquivado antes de qualquer experiência.')
figura('img/foto_traseira.jpg',110*mm,'Figura 3 — A face de solda: as trilhas, vistas por trás, ajudaram a reconstruir o esquema junto com as medições.')
saber('Quem foi o Heraeus PARAGON 50?','Era um laser médico, de uso cirúrgico, controlado por uma placa CPU com um microprocessador de 16/32 bits — o 68000 era uma escolha comum nos anos 80/90 para equipamentos que precisavam de potência de “minicomputador” a custo moderado. Depois de declarado obsoleto, o aparelho foi desmontado e a placa foi salva. Aqui ela não volta ao laser: nada nela comanda mais qualquer carga.')
esp('O 68000 em poucas linhas','Dados de 16 bits, endereços de 24 bits (16 MB), 8 registradores de dados (D0–D7) e 8 de endereço (A0–A7, com A7 como pilha; USP e SSP separadas). Dois modos: usuário e supervisor. A tabela de <b>vetores</b> começa em $000000: o primeiro longword é o SSP inicial e o segundo o PC inicial — por isso, depois do reset, o 68000 lê os 8 primeiros bytes do espaço de endereços para saber por onde começar. Como a ROM da placa vive em $F80000 e a tabela de vetores precisa estar em $000000, o monitor copia os vetores para a RAM (é também o que o stub faz ao iniciar um aplicativo de outro banco).')
licao('guarde sempre uma cópia do original antes de qualquer experiência. Os dumps de ROM e NVRAM feitos no primeiro dia continuam sendo a referência até hoje.')

# ---------- 2 ----------
h1('2. Conhecendo a placa')
para('Com o firmware original lido, o passo seguinte foi levantar o hardware. Alexandre mediu a placa com multímetro seguindo listas impressas e foi respondendo, uma a uma, perguntas que o Claude fazia para fechar o mapa.')
tabela([['Peça','O que descobrimos'],
 ['CPU','68000 P10 (10 MHz), alimentada por um módulo oscilador de 8 MHz'],
 ['Serial','MC68681 (DUART) com cristal próprio de 3,6864 MHz; drivers de linha 1488/1489; porta no conector J4'],
 ['Memória','ROM em duas EPROMs de 28 pinos (HI e LO); RAM em SRAMs; NVRAMs Dallas'],
 ['Decodificação','<b>Lógica discreta</b> (74LS138 e portas) — não há PAL/GAL, o que facilitou a engenharia reversa'],
 ['E/S','Conectores J1, J2 e J7 ligados direto a portas de E/S; os drivers de potência estavam na outra placa (do display), já desmontada'],
 ['Analógico','AD7875 (A/D de 12 bits) com multiplexador AD7501, e DACs de 12 bits']],[1.3,5])
para('Uma descoberta importante foi o <b>mapa de endereços</b>. O 68000 enxerga 16 MB (24 bits de endereço), e a placa dividia esse espaço em blocos: RAM no começo, E/S do laser em $020000, a faixa $060000–$07FFFF <i>sem resposta</i> (acessá-la trava o barramento) e a ROM no alto, em $F80000. Esse mapa aparece, ampliado, no Manual de Referência.')
quadro('Como o processador “enxerga” as peças','O 68000 não tem “portas” como o Z80: tudo é endereço. Um circuito chamado <b>decodificador</b> (aqui, um 74LS138 e algumas portas) olha os bits altos do endereço e ativa o chip certo: “endereços $F8xxxx? ligue a ROM”. Escrever em $020018 não grava em memória: aciona um <i>latch</i> cujas saídas vão para os pinos de J1/J2. Entender isso é a chave para usar qualquer pino da placa.')
h2('A serial: 57600 bps para tudo')
para('Alexandre testou velocidades: 115200 bps não funcionou; 38400 funcionou; e ele sugeriu (e adotamos) <b>57600 bps</b> como padrão único — monitor, BASIC, CP/M e a ponte do PC falam na mesma velocidade, sem precisar trocar nada ao mudar de programa.')
figura('img/foto_duart.jpg',150*mm,'Figura 4 — A região do 68681 (à direita), do cristal de 3,6864 MHz e da CPU. A serial A sai pelo conector J4.')
figura('img/foto_display_if.jpg',95*mm,'Figura 0 — A outra placa do sistema, a Display Interface, quase sem componentes: conectores do laser (J121 e outros) ainda estão lá, mas os circuitos de potência foram removidos.')
figura('img/c_decod.png',160*mm,'Figura 5 — Decodificação de endereços, simplificada: lógica discreta divide os 16 MB entre ROM, DUART, registrador de banco, E/S e RAM.')
saber('O que é /DTACK?','No 68000, toda leitura ou escrita termina quando o periférico responde com um sinal chamado <b>/DTACK</b> (“data transfer acknowledge”). Se ninguém responde, o processador fica esperando para sempre — ou até um circuito de watchdog gerar um erro de barramento. Na placa, o /DTACK é gerado por uma porta 74LS11 (U35) e, em geral, cada ciclo leva uns quatro estados de espera. A faixa $060000–$07FFFF não tem ninguém que gere /DTACK: acessá-la trava a CPU. Por isso aparece sempre com o aviso “nunca acessar”.')
esp('Folha de esquema reconstruída por medição','A figura abaixo é a folha 1 do esquema reconstruído (CPU, clock e reset): módulo oscilador de 8 MHz, DS1232 (reset + watchdog; o watchdog está desabilitado, JP6 não instalado), e cada pino da CPU anotado com “rede > destino.pino”. Verde = medido; azul = inferido do datasheet; vermelho = a rastrear. O /DTACK vem do U35 e <b>não depende do R/W</b>: escritas na região da ROM terminam normalmente, o que é o que permite gravar a flash em circuito sem mexer na geração do /DTACK.')
figura('img/esq_folha1.png',170*mm,'Figura 6 — Folha 1/6 do esquema reconstruído: CPU, clock e reset.')
licao('padronizar cedo uma coisa chata (a velocidade da serial) evita uma classe inteira de confusões depois.')

# ---------- 3 ----------
h1('3. A primeira vida: monitor, BASIC e CP/M numa EPROM')
para('A ideia: gravar numa EPROM um <b>monitor</b> (um programinha que deixa examinar e alterar a memória pela serial), o <b>EhBASIC</b> (um BASIC compacto de Lee Davison) e o <b>CP/M-68K</b>. O monitor de partida foi o ChartreuseK 68k-Monitor, que cresceu muito: ganhou assembler e disassembler de linha, depurador com breakpoints, calculadora, teste de RAM, mapa de memória, ajuda detalhada e verbosa (“inicio”, “fim”, nunca abreviado) — uma preferência explícita de Alexandre, que queria um monitor que ensinasse a usá-lo.')
para('Para não gravar às cegas, o Claude construiu ferramentas no PC: um <b>assembler</b> de 68000, um <b>emulador</b> (<font name="Mono">emu68k.py</font>) e uma <b>ponte serial</b> que envia arquivos pela porta. A regra de ouro nasceu aqui: <b>testar no emulador antes de gravar na placa</b>.')
para('A primeira ROM única (monitor + BASIC + CP/M, com menu de boot) foi gravada em EPROMs 27C256 e <b>funcionou</b>. Depois vieram as EPROMs 27C512, de 128 KB: Alexandre mediu a fiação dos endereços A13/A14 (passando por inversores 74LS14) e confirmou que a placa aceitava o chip maior sem mudança de hardware. Com mais espaço, o monitor v2 ganhou o assembler completo.')
quadro('O que é o CP/M-68K?','CP/M foi o sistema operacional dos micros de 8 bits nos anos 70/80 (Z80, 8080). A Digital Research também fez uma versão para o 68000. Ele precisa de um <b>BIOS</b> — a camada que sabe falar com o hardware específico (console, discos). Aqui o BIOS foi escrito do zero para esta placa: console pela serial, e “discos” que na verdade são arquivos no cartão SD.')
saber('Monitor, BASIC, CP/M: qual a diferença?','O <b>monitor</b> é o programa mais básico: deixa você ver e mudar a memória, carregar e rodar programas. O <b>BASIC</b> é uma linguagem interpretada, boa para experimentar. O <b>CP/M</b> é um sistema operacional completo, com arquivos, discos e programas em disco. O Paragon tem os três, e o monitor serve de “porta de entrada” para os outros.')
esp('O formato S-record e o ponto de entrada','Programas são enviados em <b>S-records</b> (S1/S2/S3 para dados com 16/24/32 bits de endereço; S7/S8/S9 para o ponto de entrada) com checksum por linha. O comando <font name="Mono">L</font> carrega os registros, guarda o ponto de entrada e informa “OK registros=… entrada=… início=… tamanho=…”. <font name="Mono">G</font> executa com JSR (o programa volta com RTS) e <font name="Mono">X</font> executa sob o depurador, trocando a instrução do breakpoint por ILLEGAL e restaurando-a ao parar.')
licao('um emulador bom economiza semanas. Vários defeitos foram achados nele antes de chegarem à placa — por exemplo, um buffer de texto que caía na flash, pega pelo emulador em novembro de 15.')

# ---------- 4 ----------
h1('4. Mais memória')
para('Com o 68000 rodando, a RAM virou o gargalo. A placa original tinha pouca. O plano de Alexandre foi pragmático: usar as SRAMs que ele tinha “aos quilos” (KM681000BLP-5, 128 K × 8) soldadas em <b>adaptadores 28→32 pinos</b>, no lugar das originais. Ele construiu os adaptadores à mão e a placa passou a ter <b>128 KB</b> em $000000–$01FFFF.')
h2('O caminho dos 256 KB (e uma serial muda)')
para('O plano de 256 KB foi trocado, retomado e adiado: o bloco $020000–$03FFFF é E/S do laser (e Alexandre queria manter o GPIO), então a RAM extra foi para <b>$040000–$05FFFF</b>, a “RAM2”. Para ligá-la foram necessárias modificações no 74LS138 (U4) e no 74LS11 (U5): o pino 2 do U5 foi levantado e preso em +5 V.')
para('Foi nessa etapa que apareceu o primeiro grande susto: depois de aplicar os fios de A17/A18/C nas SRAMs, <b>a serial ficou muda</b>. O princípio da bancada entrou em ação — desfazer tudo e voltar ao estado conhecido (a ROM v2.2 voltou a funcionar com 128 KB), depois refazer a modificação <b>por etapas, uma mudança por vez</b>, testando a cada passo.')
tabela([['Região','Uso'],['$000000–$00FFFF','RAM principal (64 KB visíveis; $010000–$01FFFF espelha/estende)'],['$040000–$05FFFF','RAM2 de 128 KB: disco RAM P: do CP/M (124 KB), gravação de imagens de banco, registro do ADL'],['$060000–$07FFFF','proibido: não gera /DTACK']],[1.5,4.5],mono_cols=(0,))
para('Esse espaço extra tem várias utilidades até hoje: o CP/M ganhou a unidade <b>P:</b> (disco RAM), o gravador de flash guarda ali a imagem de 128 KB, e o ADL grava ali seus registros.')
quadro('E o 1 MB com CPLD?','Alexandre também desenhou, num caminho paralelo, um <i>interposer</i>: uma plaquinha com CPLD EPM7128 entre o soquete e o 68000, que traria RAM contígua de 1 MB (SRAMs de 512 K × 8), vídeo TMS9118 e LCD/SD. Os modelos em Verilog existem (<font name="Mono">hardware/cpld</font>), mas o projeto foi adiado: a prioridade passou a ser o cartão SD e depois a flash.')
saber('Por que adaptadores 28→32?','As SRAMs KM681000 têm 32 pinos (128 K × 8), mas os soquetes da placa são de 28 pinos. O adaptador é uma plaquinha com um soquete de 28 pinos embaixo e um de 32 em cima; os pinos extras (A15, A16 e outros) saem por fios para onde a placa decide. Alexandre os montou à mão e em cada um levantou os pinos 32, 31, 30, 1 e 2 para religá-los por fio.')
esp('As mudanças de decodificação','Para dar à RAM2 o seu bloco de 128 KB em $040000, foi preciso alterar as ligações do decodificador U4 (74LS138): a saída Y6 foi para o pino 9 do U4, e o pino 2 do U5 (74LS11) — que antes recebia essa saída — foi levantado e preso em +5 V. A primeira tentativa, que mexia nas linhas A17/A18 e “C” das SRAMs, deixou a serial muda; o estado original foi restaurado e a modificação refeita por etapas.')
licao('quando uma modificação “quebra” a placa, a pergunta certa é “o que mudou?”, e a resposta só é confiável se você muda uma coisa por vez.')

# ---------- 5 ----------
h1('5. LCD, cartão SD e buzzer: a placa RepRap')
para('Alexandre tinha em casa uma placa de controle <b>RepRapDiscount Full Graphic Smart Controller</b> (aquelas de impressora 3D, do kit RAMPS): LCD 20×4, slot de cartão SD, encoder, botões e um buzzer ativo. A ideia: ligá-la aos conectores J1/J2 e ganhar, numa tacada, <b>tela, armazenamento e som</b>.')
para('Mas o hardware não tinha uma porta SPI. A solução foi <b>bit-bang</b>: o 68000 manipula diretamente os bits de um latch para gerar o relógio (SCK), os dados (MOSI) e o chip select, e lê a resposta (MISO) pela porta de entrada. É lento, mas funciona e não exige nenhuma peça extra. Com isso o cartão SD passou a ser lido e gravado, com um sistema de arquivos <b>FAT16</b> escrito do zero.')
quadro('O que é bit-bang?','Um periférico “de verdade” (como uma UART) gera sinais sozinho. No <i>bit-bang</i> o próprio processador faz o papel do periférico, ligando e desligando pinos na velocidade certa por software. Serve para qualquer protocolo simples (SPI, I²C...), ao custo de tempo de CPU. Foi assim que o LCD, o SD e, depois, o relógio I²C foram ligados.')
tabela([['Recurso','Como foi feito'],['LCD 20×4','Modo de 4 bits (HD44780); E, RS, D4–D7 em bits do latch $020018'],['Buzzer','Bit 9 do latch; ativo (tem oscilador interno); comando BEEP'],['Cartão SD','SPI por software: SCK, MOSI, CS no latch; MISO na porta B; detecção de cartão'],['Arquivos','FAT16 leitura/escrita; shell FATSH; discos CP/M como arquivos A.DSK..D.DSK em \\CPM'],['BASIC','LOAD, SAVE, FILES, KILL, CHDIR no estilo MSX, via driver SDFS']],[1.3,5])
para('O CP/M ganhou discos como <b>arquivos .DSK</b> no cartão (de A.DSK a D.DSK, de 512 KB cada), uma ideia de Alexandre: “pegar um .DSK no PC, copiar para o cartão, e o CP/M bootar abrindo o cartão como drive”. Assim não é preciso nenhum programa de ponte para transferir discos.')
figura('img/c_rrd.png',150*mm,'Figura 7 — As 12 ligações entre J1/J2 e a placa RepRapDiscount (EXP1 e EXP2), mais GND comum e +5 V externo.')
figura('img/c_latches.png',165*mm,'Figura 8 — Mapa de bits dos dois latches de saída: quem controla o quê.')
figura('img/c_spi.png',150*mm,'Figura 9 — Um byte pelo SPI (modo 0): o 68000 mexe nos bits do latch para gerar SCK e MOSI, e lê o MISO pela porta de entrada.')
saber('O que é FAT16?','É o sistema de arquivos que organiza um cartão SD: uma <i>tabela de alocação</i> (FAT) diz, para cada <i>cluster</i> do disco, qual é o próximo; os diretórios guardam nome, tamanho e o primeiro cluster de cada arquivo. O FAT16 é mais simples que o FAT32 e é o que o cartão de teste usa (970 MB, clusters de 16 KB).')
esp('Detalhes do SPI por software e do cartão','O cartão trabalha a 3,3 V; a placa RepRap já traz um conversor de nível 4050 — as saídas de ~4,3 V do Paragon entram direto, e o MISO volta em 3,3 V, que o 74LS240 aceita (VIH = 2 V). O 74LS240 <b>inverte</b>, então o driver lê o MISO invertido. A inicialização segue o protocolo SD padrão (CMD0, ACMD41 até o cartão sair de “idle”), com pulsos de “strobe” do watchdog durante as esperas longas. Como cada transição é uma escrita no latch ($020018), a velocidade é baixa: suficiente para BASIC e CP/M, lenta para arquivos grandes.')
licao('quando o hardware não tem o periférico, descreva o protocolo em software. É mais lento, mas costuma ser a solução mais barata e mais rápida de depurar.')

# ---------- 6 ----------
h1('6. Flash em bancos')
para('A ROM de 128 KB já era generosa, mas Alexandre queria algo maior: <b>vários programas na flash</b>, escolhidos num menu. Ele decidiu usar as memórias <b>Am29F040B</b> (512 KB cada) que já tinha em estoque, montadas em adaptadores 28→32 no lugar das EPROMs. Duas flashes (uma alta, outra baixa) formam 8 bancos de 128 KB.')
h2('As quatro peças do hardware')
bullets(['<b>Adaptadores</b> das flashes (pinos 1, 2, 30 e 31 levados por fios: bits de banco e /WE).',
 '<b>Circuito de /WE</b> com 74LS32, montado por Alexandre por baixo do processador: permite gravar a flash <i>dentro da própria placa</i>.',
 '<b>Registrador de banco</b> com 74LS175 em $FC0000: o que se escreve ali escolhe qual dos 8 bancos aparece em $F80000–$F9FFFF.',
 '<b>Pull-ups</b> de 4,7 kΩ nos dois /WE, para a flash nunca ser gravada sem querer durante o reset.'])
figura('img/mapa_bancos.png',150*mm,'Figura 2 — Os 8 bancos de 128 KB (estado em 15/11/2026).')
h2('O software: cabeçalho AB, CRC32 e gravador')
para('Cada banco válido começa com um cabeçalho de 64 bytes, no estilo dos cartuchos MSX: as letras “AB”, o nome do programa, a versão, endereços e um <b>CRC32</b>. O monitor lista os bancos, confere o CRC e inicia o escolhido. O <b>gravador de flash</b> roda na RAM (não pode rodar da flash que está apagando), recebe a imagem inteira pela serial, <b>confere o CRC antes de apagar</b> e só grava depois de o usuário digitar <font name="Mono">PROSSIGA</font> — um pedido do próprio Alexandre.')
quadro('O que é um CRC?','CRC (<i>cyclic redundancy check</i>) é uma “impressão digital” de um bloco de dados: um número de 32 bits calculado a partir de todos os bytes. Se um único bit mudar, o CRC muda. Antes de apagar a flash, o gravador calcula o CRC da imagem recebida e compara com o esperado; se não bater, nada é apagado. É o que impede uma transmissão ruim de destruir um banco.')
figura('img/c_banco175.png',165*mm,'Figura 10 — O registrador de banco: um 74LS175 clockado por (Y2 do U4) OU R/W; suas três saídas viram os bits A16, A17 e A18 das duas flashes.')
figura('img/c_escrita_we.png',160*mm,'Figura 11 — O circuito de escrita em circuito: um 74LS32 gera um /WE para cada flash (HI e LO). Os jumpers ficam abertos no uso normal.')
figura('img/c_tempo_we.png',150*mm,'Figura 12 — Temporização da escrita: /WE só cai quando R/W, ROM_CE e /UDS estão baixos.')
figura('img/c_gravador.png',160*mm,'Figura 13 — O fluxo do gravador de flash: confere, pergunta, grava, volta.')
saber('O que é memória flash?','Uma memória que mantém o conteúdo sem energia, como uma EPROM, mas que se apaga e regrava <i>eletricamente</i> e em pedaços (setores). A Am29F040B guarda 512 KB em 8 setores de 64 KB; para gravar, é preciso mandar uma sequência de comandos por escrita — e, como a flash não pode ser lida durante o apagamento, o programa que grava precisa estar na RAM.')
esp('Sequência de comandos e temporização','Os comandos seguem o padrão AMD/JEDEC: <font name="Mono">$AA</font> em <font name="Mono">$555</font>, <font name="Mono">$55</font> em <font name="Mono">$2AA</font> e então o comando (ID: <font name="Mono">$90</font>; programação: <font name="Mono">$A0</font>; apagar setor: <font name="Mono">$80</font> + <font name="Mono">$30</font>); a conclusão é detectada por <i>polling</i> de DQ7. Como o 68000 grava palavras, o mesmo comando vai nas duas flashes (por exemplo <font name="Mono">$AAAA</font>). Cada ciclo da placa dura ~1 µs (4 estados de espera), então o pulso de /WE fica em centenas de ns — muito acima dos poucos dezenas de ns exigidos. Os endereços do 68000 passam por inversores de A13–A15 do U26 antes de chegar à flash, e a leitura do ID (<font name="Mono">$01</font>/<font name="Mono">$A4</font>) confirmou o mapeamento antes de qualquer apagamento. No registrador de banco, o clock é “Y2 OU R/W”: sobe no fim da escrita em <font name="Mono">$FC0000</font>; leituras não o disparam. Escrever em <font name="Mono">$FC0000</font> por byte alto também clocka com D0–D2 sem sentido, por isso se usa palavra (<font name="Mono">move.w</font>) ou byte em <font name="Mono">$FC0001</font>.')
licao('hardware de gravação em circuito + software de gravação paranoico (confere antes, pede senha) é o que torna seguro mexer na ROM sem programador externo.')

# ---------- 7 ----------
h1('7. Os incidentes (e o que cada um ensinou)')
para('Nenhum projeto de hardware/firmware sério passa sem sustos. Os desta história foram guardados com cuidado, porque cada um virou uma regra.')
tabela([['Incidente','Causa','Lição / regra criada'],
 ['Banco 0 apagado duas vezes ao gravar a v2.5 pela ponte','O gravador voltou ao monitor v2.4 num endereço deslocado (+6 bytes por causa de um <font name="Mono">jsr</font> novo) e se re-executou sozinho','O gravador sempre volta por endereço fixo em RAM; resgate com programador externo; <i>nunca</i> depender de endereços da versão anterior'],
 ['Banco 0 “morto” com a v2.6','Fio de A18 no pino 11 do 74LS175 em vez do 10 (banco lógico N = físico N XOR 4); mais um byte 0D extra na imagem','Medir com osciloscópio o que o firmware assume; conferir a imagem byte a byte antes de gravar'],
 ['CRC do menu de bancos nunca funcionou no hardware','Rotina do strobe do monitor não salvava o D7 inteiro: só lia 1 bloco de 4 KB','Correção na v2.6.1; o CRC passou a ser conferido “de verdade” (menu A → “CRC OK”)'],
 ['CP/M dava exceção vetor 0B ao iniciar','Imagem do CP/M montada com base $8000 em vez de $F88000','Remontada com a base correta (v2.3.1)'],
 ['“driver sdfs nao carregado” no BASIC','O banco novo não copiava o driver do cartão para $50000 antes de iniciar','Driver embutido em $F90000 e copiado automaticamente (bk_drv)'],
 ['Menu de comandos sumiu depois de uma reorganização','B/C foram removidos do monitor ao criar o stub','Restaurados na v3.5a; teste de regressão no emulador'],
 ['“FLASH 7 1” copiou o banco 1 para o 7','Ordem destino→origem, invertida em relação a qualquer comando de cópia','Regra de Alexandre: <b>sempre COMANDO ORIGEM DESTINO</b> (FLASH e F do shell SD)'],
 ['Serial muda após modificação de 256 KB','Várias mudanças de fiação ao mesmo tempo','Voltar ao estado conhecido; refazer uma mudança por vez'],
 ['Buzzer disparou sozinho','Desconhecida; um reset resolveu','Anotada na lista de pequenos ajustes']],[1.6,2.2,2.4])
esp('O erro do A18 em detalhe','No 74LS175 as saídas Q e /Q ficam em pinos vizinhos (3Q = pino 10, 3Q̅ = pino 11). O fio de A18 foi ligado ao 3Q̅ — a saída invertida —, o que faz o banco lógico N aparecer como o físico N XOR 4. Na prática, o “banco 0” em que o reset caía era o físico 4, e a imagem gravada tinha ainda um byte 0D extra no início, portanto sem vetores válidos. Depois de corrigir o fio, o osciloscópio confirmou A18 baixo nos bancos 0–3 e alto nos 4–7, e o menu (teste no banco 5) mostrou o comportamento esperado.')
callout('nota','O incidente do banco 0 deixou uma marca: o <b>programador externo</b> (que tira e regrava as flashes) foi o único jeito de resgatar a placa — as flashes ficaram difíceis de remover. Foi isso que motivou o capítulo seguinte.')

# ---------- 8 ----------
h1('8. A rota de fuga: o stub do banco 0')
para('Depois do incidente, o próprio Alexandre propôs o plano de “rota de fuga”: o banco 0 deveria ser <b>mínimo, quase imutável, só gravável com senha</b>; as atualizações iriam para o banco 1. Mas foi uma segunda ideia dele que deu a forma final: “<i>faça o stub bootando com algo tipo</i> ‘SBC Paragon 50 – 2026 Tabajara Labs / Aperte R para entrar no menu de recuperação / Aguarde 5 segundos pra carregar a imagem 1 (autoload)’”. Se nada for apertado em 5 segundos, ele carrega a área 1; “se o banco 1 estiver vazio, pule pro banco 2 e por aí vai”.')
figura('img/fluxo_boot.png',160*mm,'Figura 3 — O fluxo de boot: stub no banco 0, autoload do primeiro banco válido e menu de recuperação.')
h2('O que o stub faz')
bullets(['Mostra o splash, inicializa serial e LCD e espera 5 s por <b>R</b>.',
 '<b>Sem tecla</b>: autoload — procura o primeiro banco de 1 a 7 com cabeçalho AB e CRC32 corretos; banco vazio ou corrompido é pulado.',
 '<b>R</b>: menu de recuperação com monitor, lista de bancos, shell do cartão SD (gravar banco de um arquivo), gravação pela serial, autoload e Tetris.',
 '<b>Banco 0 protegido</b>: o gravador só o altera se for digitado <font name="Mono">PROSSIGA0</font> (com zero no fim); <font name="Mono">PROSSIGA</font> sozinho vira “só comparar”.'])
para('Com o stub gravado (v3.2s), a frase de Alexandre resumiu a mudança: <i>“a partir desse momento, não tem como bricar o micro. É só não mexer no banco 0”</i>. A partir daí o Claude passou a gravar sozinho nos bancos 1 a 7 — o banco 0 ficou intocado, e qualquer erro se corrige com R no boot.')
quadro('Por que isso funciona?','Se uma gravação corrompe o banco 1, o stub (banco 0, nunca alterado) ainda inicia, vê que o CRC do banco 1 não bate, pula para o banco 2, 3... ou, se você apertar R, deixa você regravar o banco 1 pela serial ou pelo cartão SD. O único ponto de falha é o próprio banco 0 — e ele só aceita uma senha especial.')
figura('img/c_trampolim.png',160*mm,'Figura 14 — Como o monitor inicia o BASIC (banco 7): uma rotina copiada para a RAM troca o banco e salta.')
saber('Stub, bootloader, autoload: o que cada palavra quer dizer','<b>Bootloader</b> é qualquer programa que carrega outro. <b>Stub</b> é um bootloader mínimo, quase sem funções. <b>Autoload</b> é a decisão automática: sem intervenção do usuário, carrega o primeiro programa válido que encontrar. Os três juntos formam o desenho do banco 0.')
esp('Algoritmo do autoload e do CRC','Para cada banco n de 1 a 7: (1) escreve n em $FC0000, a partir de código na RAM; (2) confere a assinatura “AB” e os campos início/fim do cabeçalho em $F807C0; (3) calcula o CRC32 sobre [início..$F807BF] e [$F80800..fim] — o cabeçalho de 64 bytes (que contém o próprio CRC) fica de fora; (4) se tudo bate, copia os vetores do banco para a RAM e salta para a entrada (tipo 0: SP/PC dos vetores; tipo 1: entrada do cabeçalho, SP = $1F00). Banco vazio (todo $FF) ou com CRC errado é pulado (<font name="Mono">au_nx</font>); se nenhum for válido, cai no menu de recuperação. Antes disso, o stub aguarda 5 s por R, usando o timer do DUART. O <i>strobe</i> do watchdog é dado durante o cálculo, e foi justamente um erro nisso que fazia o CRC só ler um bloco de 4 KB no hardware (capítulo 7).')
licao('um bom bootloader é pequeno, quase imutável e sabe dizer “não”. Tudo que muda com frequência vive fora dele.')

# ---------- 9 ----------
h1('9. Descobrindo os pinos: J, ADC, DAC e o relógio')
para('Com o computador “vivo”, sobrou a parte analógica e as dezenas de pinos de J1, J2 e J7, cujo uso original era desconhecido. A estratégia foi montar um <b>mapa por medição</b>:')
bullets(['O comando <font name="Mono">J</font> do monitor lê continuamente as entradas e imprime uma linha sempre que um bit muda.',
 'Alexandre aterrava, com um resistor de 330 Ω, um pino de cada vez; o log da ponte dizia a que bit (porta A ou B) aquele pino chegava.',
 'As saídas foram descobertas ao contrário: o Claude acionava bits do latch e Alexandre via, com osciloscópio, em qual pino aparecia o sinal.',
 'O resultado foi anotado em folhas de pinos em PDF, de v1 até v14 (com correções vindas do log, como J2-35 = A14).'])
para('O conversor A/D (AD7875) e os DACs de 12 bits foram comandados com base no firmware original: o disparo é um pulso no pino OP3 do DUART, o canal vai nos bits 14–12 do latch $020020, e o resultado é lido em $020000. Isso virou os comandos <font name="Mono">ADC</font>, <font name="Mono">ADL</font> (registro em CSV na RAM2) e <font name="Mono">DAC</font>.')
h2('O relógio: do DS1302 ao DS1307')
para('Primeiro planejou-se um DS1302 (que Alexandre tinha), com pinos provisórios — a versão t5 do firmware. Mas o módulo que ele realmente tinha era um <b>DS1307 I²C</b> (5 V, GND, SCL, SDA). Em vez de insistir, o firmware foi refeito: um <b>I²C por bit-bang</b> usando dois bits do latch $020020 como saídas de coletor aberto (SCL em J1-30, SDA em J1-48) e uma entrada de leitura da linha SDA em J1-23.')
figura('img/i2c_rtc.png',140*mm,'Figura 4 — Ligação do módulo DS1307 à placa.')
para('A hora aparece na <b>linha 4 do LCD</b>, atualizada pelo laço ocioso do monitor só quando o monitor está parado no prompt (para nunca atrapalhar o cartão SD ou o A/D). O tempo foi calibrado na própria placa com <font name="Mono">RELOGIO CAL</font>: 100.000 voltas do laço levaram 24,0 s, ou 0,24 ms por volta.')
callout('aviso','A pilha CR2032 do módulo estava descarregada. Falta trocá-la e fazer o teste de retenção (ajustar a hora, desligar a placa, religar e conferir).')
figura('img/c_adc.png',160*mm,'Figura 15 — A cadeia do conversor A/D: oito entradas em J2, multiplexador, AD7875 e leitura em $020000.')
figura('img/c_i2c.png',150*mm,'Figura 16 — Um quadro I²C (endereço do DS1307 = $68) gerado por bit-bang: SCL e SDA são bits do latch $020020.')
saber('O que é I²C?','Um barramento de dois fios (SCL = relógio, SDA = dados) em que um “mestre” fala com vários “escravos” identificados por endereço. Os fios são de <i>coletor aberto</i>: ninguém empurra o nível alto, só puxa para baixo; resistores de pull-up (já no módulo) levam a linha para cima. Por isso, no latch, “1” significa “puxar para baixo”.')
esp('Leitura do SDA e temporização do bit-bang','A saída SDA do latch (J1-48) e a entrada de leitura (J1-23, porta B bit 6) são emendadas por fora para o mesmo nó do módulo, o que permite ler o ACK do escravo sem trocar a direção de um pino. A temporização é por laços de espera calibrados (o mesmo laço medido por RELOGIO CAL: 0,24 ms por volta); o I²C do DS1307 tolera velocidades até 100 kHz, bem acima do que o bit-bang entrega — nada precisa ser rápido. Como a leitura é feita no laço ocioso do monitor, a hora no LCD é lida só quando o minuto pode ter mudado (registrador 0x01).')
licao('quando a realidade (o módulo I²C) contradiz o plano (o DS1302), o certo é descartar o plano. O firmware v3.1t5 foi simplesmente jogado fora.')

# ---------- 10 ----------
h1('10. Os aplicativos')
tabela([['Aplicativo','Banco','Como entrar','Observações'],
 ['Monitor','1','automático (5 s)','Todos os comandos; assembler, depurador, periféricos'],
 ['EhBASIC','7','B ou BASIC','Com FILES, LOAD, SAVE, KILL, CHDIR e MONITOR'],
 ['CP/M-68K','7','C ou CPM','Discos A–D em \\CPM no cartão e disco RAM P:'],
 ['eForth 68k','5','F ou FORTH','Confere o CRC32 do banco antes; BYE volta'],
 ['Tetris','1 / stub','T','Q sai']],[1.2,0.8,1.5,3.2])
para('Os três sistemas viraram comandos do prompt (<font name="Mono">BASIC</font>, <font name="Mono">CPM</font>, <font name="Mono">FORTH</font>), além das teclas do menu. O <b>EhBASIC</b> precisa do driver SDFS para falar com o cartão; o <b>CP/M-68K</b> usa os discos .DSK; o <b>eForth</b> (do <i>eForth</i> de C. H. Ting para 68000, adaptado) foi validado na placa com banner, <font name="Mono">WORDS</font> e <font name="Mono">BYE</font>.')
para('Um detalhe de engenharia merece registro: o BASIC e o CP/M ficam no <b>banco 7</b> e o monitor no <b>banco 1</b>. Para iniciar um aplicativo em outro banco, o monitor copia os vetores desse banco para a RAM e executa o salto a partir de uma <b>rotina na RAM</b> (porque a troca de banco mexe no código que está sendo executado). É o mesmo princípio do gravador.')
licao('quando uma rotina troca a memória debaixo dos próprios pés, ela precisa viver em RAM.')

# ---------- 11 ----------
h1('11. Como trabalhamos')
para('O método foi tão importante quanto o código. Os princípios, destilados:')
tabela([['Princípio','Na prática'],
 ['Claude opera a placa','Pontes no PC (serial e osciloscópio): arquivos de texto com comandos (#raw, #wait, #sendbin) que o Claude escreve e a ponte executa. Alexandre só diz “encoste a ponta aqui”, <b>um passo por vez</b>.'],
 ['Emulador primeiro','Todo firmware é testado no emulador (com modelos do A/D, DACs, RTC, cartão SD) antes de ir para a placa.'],
 ['Conferir antes de medir','Antes de cada medição, confirmar que o programa na placa continua rodando (um curto entre pinos pode ter acontecido).'],
 ['Verificar tudo com CRC','Cada imagem tem CRC32; a gravação confere antes de apagar e depois de gravar.'],
 ['Versionar tudo','Todo arquivo gerado leva sufixo de versão (_v1, _v2...); versões antigas de ROM vão para uma pasta de arquivo — nunca se apaga.'],
 ['Ordem origem → destino','Regra para todos os comandos de cópia/gravação.'],
 ['Nada digitado durante a gravação','A serial é ocupada pelo gravador; qualquer tecla pode corromper a transferência.'],
 ['Repositório GitHub','Todos os fontes, ROMs, documentos e ferramentas em TabajaraLabs/SBC-Laser-Paragon-50-DIY.']],[1.7,4.6])
quadro('A regra de ouro','<b>Uma mudança por vez</b>, medida antes e depois. Ela vale para soldar fios, para escrever firmware e para gravar a flash. Todos os incidentes do capítulo 7 aconteceram quando duas coisas mudaram ao mesmo tempo.')
para('Outro hábito que valeu a pena: <b>documentar enquanto se constrói</b>. Os registros de mudança (<font name="Mono">CHANGELOG_rom.txt</font>), as folhas de pinos, os mapas e a lista de pequenos ajustes (<font name="Mono">LISTA_pequenos_ajustes_v1.txt</font>) foram essenciais — inclusive para este livro.')

# ---------- 12 ----------
h1('12. A caixa e o futuro')
para('O micro, do jeito que está, já é perfeitamente usável. Faltam <b>acertos de hardware</b> e uma <b>caixa</b>.')
h2('O gabinete')
para('O primeiro desenho foi um gabinete impresso em 3D em <b>cunha</b>, como o do TEC-1, com painel superior inclinado e J1/J2 virados para a frente; a placa RepRap fica fora, ligada por cabo. Para confirmar as medidas, o Claude gerou uma <b>placa de teste</b> (<font name="Mono">placa_teste_v9.stl</font>) em que a placa real coube com precisão — a placa mede 274 × 144,8 mm e o gabinete v2 em cunha mede cerca de 292 × 155 mm por fora, com 33 mm de altura na frente e 73,5 mm atrás.')
para('Alexandre tem olhado com carinho para uma caixa no estilo <b>Altair 8800</b>, que ele já usou numa réplica: um painel frontal vertical, com fileira de LEDs e chaves. O painel poderia ser uma peça à parte (acrílico, MDF ou impressa), aparafusada na frente, com recortes para LCD, encoder, botões, cartão SD e buzzer — e uma fileira de LEDs/chaves ligada às saídas e entradas de J1/J2. Esse desenho será o gabinete v3, sem sobrescrever o v2.')
figura('img/previa_gabinete_v2_explodida.png',130*mm,'Figura 17 — Gabinete v2 em cunha, vista explodida: base, moldura da tampa e a placa.')
figura('img/planta_medidas_v1.png',150*mm,'Figura 18 — Planta de medidas lidas nas fotos: a placa mede 274 mm de largura; J1 e J2 ficam na frente.')
figura('img/perfil_gabinete_v2_vs_croqui.png',140*mm,'Figura 19 — Perfil lateral do gabinete v2 (azul) comparado com o croqui inicial (vermelho tracejado).')
saber('Por que uma cunha?','Teclados e computadores de bancada em cunha deixam o painel superior inclinado para o usuário, e a parte de trás mais alta acomoda conectores e componentes altos. É o desenho clássico de micros como o TEC-1 e muitos kits. O Altair, por outro lado, tem um painel vertical na frente (cheio de chaves e LEDs) e um corpo retangular: o desenho do painel é o que dá a “cara” do micro.')
h2('Próximos passos')
tabela([['Item','Situação'],
 ['LCD com PCF8574 (I²C)','Ideia boa, adiada. Concentraria tudo em J1 e liberaria J2 (D7 e buzzer); exigiria LCD HD44780 + PCF8574, módulo SD novo e buzzer novo'],
 ['Pilha do relógio (CR2032)','Comprar, ajustar a hora, testar retenção'],
 ['Interposer com CPLD EPM7128','RAM de 1 MB, TMS9118 (vídeo NTSC), teclado PS/2; adiado'],
 ['Calibrar o A/D (ADL)','Escala em mV supõe 0–5 V; a confirmar na bancada'],
 ['Hardware','Ordem dos bits do 74LS273, REF OUT, AGND, loopback DAC→ADC, pinos de J7'],
 ['Software','? SISTEMA sem o Forth; lista de comandos sem RELOGIO/BASIC/CPM/FORTH; banner do shell SD ainda “FATSH v8”; testar CP/M com cartão; beeper que disparou sozinho'],
 ['Gabinete v3','Definir o painel frontal e a caixa (estilo Altair?)']],[2,4.3])
para('E o Tabajara Labs segue: há outros projetos em andamento (CPLD substituto do CDP1861, DM9368 com CH32V003, ULA do ZX81 em CPLD, placa de som para o TEC-1G...), com o mesmo método.')

# ---------- Apêndices ----------
h1('Apêndice A — Linha do tempo')
figura('img/linha_tempo.png',170*mm,'Figura 5 — As etapas do projeto.')
tabela([['Data','Marco'],
 ['12/11','ROM v2.2: RAM2 em $040000; monitor/ext novos'],
 ['12/11','v2.3: CP/M-68K com disco RAM P: (124 KB na RAM2)'],
 ['13/11','Flash Am29F040B-90 no lugar das EPROMs; v2.3.1 (CP/M com base $F88000) gravada na própria placa'],
 ['14/11','v2.4: módulo de bancos e cabeçalho AB; v2.5: FLASH no monitor — incidente do banco 0; gravação externa'],
 ['14/11','v2.6/v2.6.1: BEEP e bipes; incidente do A18; CRC32 do menu corrigido'],
 ['14/11','v3.0: banco 0 como pré-bootloader (BOOT+MONITOR), shell FAT, gravador v5c; repositório criado no GitHub'],
 ['14–15/11','v3.1t4–t8: ADC, ADL, DAC, RTC I²C, relógio no LCD (banco 4 de testes)'],
 ['15/11','<b>v3.2s: stub do banco 0</b> + imagem do banco 1; ordem origem→destino'],
 ['15/11','v3.3: BASIC/CP/M com SDFS embutido (banco 7); v3.4: comandos BASIC/CPM/FORTH; v3.5a: menu B/C restaurado'],
 ['15/11','Manual de Referência v4.0 e este livro']],[1,6],mono_cols=(0,))
h1('Apêndice B — Glossário')
gl=[('68000','Microprocessador de 16/32 bits da Motorola (1979); barramento de dados de 16 bits, endereços de 24 bits.'),
('68681 (DUART)','Circuito com duas portas seriais, timer e portas de E/S; aqui, a serial A é o console.'),
('Bank (banco)','Uma janela de 128 KB da flash; só um banco é visível por vez, escolhido por um registrador.'),
('Bit-bang','Gerar um protocolo (SPI, I²C...) ligando e desligando pinos por software.'),
('BIOS','Camada do CP/M que conversa com o hardware (console, disco).'),
('Brickar','Deixar o equipamento sem condições de iniciar — “virar tijolo”.'),
('CRC32','Número de 32 bits calculado dos dados; detecta alterações.'),
('Cabeçalho AB','Bloco de 64 bytes no início de cada banco: assinatura, nome, versão, endereços, CRC32.'),
('Disassembly','Conversão de código de máquina em instruções legíveis.'),
('EhBASIC','BASIC enxuto de Lee Davison, portado para 68000.'),
('eForth','Forth compacto de C. H. Ting; no Paragon, roda do banco 5.'),
('Flash (Am29F040B)','Memória que apaga e regrava por setor; 512 KB por chip.'),
('Latch','Registrador que guarda o valor escrito e o mantém nos pinos de saída.'),
('PROSSIGA','Palavra de confirmação digitada para o gravador de flash gravar (PROSSIGA0 para o banco 0).'),
('Ponte','Programa do PC que executa, via serial, os arquivos de comando que o Claude escreve.'),
('S-record','Formato de texto para transmitir programas (linhas S1/S2/S3...).'),
('SDFS / FATSH','Driver (BASIC/CP/M) e shell (monitor) do sistema de arquivos FAT16 do cartão SD.'),
('Stub','Programinha mínimo no banco 0 que só decide o que carregar.'),
('/DTACK','Sinal do 68000 que indica “dado pronto”; sem ele o acesso trava o barramento.')]
tabela([['Termo','Significado']]+[[a,b] for a,b in gl],[1.5,5])
h1('Apêndice C — Onde está cada coisa')
tabela([['Pasta do repositório','Conteúdo'],
 ['rom/','ROMs atuais e anteriores, fontes por versão, CHANGELOG_rom.txt'],
 ['rom/original/','Dumps originais Paragon_50_HI.BIN e Paragon_50_LO.BIN e o disassembly'],
 ['docs/','Manuais (incluindo MANUAL_PARAGON50_v4.0.pdf), mapas de endereços, pinagens, esquemas, folhas de medição'],
 ['ferramentas/','Assemblers, emuladores, ponte serial, gravador de flash (flash_v4), scripts de geração'],
 ['programas/','Programas de teste (bancos, entradas, discos CP/M)'],
 ['hardware/','Fotos da placa, modelos do CPLD, gabinete 3D']],[1.6,4.6],mono_cols=(0,))
para('<i>Este livro foi escrito por Claude com base nos registros do projeto e nas decisões de Alexandre. Sinta-se à vontade para editar: os fontes estão em <font name="Mono">conteudo_livro_v1.py</font>.</i>')
