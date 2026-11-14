// ============================================================================
//  paragon_x.v  -  CPLD do interposer do PARAGON 50 (Tabajara Labs)
//  Alvo: Altera EPM7128S (PLCC-84), 5 V, Quartus II 13.0sp1
//
//  Funcoes:
//    1) Bloqueia /AS, /UDS, /LDS para a placa original nas janelas novas
//       (a placa enxerga o barramento parado e nao responde).
//    2) SRAM 2 x 512K x 8 = 1 MB em $100000-$1FFFFF (sem wait state).
//    3) Registradores (byte, enderecos IMPARES) em $200001 + 2*n:
//         LCD 20x4 (4 bits), beeper, SD por SPI em hardware, encoder.
//    4) Strobes /CSR e /CSW do VDP TMS9118 em $300001 (dado) e $300003
//       (registrador); MODE do VDP vem direto de A1 da CPU.
//    5) Junta o /DTACK da placa com o /DTACK proprio (AND dos ativos-baixo).
//
//  Mapa (A23..A20):   0001 = SRAM    0010 = registradores    0011 = VDP
//  A19..A4 sao "don't care" nos blocos de registradores e VDP (espelhos).
// ============================================================================
module paragon_x (
    input  wire       clk,          // CLK do 68000 (8 MHz) - pino global
    input  wire       rst_n,        // /RESET do 68000
    // enderecos do 68000 (lado CPU)
    input  wire       a1, a2, a3,
    input  wire       a20, a21, a22, a23,
    // controle do 68000 (lado CPU)
    input  wire       as_n, uds_n, lds_n, rw,
    input  wire       dtack_brd_n,  // /DTACK que vem da placa original
    // para a placa original
    output wire       as_brd_n, uds_brd_n, lds_brd_n,
    // para o 68000
    output wire       dtack_cpu_n,
    // SRAM (WE vai direto do R/W da CPU)
    output wire       ram_ceh_n, ram_cel_n, ram_oe_n,
    // VDP TMS9118
    output wire       vdp_csr_n, vdp_csw_n,
    input  wire       vdp_int_n,
    // barramento de dados D0-D7 (byte baixo, enderecos impares)
    inout  wire [7:0] d,
    // Smart Controller - EXP1
    output wire       beep,         // EXP1-1 (ativo alto)
    output wire       lcd_e,        // EXP1-3
    output wire       lcd_rs,       // EXP1-4
    output wire       lcd_d4,       // EXP1-5
    output wire       lcd_d5,       // EXP1-6
    output wire       lcd_d6,       // EXP1-7
    output wire       lcd_d7,       // EXP1-8
    input  wire       enc_btn_n,    // EXP1-2 (botao do encoder, ativo baixo)
    // Smart Controller - EXP2
    input  wire       sd_miso,      // EXP2-1
    output wire       sd_sck,       // EXP2-2
    input  wire       enc_a,        // EXP2-3
    output wire       sd_cs_n,      // EXP2-4
    input  wire       enc_b,        // EXP2-5
    output wire       sd_mosi,      // EXP2-6
    input  wire       sd_det_n,     // EXP2-7 (cartao presente = 0)
    input  wire       kill_n        // EXP2-8 (botao RESET do controlador)
);
    // ------------------------------------------------------------------
    //  Decodificacao de blocos
    // ------------------------------------------------------------------
    wire blk_ram = ~a23 & ~a22 & ~a21 &  a20;   // $100000-$1FFFFF
    wire blk_reg = ~a23 & ~a22 &  a21 & ~a20;   // $200000-$2FFFFF
    wire blk_vdp = ~a23 & ~a22 &  a21 &  a20;   // $300000-$3FFFFF
    wire blk_new = blk_ram | blk_reg | blk_vdp;

    // a placa original so enxerga ciclos fora das janelas novas
    assign as_brd_n  = as_n  | blk_new;
    assign uds_brd_n = uds_n | blk_new;
    assign lds_brd_n = lds_n | blk_new;

    wire ds  = ~uds_n | ~lds_n;
    wire cyc = ~as_n & ds;

    // ------------------------------------------------------------------
    //  SRAM
    // ------------------------------------------------------------------
    wire ram_cyc = blk_ram & ~as_n;
    assign ram_ceh_n = ~(ram_cyc & ~uds_n);
    assign ram_cel_n = ~(ram_cyc & ~lds_n);
    assign ram_oe_n  = ~(ram_cyc & rw);

    // ------------------------------------------------------------------
    //  Registradores e VDP: periferico de 8 bits no byte baixo (/LDS)
    // ------------------------------------------------------------------
    wire reg_cyc = blk_reg & ~as_n & ~lds_n;
    wire vdp_cyc = blk_vdp & ~as_n & ~lds_n;
    assign vdp_csr_n = ~(vdp_cyc &  rw);
    assign vdp_csw_n = ~(vdp_cyc & ~rw);

    // wait states do VDP: DTACK so depois de VDP_WAIT clocks do ciclo
    localparam [2:0] VDP_WAIT = 3'd4;
    reg [2:0] vcnt;
    always @(posedge clk)
        vcnt <= vdp_cyc ? ((vcnt == 3'd7) ? vcnt : vcnt + 3'd1) : 3'd0;
    wire vdp_ack = vdp_cyc & (vcnt >= VDP_WAIT);

    // DTACK: baixo se a placa OU a logica nova reconhecer o ciclo
    wire our_ack = (((blk_ram | blk_reg) & cyc) | vdp_ack);
    assign dtack_cpu_n = dtack_brd_n & ~our_ack;

    // ------------------------------------------------------------------
    //  Escrita em registradores: um pulso por ciclo (amostra em posedge clk)
    // ------------------------------------------------------------------
    wire [2:0] idx = {a3, a2, a1};
    reg  wr_d;
    wire wr_act   = reg_cyc & ~rw;
    wire wr_pulse = wr_act & ~wr_d;
    always @(posedge clk) wr_d <= wr_act;

    reg [3:0] lcd_d_r;
    reg       lcd_rs_r, lcd_e_r, beep_r, sdcs_r, fast_r;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            lcd_d_r <= 4'd0; lcd_rs_r <= 1'b0; lcd_e_r <= 1'b0;
            beep_r  <= 1'b0; sdcs_r   <= 1'b1; fast_r  <= 1'b0;
        end else if (wr_pulse) begin
            case (idx)
                3'd0: begin lcd_d_r <= d[3:0]; lcd_rs_r <= d[4];
                            lcd_e_r <= d[5];   beep_r   <= d[6]; end
                3'd1: begin sdcs_r  <= d[0];   fast_r   <= d[1]; end
                default: ;
            endcase
        end
    end

    // ------------------------------------------------------------------
    //  SPI em hardware (modo 0, MSB primeiro)
    //  lento: SCK = CLK/32 (250 kHz com CLK de 8 MHz); rapido: CLK/4 (2 MHz)
    // ------------------------------------------------------------------
    reg        busy, sck;
    reg  [4:0] cnt;
    reg  [3:0] bits;
    reg  [7:0] txs, rxs, rxd;
    wire [4:0] half      = fast_r ? 5'd1 : 5'd15;
    wire       spi_start = wr_pulse & (idx == 3'd2) & ~busy;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            busy <= 1'b0; sck <= 1'b0; cnt <= 5'd0; bits <= 4'd0;
            txs  <= 8'hFF; rxs <= 8'd0; rxd <= 8'd0;
        end else if (spi_start) begin
            txs <= d; bits <= 4'd0; cnt <= 5'd0; sck <= 1'b0; busy <= 1'b1;
        end else if (busy) begin
            if (cnt == half) begin
                cnt <= 5'd0;
                if (!sck) begin                    // borda de subida
                    sck  <= 1'b1;
                    rxs  <= {rxs[6:0], sd_miso};
                    bits <= bits + 4'd1;
                end else begin                     // borda de descida
                    sck <= 1'b0;
                    if (bits == 4'd8) begin
                        busy <= 1'b0;
                        rxd  <= rxs;
                    end else begin
                        txs <= {txs[6:0], 1'b1};
                    end
                end
            end else begin
                cnt <= cnt + 5'd1;
            end
        end
    end

    // ------------------------------------------------------------------
    //  Leitura de registradores
    // ------------------------------------------------------------------
    reg [7:0] rdata;
    always @* begin
        case (idx)
            3'd0:    rdata = {1'b0, beep_r, lcd_e_r, lcd_rs_r, lcd_d_r};
            3'd1:    rdata = {6'b000000, fast_r, sdcs_r};
            3'd2:    rdata = rxd;
            3'd3:    rdata = {6'b000000, ~sd_det_n, busy};
            3'd4:    rdata = {3'b000, ~vdp_int_n, ~kill_n, ~enc_btn_n, enc_b, enc_a};
            3'd5:    rdata = 8'h5A;     // identificacao
            3'd6:    rdata = 8'h01;     // versao do projeto
            default: rdata = 8'h00;
        endcase
    end
    assign d = (reg_cyc & rw) ? rdata : 8'bzzzzzzzz;

    // ------------------------------------------------------------------
    //  Saidas para o Smart Controller
    // ------------------------------------------------------------------
    assign beep    = beep_r;
    assign lcd_e   = lcd_e_r;
    assign lcd_rs  = lcd_rs_r;
    assign lcd_d4  = lcd_d_r[0];
    assign lcd_d5  = lcd_d_r[1];
    assign lcd_d6  = lcd_d_r[2];
    assign lcd_d7  = lcd_d_r[3];
    assign sd_cs_n = sdcs_r;
    assign sd_sck  = sck;
    assign sd_mosi = txs[7];
endmodule
