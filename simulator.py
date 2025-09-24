#!/usr/bin/env python3

# (C)2025 Gabor Lenart "LGB" - lgblgblgb@gmail.com
# WARNING - WARNING: this is really ugly python code, basically I am experimenting with it, without any sanity to have nice code or anything
# at least at this early point of the project ...

import sys
# You need py65emu, install it with: pip3 install py65emu
from py65emu.cpu import CPU


#from py65emu.mmu import MMU


class MyIO(object):
    def read(self, addr):
        return 0
    def write(self, addr, value):
        if addr == 0:
            value &= 127
            sys.stdout.write(chr(value))
            sys.stdout.flush()
        pass



class MyMMU(object):
    def __init__(self, mem, rom_start, rom_end, init, io_page_start, io):
        if len(mem) != 0x10000:
            raise RuntimeError("Memory backend must be exactly 64K long")
        if init < rom_start or init > rom_end:
            raise RuntimeError("init should be inside the ROM")
        if (io_page_start & 0xFF) != 0:
            raise RuntimeError("I/O page must be at page boundary!")
        self.io = io
        self.ram = mem
        self.rom_start = rom_start
        self.rom_end = rom_end
        self.io_page_start = io_page_start
        self.io_page_end = io_page_start + 0xFF
        self.init = init
        print(f"MMU: initialized with ROM at ${rom_start:04X}-${rom_end:04X}, entry point at ${init:04X}, I/O space is at ${io_page_start>>8:02X}XX")
    def read(self, addr):
        if (addr & 0xFF00) == self.io_page_start:
            value = self.io.read(addr & 0xFF)
            print(f"MMU IO--RD @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
        else:
            value = self.ram[addr]
            print(f"MMU MEM-RD @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
        return value
    def write(self, addr, value):
        value &= 0xFF
        if (addr & 0xFF00) == self.io_page_start:
            print(f"MMU IO--WR @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
            self.io.write(addr & 0xFF, value)
        elif addr < self.rom_start or addr > self.rom_end:
            print(f"MMU MEM-WR @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
            self.ram[addr] = value
        else:
            print(f"MMU IGNORING MEM-WR @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
    def readWord(self, addr):
        return self.read(addr) + (self.read((addr + 1) & 0xFFFF) << 8)
    def writeWord(self, addr, value):
        self.write(addr, value & 0xFF)
        self.write((addr + 1) & 0xFFFF, (value >> 8) & 0xFF)
    def reset(self):
        print(f"RESET vector is set to ${self.init:04X}")
        self.ram[0xFFFC] = self.init & 0xFF
        self.ram[0xFFFD] = self.init >> 8
        cpu.r.pc = self.init







if len(sys.argv) != 2:
    raise RuntimeError("Bad usage.")
with open(sys.argv[1], "rb") as rom:
    rom = rom.read()
ID = b'{{CUT#HERE}}'
pos = rom.find(ID)
if pos < 0:
    raise RuntimeError("Cannot find ID in the binary")
loc  = rom[pos + len(ID) + 0] + (rom[pos + len(ID) + 1] * 256)
init = rom[pos + len(ID) + 2] + (rom[pos + len(ID) + 3] * 256)
IO_PAGE_ADDR = rom[pos + len(ID) + 4] + (rom[pos + len(ID) + 5] * 256)
realio = rom[pos + len(ID) + 6]
rest = pos + len(ID) + 7
print(f"Position={pos} ROMLOC={loc:04X} INIT={init:04X} REALIO={realio} IO_PAGE_ADDR=${IO_PAGE_ADDR:04X}")

if realio != 0:
    raise RuntimeError("Need SIMULATE target to set up in the source!")

rom = rom[rest:]
rom = rom.rstrip(b'\x00')



mem = bytearray(0x10000)
mem[loc:loc+len(rom)] = rom         # replace the memory content at "ROM"
mem[0xFFFC] = init & 0xFF
mem[0xFFFD] = init >> 8


mem[IO_PAGE_ADDR + 0] = 0xAD       # LDA abs opcode
mem[IO_PAGE_ADDR + 1] = 0x00
mem[IO_PAGE_ADDR + 2] = 0xD0
mem[IO_PAGE_ADDR + 3] = 0x60       # RTS


io = MyIO()
mmu = MyMMU(mem, loc, loc + len(rom) - 1, init, IO_PAGE_ADDR, io)
cpu = CPU(mmu)

cpu.reset()

while True:
    cpu.step()


