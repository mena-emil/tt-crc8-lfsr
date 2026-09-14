# Makefile
include $(shell cocotb-config --makefiles)/Makefile.sim

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Design sources (add project.v and every file listed under
# info.yaml -> project -> source_files)
PROJECT_SOURCES = tt_um_crc8_lfsr.v CRC.v

ifneq ($(GATES),yes)
# RTL simulation:
SIM_BUILD				= sim_build/rtl
VERILOG_SOURCES += $(PWD)/tb.v
# Source files listed relative to the src directory:
VERILOG_SOURCES += $(addprefix $(PWD)/../src/,$(PROJECT_SOURCES))
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -I$(PWD)/../src
else
# Gate level simulation:
SIM_BUILD				= sim_build/gl
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/ihp-sg13g2/libs.ref/sg13g2_stdcell/verilog/sg13g2_stdcell.v
VERILOG_SOURCES += $(PWD)/tb.v
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v
endif

# Must match info.yaml -> top_module
TOPLEVEL = tb

# MODULE is the basename of the Python test file
MODULE = test

include $(shell cocotb-config --makefiles)/Makefile.sim
