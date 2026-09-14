/*
 * Copyright (c) 2026 Mena Emil
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// TinyTapeout top module. Wraps the CRC (src/CRC.v) LFSR core with the
// standard tt_um pin interface. This name must match exactly in:
//   - info.yaml   (top_module:)
//   - test/tb.v   (module instantiation)
module tt_um_crc8_lfsr (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 1=output, 0=input)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // ---------------------------------------------------------------
    // Pin mapping
    //   ui_in[0]  -> DATA   (serial data in, LSB first)
    //   ui_in[1]  -> ACTIVE (high while shifting DATA in)
    //   ui_in[7:2] -> unused
    //   uo_out[0] -> CRC    (serial CRC bits out, MSB first per spec)
    //   uo_out[1] -> Valid  (high while CRC bits are being shifted out)
    //   uo_out[7:2] -> unused, driven low
    //   uio        -> unused, all set as inputs (oe = 0)
    // ---------------------------------------------------------------

    wire crc_bit;
    wire valid_bit;

    CRC #(.SEED(8'hD8)) crc_inst (
        .CLK    (clk),
        .RST    (rst_n),        // rst_n is active-low, matches CRC's active-low async RST
        .DATA   (ui_in[0]),
        .ACTIVE (ui_in[1]),
        .CRC    (crc_bit),
        .Valid  (valid_bit)
    );

    assign uo_out  = {6'b0, valid_bit, crc_bit};
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, ui_in[7:2], uio_in, 1'b0};

endmodule
