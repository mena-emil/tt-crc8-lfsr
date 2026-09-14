# SPDX-License-Identifier: Apache-2.0

"""
Cocotb testbench for the CRC-8 serial LFSR project.

This reproduces the behaviour of the original CRC_TB.v testbench
(reset -> shift 1 byte of DATA in LSB-first while ACTIVE -> wait for
Valid -> shift 8 CRC bits out) but drives the design through the
standard TinyTapeout tt_um pin interface:

    ui_in[0]  = DATA
    ui_in[1]  = ACTIVE
    uo_out[0] = CRC
    uo_out[1] = Valid

Test vectors are read from DATA_h.txt / Expec_Out_h.txt, the same
files used by the assignment's original testbench.
"""

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

CLK_PERIOD_NS = 100  # 10 MHz, per assignment spec

DATA_FILE = os.path.join(os.path.dirname(__file__), "DATA_h.txt")
EXPEC_FILE = os.path.join(os.path.dirname(__file__), "Expec_Out_h.txt")


def _read_hex_bytes(path):
    with open(path) as f:
        return [int(line.strip(), 16) for line in f if line.strip()]


async def reset_dut(dut):
    """Mirrors the `reset` task in CRC_TB.v: pulse rst_n low for one
    clock, then back high, then wait one more clock."""
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


async def load_data(dut, data_byte):
    """Mirrors the `data_ld` task: shift DATA in LSB-first while
    ACTIVE (ui_in[1]) is held high."""
    for i in range(8):
        bit = (data_byte >> i) & 1
        dut.ui_in.value = (1 << 1) | bit  # ACTIVE=1, DATA=bit
        await RisingEdge(dut.clk)
    dut.ui_in.value = 0  # ACTIVE=0, DATA=0


async def check_crc_out(dut, expected_byte, test_num):
    """Mirrors the `chk_crc_out` task: wait for the rising edge of
    Valid (uo_out[1]), then sample CRC (uo_out[0]) for 8 clocks.

    Note: cocotb's RisingEdge trigger resumes *after* the DUT's
    registers have updated for that edge, so the first CRC bit is
    already present on uo_out at the same edge that Valid is first
    seen high (unlike the original Verilog testbench's `#delay`
    sampling, which effectively samples the pre-update value at the
    same simulation time). This ordering was verified bit-for-bit
    against all 10 provided test vectors.
    """
    prev_valid = int(dut.uo_out.value) >> 1 & 1
    while True:
        await RisingEdge(dut.clk)
        cur_valid = int(dut.uo_out.value) >> 1 & 1
        if cur_valid == 1 and prev_valid == 0:
            break
        prev_valid = cur_valid

    gener_out = 0
    for i in range(8):
        bit = int(dut.uo_out.value) & 1
        gener_out |= bit << i
        if i < 7:
            await RisingEdge(dut.clk)

    assert gener_out == expected_byte, (
        f"Test case {test_num} FAILED: got CRC=0x{gener_out:02X}, "
        f"expected 0x{expected_byte:02X}"
    )
    dut._log.info(
        f"Test case {test_num}: PASSED (CRC = 0x{gener_out:02X})"
    )


@cocotb.test()
async def test_crc8_lfsr(dut):
    dut._log.info("Starting CRC-8 LFSR test")

    clock = Clock(dut.clk, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start())

    # Initialization (mirrors `initialize` task)
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    data_bytes = _read_hex_bytes(DATA_FILE)
    expected_bytes = _read_hex_bytes(EXPEC_FILE)
    assert len(data_bytes) == len(expected_bytes) == 10, (
        "Expected 10 test cases in DATA_h.txt / Expec_Out_h.txt"
    )

    for test_num, (data_byte, expected_byte) in enumerate(
        zip(data_bytes, expected_bytes)
    ):
        await reset_dut(dut)
        await load_data(dut, data_byte)
        await check_crc_out(dut, expected_byte, test_num)

    await ClockCycles(dut.clk, 5)
    dut._log.info("All 10 test cases completed")
