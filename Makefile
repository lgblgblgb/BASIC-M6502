MAPFILE	= m6502.map
SYMFILE = m6502.sym
LSTFILE	= m6502.lst
DIFFFILE= m6502-changes.diff
BIN	= m6502.bin
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

publish: $(BIN)
	cp $(BIN) $(LSTFILE) $(SYMFILE) bin/

bin/$(BIN) bin/$(LSTFILE) bin/$(SYMFILE): $(BIN) $(ALLDEPS)
	$(MAKE) publish

simulator: bin/$(BIN) bin/$(LSTFILE) bin/$(SYMFILE) $(ALLDEPS)
	$(PYTHON) simulator.py bin/$(BIN)

clean:
	rm -f $(MAPFILE) $(SYMFILE) $(LSTFILE) $(DIFFFILE) $(BIN) $(SRC65).tmp

.PHONY: all clean simulator publish
