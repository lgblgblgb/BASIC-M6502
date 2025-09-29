# NOTE: actual start addresses do not mater too much, as the source
# uses "ORG" based on its internal definitions, so it would be hard
# to put those here.
# The only trick here is to throw anything which is put into the
# the "RAM" segment, and only "ROM" will generate the output, see
# the "file = ..." parts.

MEMORY {
	ZP:		file = "", start = $0002, size = $00FE;
	RAM:		file = "", start = $0200, size = $1000;
	ROM:		file = %O, start = $2000, size = $8000;
}
SEGMENTS {
	ZEROPAGE:	load = ZP,  type = zp, optional = yes;
	RAM:		load = RAM, type = rw, optional = yes;
	ROM:		load = ROM, type = rw;
}
