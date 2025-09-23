My findings and guess-work on the assembler and assembly syntax used
by Micro-soft to write 6502 MBASIC. Warning: I can be easily wrong here,
or at least my explanation is not very precise.

(C)1978 MICRO-SOFT (the original source)
(C)2025 Gabor Lenart (lgb) - the conversion project of mine

As far as I can guess, the original assembler used by Microsoft was MACRO-10
running on a PDP-11 machine. However, MACRO-10 is a PDP assembler, it does
not know about 6502 at all. What Microsoft probably did: they wrote a macro
pack implementing 6502 opcodes. Unfortunately, there is no information about
that extra "pack". This would also explain why there are some odd choices,
like these examples:

* `LDAI  0` instead of `LDA #0`
* `LDADY addr` instad of `LDA addr,Y`

These kind of solution were needed (IMHO), because MACRO-10 wouldn't accept
`#` in a sane way as macro parameter, also `,Y` in the second example would
be considered as an extra parameter to the `LDA` macro. So it seems, any
"standard" 6502 assembly syntax which had things like `#`, `,` as part of
the syntax had to be solved differently.

Other than that, MACRO-10 has a very strange syntax from today's point of
view.

For example `<...>` were used as `(...)` in expressions but also for
marking blocks for a `DEFINE` or `REPEAT`.

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

