# -*- coding: utf-8 -*-
def ajuda(k,titulo=None): code(HLP[k].strip('\n'),titulo)
# ---------- CAPA ----------
story.append(NextPageTemplate('corpo')); story.append(PageBreak())
# ---------- SUMARIO ----------
story.append(Paragraph('Sumário',S['h1'])); story.append(LineRule()); story.append(Spacer(1,8))
toc=TableOfContents(); toc.levelStyles=[S['toc1'],S['toc2']]; toc.dotsMinLevel=0; story.append(toc)

# ================= 1 =================
h1('1. Visão geral')
para('O <b>PARAGON 50</b> é um computador de placa única baseado no microprocessador <b>Motorola 68000</b>, construído a partir da placa de controle de um laser cirúrgico Heraeus Surgical (modelo Paragon 50) reaproveitada como computador independente. Com firmware novo, ela virou uma máquina completa: monitor com desassemblador, assemblador e depurador; 8 bancos de memória flash com bootloader protegido; leitura e gravação de cartão SD; relógio de tempo real; conversores A/D e D/A; e três linguagens/sistemas — <b>EhBASIC</b>, <b>CP/M-68K</b> e <b>eForth</b> — além de um Tetris.')
h2('1.1 Características')
tabela([['Item','Descrição'],
 ['Processador','Motorola MC68000, 16 bits de dados, 24 bits de endereço'],
 ['RAM','64 KB (espelhada) em $000000; RAM2 de 128 KB em $040000'],
 ['Flash','2 × Am29F040B = 8 bancos de 128 KB, visíveis em $F80000–$F9FFFF'],
 ['Serial','DUART 68681 (porta A no conector J4), 57600 bps, 8N1, sem controle de fluxo'],
 ['Display','LCD de caracteres 20×4 (RepRap Smart Controller, modo HD44780) em J1/J2, com buzzer e botões do encoder'],
 ['Armazenamento','Cartão SD (FAT16) por interface SPI emulada em bits de J1'],
 ['Relógio','DS1307 (ou DS3231) por I²C, ligado por J1'],
 ['Analógico','Entrada A/D AD7875 de 12 bits (8 canais) e 2 saídas D/A de 12 bits (J2)'],
 ['Digital','16 entradas (portas A e B, 74LS240) e 16 saídas (74LS273) nos conectores J1/J2'],
 ['Software','Monitor v3.5a, EhBASIC 2.x, CP/M-68K, eForth 68k v1.1, Tetris']],[1,3.4])
h2('1.2 Como ler este manual')
bullets(['<b>Capítulos 2 a 5</b> — primeiros passos, arquitetura, bancos de flash e o processo de boot.',
 '<b>Capítulos 6 a 8</b> — o monitor, o gravador de bancos e o shell do cartão SD (a parte mais usada no dia a dia).',
 '<b>Capítulo 9</b> — periféricos: A/D, D/A, relógio, entradas digitais, LCD e buzzer.',
 '<b>Capítulo 10</b> — pinagem de J1, J2 e J4.',
 '<b>Capítulo 11</b> — EhBASIC, CP/M-68K, eForth e Tetris.',
 '<b>Capítulos 12 e 13</b> — serviços fixos da ROM para programadores; histórico de versões, problemas conhecidos e solução de problemas.'])
callout('nota','Todos os números dos comandos do monitor são <b>hexadecimais</b>, salvo quando indicado. Os textos de ajuda reproduzidos neste manual são os mesmos que o monitor mostra ao digitar <font name="Mono">?</font> — sem acentos, porque o monitor usa apenas ASCII.')
callout('aviso','A placa foi projetada para comandar um laser. <b>Não conecte laser, fonte de potência ou qualquer carga</b> aos conectores. As saídas D/A (J2) e os latches podem acionar circuitos de potência; use apenas instrumentos de bancada.')

# ================= 2 =================
h1('2. Primeiros passos')
h2('2.1 Ligações mínimas')
bullets(['<b>Alimentação</b>: pelos conectores originais da placa (+5 V lógico).',
 '<b>Serial</b>: conector J4 — veja a pinagem na seção 10.3. Use um conversor USB-serial de 5 V/TTL ou RS-232 conforme o estágio da placa.',
 '<b>Terminal</b>: 57600 bps, 8 bits, sem paridade, 1 stop bit (8N1), sem controle de fluxo. Terminal local com eco desligado: o monitor ecoa os caracteres.',
 '<b>LCD</b>: o RepRap Smart Controller fica em J1/J2 (seção 9.5). Nada é obrigatório para o monitor funcionar; sem LCD a serial basta.'])
h2('2.2 O que aparece ao ligar')
para('Após o reset, o <b>stub</b> (banco 0) mostra um splash no LCD e na serial e espera 5 segundos. Sem tecla, ele carrega automaticamente o primeiro banco válido (normalmente o banco 1, o monitor). O monitor então mostra o banner, o menu de aplicativos e, após 5 segundos sem tecla, o prompt:')
code('''SBC Paragon 50 - 2026 Tabajara Labs
Aperte R para entrar no menu de recuperacao
Aguarde 5 segundos para carregar a imagem 1 (autoload)

Monitor Paragon 50 - Tabajara Labs 2026
Digite ? para ajuda
>''','Sequência de boot típica (serial)')
figura('img/fluxo_boot.png',160*mm,'Figura 1 — Fluxo de inicialização: stub no banco 0, autoload e menus.')
h2('2.3 Teclas do menu de inicialização')
tabela([['Tecla','Ação'],
 ['B','EhBASIC (com driver SDFS para o cartão SD)'],['C','CP/M-68K (discos no cartão SD)'],['F','eForth'],['T','Tetris (Q sai)'],
 ['A','Aplicativos: lista os bancos da flash e inicia o escolhido (1-7; 0 ou M volta)'],['R','Shell do cartão SD (FAT16)'],
 ['M','Vai direto ao prompt do monitor (também: aguardar 5 s)']],[1,5],mono_cols=(0,))
callout('dica','Na dúvida, aperte <font name="Mono">?</font> no prompt do monitor: a ajuda é contextual (<font name="Mono">? D</font>, <font name="Mono">? ASM</font>, <font name="Mono">? DEBUG</font> ...).')
h2('2.4 Primeiro teste de sanidade')
code('''> I                 informacoes da placa (RAM detectada, versao, ROM)
> Q                 mapa de memoria
> Z                 teste de RAM (apaga a RAM de usuario!)
> D F80000 F8001F   le o inicio da ROM
> RTC               data e hora (se o modulo DS1307 estiver ligado)
> BEEP 20           bipa 200 ms''')

# ================= 3 =================
h1('3. Arquitetura')
figura('img/diagrama_blocos.png',165*mm,'Figura 2 — Diagrama de blocos simplificado da placa.')
h2('3.1 Mapa de memória')
figura('img/mapa_memoria.png',165*mm,'Figura 3 — Mapa de memória do 68000 (24 bits de endereço).')
tabela([['Faixa','Conteúdo','Observações'],
 ['$000000–$00FFFF','RAM de 64 KB (espelhada em blocos de 64 KB)','Vetores em $0–$3FF; programas de usuário em $2000 em diante; pilha em $FEFC'],
 ['$020000–$02FFFF','E/S de 16 bits','Conversores, latches de saída, portas de entrada, 8254'],
 ['$040000–$05FFFF','RAM2 de 128 KB','Usada por ADL, flasher (imagem), CP/M e SDFS ($050000)'],
 ['$060000–$07FFFF','<b>Sem /DTACK</b>','Nunca acessar: o acesso trava o barramento (erro de barramento)'],
 ['$F80000–$F9FFFF','Flash (banco selecionado)','128 KB; o banco ativo é escolhido em $FC0000'],
 ['$FA0000','DUART 68681','Serial A, timer, portas de entrada/saída do chip'],
 ['$FC0000','Registrador de banco (74LS175)','Escrita seleciona o banco 0–7; o reset volta ao banco 0']],[1.25,2.2,3],mono_cols=(0,))
h2('3.2 Registradores de E/S de 16 bits')
tabela([['Endereço','Função','Uso no firmware'],
 ['$020000','Leitura do AD7875 (resultado de 12 bits)','Comandos ADC e ADL'],
 ['$02000A','DAC A (escrita, 12 bits)','Comando DAC A'],
 ['$02000C','DAC C (escrita, 12 bits)','Comando DAC C'],
 ['$020018','Latch de saída de 16 bits (74LS273 ×2)','LCD (bits 3–8), SD (bits 0–2), buzzer (bit 9)'],
 ['$020020','Latch auxiliar','Seleção de canal do A/D (bits 12–14, bit 15 liga), I²C do RTC (bit 7 SDA, bit 10 SCL)'],
 ['$020028','Porta B de entrada (74LS240)','Botões, SD_DET, SDA do RTC (bit 6), MISO do SD (bit 0)'],
 ['$020030','Porta A de entrada (74LS240, 16 bits)','Monitor de entradas (comando J)']],[1,2.4,3.4],mono_cols=(0,))
callout('nota','Os 74LS240 invertem os níveis: ao aterrar uma entrada, o bit lido sobe para 1. As saídas de coletor aberto do latch $020020 também são invertidas (nível 1 no bit = linha puxada para baixo).')

# ================= 4 =================
h1('4. Bancos da flash')
para('A memória de programa é composta por duas flashes Am29F040B, que formam <b>8 bancos de 128 KB</b>. Apenas um banco fica visível por vez na janela $F80000–$F9FFFF. A seleção é feita escrevendo em $FC0000 (registrador 74LS175). Como o código que troca de banco não pode estar executando <i>dentro</i> da flash que muda, todas as rotinas de troca são copiadas para a RAM antes de rodar.')
figura('img/mapa_bancos.png',150*mm,'Figura 4 — Ocupação atual dos 8 bancos.')
h2('4.1 Cabeçalho AB')
para('Cada banco válido começa com um <b>cabeçalho de 64 bytes</b> em $F807C0, identificado pelas letras “AB”. O stub e o menu de bancos usam o cabeçalho para identificar e validar a imagem.')
tabela([['Offset','Tamanho','Campo'],['+0','2','Assinatura “AB”'],['+2','2','Tipo (0 = ROM de sistema, 1 = aplicativo)'],['+4','4','Endereço inicial coberto pelo CRC'],['+8','4','Endereço final'],['+12','4','Ponto de entrada'],['+16','16','Nome (ASCII)'],['+32','8','Versão (ASCII)'],['+40','4','CRC-32']],[1,1,5],mono_cols=(0,))
para('O CRC-32 cobre [início..$F807BF] e [$F80800..fim]; é o mesmo CRC do zlib/Python. Um banco vazio (FF) ou com CRC incorreto é <b>ignorado</b> pelo autoload.')
h2('4.2 Tabela de salto do módulo de bancos')
para('O módulo de bancos fica em $F833F8 e oferece pontos de entrada de 6 bytes (<font name="Mono">jmp</font>), usados pelo monitor, pelos comandos BASIC/CPM/FORTH e pelo gravador:')
tabela([['Endereço','Nome','Função'],['$F833F8','bk_menu','Menu de bancos (tecla A)'],['$F833FE','lstat','Lista o estado dos 8 bancos'],['$F83404','flchk','Gravador/verificador (FLASH)'],['$F8340A','bk_auto','Autoload: inicia o primeiro banco válido 1..7'],['$F83410','bk_sys','Copia os vetores do banco D1 para a RAM e inicia em D0'],['$F83416','bk_boot','Inicia o banco D0 após conferir CRC e cabeçalho'],['$F8341C','bk_drv','Instala o driver SDFS em $50000 (para o BASIC)']],[1.2,1.2,4],mono_cols=(0,1))
h2('4.3 Regras de proteção do banco 0')
bullets(['O <b>banco 0 nunca é regravado</b> pelo uso normal: é o stub que garante que a placa sempre inicia e sempre permite recuperar.',
 'O comando <font name="Mono">FLASH</font> só grava o banco 0 se você digitar <font name="Mono">PROSSIGA0</font> (qualquer outra coisa apenas compara).',
 'O comando <font name="Mono">F arquivo banco</font> do shell SD recusa o banco 0.',
 'O banco 3 guarda o monitor v3.0 como cópia de segurança do banco 0 antigo.'])

# ================= 5 =================
h1('5. Boot, stub e recuperação')
h2('5.1 O stub (banco 0)')
para('O stub é o primeiro código executado após o reset. Ele inicializa a serial e o LCD, exibe o splash e espera 5 segundos por uma tecla. Ele só reconhece a tecla <b>R</b>:')
bullets(['<b>Tempo esgotado</b>: chama o autoload — procura o primeiro banco válido de 1 a 7 e o inicia; bancos vazios ou com CRC errado são pulados.',
 '<b>R</b>: abre o <b>menu de recuperação</b>.'])
h2('5.2 Menu de recuperação')
tabela([['Tecla','Função'],['M','Monitor (imagem do banco 1)'],['A','Menu de bancos da flash'],['S','Shell do cartão SD (FAT): gravar bancos a partir de arquivos'],['U','Gravar banco pela serial (monta “FLASH n” e chama o gravador)'],['N','Autoload (como se o tempo tivesse esgotado)'],['T','Tetris']],[1,5],mono_cols=(0,))
callout('dica','Se uma gravação der errado, o banco 1 pode ficar inválido; o stub simplesmente pula para o próximo banco válido, ou você entra no menu de recuperação com <b>R</b> e regrava via serial (U) ou cartão SD (S). A placa não se perde.')
h2('5.3 Menu da imagem (banco 1)')
para('Ao ser iniciado pelo autoload, o monitor mostra o menu B/C/F/T/A/R/M (seção 2.3) e espera 5 segundos antes de ir ao prompt. As mesmas ações existem como comandos no prompt: <font name="Mono">B</font>, <font name="Mono">C</font>, <font name="Mono">BASIC</font>, <font name="Mono">CPM</font>, <font name="Mono">FORTH</font>, <font name="Mono">T</font>.')
h2('5.4 Voltar ao monitor')
bullets(['No <b>EhBASIC</b>: comando <font name="Mono">MONITOR</font> volta ao monitor do banco 1.',
 'No <b>eForth</b>: <font name="Mono">BYE</font>.',
 'No <b>CP/M</b> e no <b>Tetris</b>: Q (Tetris) ou reset da placa.',
 'Em qualquer caso, o reset (botão da placa) volta ao stub.'])

# ================= 6 =================
h1('6. O Monitor')
para('O monitor é o programa residente no banco 1. Ele é operado pela serial (57600 8N1). O prompt é <font name="Mono">&gt;</font>. Cada comando é uma letra (ou palavra) seguida de argumentos separados por espaço. Letras maiúsculas e minúsculas são equivalentes. Em qualquer listagem, <b>pressionar uma tecla interrompe</b> a saída.')
h2('6.1 Convenções')
bullets(['Números em <b>hexadecimal</b> sem prefixo. Na calculadora e no assemblador: <font name="Mono">$FF</font> hex, <font name="Mono">%1010</font> binário, <font name="Mono">#100</font> decimal (só na calculadora), <font name="Mono">\'A\'</font> caractere.',
 'Colchetes <font name="Mono">[ ]</font> indicam argumentos opcionais.',
 'Comandos que escrevem na memória só atuam na <b>RAM de usuário</b>: de $2000 até o fim da RAM detectada (comando I). ROM, vetores e pilha ficam protegidos.',
 'Se o segundo valor de um intervalo for menor ou igual ao primeiro, ele é tratado como <b>quantidade</b> (D, U).',
 'Nunca acesse $060000–$07FFFF (sem /DTACK).'])
h2('6.2 Resumo dos comandos')
cm=[('Comando','Função','Seção')]
for a,b,c in [('D','Dump hexadecimal + ASCII','6.3'),('P','Grava bytes','6.3'),('E','Edita memória byte a byte','6.3'),('F','Preenche faixa','6.3'),('M','Copia bloco','6.3'),('V','Compara blocos','6.3'),('S','Procura bytes','6.3'),('Z','Teste de RAM','6.3'),('Y','Checksum e CRC','6.3'),('Q','Mapa de memória','6.3'),('L','Carrega S-records','6.4'),('W','Despeja S-records','6.4'),('G','Executa programa (JSR)','6.4'),('U','Desassembla','6.5'),('A','Assembla','6.5'),('R','Registradores','6.6'),('N / O','Passo a passo','6.6'),('K','Breakpoints','6.6'),('X','Executa sob depurador','6.6'),('=','Calculadora','6.7'),('J','Monitor de entradas','9.4'),('ADC / ADL','A/D','9.1'),('DAC','D/A','9.2'),('RTC / RELOGIO','Relógio','9.3'),('BEEP','Buzzer','9.6'),('B / BASIC','EhBASIC','11.1'),('C / CPM','CP/M-68K','11.2'),('FORTH','eForth','11.3'),('T','Tetris','11.4'),('I','Informações da placa','6.8'),('FLASH','Gravador de bancos','7'),('?','Ajuda','6.8')]:
    cm.append((a,b,c))
tabela([list(x) for x in cm],[1.5,4,0.8],mono_cols=(0,))
h2('6.3 Memória')
para('Os comandos desta seção operam sobre o espaço de endereços. Os textos abaixo são a ajuda integrada de cada um.')
for k,t in [('H_D','D — dump'),('H_P','P — gravar bytes'),('H_E','E — editor'),('H_F','F — preencher'),('H_M','M — copiar'),('H_V','V — comparar'),('H_S','S — procurar'),('H_Z','Z — teste de RAM'),('H_Y','Y — checksum e CRC'),('H_Q','Q — mapa de memória')]:
    ajuda(k,t)
callout('aviso','<font name="Mono">Z</font> sem argumentos <b>apaga</b> toda a RAM de usuário e a RAM2. Não use se houver um programa carregado que você queira manter.')
h2('6.4 Programas')
for k,t in [('H_L','L — carregar S-records'),('H_W','W — despejar S-records'),('H_G','G — executar')]: ajuda(k,t)
para('O envio de arquivos S-record é feito pela ponte de bancada (<font name="Mono">ponte.bat</font> com arquivos <font name="Mono">#sendbin</font>/<font name="Mono">#raw</font>) ou pelo envio de arquivo de texto do seu terminal. Depois do <font name="Mono">L</font>, o ponto de entrada fica guardado para <font name="Mono">G</font> e <font name="Mono">X</font>.')
h2('6.5 Desassemblar e assemblar')
for k,t in [('H_U','U — desassemblador'),('H_A','A — assemblador'),('H_ASM','Sintaxe do assemblador')]: ajuda(k,t)
h2('6.6 Depuração')
for k,t in [('H_DEBUG','Roteiro de depuração'),('H_R','R — registradores'),('H_N','N e O — passo a passo'),('H_K','K — breakpoints'),('H_X','X — executar sob o depurador')]: ajuda(k,t)
callout('cuidado','Durante o <font name="Mono">X</font> o teclado não interrompe o programa. Programas com laço infinito precisam de um breakpoint ou de reset. Se o watchdog estiver ativo, chame <font name="Mono">jsr $F8082A</font> periodicamente.')
h2('6.7 Calculadora')
ajuda('H_CALC','= — calculadora')
h2('6.8 Informações e ajuda')
ajuda('H_LIST','Lista de comandos (? sem argumento)')
ajuda('H_SYS','? SISTEMA')
para('<font name="Mono">I</font> mostra as informações da placa (versão do monitor, tamanho da RAM detectada etc.). <font name="Mono">?</font> sem argumentos lista os comandos; <font name="Mono">? comando</font> mostra a ajuda detalhada (por exemplo <font name="Mono">? A</font>, <font name="Mono">? ASM</font>, <font name="Mono">? DEBUG</font>, <font name="Mono">? RTC</font>, <font name="Mono">? ADC</font>, <font name="Mono">? DAC</font>, <font name="Mono">? BASIC</font>).')
h2('6.9 Exemplo completo: assemblar, depurar e executar')
code('''> A 2000
002000> move.l #$1234,d0
002006> loop: addq.l #1,d0
002008> cmpi.l #$1240,d0
00200E> bne.s loop
002010> rts
002012> .
> U 2000 6
> K 2008
> X 2000                  (para no breakpoint; mostra registradores)
> N 3                     (3 instrucoes)
> R D0                    (mostra; R D0 0 zera)
> K -                     (tira breakpoints)
> G 2000                  (executa direto; volta com RTS)''','Sessão típica')

# ================= 7 =================
h1('7. Gravação de bancos (FLASH)')
para('O gravador roda na RAM (em $2000), pois a flash que ele apaga é a mesma de onde o monitor executa. Ele vale tanto para imagens vindas da <b>serial</b> quanto para <b>cópia entre bancos</b>. A ordem dos argumentos é sempre <b>origem → destino</b>.')
h2('7.1 Sintaxe')
tabela([['Comando','Efeito'],
 ['<font name="Mono">FLASH destino</font>','Grava no banco <i>destino</i> (0–7) uma imagem de 128 KB recebida pela serial'],
 ['<font name="Mono">FLASH origem destino</font>','Copia o banco <i>origem</i> (1–7) para o banco <i>destino</i> (0–7); origem ≠ destino'],
 ['<font name="Mono">F arquivo banco</font>','No shell SD: grava a imagem de 128 KB do cartão no banco 1–7 (banco 0 recusado)']],[2,4.5])
h2('7.2 Procedimento (imagem pela serial)')
bullets(['Digite <font name="Mono">FLASH n</font>. O gravador mostra os bancos e pergunta: <i>digite PROSSIGA (em maiúsculas); qualquer outra coisa = só comparar</i>.',
 'Responda <font name="Mono">PROSSIGA</font> para gravar, ou outra coisa para apenas <b>comparar</b> o banco com a imagem enviada.',
 'Envie a imagem de 128 KB (<font name="Mono">#sendbin arquivo 256</font> na ponte). O gravador apaga, programa e confere os setores.',
 'Ao terminar o gravador volta ao menu/monitor. <b>Não digite nada durante a gravação.</b>'])
callout('aviso','<b>Banco 0 (stub)</b>: só é gravado se você responder <font name="Mono">PROSSIGA0</font> (com zero no fim). Qualquer outra resposta apenas compara. Só regrave o banco 0 com uma imagem testada em emulador e com acesso físico para recuperação (programador externo).')
callout('dica','Antes de regravar um banco importante, copie-o para um banco livre: <font name="Mono">FLASH 1 2</font> copia o banco 1 (origem) para o banco 2 (destino).')
h2('7.3 Gravando a partir do cartão SD')
code('''> (menu de inicializacao) R           entra no shell FAT
FAT> D                              lista a pasta
FAT> F FORTH/forth_bank_v1.bin 5    grava o arquivo no banco 5
Gravar no banco? Digite PROSSIGA (apaga o banco!); outra coisa = so comparar:''','Exemplo no shell SD')
h2('7.4 Formato dos arquivos de imagem')
para('Imagens de banco têm exatamente 128 KB (131072 bytes) e cabeçalho AB em $F807C0 (seção 4.1). O arquivo <font name="Mono">.fl4</font> usado pela ponte é a mesma imagem empacotada com o CRC32 para conferência durante o envio.')

# ================= 8 =================
h1('8. Shell do cartão SD (FATSH)')
para('O shell FAT lê e grava cartões SD formatados em <b>FAT16</b> (testado com um volume de 970 MB e clusters de 16 KB). Ele é iniciado pela tecla <b>R</b> nos menus. O prompt é <font name="Mono">FAT&gt;</font>.')
tabela([['Comando','Função'],
 ['I','Inicia/monta o volume (mostra rótulo, tipo, tamanho e cluster)'],['D [pasta]','Lista a pasta'],['T arquivo','Mostra um arquivo de texto'],
 ['L arquivo endHex','Carrega o arquivo na memória, no endereço indicado'],['S','Mostra o espaço livre/ocupado'],
 ['W arquivo endHex lenHex','Grava um bloco de memória no arquivo (<font name="Mono">W caminho enderecoHex tamanhoHex</font>)'],
 ['K arquivo','Apaga o arquivo'],['C pasta','Muda a pasta atual'],['F arquivo banco','Grava a imagem de 128 KB (cabeçalho AB) no banco 1–7'],['?','Ajuda'],['Q','Sai do shell']],[2,4.5],mono_cols=(0,))
code('''FATSH v8 - FAT16 leitura/escrita + gravador de bancos - PARAGON 50
Comandos: I D T L S W K C F ? Q
FAT> I
Volume: TABAJARALAB  FAT16  970 MB, cluster 16 KB
FAT> F NADA.BIN 0
O banco 0 nao pode ser gravado por aqui.
FAT> F NADA.BIN
Uso: F arquivo banco(1-7)   (imagem de 128 KB com cabecalho AB)''','Exemplo real')
callout('nota','O shell recusa o banco 0 e valida o número do banco (1–7). Um arquivo não encontrado resulta em <i>Nao encontrado.</i>')
callout('dica','Para guardar dados de medição, use ADL (seção 9.1): ele grava um CSV na RAM2 e mostra o comando <font name="Mono">W ADL.CSV 40000 tamanho</font> para salvá-lo no cartão.')

# ================= 9 =================
h1('9. Periféricos')
h2('9.1 Conversor A/D (ADC, ADL)')
para('O AD7875 (12 bits, 8 canais multiplexados) vem do firmware original. O canal é escolhido pelos bits 14–12 de $020000+$20 (latch $020020); o disparo é um pulso no pino OP3 do DUART; o resultado é lido em $020000. Os 8 canais chegam nos pinos S1–S8 de J2 através de resistores de 1 kΩ (seção 10.2).')
ajuda('H_ADC','ADC e ADL')
callout('nota','A escala em mV supõe 0–5 V; ainda deve ser confirmada na bancada. O ADL grava um CSV em RAM2 ($040000), útil para registrar uma medição lenta.')
h2('9.2 Conversores D/A (DAC)')
ajuda('H_DAC','DAC')
callout('aviso','A saída analógica vai para o conector do laser/placa de potência. Use apenas osciloscópio ou multímetro; <b>não conecte carga</b>.')
h2('9.3 Relógio de tempo real (RTC, RELOGIO)')
para('Um módulo DS1307 (ou DS3231) é ligado ao barramento I²C emulado por dois bits do latch. O relógio aparece também na <b>linha 4 do LCD</b> (dd/mm/aa hh:mm) quando o monitor está parado no prompt.')
figura('img/i2c_rtc.png',150*mm,'Figura 5 — Ligação do módulo RTC DS1307 à placa.')
ajuda('H_RTC','RTC')
ajuda('H_REL','RELOGIO')
callout('dica','Se o chip aparece parado ou com valores impossíveis, o monitor mostra <b>ACERTAR RELOGIO</b>: use <font name="Mono">RTC SET aa mm dd hh mm ss</font>. Para o relógio manter a hora desligado, o módulo precisa de uma pilha CR2032 em bom estado.')
h2('9.4 Monitor de entradas (J)')
ajuda('H_J','J')
para('O comando J é a ferramenta usada para <i>descobrir</i> a que bit de entrada cada pino de J1/J2 corresponde — a tabela de pinagem do capítulo 10 foi levantada assim.')
h2('9.5 LCD, botões e cartão SD (J1)')
para('O RepRap Smart Controller é ligado em J1/J2. O LCD usa modo 4 bits pelos bits 3–8 do latch $020018; o buzzer, o bit 9; o cartão SD, os bits 0–2 (SPI por software) e as entradas da porta B.')
tabela([['Função','Sinal','Pino'],['LCD','E','J1-20'],['LCD','RS','J1-18'],['LCD','D4','J1-15'],['LCD','D5','J1-14'],['LCD','D6','J1-10'],['LCD','D7','J2-47'],
 ['SD','SCK','J1-28'],['SD','MOSI','J1-26'],['SD','CS','J1-24 (bit 2)'],['SD','MISO','J1-7'],['SD','SD_DET (detecção)','J1-27'],
 ['Botões do encoder','3 botões','J1-31, J1-33, J1-35'],['Buzzer','Saída $020018 bit 9','J2-40']],[1.5,2,2],mono_cols=(2,))
callout('nota','O D7 do LCD e o buzzer usam pinos de J2. Uma versão futura de hardware pode concentrar tudo em J1 (LCD com expansor PCF8574 por I²C, módulo SD e buzzer próprios).')
h2('9.6 Buzzer (BEEP)')
para('<font name="Mono">BEEP [n]</font> aciona o buzzer por n × 10 ms (padrão: um bip curto). O stub e o monitor também bipam em eventos (fim de gravação, erros).')

# ================= 10 =================
h1('10. Pinagem dos conectores')
para('As tabelas abaixo resultam de medições feitas na bancada com o comando <font name="Mono">J</font> e multímetro. “Entrada” significa bit lido pelos 74LS240 (invertido); “Saída” é bit do latch 74LS273 (não invertido) salvo indicação.')
def pintab(conn,titulo):
    d=PINS[conn]; rows=[['Pino','Função','Observação']]; sem=[]
    def key(k): return int(k)
    for k in sorted(d,key=key):
        f,o,_s,_x=d[k][0],d[k][1],None,None
        if f.startswith('nao conectado') or f.startswith('sem resposta') or f.startswith('so ruido'): sem.append(k+(' ('+f.split(' (')[0]+')' if False else '')); continue
        f=f.replace(' (coletor aberto, INVERTIDA)',' (col. aberto, invertida)')
        rows.append([k,f,d[k][1] if d[k][1] and d[k][1]!=f and not d[k][1].startswith('74LS') and 'pino' not in d[k][1] else ''])
    h2(titulo); tabela(rows,[0.7,3.8,3],mono_cols=(0,),); 
    if sem: para('Pinos sem função (não conectados ou sem resposta como entrada): <font name="Mono">%s</font>.'%', '.join(sem))
pintab('J1','10.1 Conector J1 (50 pinos)')
pintab('J2','10.2 Conector J2 (50 pinos)')
h2('10.3 Conector J4 (serial)')
tabela([['Pino','Sinal'],['1, 2, 12, 13','GND'],['3','RX (porta A)'],['5','TX (porta A)'],['7','CTS (porta A)'],['11','RTS (porta A)']],[1.5,4],mono_cols=(0,))
para('Parâmetros: 57600 bps, 8N1, sem controle de fluxo. Confira o nível elétrico (TTL ou RS-232) antes de ligar o conversor.')
h2('10.4 Alimentação e I²C')
tabela([['Sinal','Pino'],['+5 V','J7-19'],['GND','J1-9 (e demais GND de J1/J2)'],['SCL do RTC','J1-30'],['SDA do RTC (saída)','J1-48'],['SDA do RTC (leitura)','J1-23 (emendado com J1-48)']],[2,3],mono_cols=(1,))

# ================= 11 =================
h1('11. Aplicativos')
h2('11.1 EhBASIC')
para('EhBASIC 2.x de Lee Davison, adaptado ao 68000 e carregado do banco 7 em $F84000. Inicie por <font name="Mono">B</font> ou <font name="Mono">BASIC</font>; o driver SDFS (cartão SD) é copiado automaticamente para a RAM em $50000 antes de iniciar. Ao iniciar, pergunta <i>Memory size ?</i> (Enter usa toda a RAM).')
h3('Palavras-chave')
code('''END FOR NEXT DATA INPUT DIM READ LET DEC GOTO RUN IF RESTORE GOSUB RETURN REM STOP ON NULL INC
WAIT LOAD SAVE DEF POKE DOKE LOKE CALL DO LOOP PRINT CONT LIST CLEAR NEW WIDTH GET SWAP
BITSET BITCLR TAB( ELSE TO FN SPC( THEN NOT STEP UNTIL WHILE   AND EOR OR''','Comandos e instruções')
code('''SGN INT ABS USR FRE POS SQR RND LOG EXP COS SIN TAN ATN PEEK DEEP LEEK SADD LEN STR$ VAL ASC
UCASE$ LCASE$ CHR$ HEX$ BIN$ BITTST MAX MIN PI TWOPI VARPTR LEFT$ RIGHT$ MID$''','Funções')
h3('Extensões do PARAGON 50 (cartão SD)')
tabela([['Comando','Função'],['FILES','Lista o diretório do cartão'],['LOAD "arq"','Carrega um programa BASIC do cartão'],['SAVE "arq"','Grava o programa atual no cartão'],['KILL "arq"','Apaga um arquivo'],['CHDIR "pasta"','Muda de pasta'],['MONITOR','Volta ao monitor do banco 1']],[1.6,4.5],mono_cols=(0,))
code('''Memory size ? [Enter]
Ola, EhBASIC!
> 10 FOR I=1 TO 5 : PRINT I, SQR(I) : NEXT
> RUN
> FILES
> SAVE "TESTE.BAS"
> MONITOR''','Exemplo')
callout('nota','Se aparecer “driver sdfs nao carregado”, inicie o BASIC pelo comando <font name="Mono">B</font>/<font name="Mono">BASIC</font> do monitor (que instala o driver) e não por um salto direto ao banco 7.')
h2('11.2 CP/M-68K')
para('CP/M-68K com discos em arquivos no cartão SD. Inicie por <font name="Mono">C</font> ou <font name="Mono">CPM</font>. Sem cartão o sistema avisa <i>SD: sem cartao</i>.')
tabela([['Unidade','Origem'],['A:','\\CPM\\A.DSK (512 KB)'],['B:','\\CPM\\B.DSK (512 KB)'],['C:','\\CPM\\C.DSK (512 KB)'],['D:','\\CPM\\D.DSK (512 KB)'],['P:','Disco RAM de 124 KB']],[1,3],mono_cols=(0,1))
para('Comandos internos do CCP: <font name="Mono">DIR</font>, <font name="Mono">DIRS</font>, <font name="Mono">ERA</font>, <font name="Mono">REN</font>, <font name="Mono">TYPE</font>, <font name="Mono">USER</font>. Os demais programas são carregados dos discos (arquivos <font name="Mono">.68K</font>).')
h2('11.3 eForth')
para('eForth 68k v1.1 no banco 5. Inicie por <font name="Mono">F</font> (menu) ou <font name="Mono">FORTH</font> (o monitor confere o CRC32 do banco antes). Saia com <font name="Mono">BYE</font>.')
code('''SQ COLD 'BOOT hi VER WORDS SEE .ID >NAME ?CSP !CSP .S DUMP VARIABLE CREATE USER IMMEDIATE
: ; IF ELSE THEN BEGIN WHILE REPEAT UNTIL AGAIN FOR NEXT AFT RECURSE LITERAL ' QUIT ABORT"
THROW CATCH QUERY EXPECT WORD PARSE . U. U.R .R CR TYPE SPACES EMIT KEY NUMBER? DECIMAL HEX
<# # #S #> HOLD SIGN FILL CMOVE PICK DEPTH CELLS */ */MOD M* * UM* / MOD /MOD UM/MOD MIN MAX
ABS NEGATE DNEGATE + - 2DUP 2DROP ROT ?DUP @ ! C@ C! >R R> R@ SWAP DUP DROP OVER AND OR XOR
UM+ 0< BYE  ... e, no preludio: TO VALUE IS DEFER NOOP POSTPONE EVALUATE D+ D- D. UD. M+ ROLL
C, DOES> ...''','Palavras principais (WORDS mostra a lista completa)')
code('''> HEX 2000 20 DUMP
> : QUADRADO DUP * ;
> 7 QUADRADO .
49
> BYE''','Exemplo')
h2('11.4 Tetris')
para('Jogo de Tetris no LCD, inicia por <font name="Mono">T</font>. <b>Q</b> sai para o monitor.')

# ================= 12 =================
h1('12. Serviços fixos da ROM')
para('O monitor expõe rotinas em endereços <b>fixos</b> da ROM do banco 1, que programas de usuário (carregados com <font name="Mono">L</font> ou assemblados com <font name="Mono">A</font>) podem chamar com <font name="Mono">jsr</font>. Os endereços não mudam entre versões.')
tabela([['Endereço','Nome','Descrição'],
 ['$F80800','PUTC','Envia o caractere de D0 pela serial'],['$F80806','GETC','Espera e devolve um caractere em D0'],['$F8080C','PUTS','Escreve a string terminada em zero apontada por A1'],
 ['$F80812','HEXB','Escreve D0.B em hexadecimal'],['$F80818','HEXW','Escreve D0.W em hexadecimal'],['$F8081E','HEXL','Escreve D0.L em hexadecimal'],['$F80824','CRLF','Nova linha'],
 ['$F8082A','STROBE','Reinicia o watchdog (chame periodicamente)'],['$F80830','GETHEX','Lê um número hexadecimal digitado'],['$F80836','GETLINE','Lê uma linha em BUF ($0500)'],
 ['$F8083C','RESTART','Volta ao monitor'],['$F80900','RESET','Reinicia a placa'],
 ['$F80614 +0','LCD start','Inicializa o LCD'],['$F80614 +4','lcd_at','Posiciona o cursor do LCD'],['$F80614 +8','hold','Mantém a tela']],[1.3,1.1,4.1],mono_cols=(0,1))
code('''        org $2000
msg:    dc.b "Ola, mundo",13,10,0
        even
start:  lea msg(pc),a1
        jsr $F8080C        ; PUTS
        jsr $F80824        ; CRLF
        rts                ; volta ao monitor (G) ou ao depurador (X)''','Exemplo: programa mínimo (assemblar com A 2000, executar com G 2000)')
callout('nota','Rotinas do LCD ($F80614) têm convenções de registrador específicas; confira o código-fonte (<font name="Mono">monitor_v33.asm</font>) antes de usá-las em programas próprios.')

# ================= 13 =================
h1('13. Apêndices')
h2('13.1 Histórico de versões')
tabela([['Versão','Mudanças'],
 ['v2.3.1','Monitor original com ROM única e menu simples'],
 ['v2.5.1 / v2.7','Monitor ampliado: disassembler, assembler, depurador, calculadora, teste de RAM'],
 ['v3.0','Primeiro monitor com bancos e cabeçalho AB (guardado no banco 3 como backup)'],
 ['v3.1t8','Versão de teste do módulo de bancos (banco 4)'],
 ['v3.2s','<b>Stub do banco 0</b>: splash, espera de 5 s, tecla R, menu de recuperação, autoload, proteção PROSSIGA0'],
 ['v3.3 / v3.4','Monitor completo no banco 1; BASIC+CP/M+SD no banco 7 com driver SDFS embutido; ordem origem→destino nos comandos de cópia'],
 ['v3.4j','Comandos ADC, ADL, DAC, RTC, RELOGIO; relógio na linha 4 do LCD; BASIC/CPM/FORTH no prompt'],
 ['v3.5a','Retorno dos comandos B/C no prompt; banner “Monitor Paragon 50 - Tabajara Labs 2026”; versões unificadas; este manual']],[1.2,5.3],mono_cols=(0,))
h2('13.2 Problemas conhecidos e pendências')
bullets(['A ajuda <font name="Mono">? SISTEMA</font> ainda não lista o FORTH (o módulo estendido está 100% cheio; só cabem trocas de texto do mesmo tamanho).',
 'A lista de comandos (<font name="Mono">?</font>) ainda não cita RELOGIO, BASIC, CPM e FORTH (eles têm ajuda própria: <font name="Mono">? RELOGIO</font>, <font name="Mono">? BASIC</font>...).',
 'O banner do shell SD ainda diz “FATSH v8”.',
 'CP/M precisa de teste completo com cartão; EhBASIC (FILES, MONITOR) e eForth devem ser conferidos na placa.',
 'Menu de aplicativos: a tecla “0/M” reinicia a placa.',
 'RTC: pilha CR2032 do módulo esgotada; falta o teste de retenção da hora.',
 'Em uma ocasião o buzzer disparou sozinho; um reset resolveu. Causa desconhecida.',
 'Pendências de hardware: ordem de bits do 74LS273, REF OUT, AGND, loopback DAC→ADC, calibração do ADL.'])
h2('13.3 Solução de problemas')
tabela([['Sintoma','Causa provável / ação'],
 ['Nada aparece na serial','Confira 57600 8N1, RX/TX (J4 pinos 3 e 5) e GND; aperte reset.'],
 ['Prompt não responde à ponte','O monitor precisa estar no prompt “&gt;”; saia do shell SD (Q) ou do BASIC (MONITOR) antes de enviar arquivos.'],
 ['“driver sdfs nao carregado” no BASIC','Inicie com B/BASIC a partir do monitor; ele instala o driver.'],
 ['Banco novo não inicia','O CRC do cabeçalho AB está errado ou o banco está vazio; o autoload pula. Use R no boot e regrave.'],
 ['Placa “travada” durante o uso','Acesso a $060000–$07FFFF ou watchdog; aperte reset.'],
 ['Nada deve ser digitado durante a gravação','Espere o gravador terminar; interromper pode corromper o banco (o stub continua intacto).'],
 ['Hora do relógio errada','RTC SET aa mm dd hh mm ss; troque a pilha CR2032.']],[2.4,4.2])
h2('13.4 Créditos e licenças')
para('Projeto PARAGON 50 — Tabajara Labs. EhBASIC é de Lee Davison; CP/M-68K, de Digital Research (distribuído livremente); eForth segue a linhagem de C. H. Ting. Todo o firmware de sistema e as ferramentas de bancada deste projeto estão no repositório <font name="Mono">sbc-laser-paragon-50-diy</font>.')
para('<i>Este manual foi escrito para ser lido e editado: as fontes (<font name="Mono">manual_v4.py</font>, <font name="Mono">conteudo_v4.py</font> e os diagramas) acompanham o PDF.</i>')
