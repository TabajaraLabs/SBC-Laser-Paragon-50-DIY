# Laser Paragon 50 - SBC 68000 DIY

Placa CPU de um laser cirúrgico **PARAGON 50 (Heraeus Surgical)**, sucateado, reaproveitada como
**computador 68000 standalone**: monitor, BASIC, Forth, CP/M-68K, cartão SD, LCD e flash em bancos.

Projeto do **Tabajara Labs** (tabalabs.com.br). Tudo aqui foi feito por engenharia reversa da placa
e de um monte de teste de bancada. Os documentos estão em português.

## O que a placa tem

| Item | Detalhe |
|---|---|
| CPU | Motorola 68000 P10, clock de 8 MHz (módulo oscilador) |
| ROM | duas **Am29F040B** (HI e LO), 8 bancos de 128 KB em `$F80000-$F9FFFF`, registrador de banco 74LS175 em `$FC0000` |
| RAM | 128 KB em `$000000-$01FFFF` + RAM2 de 128 KB em `$040000-$05FFFF` |
| Serial | 68681 DUART em `$FA0000`, 57600 bps, console no canal A |
| Cartão SD | SPI por bit-bang no latch `$020018` (SCK, MOSI, CS) e porta `$020028` (MISO) |
| LCD | 20x4 HD44780 em 4 bits, pelo mesmo latch |
| Buzzer | ativo, bit 9 do latch |
| Outros | conversor A/D AD7875, DACs, conectores J1/J2/J7 com E/S do laser (ainda sendo mapeados) |

Mapa de endereços, pinagens e esquemas estão em [`docs/`](docs). O manual atual do banco 0 é `docs/MANUAL_PARAGON50_v3.0.txt`
(o `MONITOR_V2_MANUAL.txt` descreve o monitor v2.0 e ficou desatualizado nos itens de boot e bancos).

## Software

* **Banco 0 - BOOT+MONITOR (v3.0)**: o pré-bootloader, que quase nunca muda.
  Monitor v2.8 (disassembler/assembler, depurador), Tetris, menu de bancos com CRC32,
  gravador de flash e **recuperação pelo cartão SD** (tecla `R`).
* **Banco 1 - sistema**: EhBASIC 1.10 (com `LOAD`, `SAVE`, `FILES`, `KILL`, `CHDIR` no cartão)
  e **CP/M-68K** rodando de imagens `A.DSK`..`D.DSK` de 512 KB na pasta `\CPM` do cartão (FAT16),
  mais o disco RAM `P:`.
* **Banco 5 (exemplo)**: eForth 68000 1.1.
* Os bancos 0 a 7 têm cabeçalho "AB" (nome, versão, CRC32), estilo cartucho MSX.

Menu de boot (aguarda 5 s e cai no monitor):

```
[B]asic        (banco 1)
[C]P/M 68K     (banco 1)
[A]plicativos  (bancos da flash)
[R]ecuperacao  (cartao SD)
[M]onitor
[T]etris
```

### Gravador de flash

O gravador (`ferramentas/flash_v4/`) roda **só na RAM**, recebe a imagem inteira, **confere o CRC32 antes de
apagar** e só grava depois de digitar `PROSSIGA`. A imagem pode vir:

* pela serial (ponte do PC),
* de **outro banco** da própria flash (`FLASH destino origem`, comando COPIAR),
* de um arquivo de 128 KB no **cartão SD** (`F banco arquivo`, na tecla `R`).

O banco 0 só é gravado com uma confirmação extra. A versão atual é `flash_v5d` (aceita o banco 0 como origem de cópia,
usada para o backup do banco 0 no banco 3).

### Teste de E/S (J1, J2, J7)

`programas/iotest_v1.s19` (fonte `.asm` ao lado): carregue pelo monitor e rode `G 2000`. Escreve bit a bit nos latches
`$020018` e `$020020` e monitora as entradas, para mapear os pinos dos conectores. Detalhes no manual, item 6.

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `docs/` | esquemas, mapas de endereços, pinagens, manuais, listagens |
| `fontes/` | fontes do monitor, módulos e ROMs (versões 2.x) |
| `rom/` | imagens de ROM (`original/` = dumps originais do laser) |
| `ferramentas/` | gravador de flash, ponte serial e do osciloscópio, montadores e emuladores em Python |
| `programas/` | eForth, EhBASIC, CP/M-68K e programas de teste |
| `hardware/` | CPLD e hardware novo |

O histórico completo de mudanças da ROM está no `CHANGELOG_rom.txt` (em `rom/`).

## Estado

Funcionando na placa real: monitor, EhBASIC, CP/M-68K com cartão SD, eForth, LCD, buzzer,
gravação de bancos pela serial, por cópia entre bancos e pelo cartão SD.

Na lista: discos CP/M A-O, relógio DS1302 no barramento do SD, jig de teste de J1/J2/J7,
gabinete impresso em 3D, expansão de RAM e interposer com CPLD.

## Licenças e créditos

Este repositório reúne código próprio e material de terceiros, cada um sob a sua licença:
EhBASIC (Lee Davison), eForth (Bill Muench / C. H. Ting e portes), CP/M-68K (Digital Research /
Lineo, distribuição liberada pela Caldera), Am29F040B e demais datasheets são dos fabricantes.
Os dumps das ROMs do laser são publicados para preservação e manutenção.
Uma licença para o código original do projeto ainda será escolhida.
