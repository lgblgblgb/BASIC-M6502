MAPFILE	= m6502.map
LSTFILE	= m6502.lst
DIFFFILE= m6502-changes.diff
BIN	= m6502.bin
BINTMP	= m6502-uncut.bin
SRCOLD	= m6502-orig-really.asm
SRC	= m6502-orig.asm
SRC65	= m6502-converted.asm
CL65	= cl65
CL65OPTS= -t none --listing $(LSTFILE) --mapfile $(MAPFILE)
PYTHON	= python3
ALLDEPS	= Makefile converter.py cutter.py

all:
	$(MAKE) $(BIN)

$(SRC65): $(SRC) macros.inc $(ALLDEPS)
	rm -f $@.tmp
	$(PYTHON) converter.py $< > $@.tmp
	mv $@.tmp $@
	diff -u $(SRCOLD) $@ > $(DIFFFILE) || true

$(BINTMP): $(SRC65) $(ALLDEPS)
	$(CL65) $(CL65OPTS) -o $@ $<

$(BIN): $(BINTMP) $(ALLDEPS)
	$(PYTHON) cutter.py $< $@

publish: $(BIN) $(BINTMP)
	cp $(BIN) $(BINTMP) $(LSTFILE) bin/

bin/$(BINTMP) bin/$(LSTFILE): $(BIN) $(ALLDEPS)
	$(MAKE) publish

simulator: bin/$(BINTMP) bin/$(LSTFILE) $(ALLDEPS)
	$(PYTHON) simulator.py bin/$(BINTMP) bin/$(LSTFILE)

clean:
	rm -f $(MAPFILE) $(LSTFILE) $(DIFFFILE) $(BIN) $(BINTMP) $(SRC65).tmp

.PHONY: all clean simulator publish
