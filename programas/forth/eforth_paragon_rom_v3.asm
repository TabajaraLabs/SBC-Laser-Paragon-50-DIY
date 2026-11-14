        TTL eFORTH
        OPT p=68000
VER equ 1
EXT equ 1
TRUEE equ $FFFFFFFF
COMPO equ $040
COMPOL equ $40000000
IMEDD equ $080
IMEDDL equ $80000000
MASKK equ $1F7F7F7F
ALGNUM equ 3
CELLL equ 4
BASEE equ 10
VOCSS equ 8
BKSPP equ 8
LF equ 10
CRR equ 13
ERR equ 27
TIC equ 39
charS equ 36
char_ equ 95
chminus equ 45
char0 equ 48
charq equ 34
chblnk equ 32
charbr equ 41
CALLL equ $4E714EB9
EM equ $00020000
US equ 64*CELLL
RTS equ 64*CELLL
SPS equ 64*CELLL
RPP equ EM
SPP equ EM-RTS
TIBB equ SPP
NAMEE equ SPP-(US+SPS)
UPP equ NAMEE
COLDD equ $00000100
COLD68 equ $00004000
CODEE equ COLD68+US
LINK_ set 0
NAME_ set NAMEE
CODE_ set CODEE
USER_ set 4*CELLL
        ORG COLD68
ORIG:
        MOVE.L SP,$3F00
        MOVE.W #$2700,SR
        LEA.L SPP,SP
        LEA.L RPP,A6
        LEA.L COLD1,A5
        MOVEA.L (A5)+,A0
        JMP (A0)
        DS.L 0
UZERO:
        dcb.l 4,0
        dc.l SPP
        dc.l RPP
        dc.l QRX
        dc.l TXSTO
        dc.l ACCEP
        dc.l KTAP
        dc.l TXSTO
        dc.l DOTOK
        dc.l BASEE
        dc.l 0
        dc.l 0
        dc.l 0
        dc.l 0
        dc.l TIBB
        dc.l 0
        dc.l INTER
        dc.l NUMBQ
        dc.l 0
        dc.l 0
        dc.l 0
        dcb.l VOCSS,0
        dc.l 0
        dc.l 0
        dc.l CTOP
        dc.l NTOP
        dc.l LASTN
ULAST:
        ORG CODEE
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BYE:
        MOVE.W #$2700,SR
        MOVE.W #0,$FC0000
        MOVEA.L $F80000,SP
        MOVEA.L $F80004,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QRX:
        CLR.L D1
        CLR.L D0
        BTST #0,$FA0003
        BEQ.B QRX1
        MOVE.B $FA0007,D0
        AND.B #$7F,D0
        MOVEQ.L #TRUEE,D1
        MOVE.L D0,-(SP)
QRX1:
        MOVE.L D1,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TXSTO:
        MOVE.L (SP)+,D0
TXSTO2:
        BTST #2,$FA0003
        BEQ TXSTO2
        MOVE.B D0,$FA0007
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STOIO:
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOLIT:
        MOVE.L (A5)+,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOLST:
        MOVE.L A5,-(A6)
        MOVEA.L (SP)+,A5
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DONXT:
        SUBQ.L #1,(A6)
        BMI.s DONXT1
        MOVEA.L (A5),A5
        MOVEA.L (A5)+,A0
        JMP (A0)
DONXT1:
        LEA.L 4(A6),A6
        LEA.L 4(A5),A5
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QBRAN:
        MOVE.L (SP)+,D0
        OR.L D0,D0
        BNE.s QBRAN1
        MOVEA.L (A5),A5
        MOVEA.L (A5)+,A0
        JMP (A0)
QBRAN1:
        LEA.L 4(A5),A5
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BRAN:
        MOVEA.L (A5),A5
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EXECU:
        MOVEA.L (SP)+,A0
        JMP (A0)
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EXIT:
        MOVEA.L (A6)+,A5
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STORE:
        MOVEA.L (SP)+,A0
        MOVE.L (SP)+,(A0)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
AT:
        MOVEA.L (SP)+,A0
        MOVE.L (A0),-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CSTOR:
        MOVEA.L (SP)+,A0
        MOVE.L (SP)+,D0
        MOVE.B D0,(A0)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CAT:
        MOVEA.L (SP)+,A0
        CLR.L D0
        MOVE.B (A0),D0
        MOVE.L D0,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RPAT:
        MOVE.L A6,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RPSTO:
        MOVEA.L (SP)+,A6
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RFROM:
        MOVE.L (A6)+,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RAT:
        MOVE.L (A6),-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TOR:
        MOVE.L (SP)+,-(A6)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SPAT:
        MOVE.L A7,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SPSTO:
        MOVE.L (SP)+,A7
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DROP:
        LEA.L 4(SP),SP
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DUPP:
        MOVE.L (SP),-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SWAP:
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
        MOVE.L D0,-(SP)
        MOVE.L D1,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
OVER:
        MOVE.L 4(SP),-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ZLESS:
        MOVE.L (SP)+,D0
        MOVE.L #31,D1
        ASR.L D1,D0
        MOVE.L D0,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ANDD:
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
        AND.L D1,D0
        MOVE.L D0,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ORR:
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
        OR.L D1,D0
        MOVE.L D0,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
XORR:
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
        EOR.L D1,D0
        MOVE.L D0,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UPLUS:
        CLR.L D2
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
        ADD.L D1,D0
        ROXL.L #1,D2
        MOVE.L D0,-(SP)
        MOVE.L D2,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOVAR:
        bsr DOLST
        dc.l RFROM,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UP:
        bsr DOLST
        dc.l DOVAR
        dc.l UPP
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOUSE:
        bsr DOLST
        dc.l RFROM,AT,UP,AT,PLUS,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SZERO:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RZERO:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TQKEY:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TEMIT:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TEXPE:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TTAP:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TECHO:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TPROM:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BASE:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TEMP:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SPAN:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
INN:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NTIB:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
USER_ set USER_+CELLL
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CSP:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TEVAL:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TNUMB:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HLD:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HANDL:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CNTXT:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
USER_ set USER_+VOCSS*CELLL
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CRRNT:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
USER_ set USER_+CELLL
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CP:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NP:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
LAST:
        bsr DOLST
        dc.l DOUSE,USER_
USER_ set USER_+CELLL
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOVOC:
        bsr DOLST
        dc.l RFROM,CNTXT,STORE,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
FORTH:
        bsr DOLST
        dc.l DOVOC
        dc.l 0
        dc.l 0
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QDUP:
        bsr DOLST
        dc.l DUPP
        dc.l QBRAN,QDUP1
        dc.l DUPP
QDUP1:
        dc.l EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ROT:
        bsr DOLST
        dc.l TOR,SWAP,RFROM,SWAP,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DDROP:
        bsr DOLST
        dc.l DROP,DROP,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DDUP:
        bsr DOLST
        dc.l OVER,OVER,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PLUS:
        bsr DOLST
        dc.l UPLUS,DROP,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
INVER:
        bsr DOLST
        dc.l DOLIT,$ffffffff,XORR,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NEGAT:
        bsr DOLST
        dc.l INVER,DOLIT,1,PLUS,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DNEGA:
        bsr DOLST
        dc.l INVER,TOR,INVER
        dc.l DOLIT,1,UPLUS
        dc.l RFROM,PLUS,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SUBB:
        bsr DOLST
        dc.l NEGAT,PLUS,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ABSS:
        bsr DOLST
        dc.l DUPP,ZLESS
        dc.l QBRAN,ABS1
        dc.l NEGAT
ABS1:
        dc.l EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EQUAL:
        bsr DOLST
        dc.l XORR
        dc.l QBRAN,EQU1
        dc.l DOLIT,0,EXIT
EQU1:
        dc.l DOLIT,TRUEE,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ULESS:
        bsr DOLST
        dc.l DDUP,XORR,ZLESS
        dc.l QBRAN,ULES1
        dc.l SWAP,DROP,ZLESS,EXIT
ULES1:
        dc.l SUBB,ZLESS,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
LESS:
        bsr DOLST
        dc.l DDUP,XORR,ZLESS
        dc.l QBRAN,LESS1
        dc.l DROP,ZLESS,EXIT
LESS1:
        dc.l SUBB,ZLESS,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
MAX:
        bsr DOLST
        dc.l DDUP,LESS
        dc.l QBRAN,MAX1
        dc.l SWAP
MAX1:
        dc.l DROP,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
MIN:
        bsr DOLST
        dc.l DDUP,SWAP,LESS
        dc.l QBRAN,MIN1
        dc.l SWAP
MIN1:
        dc.l DROP,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
WITHI:
        bsr DOLST
        dc.l OVER,SUBB,TOR
        dc.l SUBB,RFROM,ULESS,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UMMOD:
        MOVE.L (SP)+,D2
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
divuql:
        move.L d2,d3
        swap d3
        tst.w d3
        beq.s qdivuql
        moveq.L #31,d3
divql:
        lsl.L #1,d1
        roxl.L #1,d0
        cmp.L d2,d0
        bcs.s divql1
        sub.L d2,d0
        addq.b #1,d1
divql1:
        dbra d3,divql
        MOVE.L D0,-(SP)
        MOVE.L D1,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
qdivuql:
        swap d0
        swap d1
        move.w d1,d0
        divu d2,d0
        move.w d0,d1
        swap d1
        move.w d1,d0
        divu d2,d0
        move.w d0,d1
        clr.w d0
        swap d0
        MOVE.L D0,-(SP)
        MOVE.L D1,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
MSMOD:
        bsr DOLST
        dc.l DUPP,ZLESS,DUPP,TOR
        dc.l QBRAN,MMOD1
        dc.l NEGAT,TOR,DNEGA,RFROM
MMOD1:
        dc.l TOR,DUPP,ZLESS
        dc.l QBRAN,MMOD2
        dc.l RAT,PLUS
MMOD2:
        dc.l RFROM,UMMOD,RFROM
        dc.l QBRAN,MMOD3
        dc.l SWAP,NEGAT,SWAP
MMOD3:
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SLMOD:
        bsr DOLST
        dc.l OVER,ZLESS,SWAP,MSMOD,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
MODD:
        bsr DOLST
        dc.l SLMOD,DROP,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SLASH:
        bsr DOLST
        dc.l SLMOD,SWAP,DROP,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UMSTA:
        MOVE.L (SP)+,D0
        MOVE.L (SP)+,D1
        MOVE.W D0,D2
        MOVE.W D1,D3
        MULU D3,D2
        SWAP D0
        MOVE.W D0,D4
        MULU D3,D4
        SWAP D1
        MOVE.W D1,D5
        MOVE.W D0,D3
        MULU D5,D3
        SWAP D0
        MULU D0,D5
        MOVE.L D4,D6
        SWAP D6
        MOVE.W #0,D6
        ADD.L D6,D2
        MOVE.L D4,D6
        MOVE.W #0,D6
        SWAP D6
        ADDX.L D6,D3
        MOVE.L D5,D6
        SWAP D6
        MOVE.W #0,D6
        ADD.L D6,D2
        MOVE.L D5,D6
        MOVE.W #0,D6
        SWAP D6
        ADDX.L D6,D3
        MOVE.L D2,-(SP)
        MOVE.L D3,-(SP)
        MOVEA.L (A5)+,A0
        JMP (A0)
        dcb.b $24,0
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STAR:
        bsr DOLST
        dc.l UMSTA,DROP,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
MSTAR:
        bsr DOLST
        dc.l DDUP,XORR,ZLESS,TOR
        dc.l ABSS,SWAP,ABSS,UMSTA
        dc.l RFROM
        dc.l QBRAN,MSTA1
        dc.l DNEGA
MSTA1:
        dc.l EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SSMOD:
        bsr DOLST
        dc.l TOR,MSTAR,RFROM,MSMOD,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STASL:
        bsr DOLST
        dc.l SSMOD,SWAP,DROP,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CELLP:
        bsr DOLST
        dc.l DOLIT,CELLL,PLUS,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CELLM:
        bsr DOLST
        dc.l DOLIT
        dc.l 0-CELLL
        dc.l PLUS,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CELLS:
        bsr DOLST
        dc.l DOLIT,CELLL,STAR,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ALGND:
        move.L (sp)+,d0
        add.L #3,d0
        and.L #$fffffffc,d0
        move.L d0,-(sp)
        MOVEA.L (A5)+,A0
        JMP (A0)
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BLANK:
        bsr DOLST
        dc.l DOLIT,chblnk,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TCHAR:
        bsr DOLST
        dc.l DOLIT,$07F,ANDD,DUPP
        dc.l DOLIT,127,BLANK,WITHI
        dc.l QBRAN,TCHA1
        dc.l DROP,DOLIT,char_
TCHA1:
        dc.l EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DEPTH:
        bsr DOLST
        dc.l SPAT,SZERO,AT,SWAP,SUBB
        dc.l DOLIT,CELLL,SLASH,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PICK:
        bsr DOLST
        dc.l DOLIT,1,PLUS,CELLS
        dc.l SPAT,PLUS,AT,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PSTOR:
        bsr DOLST
        dc.l SWAP,OVER,AT,PLUS
        dc.l SWAP,STORE,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DSTOR:
        bsr DOLST
        dc.l SWAP,OVER,STORE
        dc.l CELLP,STORE,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DAT:
        bsr DOLST
        dc.l DUPP,CELLP,AT
        dc.l SWAP,AT,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
COUNT:
        bsr DOLST
        dc.l DUPP,DOLIT,1,PLUS
        dc.l SWAP,CAT,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HERE:
        bsr DOLST
        dc.l CP,AT,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PAD:
        bsr DOLST
        dc.l HERE,DOLIT,80,PLUS,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TIB:
        bsr DOLST
        dc.l NTIB,CELLP,AT,EXIT
LEN_ set (8&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ATEXE:
        bsr DOLST
        dc.l AT,QDUP
        dc.l QBRAN,EXE1
        dc.l EXECU
EXE1:
        dc.l EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CMOVE:
        bsr DOLST
        dc.l TOR
        dc.l BRAN,CMOV2
CMOV1:
        dc.l TOR,DUPP,CAT
        dc.l RAT,CSTOR
        dc.l DOLIT,1,PLUS
        dc.l RFROM,DOLIT,1,PLUS
CMOV2:
        dc.l DONXT,CMOV1
        dc.l DDROP,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
FILL:
        bsr DOLST
        dc.l SWAP,TOR,SWAP
        dc.l BRAN,FILL2
FILL1:
        dc.l DDUP,CSTOR,DOLIT,1,PLUS
FILL2:
        dc.l DONXT,FILL1
        dc.l DDROP,EXIT
LEN_ set (9&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DTRAI:
        bsr DOLST
        dc.l TOR
        dc.l BRAN,DTRA2
DTRA1:
        dc.l BLANK,OVER,RAT,PLUS,CAT,LESS
        dc.l QBRAN,DTRA2
        dc.l RFROM,DOLIT,1,PLUS,EXIT
DTRA2:
        dc.l DONXT,DTRA1
        dc.l DOLIT,0,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PACKS:
        bsr DOLST
        dc.l ALGND,DUPP,TOR
        dc.l OVER,DUPP,DOLIT,0
        dc.l DOLIT,CELLL,UMMOD,DROP
        dc.l SUBB,OVER,PLUS
        dc.l DOLIT,0,SWAP,STORE
        dc.l DDUP,CSTOR,DOLIT,1,PLUS
        dc.l SWAP,CMOVE,RFROM,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DIGIT:
        bsr DOLST
        dc.l DOLIT,9,OVER,LESS
        dc.l DOLIT,7,ANDD,PLUS
        dc.l DOLIT,char0,PLUS,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EXTRC:
        bsr DOLST
        dc.l DOLIT,0,SWAP,UMMOD
        dc.l SWAP,DIGIT,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BDIGS:
        bsr DOLST
        dc.l PAD,HLD,STORE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HOLD:
        bsr DOLST
        dc.l HLD,AT,DOLIT,1,SUBB
        dc.l DUPP,HLD,STORE,CSTOR,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DIG:
        bsr DOLST
        dc.l BASE,AT,EXTRC,HOLD,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DIGS:
        bsr DOLST
DIGS1:
        dc.l DIG,DUPP
        dc.l QBRAN,DIGS2
        dc.l BRAN,DIGS1
DIGS2:
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SIGN:
        bsr DOLST
        dc.l ZLESS
        dc.l QBRAN,SIGN1
        dc.l DOLIT,chminus,HOLD
SIGN1:
        dc.l EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EDIGS:
        bsr DOLST
        dc.l DROP,HLD,AT
        dc.l PAD,OVER,SUBB,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STR:
        bsr DOLST
        dc.l DUPP,TOR,ABSS
        dc.l BDIGS,DIGS,RFROM
        dc.l SIGN,EDIGS,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HEX:
        bsr DOLST
        dc.l DOLIT,16,BASE,STORE,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DECIM:
        bsr DOLST
        dc.l DOLIT,10,BASE,STORE,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DIGTQ:
        bsr DOLST
        dc.l TOR,DOLIT,char0,SUBB
        dc.l DOLIT,9,OVER,LESS
        dc.l QBRAN,DGTQ1
        dc.l DOLIT,7,SUBB
        dc.l DUPP,DOLIT,10,LESS,ORR
DGTQ1:
        dc.l DUPP,RFROM,ULESS,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NUMBQ:
        bsr DOLST
        dc.l BASE,AT,TOR,DOLIT,0,OVER,COUNT
        dc.l OVER,CAT,DOLIT,charS,EQUAL
        dc.l QBRAN,NUMQ1
        dc.l HEX,SWAP,DOLIT,1,PLUS
        dc.l SWAP,DOLIT,1,SUBB
NUMQ1:
        dc.l OVER,CAT,DOLIT,chminus,EQUAL,TOR
        dc.l SWAP,RAT,SUBB,SWAP,RAT,PLUS,QDUP
        dc.l QBRAN,NUMQ6
        dc.l DOLIT,1,SUBB,TOR
NUMQ2:
        dc.l DUPP,TOR,CAT,BASE,AT,DIGTQ
        dc.l QBRAN,NUMQ4
        dc.l SWAP,BASE,AT,STAR,PLUS,RFROM
        dc.l DOLIT,1,PLUS
        dc.l DONXT,NUMQ2
        dc.l RAT,SWAP,DROP
        dc.l QBRAN,NUMQ3
        dc.l NEGAT
NUMQ3:
        dc.l SWAP
        dc.l BRAN,NUMQ5
NUMQ4:
        dc.l RFROM,RFROM,DDROP,DDROP,DOLIT,0
NUMQ5:
        dc.l DUPP
NUMQ6:
        dc.l RFROM,DDROP
        dc.l RFROM,BASE,STORE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QKEY:
        bsr DOLST
        dc.l TQKEY,ATEXE,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
KEY:
        bsr DOLST
KEY1:
        dc.l QKEY
        dc.l QBRAN,KEY1
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EMIT:
        bsr DOLST
        dc.l TEMIT,ATEXE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NUFQ:
        bsr DOLST
        dc.l QKEY,DUPP
        dc.l QBRAN,NUFQ1
        dc.l DDROP,KEY,DOLIT,CRR,EQUAL
NUFQ1:
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PACE:
        bsr DOLST
        dc.l DOLIT,11,EMIT,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SPACE:
        bsr DOLST
        dc.l BLANK,EMIT,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SPACS:
        bsr DOLST
        dc.l DOLIT,0,MAX,TOR
        dc.l BRAN,CHAR2
CHAR1:
        dc.l SPACE
CHAR2:
        dc.l DONXT,CHAR1
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TYPES:
        bsr DOLST
        dc.l TOR
        dc.l BRAN,TYPE2
TYPE1:
        dc.l DUPP,CAT,EMIT
        dc.l DOLIT,1,PLUS
TYPE2:
        dc.l DONXT,TYPE1
        dc.l DROP,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CR:
        bsr DOLST
        dc.l DOLIT,CRR,EMIT
        dc.l DOLIT,LF,EMIT,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOSTR:
        bsr DOLST
        dc.l RFROM,RAT,RFROM,COUNT,PLUS
        dc.l ALGND,TOR,SWAP,TOR,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STRQP:
        bsr DOLST
        dc.l DOSTR,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTQP:
        bsr DOLST
        dc.l DOSTR,COUNT,TYPES,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTR:
        bsr DOLST
        dc.l TOR,STR,RFROM,OVER,SUBB
        dc.l SPACS,TYPES,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UDOTR:
        bsr DOLST
        dc.l TOR,BDIGS,DIGS,EDIGS
        dc.l RFROM,OVER,SUBB
        dc.l SPACS,TYPES,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UDOT:
        bsr DOLST
        dc.l BDIGS,DIGS,EDIGS
        dc.l SPACE,TYPES,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOT:
        bsr DOLST
        dc.l BASE,AT,DOLIT,10,XORR
        dc.l QBRAN,DOT1
        dc.l UDOT,EXIT
DOT1:
        dc.l STR,SPACE,TYPES,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QUEST:
        bsr DOLST
        dc.l AT,DOT,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PARS:
        bsr DOLST
        dc.l TEMP,STORE,OVER,TOR,DUPP
        dc.l QBRAN,PARS8
        dc.l DOLIT,1,SUBB,TEMP,AT,BLANK,EQUAL
        dc.l QBRAN,PARS3
        dc.l TOR
PARS1:
        dc.l BLANK,OVER,CAT
        dc.l SUBB,ZLESS,INVER
        dc.l QBRAN,PARS2
        dc.l DOLIT,1,PLUS
        dc.l DONXT,PARS1
        dc.l RFROM,DROP,DOLIT,0,DUPP,EXIT
PARS2:
        dc.l RFROM
PARS3:
        dc.l OVER,SWAP
        dc.l TOR
PARS4:
        dc.l TEMP,AT,OVER,CAT,SUBB
        dc.l TEMP,AT,BLANK,EQUAL
        dc.l QBRAN,PARS5
        dc.l ZLESS
PARS5:
        dc.l QBRAN,PARS6
        dc.l DOLIT,1,PLUS
        dc.l DONXT,PARS4
        dc.l DUPP,TOR
        dc.l BRAN,PARS7
PARS6:
        dc.l RFROM,DROP,DUPP
        dc.l DOLIT,1,PLUS,TOR
PARS7:
        dc.l OVER,SUBB
        dc.l RFROM,RFROM,SUBB,EXIT
PARS8:
        dc.l OVER,RFROM,SUBB,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PARSE:
        bsr DOLST
        dc.l TOR,TIB,INN,AT,PLUS
        dc.l NTIB,AT,INN,AT,SUBB
        dc.l RFROM,PARS,INN,PSTOR,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTPR:
        bsr DOLST
        dc.l DOLIT,charbr,PARSE,TYPES,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PAREN:
        bsr DOLST
        dc.l DOLIT,charbr,PARSE,DDROP,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BKSLA:
        bsr DOLST
        dc.l NTIB,AT,INN,STORE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CHAR:
        bsr DOLST
        dc.l BLANK,PARSE,DROP,CAT,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TOKEN:
        bsr DOLST
        dc.l BLANK,PARSE,DOLIT,31,MIN
        dc.l NP,AT,OVER,SUBB,CELLM
        dc.l PACKS,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
WORDD:
        bsr DOLST
        dc.l PARSE,HERE,PACKS,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NAMET:
        bsr DOLST
        dc.l CELLM,CELLM,AT,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SAMEQ:
        bsr DOLST
        dc.l TOR
        dc.l BRAN,SAME2
SAME1:
        dc.l OVER,RAT,CELLS,PLUS,AT
        dc.l OVER,RAT,CELLS,PLUS,AT
        dc.l SUBB,QDUP
        dc.l QBRAN,SAME2
        dc.l RFROM,DROP,EXIT
SAME2:
        dc.l DONXT,SAME1
        dc.l DOLIT,0,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
FIND:
        bsr DOLST
        dc.l SWAP,DUPP,CAT
        dc.l DOLIT,CELLL,SLASH,TEMP,STORE
        dc.l DUPP,AT,TOR,CELLP,SWAP
FIND1:
        dc.l AT,DUPP
        dc.l QBRAN,FIND6
        dc.l DUPP,AT,DOLIT,MASKK,ANDD,RAT,XORR
        dc.l QBRAN,FIND2
        dc.l CELLP,DOLIT,$ffffffff
        dc.l BRAN,FIND3
FIND2:
        dc.l CELLP,TEMP,AT,SAMEQ
FIND3:
        dc.l BRAN,FIND4
FIND6:
        dc.l RFROM,DROP
        dc.l SWAP,CELLM,SWAP,EXIT
FIND4:
        dc.l QBRAN,FIND5
        dc.l CELLM,CELLM
        dc.l BRAN,FIND1
FIND5:
        dc.l RFROM,DROP,SWAP,DROP
        dc.l CELLM
        dc.l DUPP,NAMET,SWAP,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NAMEQ:
        bsr DOLST
        dc.l CNTXT,DUPP,DAT,XORR
        dc.l QBRAN,NAMQ1
        dc.l CELLM
NAMQ1:
        dc.l TOR
NAMQ2:
        dc.l RFROM,CELLP,DUPP,TOR
        dc.l AT,QDUP
        dc.l QBRAN,NAMQ3
        dc.l FIND,QDUP
        dc.l QBRAN,NAMQ2
        dc.l RFROM,DROP,EXIT
NAMQ3:
        dc.l RFROM,DROP
        dc.l DOLIT,0,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BKSP:
        bsr DOLST
        dc.l TOR,OVER,RFROM,SWAP,OVER,XORR
        dc.l QBRAN,BACK1
        dc.l DOLIT,BKSPP,TECHO,ATEXE,DOLIT,1,SUBB
        dc.l BLANK,TECHO,ATEXE
        dc.l DOLIT,BKSPP,TECHO,ATEXE
BACK1:
        dc.l EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TAP:
        bsr DOLST
        dc.l DUPP,TECHO,ATEXE
        dc.l OVER,CSTOR,DOLIT,1,PLUS,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
KTAP:
        bsr DOLST
        dc.l DUPP,DOLIT,CRR,XORR
        dc.l QBRAN,KTAP2
        dc.l DOLIT,BKSPP,XORR
        dc.l QBRAN,KTAP1
        dc.l BLANK,TAP,EXIT
KTAP1:
        dc.l BKSP,EXIT
KTAP2:
        dc.l DROP,SWAP,DROP,DUPP,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ACCEP:
        bsr DOLST
        dc.l OVER,PLUS,OVER
ACCP1:
        dc.l DDUP,XORR
        dc.l QBRAN,ACCP4
        dc.l KEY,DUPP
        dc.l BLANK,DOLIT,127,WITHI
        dc.l QBRAN,ACCP2
        dc.l TAP
        dc.l BRAN,ACCP3
ACCP2:
        dc.l TTAP,ATEXE
ACCP3:
        dc.l BRAN,ACCP1
ACCP4:
        dc.l DROP,OVER,SUBB,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EXPEC:
        bsr DOLST
        dc.l TEXPE,ATEXE,SPAN,STORE,DROP,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QUERY:
        bsr DOLST
        dc.l TIB,DOLIT,80,TEXPE,ATEXE,NTIB,STORE
        dc.l DROP,DOLIT,0,INN,STORE,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CATCH:
        bsr DOLST
        dc.l SPAT,TOR,HANDL,AT,TOR
        dc.l RPAT,HANDL,STORE,EXECU
        dc.l RFROM,HANDL,STORE
        dc.l RFROM,DROP,DOLIT,0,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
THROW:
        bsr DOLST
        dc.l HANDL,AT,RPSTO
        dc.l RFROM,HANDL,STORE
        dc.l RFROM,SWAP,TOR,SPSTO
        dc.l DROP,RFROM,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NULLS:
        bsr DOLST
        dc.l DOVAR
        dc.l 0
        dc.b 99,111,121,111
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ABORT:
        bsr DOLST
        dc.l NULLS,THROW
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ABORQ:
        bsr DOLST
        dc.l QBRAN,ABOR1
        dc.l DOSTR,THROW
ABOR1:
        dc.l DOSTR,DROP,EXIT
LEN_ set (10&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
INTER:
        bsr DOLST
        dc.l NAMEQ,QDUP
        dc.l QBRAN,INTE1
        dc.l AT,DOLIT,COMPOL,ANDD
        dc.l ABORQ
        dc.b 15,32,99,111,109,112,105,108,101,32,111,110,108,121,32,32
        dc.l EXECU,EXIT
INTE1:
        dc.l TNUMB,ATEXE
        dc.l QBRAN,INTE2
        dc.l EXIT
INTE2:
        dc.l THROW
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
LBRAC:
        bsr DOLST
        dc.l DOLIT,INTER,TEVAL,STORE,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTOK:
        bsr DOLST
        dc.l DOLIT,INTER,TEVAL,AT,EQUAL
        dc.l QBRAN,DOTO1
        dc.l DOTQP
        dc.b 3,32,111,107
DOTO1:
        dc.l CR,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QSTAC:
        bsr DOLST
        dc.l DEPTH,ZLESS
        dc.l ABORQ
        dc.b 11,32,117,110,100,101,114,102,108,111,119,32
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
EVAL:
        bsr DOLST
EVAL1:
        dc.l TOKEN,DUPP,CAT
        dc.l QBRAN,EVAL2
        dc.l TEVAL,ATEXE,QSTAC
        dc.l BRAN,EVAL1
EVAL2:
        dc.l DROP,TPROM,ATEXE,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
PRESE:
        bsr DOLST
        dc.l SZERO,AT,SPSTO
        dc.l DOLIT,TIBB,NTIB,CELLP,STORE,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
XIO:
        bsr DOLST
        dc.l DOLIT,ACCEP,TEXPE,DSTOR
        dc.l TECHO,DSTOR,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
FILE:
        bsr DOLST
        dc.l DOLIT,PACE,DOLIT,DROP
        dc.l DOLIT,KTAP,XIO,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HAND:
        bsr DOLST
        dc.l DOLIT,DOTOK,DOLIT,EMIT
        dc.l DOLIT,KTAP,XIO,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ISLO:
        bsr DOLST
        dc.l DOVAR
        dc.l QRX,TXSTO
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CONSO:
        bsr DOLST
        dc.l ISLO,DAT,TQKEY,DSTOR
        dc.l HAND,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QUIT:
        bsr DOLST
        dc.l RZERO,AT,RPSTO
QUIT1:
        dc.l LBRAC
QUIT2:
        dc.l QUERY
        dc.l DOLIT,EVAL,CATCH,QDUP
        dc.l QBRAN,QUIT2
        dc.l TPROM,AT,TOR
        dc.l CONSO,NULLS,OVER,XORR
        dc.l QBRAN,QUIT3
        dc.l SPACE,COUNT,TYPES
        dc.l DOTQP
        dc.b 3,32,63,32
QUIT3:
        dc.l RFROM,DOLIT,DOTOK,XORR
        dc.l QBRAN,QUIT4
        dc.l DOLIT,ERR,EMIT
QUIT4:
        dc.l PRESE
        dc.l BRAN,QUIT1
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TICK:
        bsr DOLST
        dc.l TOKEN,NAMEQ
        dc.l QBRAN,TICK1
        dc.l EXIT
TICK1:
        dc.l THROW
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ALLOT:
        bsr DOLST
        dc.l CP,PSTOR,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
COMMA:
        bsr DOLST
        dc.l HERE,DUPP,CELLP
        dc.l CP,STORE,STORE,EXIT
LEN_ set (9&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BCOMP:
        bsr DOLST
        dc.l TICK,COMMA,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
COMPI:
        bsr DOLST
        dc.l RFROM,DUPP,AT,COMMA
        dc.l CELLP,TOR,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
LITER:
        bsr DOLST
        dc.l COMPI,DOLIT,COMMA,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STRCQ:
        bsr DOLST
        dc.l DOLIT,charq,WORDD
        dc.l COUNT,PLUS,ALGND
        dc.l CP,STORE,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RECUR:
        bsr DOLST
        dc.l LAST,AT,NAMET,COMMA,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
FOR:
        bsr DOLST
        dc.l COMPI,TOR,HERE,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
BEGIN:
        bsr DOLST
        dc.l HERE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
NEXT:
        bsr DOLST
        dc.l COMPI,DONXT,COMMA,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UNTIL:
        bsr DOLST
        dc.l COMPI,QBRAN,COMMA,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
AGAIN:
        bsr DOLST
        dc.l COMPI,BRAN,COMMA,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
IFF:
        bsr DOLST
        dc.l COMPI,QBRAN,HERE
        dc.l DOLIT,0,COMMA,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
AHEAD:
        bsr DOLST
        dc.l COMPI,BRAN,HERE,DOLIT,0,COMMA,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
REPEA:
        bsr DOLST
        dc.l AGAIN,HERE,SWAP,STORE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
THENN:
        bsr DOLST
        dc.l HERE,SWAP,STORE,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
AFT:
        bsr DOLST
        dc.l DROP,AHEAD,BEGIN,SWAP,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ELSEE:
        bsr DOLST
        dc.l AHEAD,SWAP,THENN,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
WHILE:
        bsr DOLST
        dc.l IFF,SWAP,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
ABRTQ:
        bsr DOLST
        dc.l COMPI,ABORQ,STRCQ,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STRQ:
        bsr DOLST
        dc.l COMPI,STRQP,STRCQ,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTQ:
        bsr DOLST
        dc.l COMPI,DOTQP,STRCQ,EXIT
LEN_ set (7&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UNIQU:
        bsr DOLST
        dc.l DUPP,NAMEQ
        dc.l QBRAN,UNIQ1
        dc.l DOTQP
        dc.b 7,32,114,101,68,101,102,32
        dc.l OVER,COUNT,TYPES
UNIQ1:
        dc.l DROP,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SNAME:
        bsr DOLST
        dc.l DUPP,CAT
        dc.l QBRAN,PNAM1
        dc.l UNIQU
        dc.l DUPP,LAST,STORE
        dc.l HERE,ALGND,SWAP
        dc.l CELLM
        dc.l CRRNT,AT,AT,OVER,STORE
        dc.l CELLM,DUPP,NP,STORE
        dc.l STORE,EXIT
PNAM1:
        dc.l STRQP
        dc.b 7,32,110,97,109,101,32,32
        dc.l THROW
LEN_ set (8&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SCOMP:
        bsr DOLST
        dc.l NAMEQ,QDUP
        dc.l QBRAN,SCOM2
        dc.l AT,DOLIT,IMEDDL,ANDD
        dc.l QBRAN,SCOM1
        dc.l EXECU,EXIT
SCOM1:
        dc.l COMMA,EXIT
SCOM2:
        dc.l TNUMB,ATEXE
        dc.l QBRAN,SCOM3
        dc.l LITER,EXIT
SCOM3:
        dc.l THROW
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
OVERT:
        bsr DOLST
        dc.l LAST,AT,CRRNT,AT,STORE,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SEMIS:
        bsr DOLST
        dc.l COMPI,EXIT,LBRAC,OVERT,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
RBRAC:
        bsr DOLST
        dc.l DOLIT,SCOMP,TEVAL,STORE,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CALLC:
        bsr DOLST
        dc.l DOLIT
        dc.l CALLL,COMMA
        dc.l COMMA,EXIT
LEN_ set (1&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
COLON:
        bsr DOLST
        dc.l TOKEN,SNAME,DOLIT,DOLST
        dc.l CALLC,RBRAC,EXIT
LEN_ set (9&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
IMMED:
        bsr DOLST
        dc.l DOLIT,IMEDDL,LAST,AT,AT,ORR
        dc.l LAST,AT,STORE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
USER:
        bsr DOLST
        dc.l TOKEN,SNAME,OVERT
        dc.l DOLIT,DOLST,CALLC
        dc.l DOLIT,DOUSE,COMMA
        dc.l COMMA,EXIT
LEN_ set (6&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
CREAT:
        bsr DOLST
        dc.l TOKEN,SNAME,OVERT
        dc.l DOLIT,DOLST,CALLC
        dc.l DOLIT,DOVAR,COMMA,EXIT
LEN_ set (8&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
VARIA:
        bsr DOLST
        dc.l CREAT,DOLIT,0,COMMA,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
UTYPE:
        bsr DOLST
        dc.l TOR
        dc.l BRAN,UTYP2
UTYP1:
        dc.l DUPP,CAT,TCHAR,EMIT
        dc.l DOLIT,1,PLUS
UTYP2:
        dc.l DONXT,UTYP1
        dc.l DROP,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DUMPP:
        bsr DOLST
        dc.l OVER,DOLIT,4,UDOTR
        dc.l SPACE,TOR
        dc.l BRAN,PDUM2
PDUM1:
        dc.l DUPP,CAT,DOLIT,3,UDOTR
        dc.l DOLIT,1,PLUS
PDUM2:
        dc.l DONXT,PDUM1
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DUMP:
        bsr DOLST
        dc.l BASE,AT,TOR,HEX
        dc.l DOLIT,16,SLASH
        dc.l TOR
DUMP1:
        dc.l CR,DOLIT,16,DDUP,DUMPP
        dc.l ROT,ROT
        dc.l DOLIT,2,SPACS,UTYPE
        dc.l NUFQ,INVER
        dc.l QBRAN,DUMP2
        dc.l DONXT,DUMP1
        dc.l BRAN,DUMP3
DUMP2:
        dc.l RFROM,DROP
DUMP3:
        dc.l DROP,RFROM,BASE,STORE
        dc.l EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTS:
        bsr DOLST
        dc.l CR,DEPTH
        dc.l TOR
        dc.l BRAN,DOTS2
DOTS1:
        dc.l RAT,PICK,DOT
DOTS2:
        dc.l DONXT,DOTS1
        dc.l DOTQP
        dc.b 3,60,115,112
        dc.l EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
STCSP:
        bsr DOLST
        dc.l SPAT,CSP,STORE,EXIT
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
QCSP:
        bsr DOLST
        dc.l SPAT,CSP,AT,XORR
        dc.l ABORQ
        dc.b 7,115,116,97,99,107,115,32
        dc.l EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TNAME:
        bsr DOLST
        dc.l CRRNT
TNAM1:
        dc.l CELLP,AT,QDUP
        dc.l QBRAN,TNAM4
        dc.l DDUP
TNAM2:
        dc.l AT,DUPP
        dc.l QBRAN,TNAM3
        dc.l DDUP,NAMET,XORR
        dc.l QBRAN,TNAM3
        dc.l CELLM
        dc.l BRAN,TNAM2
TNAM3:
        dc.l SWAP,DROP,QDUP
        dc.l QBRAN,TNAM1
        dc.l SWAP,DROP,SWAP,DROP,EXIT
TNAM4:
        dc.l DROP,DOLIT,0,EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
DOTID:
        bsr DOLST
        dc.l QDUP
        dc.l QBRAN,DOTI1
        dc.l COUNT,DOLIT,$01F,ANDD
        dc.l UTYPE,EXIT
DOTI1:
        dc.l DOTQP
        dc.b 11,32,123,110,111,78,97,109,101,125,32,32
        dc.l EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
SEE:
        bsr DOLST
        dc.l TICK
        dc.l CR,CELLP
SEE1:
        dc.l CELLP,DUPP,AT,DUPP
        dc.l QBRAN,SEE2
        dc.l TNAME
SEE2:
        dc.l QDUP
        dc.l QBRAN,SEE3
        dc.l SPACE,DOTID
        dc.l BRAN,SEE4
SEE3:
        dc.l DUPP,AT,UDOT
SEE4:
        dc.l NUFQ
        dc.l QBRAN,SEE1
        dc.l DROP,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
WORDS:
        bsr DOLST
        dc.l CR,CNTXT,AT
WORS1:
        dc.l AT,QDUP
        dc.l QBRAN,WORS2
        dc.l DUPP,SPACE,DOTID
        dc.l CELLM,NUFQ
        dc.l QBRAN,WORS1
        dc.l DROP
WORS2:
        dc.l EXIT
LEN_ set (3&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
VERSN:
        bsr DOLST
        dc.l DOLIT,VER*256+EXT,EXIT
LEN_ set (2&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
HI:
        bsr DOLST
        dc.l STOIO,CR,DOTQP
        dc.b 15,101,70,111,114,116,104,32,54,56,107,32,118
        dc.b VER+'0',46,EXT+'0'
        dc.l CR,EXIT
LEN_ set (5&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
TBOOT:
        bsr DOLST
        dc.l DOVAR
        dc.l HI
LEN_ set (4&$01F)/CELLL
NAME_ set NAME_-((LEN_+3)*CELLL)
        DS.L 0
COLD:
        bsr DOLST
COLD1:
        dc.l DOLIT,UZERO,DOLIT,UPP
        dc.l DOLIT,ULAST-UZERO,CMOVE
        dc.l PRESE
        dc.l TBOOT,ATEXE
        dc.l FORTH,CNTXT,AT,DUPP
        dc.l CRRNT,DSTOR,OVERT
        dc.l QUIT
        dc.l BRAN,COLD1
LASTN equ NAME_+8
NTOP equ NAME_-0
        DS.L 0
CTOP:
        ORG NAME_
L220_:
        dc.l COLD,L218_
L219_:
        dc.b 4,67,79,76,68,0,0,0
        DS.L 0
        dc.l TBOOT,L217_
L218_:
        dc.b 5,39,66,79,79,84,0,0
        DS.L 0
        dc.l HI,L216_
L217_:
        dc.b 2,104,105,0
        DS.L 0
        dc.l VERSN,L215_
L216_:
        dc.b 3,86,69,82
        DS.L 0
        dc.l WORDS,L214_
L215_:
        dc.b 5,87,79,82,68,83,0,0
        DS.L 0
        dc.l SEE,L213_
L214_:
        dc.b 3,83,69,69
        DS.L 0
        dc.l DOTID,L212_
L213_:
        dc.b 3,46,73,68
        DS.L 0
        dc.l TNAME,L211_
L212_:
        dc.b 5,62,78,65,77,69,0,0
        DS.L 0
        dc.l QCSP,L210_
L211_:
        dc.b 4,63,67,83,80,0,0,0
        DS.L 0
        dc.l STCSP,L209_
L210_:
        dc.b 4,33,67,83,80,0,0,0
        DS.L 0
        dc.l DOTS,L208_
L209_:
        dc.b 2,46,83,0
        DS.L 0
        dc.l DUMP,L207_
L208_:
        dc.b 4,68,85,77,80,0,0,0
        DS.L 0
        dc.l DUMPP,L206_
L207_:
        dc.b 3,100,109,43
        DS.L 0
        dc.l UTYPE,L205_
L206_:
        dc.b 5,95,84,89,80,69,0,0
        DS.L 0
        dc.l VARIA,L204_
L205_:
        dc.b 8,86,65,82,73,65,66,76,69,0,0,0
        DS.L 0
        dc.l CREAT,L203_
L204_:
        dc.b 6,67,82,69,65,84,69,0
        DS.L 0
        dc.l USER,L202_
L203_:
        dc.b 4,85,83,69,82,0,0,0
        DS.L 0
        dc.l IMMED,L201_
L202_:
        dc.b 9,73,77,77,69,68,73,65,84,69,0,0
        DS.L 0
        dc.l COLON,L200_
L201_:
        dc.b 1,58,0,0
        DS.L 0
        dc.l CALLC,L199_
L200_:
        dc.b 5,99,97,108,108,44,0,0
        DS.L 0
        dc.l RBRAC,L198_
L199_:
        dc.b 1,93,0,0
        DS.L 0
        dc.l SEMIS,L197_
L198_:
        dc.b IMEDD+COMPO+1,59,0,0
        DS.L 0
        dc.l OVERT,L196_
L197_:
        dc.b 5,79,86,69,82,84,0,0
        DS.L 0
        dc.l SCOMP,L195_
L196_:
        dc.b 8,36,67,79,77,80,73,76,69,0,0,0
        DS.L 0
        dc.l SNAME,L194_
L195_:
        dc.b 3,36,44,110
        DS.L 0
        dc.l UNIQU,L193_
L194_:
        dc.b 7,63,85,78,73,81,85,69
        DS.L 0
        dc.l DOTQ,L192_
L193_:
        dc.b IMEDD+2,46,34,0
        DS.L 0
        dc.l STRQ,L191_
L192_:
        dc.b IMEDD+2,36,34,0
        DS.L 0
        dc.l ABRTQ,L190_
L191_:
        dc.b IMEDD+6,65,66,79,82,84,34,0
        DS.L 0
        dc.l WHILE,L189_
L190_:
        dc.b IMEDD+5,87,72,73,76,69,0,0
        DS.L 0
        dc.l ELSEE,L188_
L189_:
        dc.b IMEDD+4,69,76,83,69,0,0,0
        DS.L 0
        dc.l AFT,L187_
L188_:
        dc.b IMEDD+3,65,70,84
        DS.L 0
        dc.l THENN,L186_
L187_:
        dc.b IMEDD+4,84,72,69,78,0,0,0
        DS.L 0
        dc.l REPEA,L185_
L186_:
        dc.b IMEDD+6,82,69,80,69,65,84,0
        DS.L 0
        dc.l AHEAD,L184_
L185_:
        dc.b IMEDD+5,65,72,69,65,68,0,0
        DS.L 0
        dc.l IFF,L183_
L184_:
        dc.b IMEDD+2,73,70,0
        DS.L 0
        dc.l AGAIN,L182_
L183_:
        dc.b IMEDD+5,65,71,65,73,78,0,0
        DS.L 0
        dc.l UNTIL,L181_
L182_:
        dc.b IMEDD+5,85,78,84,73,76,0,0
        DS.L 0
        dc.l NEXT,L180_
L181_:
        dc.b IMEDD+4,78,69,88,84,0,0,0
        DS.L 0
        dc.l BEGIN,L179_
L180_:
        dc.b IMEDD+5,66,69,71,73,78,0,0
        DS.L 0
        dc.l FOR,L178_
L179_:
        dc.b IMEDD+3,70,79,82
        DS.L 0
        dc.l RECUR,L177_
L178_:
        dc.b IMEDD+7,82,69,67,85,82,83,69
        DS.L 0
        dc.l STRCQ,L176_
L177_:
        dc.b 3,36,44,34
        DS.L 0
        dc.l LITER,L175_
L176_:
        dc.b IMEDD+7,76,73,84,69,82,65,76
        DS.L 0
        dc.l COMPI,L174_
L175_:
        dc.b COMPO+7,67,79,77,80,73,76,69
        DS.L 0
        dc.l BCOMP,L173_
L174_:
        dc.b IMEDD+9,91,67,79,77,80,73,76,69,93,0,0
        DS.L 0
        dc.l COMMA,L172_
L173_:
        dc.b 1,$2c,0,0
        DS.L 0
        dc.l ALLOT,L171_
L172_:
        dc.b 5,65,76,76,79,84,0,0
        DS.L 0
        dc.l TICK,L170_
L171_:
        dc.b 1,39,0,0
        DS.L 0
        dc.l QUIT,L169_
L170_:
        dc.b 4,81,85,73,84,0,0,0
        DS.L 0
        dc.l CONSO,L168_
L169_:
        dc.b 7,67,79,78,83,79,76,69
        DS.L 0
        dc.l ISLO,L167_
L168_:
        dc.b 3,73,47,79
        DS.L 0
        dc.l HAND,L166_
L167_:
        dc.b 4,72,65,78,68,0,0,0
        DS.L 0
        dc.l FILE,L165_
L166_:
        dc.b 4,70,73,76,69,0,0,0
        DS.L 0
        dc.l XIO,L164_
L165_:
        dc.b COMPO+3,120,105,111
        DS.L 0
        dc.l PRESE,L163_
L164_:
        dc.b 6,80,82,69,83,69,84,0
        DS.L 0
        dc.l EVAL,L162_
L163_:
        dc.b 4,69,86,65,76,0,0,0
        DS.L 0
        dc.l QSTAC,L161_
L162_:
        dc.b 6,63,83,84,65,67,75,0
        DS.L 0
        dc.l DOTOK,L160_
L161_:
        dc.b 3,46,79,75
        DS.L 0
        dc.l LBRAC,L159_
L160_:
        dc.b IMEDD+1,91,0,0
        DS.L 0
        dc.l INTER,L158_
L159_:
        dc.b 10,36,73,78,84,69,82,80,82,69,84,0
        DS.L 0
        dc.l ABORQ,L157_
L158_:
        dc.b COMPO+6,97,98,111,114,116,34,0
        DS.L 0
        dc.l ABORT,L156_
L157_:
        dc.b 5,65,66,79,82,84,0,0
        DS.L 0
        dc.l NULLS,L155_
L156_:
        dc.b 5,78,85,76,76,36,0,0
        DS.L 0
        dc.l THROW,L154_
L155_:
        dc.b 5,84,72,82,79,87,0,0
        DS.L 0
        dc.l CATCH,L153_
L154_:
        dc.b 5,67,65,84,67,72,0,0
        DS.L 0
        dc.l QUERY,L152_
L153_:
        dc.b 5,81,85,69,82,89,0,0
        DS.L 0
        dc.l EXPEC,L151_
L152_:
        dc.b 6,69,88,80,69,67,84,0
        DS.L 0
        dc.l ACCEP,L150_
L151_:
        dc.b 6,97,99,99,101,112,116,0
        DS.L 0
        dc.l KTAP,L149_
L150_:
        dc.b 4,107,84,65,80,0,0,0
        DS.L 0
        dc.l TAP,L148_
L149_:
        dc.b 3,84,65,80
        DS.L 0
        dc.l BKSP,L147_
L148_:
        dc.b 2,94,72,0
        DS.L 0
        dc.l NAMEQ,L146_
L147_:
        dc.b 5,78,65,77,69,63,0,0
        DS.L 0
        dc.l FIND,L145_
L146_:
        dc.b 4,102,105,110,100,0,0,0
        DS.L 0
        dc.l SAMEQ,L144_
L145_:
        dc.b 5,83,65,77,69,63,0,0
        DS.L 0
        dc.l NAMET,L143_
L144_:
        dc.b 5,78,65,77,69,62,0,0
        DS.L 0
        dc.l WORDD,L142_
L143_:
        dc.b 4,87,79,82,68,0,0,0
        DS.L 0
        dc.l TOKEN,L141_
L142_:
        dc.b 5,84,79,75,69,78,0,0
        DS.L 0
        dc.l CHAR,L140_
L141_:
        dc.b 4,67,72,65,82,0,0,0
        DS.L 0
        dc.l BKSLA,L139_
L140_:
        dc.b IMEDD+1,92,0,0
        DS.L 0
        dc.l PAREN,L138_
L139_:
        dc.b IMEDD+1,40,0,0
        DS.L 0
        dc.l DOTPR,L137_
L138_:
        dc.b IMEDD+2,46,40,0
        DS.L 0
        dc.l PARSE,L136_
L137_:
        dc.b 5,80,65,82,83,69,0,0
        DS.L 0
        dc.l PARS,L135_
L136_:
        dc.b 5,112,97,114,115,101,0,0
        DS.L 0
        dc.l QUEST,L134_
L135_:
        dc.b 1,63,0,0
        DS.L 0
        dc.l DOT,L133_
L134_:
        dc.b 1,46,0,0
        DS.L 0
        dc.l UDOT,L132_
L133_:
        dc.b 2,85,46,0
        DS.L 0
        dc.l UDOTR,L131_
L132_:
        dc.b 3,85,46,82
        DS.L 0
        dc.l DOTR,L130_
L131_:
        dc.b 2,46,82,0
        DS.L 0
        dc.l DOTQP,L129_
L130_:
        dc.b COMPO+3,46,34,124
        DS.L 0
        dc.l STRQP,L128_
L129_:
        dc.b COMPO+3,36,34,124
        DS.L 0
        dc.l DOSTR,L127_
L128_:
        dc.b COMPO+3,100,111,36
        DS.L 0
        dc.l CR,L126_
L127_:
        dc.b 2,67,82,0
        DS.L 0
        dc.l TYPES,L125_
L126_:
        dc.b 4,84,89,80,69,0,0,0
        DS.L 0
        dc.l SPACS,L124_
L125_:
        dc.b 6,83,80,65,67,69,83,0
        DS.L 0
        dc.l SPACE,L123_
L124_:
        dc.b 5,83,80,65,67,69,0,0
        DS.L 0
        dc.l PACE,L122_
L123_:
        dc.b 4,80,65,67,69,0,0,0
        DS.L 0
        dc.l NUFQ,L121_
L122_:
        dc.b 4,78,85,70,63,0,0,0
        DS.L 0
        dc.l EMIT,L120_
L121_:
        dc.b 4,69,77,73,84,0,0,0
        DS.L 0
        dc.l KEY,L119_
L120_:
        dc.b 3,75,69,89
        DS.L 0
        dc.l QKEY,L118_
L119_:
        dc.b 4,63,75,69,89,0,0,0
        DS.L 0
        dc.l NUMBQ,L117_
L118_:
        dc.b 7,78,85,77,66,69,82,63
        DS.L 0
        dc.l DIGTQ,L116_
L117_:
        dc.b 6,68,73,71,73,84,63,0
        DS.L 0
        dc.l DECIM,L115_
L116_:
        dc.b 7,68,69,67,73,77,65,76
        DS.L 0
        dc.l HEX,L114_
L115_:
        dc.b 3,72,69,88
        DS.L 0
        dc.l STR,L113_
L114_:
        dc.b 3,115,116,114
        DS.L 0
        dc.l EDIGS,L112_
L113_:
        dc.b 2,35,62,0
        DS.L 0
        dc.l SIGN,L111_
L112_:
        dc.b 4,83,73,71,78,0,0,0
        DS.L 0
        dc.l DIGS,L110_
L111_:
        dc.b 2,35,83,0
        DS.L 0
        dc.l DIG,L109_
L110_:
        dc.b 1,35,0,0
        DS.L 0
        dc.l HOLD,L108_
L109_:
        dc.b 4,72,79,76,68,0,0,0
        DS.L 0
        dc.l BDIGS,L107_
L108_:
        dc.b 2,$3c,$23,0
        DS.L 0
        dc.l EXTRC,L106_
L107_:
        dc.b 7,69,88,84,82,65,67,84
        DS.L 0
        dc.l DIGIT,L105_
L106_:
        dc.b 5,68,73,71,73,84,0,0
        DS.L 0
        dc.l PACKS,L104_
L105_:
        dc.b 5,80,65,67,75,36,0,0
        DS.L 0
        dc.l DTRAI,L103_
L104_:
        dc.b 9,45,84,82,65,73,76,73,78,71,0,0
        DS.L 0
        dc.l FILL,L102_
L103_:
        dc.b 4,70,73,76,76,0,0,0
        DS.L 0
        dc.l CMOVE,L101_
L102_:
        dc.b 5,67,77,79,86,69,0,0
        DS.L 0
        dc.l ATEXE,L100_
L101_:
        dc.b 8,64,69,88,69,67,85,84,69,0,0,0
        DS.L 0
        dc.l TIB,L099_
L100_:
        dc.b 3,84,73,66
        DS.L 0
        dc.l PAD,L098_
L099_:
        dc.b 3,80,65,68
        DS.L 0
        dc.l HERE,L097_
L098_:
        dc.b 4,72,69,82,69,0,0,0
        DS.L 0
        dc.l COUNT,L096_
L097_:
        dc.b 5,67,79,85,78,84,0,0
        DS.L 0
        dc.l DAT,L095_
L096_:
        dc.b 2,50,64,0
        DS.L 0
        dc.l DSTOR,L094_
L095_:
        dc.b 2,50,33,0
        DS.L 0
        dc.l PSTOR,L093_
L094_:
        dc.b 2,43,33,0
        DS.L 0
        dc.l PICK,L092_
L093_:
        dc.b 4,80,73,67,75,0,0,0
        DS.L 0
        dc.l DEPTH,L091_
L092_:
        dc.b 5,68,69,80,84,72,0,0
        DS.L 0
        dc.l TCHAR,L090_
L091_:
        dc.b 5,62,67,72,65,82,0,0
        DS.L 0
        dc.l BLANK,L089_
L090_:
        dc.b 2,66,76,0
        DS.L 0
        dc.l ALGND,L088_
L089_:
        dc.b 7,65,76,73,71,78,69,68
        DS.L 0
        dc.l CELLS,L087_
L088_:
        dc.b 5,67,69,76,76,83,0,0
        DS.L 0
        dc.l CELLM,L086_
L087_:
        dc.b 5,67,69,76,76,45,0,0
        DS.L 0
        dc.l CELLP,L085_
L086_:
        dc.b 5,67,69,76,76,43,0,0
        DS.L 0
        dc.l STASL,L084_
L085_:
        dc.b 2,42,47,0
        DS.L 0
        dc.l SSMOD,L083_
L084_:
        dc.b 5,42,47,77,79,68,0,0
        DS.L 0
        dc.l MSTAR,L082_
L083_:
        dc.b 2,77,42,0
        DS.L 0
        dc.l STAR,L081_
L082_:
        dc.b 1,42,0,0
        DS.L 0
        dc.l UMSTA,L080_
L081_:
        dc.b 3,85,77,42
        DS.L 0
        dc.l SLASH,L079_
L080_:
        dc.b 1,47,0,0
        DS.L 0
        dc.l MODD,L078_
L079_:
        dc.b 3,77,79,68
        DS.L 0
        dc.l SLMOD,L077_
L078_:
        dc.b 4,47,77,79,68,0,0,0
        DS.L 0
        dc.l MSMOD,L076_
L077_:
        dc.b 5,77,47,77,79,68,0,0
        DS.L 0
        dc.l UMMOD,L075_
L076_:
        dc.b 6,85,77,47,77,79,68,0
        DS.L 0
        dc.l WITHI,L074_
L075_:
        dc.b 6,87,73,84,72,73,78,0
        DS.L 0
        dc.l MIN,L073_
L074_:
        dc.b 3,77,73,78
        DS.L 0
        dc.l MAX,L072_
L073_:
        dc.b 3,77,65,88
        DS.L 0
        dc.l LESS,L071_
L072_:
        dc.b 1,60,0,0
        DS.L 0
        dc.l ULESS,L070_
L071_:
        dc.b 2,85,60,0
        DS.L 0
        dc.l EQUAL,L069_
L070_:
        dc.b 1,61,0,0
        DS.L 0
        dc.l ABSS,L068_
L069_:
        dc.b 3,65,66,83
        DS.L 0
        dc.l SUBB,L067_
L068_:
        dc.b 1,45,0,0
        DS.L 0
        dc.l DNEGA,L066_
L067_:
        dc.b 7,68,78,69,71,65,84,69
        DS.L 0
        dc.l NEGAT,L065_
L066_:
        dc.b 6,78,69,71,65,84,69,0
        DS.L 0
        dc.l INVER,L064_
L065_:
        dc.b 3,78,79,84
        DS.L 0
        dc.l PLUS,L063_
L064_:
        dc.b 1,43,0,0
        DS.L 0
        dc.l DDUP,L062_
L063_:
        dc.b 4,50,68,85,80,0,0,0
        DS.L 0
        dc.l DDROP,L061_
L062_:
        dc.b 5,50,68,82,79,80,0,0
        DS.L 0
        dc.l ROT,L060_
L061_:
        dc.b 3,82,79,84
        DS.L 0
        dc.l QDUP,L059_
L060_:
        dc.b 4,63,68,85,80,0,0,0
        DS.L 0
        dc.l FORTH,L058_
L059_:
        dc.b 5,70,79,82,84,72,0,0
        DS.L 0
        dc.l DOVOC,L057_
L058_:
        dc.b COMPO+5,100,111,86,79,67,0,0
        DS.L 0
        dc.l LAST,L056_
L057_:
        dc.b 4,76,65,83,84,0,0,0
        DS.L 0
        dc.l NP,L055_
L056_:
        dc.b 2,78,80,0
        DS.L 0
        dc.l CP,L054_
L055_:
        dc.b 2,67,80,0
        DS.L 0
        dc.l CRRNT,L053_
L054_:
        dc.b 7,67,85,82,82,69,78,84
        DS.L 0
        dc.l CNTXT,L052_
L053_:
        dc.b 7,67,79,78,84,69,88,84
        DS.L 0
        dc.l HANDL,L051_
L052_:
        dc.b 7,72,65,78,68,76,69,82
        DS.L 0
        dc.l HLD,L050_
L051_:
        dc.b 3,72,76,68
        DS.L 0
        dc.l TNUMB,L049_
L050_:
        dc.b 7,39,78,85,77,66,69,82
        DS.L 0
        dc.l TEVAL,L048_
L049_:
        dc.b 5,39,69,86,65,76,0,0
        DS.L 0
        dc.l CSP,L047_
L048_:
        dc.b 3,67,83,80
        DS.L 0
        dc.l NTIB,L046_
L047_:
        dc.b 4,35,84,73,66,0,0,0
        DS.L 0
        dc.l INN,L045_
L046_:
        dc.b 3,62,73,78
        DS.L 0
        dc.l SPAN,L044_
L045_:
        dc.b 4,83,80,65,78,0,0,0
        DS.L 0
        dc.l TEMP,L043_
L044_:
        dc.b COMPO+3,116,109,112
        DS.L 0
        dc.l BASE,L042_
L043_:
        dc.b 4,66,65,83,69,0,0,0
        DS.L 0
        dc.l TPROM,L041_
L042_:
        dc.b 7,39,80,82,79,77,80,84
        DS.L 0
        dc.l TECHO,L040_
L041_:
        dc.b 5,39,69,67,72,79,0,0
        DS.L 0
        dc.l TTAP,L039_
L040_:
        dc.b 4,39,84,65,80,0,0,0
        DS.L 0
        dc.l TEXPE,L038_
L039_:
        dc.b 7,39,69,88,80,69,67,84
        DS.L 0
        dc.l TEMIT,L037_
L038_:
        dc.b 5,39,69,77,73,84,0,0
        DS.L 0
        dc.l TQKEY,L036_
L037_:
        dc.b 5,39,63,75,69,89,0,0
        DS.L 0
        dc.l RZERO,L035_
L036_:
        dc.b 3,82,80,48
        DS.L 0
        dc.l SZERO,L034_
L035_:
        dc.b 3,83,80,48
        DS.L 0
        dc.l DOUSE,L033_
L034_:
        dc.b COMPO+6,100,111,85,83,69,82,0
        DS.L 0
        dc.l UP,L032_
L033_:
        dc.b 2,85,80,0
        DS.L 0
        dc.l DOVAR,L031_
L032_:
        dc.b COMPO+5,100,111,86,65,82,0,0
        DS.L 0
        dc.l UPLUS,L030_
L031_:
        dc.b 3,85,77,43
        DS.L 0
        dc.l XORR,L029_
L030_:
        dc.b 3,88,79,82
        DS.L 0
        dc.l ORR,L028_
L029_:
        dc.b 2,79,82,0
        DS.L 0
        dc.l ANDD,L027_
L028_:
        dc.b 3,65,78,68
        DS.L 0
        dc.l ZLESS,L026_
L027_:
        dc.b 2,48,60,0
        DS.L 0
        dc.l OVER,L025_
L026_:
        dc.b 4,79,86,69,82,0,0,0
        DS.L 0
        dc.l SWAP,L024_
L025_:
        dc.b 4,83,87,65,80,0,0,0
        DS.L 0
        dc.l DUPP,L023_
L024_:
        dc.b 3,68,85,80
        DS.L 0
        dc.l DROP,L022_
L023_:
        dc.b 4,68,82,79,80,0,0,0
        DS.L 0
        dc.l SPSTO,L021_
L022_:
        dc.b 3,83,80,33
        DS.L 0
        dc.l SPAT,L020_
L021_:
        dc.b 3,83,80,64
        DS.L 0
        dc.l TOR,L019_
L020_:
        dc.b COMPO+2,62,82,0
        DS.L 0
        dc.l RAT,L018_
L019_:
        dc.b 2,82,64,0
        DS.L 0
        dc.l RFROM,L017_
L018_:
        dc.b COMPO+2,82,62,0
        DS.L 0
        dc.l RPSTO,L016_
L017_:
        dc.b COMPO+3,82,80,33
        DS.L 0
        dc.l RPAT,L015_
L016_:
        dc.b 3,82,80,64
        DS.L 0
        dc.l CAT,L014_
L015_:
        dc.b 2,67,64,0
        DS.L 0
        dc.l CSTOR,L013_
L014_:
        dc.b 2,67,33,0
        DS.L 0
        dc.l AT,L012_
L013_:
        dc.b 1,64,0,0
        DS.L 0
        dc.l STORE,L011_
L012_:
        dc.b 1,33,0,0
        DS.L 0
        dc.l EXIT,L010_
L011_:
        dc.b 4,69,88,73,84,0,0,0
        DS.L 0
        dc.l EXECU,L009_
L010_:
        dc.b 7,69,88,69,67,85,84,69
        DS.L 0
        dc.l BRAN,L008_
L009_:
        dc.b COMPO+6,98,114,97,110,99,104,0
        DS.L 0
        dc.l QBRAN,L007_
L008_:
        dc.b COMPO+7,63,98,114,97,110,99,104
        DS.L 0
        dc.l DONXT,L006_
L007_:
        dc.b COMPO+4,110,101,120,116,0,0,0
        DS.L 0
        dc.l DOLST,L005_
L006_:
        dc.b COMPO+6,100,111,76,73,83,84,0
        DS.L 0
        dc.l DOLIT,L004_
L005_:
        dc.b COMPO+5,100,111,76,73,84,0,0
        DS.L 0
        dc.l STOIO,L003_
L004_:
        dc.b 3,33,73,79
        DS.L 0
        dc.l TXSTO,L002_
L003_:
        dc.b 3,84,88,33
        DS.L 0
        dc.l QRX,L001_
L002_:
        dc.b 3,63,82,88
        DS.L 0
        dc.l BYE,0000
L001_:
        dc.b 3,66,89,69
        END 
