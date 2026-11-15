import re
s=open('conteudo_livro_v1.py',encoding='utf-8').read()
def antes(prefixo,bloco):
    global s
    i=s.index(prefixo); s=s[:i]+bloco.strip('\n')+'\n'+s[i:]
# ---- Cap 1
antes("licao('guarde sempre uma cópia", '''
figura('img/foto_nvram.jpg',150*mm,'Figura 2 — Detalhe: as duas NVRAMs Dallas DS1230Y (SRAM de 32 KB com bateria) e a ROM. As NVRAMs guardavam a configuração do laser; o conteúdo foi lido e arquivado antes de qualquer experiência.')
figura('img/foto_traseira.jpg',110*mm,'Figura 3 — A face de solda: placa de quatro camadas, com trilhas finas. Foi a partir dela (e das medições) que o esquema foi reconstruído.')
saber('Quem foi o Heraeus PARAGON 50?','Era um laser médico, de uso cirúrgico, controlado por uma placa CPU com um microprocessador de 16/32 bits — o 68000 era uma escolha comum nos anos 80/90 para equipamentos que precisavam de potência de “minicomputador” a custo moderado. Depois de declarado obsoleto, o aparelho foi desmontado e a placa foi salva. Aqui ela não volta ao laser: nada nela comanda mais qualquer carga.')
esp('O 68000 em poucas linhas','Dados de 16 bits, endereços de 24 bits (16 MB), 8 registradores de dados (D0–D7) e 8 de endereço (A0–A7, com A7 como pilha; USP e SSP separadas). Dois modos: usuário e supervisor. A tabela de <b>vetores</b> começa em $000000: o primeiro longword é o SSP inicial e o segundo o PC inicial — por isso, depois do reset, o 68000 lê os 8 primeiros bytes do espaço de endereços para saber por onde começar. Na placa, a ROM aparece em $000000 só durante o reset (um ciclo de “shadow”) e depois vai para $F80000; é essa gambiarra clássica que o stub explora ao copiar vetores para a RAM.')
''')
# ---- Cap 2
antes("licao('padronizar cedo", '''
figura('img/foto_duart.jpg',150*mm,'Figura 4 — A região do 68681 (à direita), do cristal de 3,6864 MHz e da CPU. A serial A sai pelo conector J4.')
figura('img/c_decod.png',160*mm,'Figura 5 — Decodificação de endereços, simplificada: lógica discreta divide os 16 MB entre ROM, DUART, registrador de banco, E/S e RAM.')
saber('O que é /DTACK?','No 68000, toda leitura ou escrita termina quando o periférico responde com um sinal chamado <b>/DTACK</b> (“data transfer acknowledge”). Se ninguém responde, o processador fica esperando para sempre — ou até um circuito de watchdog gerar um erro de barramento. Na placa, o /DTACK é gerado por uma porta 74LS11 (U35) e, em geral, cada ciclo leva uns quatro estados de espera. A faixa $060000–$07FFFF não tem ninguém que gere /DTACK: acessá-la trava a CPU. Por isso aparece sempre com o aviso “nunca acessar”.')
esp('Folha de esquema reconstruída por medição','A figura abaixo é a folha 1 do esquema reconstruído (CPU, clock e reset): módulo oscilador de 8 MHz, DS1232 (reset + watchdog; o watchdog está desabilitado, JP6 não instalado), e cada pino da CPU anotado com “rede > destino.pino”. Verde = medido; azul = inferido do datasheet; vermelho = a rastrear. O /DTACK vem do U35 e <b>não depende do R/W</b>: escritas na região da ROM terminam normalmente, o que é o que permite gravar a flash em circuito sem mexer na geração do /DTACK.')
figura('img/esq_folha1.png',170*mm,'Figura 6 — Folha 1/6 do esquema reconstruído: CPU, clock e reset.')
''')
# ---- Cap 3
antes("licao('um emulador bom", '''
saber('Monitor, BASIC, CP/M: qual a diferença?','O <b>monitor</b> é o programa mais básico: deixa você ver e mudar a memória, carregar e rodar programas. O <b>BASIC</b> é uma linguagem interpretada, boa para experimentar. O <b>CP/M</b> é um sistema operacional completo, com arquivos, discos e programas em disco. O Paragon tem os três, e o monitor serve de “porta de entrada” para os outros.')
esp('O formato S-record e o ponto de entrada','Programas são enviados em <b>S-records</b> (S1/S2/S3 para dados com 16/24/32 bits de endereço; S7/S8/S9 para o ponto de entrada) com checksum por linha. O comando <font name="Mono">L</font> carrega os registros, guarda o ponto de entrada e informa “OK registros=… entrada=… início=… tamanho=…”. <font name="Mono">G</font> executa com JSR (o programa volta com RTS) e <font name="Mono">X</font> executa sob o depurador, trocando a instrução do breakpoint por ILLEGAL e restaurando-a ao parar.')
''')
# ---- Cap 4
antes("licao('quando uma modificação", '''
saber('Por que adaptadores 28→32?','As SRAMs KM681000 têm 32 pinos (128 K × 8), mas os soquetes da placa são de 28 pinos. O adaptador é uma plaquinha com um soquete de 28 pinos embaixo e um de 32 em cima; os pinos extras (A15, A16 e outros) saem por fios para onde a placa decide. Alexandre os montou à mão e em cada um levantou os pinos 32, 31, 30, 1 e 2 para religá-los por fio.')
esp('As mudanças de decodificação','Para dar à RAM2 o seu bloco de 128 KB em $040000, foi preciso alterar as ligações do decodificador U4 (74LS138): a saída Y6 foi para o pino 9 do U4, e o pino 2 do U5 (74LS11) — que antes recebia essa saída — foi levantado e preso em +5 V. A primeira tentativa, que mexia nas linhas A17/A18 e “C” das SRAMs, deixou a serial muda; o estado original foi restaurado e a modificação refeita por etapas.')
''')
# ---- Cap 5
antes("licao('quando o hardware não tem", '''
figura('img/c_rrd.png',150*mm,'Figura 7 — As 12 ligações entre J1/J2 e a placa RepRapDiscount (EXP1 e EXP2), mais GND comum e +5 V externo.')
figura('img/c_latches.png',165*mm,'Figura 8 — Mapa de bits dos dois latches de saída: quem controla o quê.')
figura('img/c_spi.png',150*mm,'Figura 9 — Um byte pelo SPI (modo 0): o 68000 mexe nos bits do latch para gerar SCK e MOSI, e lê o MISO pela porta de entrada.')
saber('O que é FAT16?','É o sistema de arquivos que organiza um cartão SD: uma <i>tabela de alocação</i> (FAT) diz, para cada <i>cluster</i> do disco, qual é o próximo; os diretórios guardam nome, tamanho e o primeiro cluster de cada arquivo. O FAT16 é mais simples que o FAT32 e é o que o cartão de teste usa (970 MB, clusters de 16 KB).')
esp('Detalhes do SPI por software e do cartão','O cartão trabalha a 3,3 V; a placa RepRap já traz um conversor de nível 4050 — as saídas de ~4,3 V do Paragon entram direto, e o MISO volta em 3,3 V, que o 74LS240 aceita (VIH = 2 V). O 74LS240 <b>inverte</b>, então o driver lê o MISO invertido. A inicialização segue o protocolo SD padrão (CMD0, CMD8, ACMD41 até sair de “idle”, CMD58 para detectar SDHC), com pulsos de “strobe” do watchdog durante as esperas longas. Como cada transição é uma escrita no latch ($020018), a velocidade é de dezenas de kbit/s: suficiente para BASIC e CP/M, lenta para arquivos grandes.')
''')
# ---- Cap 6
antes("licao('hardware de gravação em circuito", '''
figura('img/c_banco175.png',165*mm,'Figura 10 — O registrador de banco: um 74LS175 clockado por (Y2 do U4) OU R/W; suas três saídas viram os bits A16, A17 e A18 das duas flashes.')
figura('img/c_escrita_we.png',160*mm,'Figura 11 — O circuito de escrita em circuito: um 74LS32 gera um /WE para cada flash (HI e LO). Os jumpers ficam abertos no uso normal.')
figura('img/c_tempo_we.png',150*mm,'Figura 12 — Temporização da escrita: /WE só cai quando R/W, ROM_CE e /UDS estão baixos.')
figura('img/c_gravador.png',160*mm,'Figura 13 — O fluxo do gravador de flash: confere, pergunta, grava, volta.')
saber('O que é memória flash?','Uma memória que mantém o conteúdo sem energia, como uma EPROM, mas que se apaga e regrava <i>eletricamente</i> e em pedaços (setores). A Am29F040B guarda 512 KB em 8 setores de 64 KB; para gravar, é preciso mandar uma sequência de comandos por escrita — e, como a flash não pode ser lida durante o apagamento, o programa que grava precisa estar na RAM.')
esp('Sequência de comandos e temporização','Os comandos seguem o padrão AMD/JEDEC: <font name="Mono">$AA</font> em <font name="Mono">$555</font>, <font name="Mono">$55</font> em <font name="Mono">$2AA</font> e então o comando (ID: <font name="Mono">$90</font>; programação: <font name="Mono">$A0</font>; apagar setor: <font name="Mono">$80</font> + <font name="Mono">$30</font>); a conclusão é detectada por <i>polling</i> de DQ7. Como o 68000 grava palavras, o mesmo comando vai nas duas flashes (por exemplo <font name="Mono">$AAAA</font>). Cada ciclo da placa dura ~1 µs (4 estados de espera), então o pulso de /WE fica em centenas de ns — muito acima dos poucos dezenas de ns exigidos. Os endereços do 68000 passam por inversores de A13–A15 do U26 antes de chegar à flash, e a leitura do ID (<font name="Mono">$01</font>/<font name="Mono">$A4</font>) confirmou o mapeamento antes de qualquer apagamento. No registrador de banco, o clock é “Y2 OU R/W”: sobe no fim da escrita em <font name="Mono">$FC0000</font>; leituras não o disparam. Escrever em <font name="Mono">$FC0000</font> por byte alto também clocka com D0–D2 sem sentido, por isso se usa palavra (<font name="Mono">move.w</font>) ou byte em <font name="Mono">$FC0001</font>.')
''')
# ---- Cap 7 expert
antes("callout('nota','O incidente do banco 0 deixou", '''
esp('O erro do A18 em detalhe','No 74LS175 as saídas Q e /Q ficam em pinos vizinhos (3Q = pino 10, 3Q̅ = pino 11). O fio de A18 foi ligado ao 3Q̅ — a saída invertida —, o que faz o banco lógico N aparecer como o físico N XOR 4. Na prática, o “banco 0” em que o reset caía era o físico 4, e a imagem gravada ali (com um byte 0D extra no início, ruído da transferência) não tinha vetores válidos. A medição com osciloscópio mostrou o A18 baixo nos bancos 0–3 e alto nos 4–7 <i>invertido</i>; corrigido o fio, tudo bateu.')
''')
# ---- Cap 8
antes("licao('um bom bootloader", '''
figura('img/c_trampolim.png',160*mm,'Figura 14 — Como o monitor inicia o BASIC (banco 7): uma rotina copiada para a RAM troca o banco e salta.')
saber('Stub, bootloader, autoload: o que cada palavra quer dizer','<b>Bootloader</b> é qualquer programa que carrega outro. <b>Stub</b> é um bootloader mínimo, quase sem funções. <b>Autoload</b> é a decisão automática: sem intervenção do usuário, carrega o primeiro programa válido que encontrar. Os três juntos formam o desenho do banco 0.')
esp('Algoritmo do autoload e do CRC','Para cada banco n de 1 a 7: (1) escreve n em $FC0000, a partir de código na RAM; (2) confere a assinatura “AB” e os campos início/fim do cabeçalho em $F807C0; (3) calcula o CRC32 sobre [início..$F807BF] e [$F80800..fim] — o cabeçalho de 64 bytes (que contém o próprio CRC) fica de fora; (4) se tudo bate, copia os vetores do banco para a RAM e salta para a entrada (tipo 0: SP/PC dos vetores; tipo 1: entrada do cabeçalho, SP = $1F00). Banco vazio (todo $FF) ou com CRC errado é pulado (<font name="Mono">au_nx</font>); se nenhum for válido, cai no menu de recuperação. Antes disso, o stub aguarda 5 s por R, usando o timer do DUART. O <i>strobe</i> do watchdog é dado durante o cálculo, e foi justamente um erro nisso que fazia o CRC só ler um bloco de 4 KB no hardware (capítulo 7).')
''')
# ---- Cap 9
antes("licao('quando a realidade", '''
figura('img/c_adc.png',160*mm,'Figura 15 — A cadeia do conversor A/D: oito entradas em J2, multiplexador, AD7875 e leitura em $020000.')
figura('img/c_i2c.png',150*mm,'Figura 16 — Um quadro I²C (endereço do DS1307 = $68) gerado por bit-bang: SCL e SDA são bits do latch $020020.')
saber('O que é I²C?','Um barramento de dois fios (SCL = relógio, SDA = dados) em que um “mestre” fala com vários “escravos” identificados por endereço. Os fios são de <i>coletor aberto</i>: ninguém empurra o nível alto, só puxa para baixo; resistores de pull-up (já no módulo) levam a linha para cima. Por isso, no latch, “1” significa “puxar para baixo”.')
esp('Leitura do SDA e temporização do bit-bang','A saída SDA do latch (J1-48) e a entrada de leitura (J1-23, porta B bit 6) são emendadas por fora para o mesmo nó do módulo, o que permite ler o ACK do escravo sem trocar a direção de um pino. A temporização é por laços de espera calibrados (o mesmo laço usado em RELOGIO CAL: ~0,24 ms por 100 voltas/…); o I²C do DS1307 tolera velocidades até 100 kHz, bem acima do que o bit-bang entrega — nada precisa ser rápido. Como a leitura é feita no laço ocioso do monitor, a hora no LCD é lida só quando o minuto pode ter mudado (registrador 0x01).')
''')
# ---- Cap 12 figs
antes("h2('Próximos passos')", '''
figura('img/previa_gabinete_v2_explodida.png',130*mm,'Figura 17 — Gabinete v2 em cunha, vista explodida: base, moldura da tampa e a placa.')
figura('img/planta_medidas_v1.png',150*mm,'Figura 18 — Planta de medidas lidas nas fotos: a placa mede 274 mm de largura; J1 e J2 ficam na frente.')
figura('img/perfil_gabinete_v2_vs_croqui.png',140*mm,'Figura 19 — Perfil lateral do gabinete v2 (azul) comparado com o croqui inicial (vermelho tracejado).')
saber('Por que uma cunha?','Teclados e computadores de bancada em cunha deixam o painel superior inclinado para o usuário, e a parte de trás mais alta acomoda conectores e componentes altos. É o desenho clássico de micros como o TEC-1 e muitos kits. O Altair, por outro lado, tem um painel vertical na frente (cheio de chaves e LEDs) e um corpo retangular: o desenho do painel é o que dá a “cara” do micro.')
''')
s=s.replace("o gabinete v2 mede cerca de 292 × 155 mm por fora","a placa mede 274 × 144,8 mm e o gabinete v2 em cunha mede cerca de 292 × 155 mm por fora, com 33 mm de altura na frente e 73,5 mm atrás")
s=s.replace("'Figura 1 — A placa CPU","'Figura 1 — A placa CPU")
open('conteudo_livro_v1.py','w',encoding='utf-8').write(s)
print('ok')
