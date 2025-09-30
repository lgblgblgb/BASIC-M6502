MAPFILE	= m6502.map
SYMFILE = bin/m6502.sym
LSTFILE	= bin/m6502.lst
DIFFFILE= m6502-changes.diff
BIN	= bin/m6502.bin
SRCOLD	= m6502-orig-really.asm
SRC	= m6502-orig.asm
SRC65	= m6502-converted.asm
LDCFG	= m6502.ld
CL65	= cl65
CL65OPTS= -t none --config $(LDCFG) --listing $(LSTFILE) --mapfile $(MAPFILE) -Ln $(SYMFILE)
PYTHON	= python3
ALLDEPS	= Makefile converter.py

all:
	$(MAKE) $(BIN)

$(SRC65): $(SRC) macros.inc $(ALLDEPS)
	rm -f $@.tmp
	$(PYTHON) converter.py $< > $@.tmp
	mv $@.tmp $@
	diff -u $(SRCOLD) $@ > $(DIFFFILE) || true

$(BIN): $(SRC65) $(ALLDEPS)
	$(CL65) $(CL65OPTS) -o $@ $<

simulator:
	$(PYTHON) simulator.py $(BIN)

clean:
	rm -f $(SRC65).tmp $(DIFFFILE) $(MAPFILE) *.o

.PHONY: all clean simulator publish
