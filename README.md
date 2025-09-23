## The project

This project meant to be a conversion of Microsoft's open sourced (under the
MIT license) 6502 BASIC to a modern 6502 assember (CA65). Of course this
project of mine is also MIT licensed, based on Microsoft's MIT licensed
original source.

--- [ WARNING ! WARNING ] --------------------------------------------------
This is WIP stage. The result won't even assemble, or even if it does, won't
run correctly on a 6502 system. Once I hit the point to have usable result,
I'll remove this warning section.
--- [ WARNING ! WARNING ] --------------------------------------------------

(C)1978 MICRO-SOFT (the original source)
(C)2025 Gabor Lenart (lgb) - the conversion project of mine

## Useful information

Microsoft's 6502 BASIC repository: https://github.com/microsoft/BASIC-M6502

My findings about the original assembly source, the syntax and assember used by MICRO-SOFT: README-ASM.md

Original readme from Microsoft: https://github.com/microsoft/BASIC-M6502/blob/main/README.md

(By the way, "MICRO-SOFT" is intentional, as they used the name this way in 1978. I try to
be consistent and use MICRO-SOFT when I talk about the source from 1978, and Microsoft, when
we talk about the current Microsoft who released the source. Of course Microsoft - and probably
also MICRO-SOFT - is a registered trendmark owned by Microsoft, ... sorry, IANAL).

## Files

* `m6502-orig-really.asm` - the original assembly source from MICRO-SOFT
* `m6502-orig.asm` - my "hand modified" version of the above, to easy the task of the converter script, which does not do a full automated conversion
* `m6502-converted.asm` - the result assembly file from my conversion, which should be assembled with CA65
* `converter.py` - my VERY ugly converter, under constant hacking and rewriting/experimenting - does a "half job", manual work is needed before (see above the comment on file `m6502-orig.asm`)

## Assembly process

Simply say `make`, if all the needed tools are installed. What you need:

* standard UNIX or UNIX-like environment, with the usual common tools/utilities
* `CC65` suite installed (including `CA65` assembler and it's `CL65` frontend)
* Python3 for the converter utility
* GNU make (probably BSD make would work as well, I am not sure)

If needed, `Makefile` can be customized.
