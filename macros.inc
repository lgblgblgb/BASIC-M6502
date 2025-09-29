.MACRO	ORG	addr
	.ORG	addr
.ENDMACRO

.MACRO	BLOCK	n
	.RES	n
.ENDMACRO


.DEFINE	ADR(W)	.WORD	W

.MACRO	DT	txt
	.BYTE	txt
.ENDMACRO

.MACRO	REPEAT	n,what
	.REPEAT	n
		what
	.ENDREPEAT
.ENDMACRO


; Guessing: EXP emits a byte, however it was removed to EXPOP not to collide with EXP as a label ...
.MACRO	EXPOP	n
	.BYTE	n
.ENDMACRO

.MACRO  LDADY	addr
	LDA	(addr),Y
.ENDMACRO

.MACRO  STADY	addr
	STA	(addr),Y
.ENDMACRO

.MACRO	SBCDY addr
	SBC	(addr),Y
.ENDMACRO

.MACRO	CMPDY	addr
	CMP	(addr),Y
.ENDMACRO

.MACRO	ADCDY	addr
	ADC	(addr),Y
.ENDMACRO

.MACRO	JMPD	addr
	JMP	(addr)
.ENDMACRO

; ---- Only for the simulation target ---

IO_START_ADDR = $D000

.MACRO	SIM_INSIM
	JSR	LGB_INSIM
.ENDMACRO

.MACRO	SIM_OUTSIM
	STA	IO_START_ADDR + 0
.ENDMACRO

.MACRO SIMULATION_TARGET_ROUTINES
; Was missing from the source: CZGETL = SIM_CZGETL_ADDR if REALIO = 0 (simulation)
; That was $FFE4 for COMMODORE target, meaning KERNAL routine "GET".
; No idea about the difference from "INSIM" ...
; However, this is a label, so a routine should be put somewhere, and RTS from it?
SIM_CZGETL_ADDR:
	LDA	$D000
	CLC
	RTS

LGB_INSIM:
	LDA	$D000
	CMP	#0
	BEQ	LGB_INSIM
	CLC
	RTS
.ENDMACRO
