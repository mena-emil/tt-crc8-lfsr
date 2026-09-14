<!--
Replace <YOUR_USERNAME>/<YOUR_REPO> in the badge URLs below with your
actual GitHub username and repo name once you've created the repo.
-->

## CRC-8 Serial LFSR

[![GDS](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/gds.yaml/badge.svg)](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/gds.yaml)
[![Docs](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/docs.yaml/badge.svg)](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/docs.yaml)
[![Test](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/test.yaml/badge.svg)](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/test.yaml)

A Tiny Tapeout project implementing an 8-bit **Linear Feedback Shift
Register (LFSR)** used as a serial **CRC-8** generator/checker, seeded
with `8'hD8`, matching the "Assignment 5.0" specification.

## How it works

The design is a classic Galois-style LFSR built from 8 registers
(`R7..R0`) with two internal XOR feedback taps — one between `R7`/`R6`,
one between `R3`/`R2`. The feedback signal is:

```
Feedback = DATA_in XOR R0
```

**Loading a byte (ACTIVE high):** one bit of `DATA` is shifted in per
clock, LSB first, and XORed into the feedback path at both tap points and
at the register's input (`R7`). After 8 clocks, the register holds the
8-bit CRC remainder for that byte.

**Reading out the CRC (ACTIVE low):** the register simply shifts itself
out serially for 8 clocks, `R0` first, while `Valid` stays high to mark
the output as meaningful. `Valid` drops low again once all 8 bits have
been shifted out.

| Signal   | Width | Purpose                                          |
| -------- | ----- | ------------------------------------------------- |
| DATA     | 1-bit | Serial data input, LSB first                       |
| ACTIVE   | 1-bit | High while a data byte is being shifted in          |
| LFSR     | 8-bit | Shift register, seeded to `8'hD8` on reset          |
| CRC      | 1-bit | Serial CRC output, R0 first                         |
| Valid    | 1-bit | High for exactly 8 clocks while CRC bits shift out   |

## Repository structure

```
src/tt_um_crc8_lfsr.v   Tiny Tapeout top module: tt_um_crc8_lfsr
src/CRC.v                CRC/LFSR core (registers, feedback taps, output counter)

test/tb.v                Cocotb wrapper
test/test.py              Cocotb test, replays the assignment's 10 test vectors
test/DATA_h.txt           Test data bytes (10 cases)
test/Expec_Out_h.txt      Expected CRC bytes (10 cases)
test/Makefile             Runs the simulation with Icarus Verilog + cocotb

docs/info.md              Tiny Tapeout project documentation
info.yaml                  Tiny Tapeout project/pinout metadata
```

## Pins

```
ui_in[0]     DATA   - serial data in, LSB first
ui_in[1]     ACTIVE - high while DATA is being shifted in
ui_in[7:2]   unused

uo_out[0]    CRC    - serial CRC bit out, R0 first
uo_out[1]    Valid  - high while CRC bits are being shifted out
uo_out[7:2]  unused, driven low

uio[7:0]     unused (all configured as inputs)

clk          10 MHz intended operating frequency
rst_n        active-low async reset - matches the original design's RST directly
```

## How to test

The automated Cocotb test is in `test/test.py`:

```
cd test
python -m pip install -r requirements.txt
make
```

The test resets the design, shifts each of the 10 provided data bytes in
LSB-first while ACTIVE is held high, waits for Valid, and checks the 8 CRC
bits shifted out against the expected value from `Expec_Out_h.txt`. All 10
cases should report `PASSED`.

## External hardware

None. This project only uses the TinyTapeout dedicated I/O pins — no PMOD,
display, or other external hardware is required, in simulation or on the
fabricated chip.

## Project info

|                |                     |
| -------------- | ------------------- |
| **Title**      | CRC-8 Serial LFSR    |
| **Language**   | Verilog              |
| **Clock**      | 10 MHz               |
| **Tiles**      | 1x1                  |
| **Top module** | `tt_um_crc8_lfsr`    |

**Author:** Mena Emil

See [`docs/info.md`](docs/info.md) for the full write-up.
