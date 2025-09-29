#!/usr/bin/env python3

# (C)2025 Gabor Lenart "LGB" - lgblgblgb@gmail.com
# WARNING - WARNING: this is really ugly python code, basically I am experimenting with it, without any sanity to have nice code or anything
# at least at this early point of the project ...

import sys
# You need py65emu, install it with: pip3 install py65emu
from py65emu.cpu import CPU
# You need PySDL2, install it with: pip3 install PySDL2
import sdl2
import sdl2.ext
import ctypes
import base64
import re
from collections import deque



ALLOW_DEBUG = False
ALLOW_DEBUG_READING_CONSOLE = False


class Console(object):

    init_done = False
    COLS, ROWS = 80, 25
    FONT_W, FONT_H = 9, 16      # FONT_W = 9 -> leave an empty pixel after a 8-width font
    WIDTH, HEIGHT = COLS * FONT_W, ROWS * FONT_H
    KBD_BUFFER_SIZE = 120       # actually it's also a line buffer, so it shouldn't be too short ...
    CURSOR_CODE = 219
    COLOUR = (
        (0, 255, 100),      # 0: BRIGHT GREEN
        (0x00, 0xFF, 0x00), # 1: GREEN
        (255, 191, 0)       # 2: AMBER
    )
    COLOUR_SCHEME = 2
    BG_DIM_FACTOR = 0.1
    WIN_ZOOM = 1
    CAPITALIZE_INPUT = True
    FONT_FILE = "bin/vgafont16h.bin"

    def __init__(self, title_str):

        sdl2.ext.init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.ext.Window(title_str, size = (int(self.WIDTH * self.WIN_ZOOM), int(self.HEIGHT * self.WIN_ZOOM)))
        self.renderer = sdl2.ext.Renderer(self.window)
        if self.WIN_ZOOM != 1:
            sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"1")
            sdl2.SDL_RenderSetLogicalSize(self.renderer.sdlrenderer, self.WIDTH, self.HEIGHT)
        else:
            sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"0")
        self.window.show()
        self.COLOUR = self.COLOUR[self.COLOUR_SCHEME]
        self.screen = [[" "] * self.COLS for _ in range(self.ROWS)]
        self.font_tex = self._get_font()
        self.x = 0
        self.y = 0
        self.cursor_on = True
        self.event = sdl2.SDL_Event()
        self.kbdbuf = deque(maxlen = self.KBD_BUFFER_SIZE)
        self.input_line_ready = False
        self.init_done = True
        print(f"Console prepared for {self.COLS}x{self.ROWS} text resolution")

    def __del__(self):

        if self.init_done:
            print("Console (so SDL2 too) exiting ...")
            sdl2.SDL_DestroyTexture(self.font_tex)
            self.window.close()
            sdl2.ext.quit()

    def putchar(self, c):

        if not isinstance(c, str) or len(c) != 1:
            raise RuntimeError("putchar must be called with 1-byte long character-string")
        if c == '\r':
            self.x = 0
        elif c == '\n':
            self.y += 1
        elif ord(c) == 8:
            if self.x > 0:
                self.x -= 1
                self.screen[self.y][self.x] = ' '
        elif ord(c) < 32:
            self.putchar(chr(ord('^')))
            c = chr(ord('A') + ord(c))
        elif ord(c) >= 127:
            c = '?'
        if ord(c) >= 32:
            self.screen[self.y][self.x] = c
            self.x += 1
        if self.x >= self.COLS:
            self.y += 1
            self.x = 0
        if self.y >= self.ROWS:
            self.y = self.ROWS - 1
            for x in range(self.COLS):
                for y in range(self.ROWS - 1):
                    self.screen[y][x] = self.screen[y + 1][x]
                self.screen[self.ROWS - 1][x] = ' '

    def putstring(self, s):

        for c in s:
            self.putchar(c)

    def _get_font(self):

        assert self.FONT_W in (8, 9)
        with open(self.FONT_FILE, "rb") as font:
            font = font.read()
        assert len(font) == 256 * self.FONT_H
        t0 = sdl2.SDL_GetTicks()
        surface = sdl2.SDL_CreateRGBSurface(0, self.FONT_W * 256, self.FONT_H, 32, 0, 0, 0, 0)
        fg = sdl2.SDL_MapRGBA(surface.contents.format, self.COLOUR[0], self.COLOUR[1], self.COLOUR[2], 0xFF)
        BG_COLOUR = tuple(int(c * self.BG_DIM_FACTOR) for c in self.COLOUR)
        bg = sdl2.SDL_MapRGBA(surface.contents.format, BG_COLOUR[0], BG_COLOUR[1], BG_COLOUR[2], 0xFF)
        sdl2.SDL_FillRect(surface, ctypes.byref(sdl2.SDL_Rect(0, 0, self.WIDTH, self.HEIGHT)), bg)
        for i in range(256):
            for y in range(self.FONT_H):
                line = font[i * self.FONT_H + y]
                for x in range(self.FONT_W):
                    # Yeah, horrible trick. However the "font sheet" (texture) is done only once at startup
                    sdl2.SDL_FillRect(surface, ctypes.byref(sdl2.SDL_Rect(i * self.FONT_W + x, y, 1, 1)), fg if x < 8 and line & (1 << (7 - x)) else bg)
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer.renderer, surface)
        sdl2.SDL_FreeSurface(surface)
        print("Font texture prepared within {} msecs for a {}x{} font.".format(sdl2.SDL_GetTicks() - t0, self.FONT_W, self.FONT_H))
        return texture

    def render(self):

        cursor_phase = (sdl2.SDL_GetTicks() & 512) and self.cursor_on
        self.renderer.clear(sdl2.ext.Color(0, 0, 0))
        for y in range(self.ROWS):
            for x in range(self.COLS):
                asc = self.CURSOR_CODE if x == self.x and y == self.y and cursor_phase else ord(self.screen[y][x])
                src = sdl2.SDL_Rect(asc * self.FONT_W, 0, self.FONT_W, self.FONT_H)
                dst = sdl2.SDL_Rect(x * self.FONT_W, y * self.FONT_H, self.FONT_W, self.FONT_H)
                sdl2.SDL_RenderCopy(self.renderer.renderer, self.font_tex, src, dst)
        self.renderer.present()

    def _push_input(self, c):

        if self.input_line_ready:
            print("KBD: blocked keyboard push: unconsumed line buffer is already ready")
            return
        if c == 8:
            if len(self.kbdbuf) > 0:
                self.kbdbuf.popleft()
                self.putchar(chr(8))
            return
        if len(self.kbdbuf) < self.kbdbuf.maxlen:
            self.kbdbuf.append(c)
            print("KBD: buffer size is: {}".format(len(self.kbdbuf)))
            if c == 13:
                self.input_line_ready = True
        else:
            print("KBD: WARNING: keyboard buffer is full!")
        if c == 13:
            self.putstring("\r\n")
        else:
            if self.CAPITALIZE_INPUT and c >= ord('a') and c <= ord('z'):
                c = c - ord('a') + ord('A')
            self.putchar(chr(c))

    def read_keyboard(self):

        if len(self.kbdbuf) == 0:
            self.input_line_ready = False
            return 0
        value = self.kbdbuf.popleft()
        if len(self.kbdbuf) == 0:
            self.input_line_ready = False
        return value

    def read_queue_size(self):

        return len(self.kbdbuf)

    def read_input_line_ready(self):

        return self.input_line_ready

    def handle_events(self):

        while sdl2.SDL_PollEvent(self.event):
            if self.event.type == sdl2.SDL_QUIT:
                return False
            elif self.event.type == sdl2.SDL_KEYDOWN:
                sym = self.event.key.keysym.sym
                if sym == sdl2.SDLK_F9:
                    return False
                elif sym == sdl2.SDLK_F1:
                    #print("F1 pressed!")
                    pass
                elif sym == sdl2.SDLK_RETURN:
                    self._push_input(13)
                elif sym == sdl2.SDLK_BACKSPACE:
                    self._push_input(8)
            elif self.event.type == sdl2.SDL_TEXTINPUT:
                text = self.event.text.text.decode("utf-8")
                for ch in text:
                    print(f"KBD: Typed char: {ch} (ord={ord(ch)})")
                    self._push_input(ord(ch))
        return True


def get_last_jsr_return_addr():

    lo = mem[0x100 + ((cpu.r.s + 1) & 0xFF)]
    hi = mem[0x100 + ((cpu.r.s + 2) & 0xFF)]
    return_addr = (hi << 8) | lo
    return (return_addr + 1) & 0xFFFF   # JSR pushes ret-1 ...



lastdebug = "x"


def DEBUG(s):
    global lastdebug, lst, sym
    if ALLOW_DEBUG:
        print(s)
        if cpu.r.pc in lst:
            if lastdebug != lst[cpu.r.pc]:
                lastdebug = lst[cpu.r.pc]
                if cpu.r.pc in sym:
                    s = " [{}]".format(sym[cpu.r.pc])
                else:
                    s = ""
                print(lst[cpu.r.pc] + s)


class MyIO(object):
    def read(self, addr):
        if addr == 0:
            ret = get_last_jsr_return_addr()
            if ALLOW_DEBUG_READING_CONSOLE:
                print(f"IO: reading console at PC=${cpu.r.pc:04X} caller on stack is ${ret:04X}")
            return con.read_keyboard()
        elif addr == 1:
            return con.read_queue_size() + (128 if con.read_input_line_ready() else 0)
        return 0xFF
    def write(self, addr, value):
        if addr == 0:
            con.putchar(chr(value&127))



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
        self.touched = []
        for a in range(0x10000):
            self.touched.append(True if (a >= rom_start and a <= rom_end) or (a & 0xFF00) == io_page_start else False)
        print(f"MMU: initialized with ROM at ${rom_start:04X}-${rom_end:04X}, entry point at ${init:04X}, I/O space is at ${io_page_start>>8:02X}XX")
    def read(self, addr):
        if (addr & 0xFF00) == self.io_page_start:
            value = self.io.read(addr & 0xFF)
            DEBUG(f"MMU IO--RD @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
        else:
            value = self.ram[addr]
            DEBUG(f"MMU MEM-RD @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
        if not self.touched[addr]:
            DEBUG(f"MMU WARNING: reading uninitialized memory: ${addr:04X} at PC=${cpu.r.pc:04X}")
        return value
    def write(self, addr, value):
        self.touched[addr] = True
        value &= 0xFF
        if (addr & 0xFF00) == self.io_page_start:
            DEBUG(f"MMU IO--WR @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
            self.io.write(addr & 0xFF, value)
        elif addr < self.rom_start or addr > self.rom_end:
            DEBUG(f"MMU MEM-WR @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
            self.ram[addr] = value
        else:
            DEBUG(f"MMU WARNING IGNORING MEM-WR @ ${addr:04X} = ${value:02X} at PC=${cpu.r.pc:04X}")
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



def load_lst(fn):
    db, sym = {}, {}
    with open(fn, "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) < 20:
                continue
            sep = line.split()
            if len(sep) < 3:
                continue
            try:
                addr = int(sep[0], 16)
            except ValueError:
                continue
            if line[11] in ("0123456789ABCDEF"):
                db[addr] = line
            if len(line) > 24:
                r = re.sub(r"^([A-Z][A-Z0-9]*):.*$", r"\1", line[24:])
                if r != line[24:] and len(r) > 0:
                    sym[addr] = r
    return db, sym



def load_labels(fn):
    db = {}
    with open(fn, "rt") as f:
        for line in f:
            line = line.strip().split()
            if len(line) < 3 or line[0] != "al":
                continue
            addr = int(line[1], 16)
            sym = line[2].lstrip(".")
            if sym.startswith("__"):
                continue
            if sym.endswith("_EXPORTED"):
                sym = sym[:-9]
            db[sym] = addr
    for a in ("ROMLOC", "INIT", "REALIO", "IO_PAGE"):
        if a not in db:
            raise RuntimeError(f"Sym-file {fn} does not contain symbol {a}")
    return db



def run(fn):
    global cpu, con, mem, mmu, io, lst, sym
    fn_base = re.sub(r"-uncut$", "", re.sub(r"\..*$", "", fn))
    lst, sym = load_lst(fn_base + ".lst")
    with open(fn, "rb") as rom:
        rom = rom.read()
    ID = b'{{CUT#HERE}}'
    pos = rom.find(ID)
    if pos >= 0:
        print(f"FOUND marker <{ID.decode('UTF-8')}> at position <{pos}>, using old code")
        loc  = rom[pos + len(ID) + 0] + (rom[pos + len(ID) + 1] * 256)
        init = rom[pos + len(ID) + 2] + (rom[pos + len(ID) + 3] * 256)
        IO_PAGE_ADDR = rom[pos + len(ID) + 4] + (rom[pos + len(ID) + 5] * 256)
        realio = rom[pos + len(ID) + 6]
        rest = pos + len(ID) + 7
    else:
        print(f"NOT FOUND market <{ID.decode('UTF-8')}>, using new code")
        exported = load_labels(fn_base + ".sym")
        loc = exported["ROMLOC"]
        init = exported["INIT"]
        IO_PAGE_ADDR = exported["IO_PAGE"]
        realio = exported["REALIO"]
    print(f"Position={pos} ROMLOC={loc:04X} INIT={init:04X} REALIO={realio} IO_PAGE_ADDR=${IO_PAGE_ADDR:04X}")
    if realio != 0:
        raise RuntimeError("Need SIMULATE target to set up in the source, ie REALIO must be 0")
    if pos >= 0:
        rom = rom[rest:]                    # "cut out" the real ROM image part of the "uncut" version of "ROM"
    rom = rom.rstrip(b'\x00')
    mem = bytearray(0x10000)            # full 64K address space for 6502
    mem[loc:loc+len(rom)] = rom         # replace the memory content at "ROM"
    mem[0xFFFC] = init & 0xFF
    mem[0xFFFD] = init >> 8
    io = MyIO()
    mmu = MyMMU(mem, loc, loc + len(rom) - 1, init, IO_PAGE_ADDR, io)
    cpu = CPU(mmu)
    cpu.reset()
    con = Console("MBASIC-6502 SIMULATOR")
    con.putstring(f"SIMULATION: ROM=${loc:04X}-${loc+len(rom)-1:04X} INIT=${init:04X} SIO=${IO_PAGE_ADDR:04X}\r\n")
    running = True
    t0, t1, cycles = sdl2.SDL_GetTicks(), 0, 0
    while running:
        # Make "some" CPU steps at once to be faster. It's not critical, calling event handler and renderer is just "cosmetic" and human I/O bound
        for _ in range(256):
            cpu.step()
            cycles += cpu.cc
        t2 = sdl2.SDL_GetTicks()
        if t2 - t1 >= 1000 // 25:
            t1 = t2
            running = con.handle_events()
            con.render()
    t0 = (sdl2.SDL_GetTicks() - t0) / 1000
    del con
    print(f"UPTIME: {t0} sec, avg eff clock {int(cycles/t0/1000)}KHz")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("Bad usage.")
    run(sys.argv[1])
    sys.exit(0)
