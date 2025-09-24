#!/usr/bin/env python3


import sys


# (C)2025 Gabor Lenart "LGB" - lgblgblgb@gmail.com

# WARNING - WARNING: this is really ugly python code, basically I am experimenting with it, without any sanity to have nice code or anything
# at least at this early point of the project ...


if len(sys.argv) != 3:
    raise RuntimeError("Bad usage.")

with open(sys.argv[1], "rb") as f:
    rom = f.read()




ID=b'{{CUT#HERE}}'

pos = rom.find(ID)

loc  = rom[pos + len(ID) + 0] + (rom[pos + len(ID) + 1] * 256)
init = rom[pos + len(ID) + 2] + (rom[pos + len(ID) + 3] * 256)
ioad = rom[pos + len(ID) + 4] + (rom[pos + len(ID) + 5] * 256)
rio  = rom[pos + len(ID) + 6]
rest = pos + len(ID) + 7

print(f"Position={pos} ROMLOC={loc:04X} INIT={init:04X} REALIO={rio} IO=${ioad:04X}")

rom = rom[rest:]

rom = rom.rstrip(b'\x00')

with open(sys.argv[2], "wb") as f:
    f.write(rom)




