#!/usr/bin/env python3


import re, sys


# (C)2025 Gabor Lenart "LGB" - lgblgblgb@gmail.com

# my VERY ugly converter, under constant hacking and rewriting/experimenting - does a "half job", manual work is needed before on the original source
# WARNING - WARNING: this is really ugly python code, basically I am experimenting with it, without any sanity to have nice code or anything
# at least at this early point of the project ...

conv_errors = []



def convert_numbers(match):
    global radix
    global conv_errors
    # !!!! was group(1) !!!!
    s = match.group(0)
    #print(f"Convering: {s} while radix is {radix}")
    hx = False
    if s[0] == "^":
        if s[1] == "D":
            value = int(s[2:], 10)
        elif s[1] == "H":
            value = int(s[2:], 16)
            hx = True
        elif s[1] == "O":
            value = int(s[2:], 8)
            hx = True
        else:
            raise RuntimeError(f"Unknown ^B base in {s}")
    else:
        if radix == 10:
            value = int(s, 10)
        else:
            try:
                value = int(s, radix)
                hx = True
                if radix < 10 and value < radix:
                    hx = False
            except ValueError:
                value = int(s, 10)
                hx = False
                conv_errors.append(s)
    if hx:
        return '$' + format(value, "X")
    else:
        return str(value)


comment = ""
radix = 10


#line = "ez ^O66 az ^O55"
#re.sub(r'\^O([0-7]+)', convert_numbers, line)
#faszom()

emithelper = """
; (C)1976 MICRO-SOFT (the original source)
; (C)2025 Gabor Lenart "LGB" - the conversion/modification/etc project of mine to port this to CA65 assembler

.MACRO ORG n
.ORG n
.ENDMACRO

.DEFINE ADR(W) .WORD W

.MACRO DT txt
.BYTE txt
.ENDMACRO

.MACRO  REPEAT  n,what
.REPEAT n
what
.ENDREPEAT
.ENDMACRO

.MACRO  LDADY addr
;       LDADY --> LDA addr,Y
    LDA addr,Y
.ENDMACRO

.MACRO  STADY addr
;       STADY --> STA addr,Y
    STA addr,Y
.ENDMACRO

.MACRO  SBCDY addr
    SBC addr,Y
.ENDMACRO

.MACRO  CMPDY addr
    CMP addr,Y
.ENDMACRO

.MACRO  ADCDY addr
    ADC addr,Y
.ENDMACRO

.MACRO  JMPD addr
    JMP (addr)
.ENDMACRO


"""






with open(sys.argv[1]) as f:
    for line in f:
        line = line.rstrip()
        #print(line)
        if line and ord(line[0]) == 12:
            line = line[1:]
        if not line and emithelper:
            print(emithelper)
            emithelper = ""
        sep = line.split()
        if len(sep) == 2 and sep[0] == "COMMENT":
            print("")
            comment = sep[1].strip()
            continue
        if comment and line and line.startswith(comment):
            comment = ""
            print("")
            continue
        if comment:
            print("; " + line)
            continue
        if len(sep) > 1 and sep[0] == "RADIX":
            radix = int(sep[1])
            print("; " + line)
            continue
        if len(sep) > 0 and (sep[0] in ("PAGE", "SUBTTL", "TITLE", "SEARCH", "SALL") or sep[0].startswith("$")):
            print("; " + line)
            continue
        if re.match("^[>]+$", line.strip()):
            print("\n".join([".ENDIF"] * len(line.strip())))
            continue


        #extra = ""
        main = line.split(";", 1)
        main, aux = main[0], (";" + main[1] if len(main) > 1 else "")
        # ------------------------------
        main = re.sub(r",([\t ]*)$", r" \1", main)    # it seems some ops have comma at the end?!
        main = re.sub(r"(ADC|AND|CMP|CPX|CPY|EOR|LDA|LDX|LDY|ORA|SBC)I[\t ]+", r"\1\t#", main)

        main = re.sub(r'([\t ]#.*)"(.+)"(.*)$', r"\1'\2'\3", main)


        #main = re.sub(r'\^O([0-7]+)', convert_numbers, main)
        #main = re.sub(r'((\^[DO]){0,1}[0-7]+)', convert_numbers, main)
        #main = re.sub(r'\b(\^[OD])?\d+\b', convert_numbers, main)
        main = re.sub(r'\^(O|D)([0-7]+)', convert_numbers, main)       # for octal/decimal with prefix
        main = re.sub(r'\b\d+\b', convert_numbers, main)              # for unprefixed numbers

        main = re.sub(r"(^[\t ]*)([0-9]|[$][0-9A-F])", r".BYTE\t\2", main)
        main = re.sub(r":([\t ]*)([0-9]|[$][0-9A-F])", r":\1.BYTE \2", main)

        main = main.replace("==", " .SET ")

        main = re.sub(r"^[\t ]*IFE[\t ]+([^,]+)", r".IF\t\1 = 0", main)
        main = re.sub(r"^[\t ]*IFN[\t ]+([^,]+)", r".IF\t\1 != 0", main)

        main = re.sub(r"([\t :])BLOCK([\t ])", r"\1.RES\2", main)

        main = re.sub(r"XWD[\t ]+[^,]+,", r".BYTE\t", main)

        main = re.sub(r",([\t ]*)[<]([\t ]*)$", r"\1\2", main)

        #r = len(main.rstrip()) - len(main.rstrip().rstrip('>'))
        #if r:
        #    main =
        #    print(f"OK {r}")


        # the final stuff!!!
        main = main.replace("!=", "<>")

        # ------------------------------
        line2 = main + aux
        line2 = line2.rstrip()
        print(line2)
        #if extra:
        #    print(extra)

print("; --- CONV ERRORS ---\n; " + "\n; ".join(conv_errors))




