# The project

This project meant to be a conversion of Microsoft's open sourced (under the
MIT license) 6502 BASIC to a modern 6502 assember (CA65). Of course this
project of mine is also MIT licensed, based on Microsoft's MIT licensed
original source.

* (C)1976 MICRO-SOFT (the original source)
* (C)2025 Gabor Lenart "LGB" - the conversion/modification/etc project of mine

Note: at least now initially, it's not the goal of the project to "modernize"
the source, what I try is to be able to be assembled with a modern assembler
(CA65) but trying to preserve as many "old/original style" of the source as
possible. Clearly, there is room to make it much more clear at many-many
places, but it's not on my radar (yet).

Also, I have some experimental simulation stuff included to run the ROM.

TL;DR what you want to check out here is `m6502-converted.asm`, but first:

## WARNING

This is WIP stage. The result won't even assemble, or even if it does, won't
run correctly on a 6502 system. Once I hit the point to have usable result,
I'll remove this warning section.

## Useful information

Microsoft's 6502 BASIC repository: https://github.com/microsoft/BASIC-M6502

Original readme from Microsoft: https://github.com/microsoft/BASIC-M6502/blob/main/README.md

(By the way, "MICRO-SOFT" is intentional, as they used the name this way in 1976-78. I try to
be consistent and use MICRO-SOFT when I talk about the source from ~1978, and Microsoft, when
we talk about the current Microsoft who released the source. Of course Microsoft - and probably
also MICRO-SOFT - is a registered trendmark owned by Microsoft, ... sorry, IANAL).

## Files

* `m6502-orig-really.asm` - the original assembly source from MICRO-SOFT
* `m6502-orig.asm` - my "hand modified" version of the above, to easy the task of the converter script, which does not do a full automated conversion
* `m6502-converted.asm` - the result assembly file from my conversion, which should be assembled with CA65
* `converter.py` - my VERY ugly converter, under constant hacking and rewriting/experimenting - does a "half job", manual work is needed before (see above the comment on file `m6502-orig.asm`)
* `cutter.py` - cuts the final binary, see the "in depth" section's "link" sub-section ... Quite unfortunate ...

## Assembly process

Simply say `make`, if all the needed tools are installed. What you need:

* standard UNIX or UNIX-like environment, with the usual common tools/utilities
* `CC65` suite installed (including `CA65` assembler and it's `CL65` frontend)
* `Python3` for the converter utility
* GNU `make` (probably BSD make would work as well, I am not sure)

If needed, `Makefile` can be customized.

## Simulation

The original MACRO-10 assembly source suggests that there was a "SIMULATION"
mode when the development PDP-10 emulated 6502. For that, the source must be
assembled with `REALIO=0`. I try to replicate this with a modern environment
by implementing a simulator; not for PDP-10 though, but in Python. It uses
py65emu, which you can install with `pip` (probably you need `pip3`):

    pip3 install py65emu

Also you need SDL2 bindings:

    pip3 install PySDL2

After that, you can use the "simulate" target in the `Makefile`:

    make simulator

Notes:

* I call it "simulator" or "simulation" not "emulator". This is because the
original jargon used by the MS asm source.
* Since it's written in Python, it's quite slow ... It's not intended to be
a good general purpose emulator (oops, simulator ...), just to catch problems
with my conversion.

## In-depth details about the conversion and the original assembly source

My findings and guess-work on the assembler and assembly syntax used
by MICRO-SOFT to write 6502 MBASIC. Warning: I can be easily wrong here,
or at least my explanation is not very precise.

As far as I can guess, the original assembler used by MICRO-SOFT was MACRO-10
running on a PDP-10 machine. However, MACRO-10 is a PDP assembler, it does
not know about 6502 at all. What MICRO-SOFT probably did: they wrote a macro
pack implementing 6502 opcodes. Unfortunately, there is no information about
that extra "pack". This would also explain why there are some odd choices,
like these examples:

* `LDAI  0` instead of `LDA #0`
* `LDADY addr` instad of `LDA (addr),Y`

These kind of solution were needed (IMHO), because MACRO-10 wouldn't accept
`#` in a sane way as macro parameter, also `(`,`)` in the second example would
be considered as an illegal syntax in MACRO-10 (probably). So it seems, any
"standard" 6502 assembly syntax which had things like `#`, `(`, `)` as part of
the syntax had to be solved differently.

How do I know it was MACRO-10? I cannot know for sure, just guessing. After
searching the web for assembler directives used in the source, I had the
conclusion that maybe it was MACRO-10. Just by have a look on some MACRO-10
assembly sources then, it was quite clear, that it should be that, or at
least very close. The source also has a "REALIO target" called "SIMULATION"
and some conditional assembly statements in that case uses "strange" opcodes
which - after some search - turned out to be PDP-10 assembly instructions
(I'm not too familiar with PDP-10 and PDP-11 but now it seems it should have
been PDP-10 rather than PDP-11 because of the "HRLI" opcode).
Also, I wouldn't ever think a PDP-10 assembler knows about 6502. Combined
this with some "strange" syntax like "LDAI", I had the conclusion, that they
are just macros, basically implementing a "kind of" 6502 assembler based on
MACRO-10's macro capabilities. Again: this is guess-work from my side, I
can be wrong ...

(BREAKING NEWS: Oh, stupid me, it's right there in the source released by MS:
`0=PDP-10 SIMULATING 6502`, so indeed, it's a PDP-10)

Other than those above, MACRO-10 has a very strange syntax from today's
point of view.

For example `<...>` were used as `(...)` in expressions but also for
marking blocks for a `DEFINE` or `REPEAT`. This is a pattern with MACRO-10,
many things used for multiple purposes, and hard to tell the actual meaning.
This also means, a fully automated converter is harder to be written, thus
my choice to use a semi-automated approach: I have some manually massaged
source (`m6502-orig.asm`) which couldn't be compiled neither MACRO-10
nor CA65. It's just an intermediate step, to help my converter to be really
simple (sort of ...) and trivial.

Also "naked" numbers in the source are translated to directly emitting byte
into the output file:

* `0` means `.BYTE 0`
* `SYM` means `.BYTE SYM`
* `LABEL: SYM` means `LABEL: .BYTE SYM`

There are other very confusing things as well, like the `EXP` directive. I
couldn't find a clear meaning of this MACRO-10 directive, but it seems it
has dual purpose:

* it can emit bytes: `EXP 10,20` meaning `.BYTE 10,10`
* but also to mark a symbol exported for the linking stage (maybe)

About labels/symbols: it seems, MACRO-10 had the limitation of the names
to be 6 characters. So `RESTORE` is same as `RESTOR` since only the first
6 characters of symbols/labels names are considered at all.

6502 BASIC uses lots of octal numbers, but in a strange way.
`^D12` syntax was used to denote for decimal numbers, `^O12` for octals.
`RADIX` directive can set the _default_ what is used for un-prefixed
numbers (no `^D` etc prefix). A strange example from me:

    RADIX 10
    table1: 20, 30, 88, ^D10, ^O10
    RADIX 8
    table2: 20, 30, 88, ^D10, ^O10

`table1` will contain bytes `20`, `30`, `88`, `10`, `8`. `table2` is much
more tricky: `20` will be considered as an octal number, so it will mean
decimal `16`. `30` is again considered as an octal number, meaning `24`
in decimal. Now the odd part: `8` - according to the rules - must be
considered an octal number after `RADIX 8`, however `88` is not valid
in octal, since only digits `0...7` are only allowed there. In this
case - my assumption - MACRO-10 silently treat it as decimal, leaving
it decimal (regardless of the naked-number must be in `RADIX`) thus `88`.
`^D10` and `^O10` mean the same as in `table1` though, as they have
prefixes which overrides the default `RADIX` anyway.

There are very strange things in the source, like this monster, try
to guess what is does:

    DEFINE  DT(Q),<
    IRPC    Q,<IFDIF <Q><">,<EXP "Q">>>

Actually `IRPC` seems to iterate over characters. `IFDIF` assembles
the third argument if the first and second are different. So a line
like this:

    DT"text"

will be processed to interate over `"text"` (including the `"`
signs), and if it's not `"` it emits that character into the output
binary. So basically what this ugly macro does, is the same as CA65
would do with: `.BYTE "text"`

Other oddity is the pass controlled process. MACRO-10 seems to be
a two pass assembler, but it's not smart enough to do all the tricks
like referencing a symbol defined later. So, a trick like this is
used:

    IF1,<
    MRCHR:  LDA     60000,X,>
    IF2,<
    MRCHR:  LDA     SINCON+36,X,>

`IF1` and `IF2` only considers the `<...>` block if the assembler
in pass-1 or pass-2 phase. In pass-1 phase, a dummy constant `60000`
is used as the placeholder. In pass2 however, the symbol is already
known, so the proper address can be used. One must be careful to
have the pass-1 variant otherwise identical, ie same number of bytes,
otherwise it would cause massive problems.

The example above also shows the typical extra `,` at the end of the
opcode for whatever reason.

MACRO-10 seems to have reassingable symbols. It looks like the syntax
`SYM = 10` defines a symbol with value of `10`, and `SYM == 10` does
this in a way that it's re-definable. My idea here, that I simply
replace `==` with `.SET` for CA65.

### Link it ...

The final major problem, that probably some kind of linking phase was
done. But we don't have ANY information about the linker config as
we don't have any "macro pack" for MACRO-10 either :(

What's the problem? Well, it's quite interesting. It's mainly about
relocatable code. In modern CA65 way, we usually create a segment with
different "LOAD" and "RUN" address. Surely, the code must relocate
the code based on that information. Anyway, M6502 BASIC does something
horrific: it acually codes the same routine TWICE. In the real place
(RAM routine) and in ROM too, so ROM can copy to RAM. The danger here,
that those two copies must be identical, though one is a "place holder",
labels and the code length must much, also with non-ROM-able code,
the role is different. So indeed, it's a very sensitive and hard to
follow code in general.

This alone is not even the problem, but a modern assembler wouldn't
understand the two copies being one actually. I have the suspect that
the missing "linkage" phase would solve the problem in the original
development environment.

Since I don't know the details, I used an ugly trick: just before
the "real" ROM starts in the source, I put a placeholder ID string
to be in the output binary. And an external python script - cutter.py -
will cut the binary till that point.

The normal solution would be, to remove the duplicated routine, t put
it into a segment, etc etc. But my goal here is try to preserve the
original source as much as possible even if it's a horrofic thing
as its own ... Also that solution will cause to loose the ability
to build exact image (hopefully) as MACRO-10 would be, since in
different segment, the placement would be different.
