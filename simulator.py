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
from collections import deque



ALLOW_DEBUG = False


class Console(object):

    init_done = False
    COLS, ROWS = 80, 25
    FONT_W, FONT_H = 9, 16      # FONT_W = 9 -> leave an empty pixel after a 8-width font
    WIDTH, HEIGHT = COLS * FONT_W, ROWS * FONT_H
    KBD_BUFFER_SIZE = 16
    CURSOR_CODE = 219
    COLOUR = (
        (0, 255, 100),      # 0: BRIGHT GREEN
        (0x00, 0xFF, 0x00), # 1: GREEN
        (255, 191, 0)       # 2: AMBER
    )
    COLOUR_SCHEME = 2
    BG_DIM_FACTOR = 0.1
    WIN_ZOOM = 1.5

    def __init__(self, title_str):

        sdl2.ext.init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.ext.Window(title_str, size = (int(self.WIDTH * self.WIN_ZOOM), int(self.HEIGHT * self.WIN_ZOOM)))
        self.renderer = sdl2.ext.Renderer(self.window)
        sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"1")
        sdl2.SDL_RenderSetLogicalSize(self.renderer.sdlrenderer, self.WIDTH, self.HEIGHT)
        self.window.show()
        self.COLOUR = self.COLOUR[self.COLOUR_SCHEME]
        self.screen = [[" "] * self.COLS for _ in range(self.ROWS)]
        self.font_tex = self._get_font()
        self.x = 0
        self.y = 0
        self.cursor_on = True
        self.event = sdl2.SDL_Event()
        self.kbdbuf = deque(maxlen = self.KBD_BUFFER_SIZE)
        self.init_done = True

    def __del__(self):

        if self.init_done:
            print("Console (so SDL2 too) exiting ...")
            sdl2.SDL_DestroyTexture(self.font_tex)
            self.window.close()
            sdl2.ext.quit()

    def putchar(self, c):

        if c == '\r':
            self.x = 0
        elif c == '\n':
            self.y += 1
        elif ord(c) >= 32:
            self.screen[self.y][self.x] = c
            self.x += 1
        if self.x >= self.COLS:
            self.y += 1
            self.x = 0
        if self.y >= self.ROWS:
            self.y = self.ROWS - 1
            for y in range(self.ROWS - 1):
                for x in range(self.COLS):
                    self.screen[y][x] = self.screen[y + 1][x]
            for x in range(self.COLS):
                self.screen[self.ROWS - 1][x] = ' '

    def putstring(self, s):

        for c in s:
            self.putchar(c)

    def _get_font(self):

        t0 = sdl2.SDL_GetTicks()
        # THIS "SUSPECT" PART: base85 encoded VGA font, so it won't take too much space here ...
        font = r"""zzzz!!%J!V1F32R=Tp<z!!%KJg].;kkPtR2zzD#XG5rd6[:zz&3,(:HoMZ;z!!!!94?Vfik85$uz!!!!94F[>1IM`nazz!!!iu4;\%uzs8W-!s8V9"_rq("s8W-!z!'Fj[6=r=[zs8W-!s218<]pZe<s8W-!!!"&M)DZQ]bfn:Uz!!#,nAnGX;(k*;
        =z!!#5>5;4cF0Q?O>z!!%LYIq)tu@qXue^]4?7!!!!9(u%194PL\iz!._lCnG*"XnDM*4z!!3?7*^9Qe*Y&AUz!!!iuIM`n=IQSGIz!!$VCAnGXeAcQFTz!!%N'gY7&o)]K_8z!.;do3,HUSCcDjCHiO-Hzzrr2orz!!!iuIM`n=IQSHrz!!!iuIM`n=(`4),z!!!iQ
        (`4),(k+Razz!#Q.D$lAsEzz!&.g[?n_Q\zz!!'gM_#=<6zz!$l1VAg@?Vzz&3)XsI/a*Fzzrr.:m3&hHLzzzzz!!!iu4?OGt(]YBiz!+ohT,QIfEzz!!!"8D#S6eD#S6ez(`7Y?_SCO'#):-F(`35Qz_T!!$0OVnTz!!"upCcHUnbfn:Sz!&-)\?iU0,zz!!!EE0JG
        170JF=Pz!!"\i$k*OQ$k*t,zz!+n@n4D"Qnzz!#QQ%(`35Qzzz!#QOi0E;(Qz!!!#uzzzz!!!iQzz!X9&M0OV\Hz!!#,n_o(6`_o$(Kz!!!iqGSh87(`4*=z!!%Dd"q2>&@)0e]z!!%Dd"pR0o"pW(pz!!!EI4D`7@$k*Ocz!!*#6^qfjP"pW(pz!!"ud^qflf`l?#G
        z!!*#<"pPJQ0JG17z!!%Dd`l<DG`l?#Gz!!%Dd`l<H3"pPK\zz(`35Q!#QOQzz(`35Q!#QP,z!!!!'$lC[+0Gk3&zz!.FnJIK0?Jz!!!",0Gk3&$lC[+z!!%Dd`XE\$(]YBiz!!!"H`l?llhV>noz!!!QiCrXKo`l?$<z!!)q/AnHF&AnGZQz!!#,n_SEt&^qs\Gz!!
        )e1AnGXeAnGlSz!!*"1@VC""?t*aIz!!*"1@VC""?smC3z!!#,n_SEtD`l;UOz!!($Y`lA"t`l?$<z!!#+u(`4),(`4)Pz!!"&K$k*OQbfn:Uz!!).nAo)^:Ch@;Az!!)Lr?smAM?t*aIz!!'q"s8Uik_o'C0z!!(%$pAWpo`l?$<z!!%Dd`l?$<`l?#Gz!!)q/AnHE
        u?smC3z!!%Dd`l?$<`n'!o$k<7;!!)q/AnHF,AnGZ;z!!%Dd`aCb7#0+Z1z!!*&RR2?bX(`4)Pz!!($Y`l?$<`l?#Gz!!'pS_o'C0_e)"Jz!!'pS_o'CHg](ktz!!'pSAipnI4D)LKz!!'pS_e)"J(`4)Pz!!*&:L("nQ@)9b\z!!#,80JG170JG1Cz!!!"L^u0/k*"
        E/Sz!!#+i$k*OQ$k*P,z&3+LGzzzzzz!<3$!0JF=Dzzzz!-ep"bfn:Sz!!(qb@!HL"AnGY&zz!.;f%^qds;z!!!uI$p8@Mbfn:Szz!.;fc^qds;z!!"upA74n7?smC3zz!-ZT1bfn:Y%*Wqr!!(qb?u1!uAnGZ;z!!!iQ!&tf4(`4)Pz!!!3-!"K2;"pP89AnF.*!!(
        qb?tO5"G\h!Sz!!"tq(`4),(`4)Pzz!9X=9gY:K;zz!8M0uAnGXezz!.;f+`l?#Gzz!8M0uAnGY&?srI(z!-ZT1bfn:Y$k+0Wz!8Ma0?smC3zz!.;do3"3fSz!!!Qa0`3UY0JGC)zz!6i[2bfn:Szz!5l^l_e)"Jzz!5l^lgY;a?zz!5iD2(d)EJzz!63$u`l?#I"q:
        8,z!<11Z0OVp"z!!!KG(`73/(`4)"z!!!iQ(`35i(`4),z!!$sT(`3`"(`4*/z!!%2tzzzz&3+LG`l@uXz!!#,n_SEt&_Ibn=#(-CN!!(4C!6i[2bfn:Sz!"9\u!.;fc^qds;z!"_,+!-ep"bfn:Sz!!(4C!-ep"bfn:Sz!+7Jt!-ep"bfn:Sz!'"dS!-ep"bfn
        :Szz4D%u/AipJ+49,?]!"_,+!.;fc^qds;z!!("=!.;fc^qds;z!+7Jt!.;fc^qds;z!!$U2!&tf4(`4)Pz!#Rh1!&tf4(`4)Pz!+7Jt!&tf4(`4)Pz!6,!M3,HUSrl2stz3,CPS3,HUSrl2stz(bf=traoPc?smUGzz!,ak;Ib<G"z!!#3!bfp(1bfn;Vz!"_,
        +!.;f+`l?#Gz!!("=!.;f+`l?#Gz!+7Jt!.;f+`l?#Gz!&/ZA!6i[2bfn:Sz!+7Jt!6i[2bfn:Sz!!("=!63$u`l?#I"q5_V!6,"d`l?$<`l?#Gz!6,#Y`l?$<`l?#Gz!#QQ%_na('_gWF>z!'"e*@.7Q3?sr-pz!!'oK4;e)8rtlRiz!;pG@Ht$]+AnGZHz!"K
        qb(`7]=(`4),fPgfj!#RCt!-ep"bfn:Sz!"9\u!&tf4(`4)Pz!#RCt!.;f+`l?#Gz!#RCt!6i[2bfn:Sz!!%2t!8M0uAnGXezG2*);k4\f2cGmlDz!'G(64og$3zz!'"e22un=+zz!!"],!&-*7^rFBAzz!!*#6^qd_czz!!*!&"pP83z!5QCe`lo8R@*Y5G$m,
        HL!5QCe`lo8RB$Q]+"pP&-!!!iQ!#QOi4?P_Czz!&eZGCc27nzz!8)*GCtJ^fz&O[4!&O[4!&O[4!&O[4!<N9'!<N9'!<N9'!<N9'!h07\!h07\!h07\!h07\!(`4),(`4),(`4),(`4),(`4),(`4+b(`4),(`4),(`4),)#+sC(`4),(`4),2E!HO2E!Je2E!
        HO2E!HOz!!!#u2E!HO2E!HOz!;IE+(`4),(`4),2E!HO2YI@K2E!HO2E!HO2E!HO2E!HO2E!HO2E!HOz!<*2r2E!HO2E!HO2E!HO2YI@Szz2E!HO2E!Jmzz(`4),)#+sCzzz!!!#o(`4),(`4),(`4),(`4)3zz(`4),(`4+izzz!!!$!(`4),(`4),(`4),(`4
        )3(`4),(`4),z!!!$!zz(`4),(`4+i(`4),(`4),(`4),(`sS:(`4),(`4),2E!HO2E!HP2E!HO2E!HO2E!HO2E*<Szzz!'`.r2E!HO2E!HO2E!HO2YR4Ozzz!<3&n2E!HO2E!HO2E!HO2E*<K2E!HO2E!HOz!<3'!zz2E!HO2YR4G2E!HO2E!HO(`4),)#jU9z
        z2E!HO2E!Jnzzz!<3'!(`4),(`4),z!!!$!2E!HO2E!HO2E!HO2E!HXzz(`4),(`sS:zzz!$<%"(`4),(`4),z!!!!`2E!HO2E!HO2E!HO2E!Jn2E!HO2E!HO(`4),)#kHQ(`4),(`4),(`4),(`4+bzzz!!!!@(`4),(`4),s8W-!s8W-!s8W-!s8W-!z!!!$!
        s8W-!s8W-!nF5r:nF5r:nF5r:nF5r:%hB0]%hB0]%hB0]%hB0]s8W-!s8W*!zzz!-[/Mf\"u&z!!%8fbfn_``l?$Bz!!*#<`k]C*^qdb$zzrbQCeCi!p(z!!!#u`aCJ;0OVp"zz!.NSQf\"hqzzAnGXeApduo^]4?7zG2*oO(`4),z!!!"J(d)DBAipoZz!!!!Y
        CrXKo`l;gSz!!"up`l?#7Ci!qUz!!"&o(^rT?AnGX;zz!.N\WgO9,&z!!!!$#(G=]o6t)_z!!!um?sn@i?skZ.z!!!"H`l?$<`l?$<zzrVurt!!)uuzz(`7]=(]XR9z!!!!Q(^pTW(bbr=z!!!!-(bf>O(^pCnz!!!KJ)]0D/(`4),(`4),(`4),(`4),f\"hqz
        z(`37%!#QOQzz!-[,tG2*&tz!'"e22uipYzzz!!!!9(]XO9zzz(]XO9z!"TJH$k*R2Chu3Rz!8)+(Ci!nfzz!-$RE@*&*CzzzI!g<hI!g;Azzzzz"""
        font = base64.a85decode(font)
        assert len(font) == 256 * self.FONT_H
        assert self.FONT_W in (8, 9)
        surface = sdl2.SDL_CreateRGBSurface(0, self.FONT_W * 256, self.FONT_H, 32, 0, 0, 0, 0)
        fg = sdl2.SDL_MapRGBA(surface.contents.format, self.COLOUR[0], self.COLOUR[1], self.COLOUR[2], 0xFF)
        BG_COLOUR = tuple(int(c * self.BG_DIM_FACTOR) for c in self.COLOUR)
        bg = sdl2.SDL_MapRGBA(surface.contents.format, BG_COLOUR[0], BG_COLOUR[1], BG_COLOUR[2], 0xFF)
        sdl2.SDL_FillRect(surface, ctypes.byref(sdl2.SDL_Rect(0, 0, self.WIDTH, self.HEIGHT)), bg)
        for i in range(256):
            for y in range(self.FONT_H):
                line = font[i * self.FONT_H + y]
                for x in range(self.FONT_W):
                    if x < 7 and line & (1 << (7 - x)):
                        px = i*self.FONT_W + x
                        # Yeah, horrible trick. However the "font sheet" (texture) is done only once at startup
                        sdl2.SDL_FillRect(surface, ctypes.byref(sdl2.SDL_Rect(px, y, 1, 1)), fg)
        del font
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

        if len(self.kbdbuf) < self.kbdbuf.maxlen:
            self.kbdbuf.append(c)
            print("KBD: buffer size is: {}".format(len(self.kbdbuf)))
        else:
            print("KBD: WARNING: keyboard buffer is full!")
        #self.putstring(chr(c))

    def read_keyboard(self):

        if self.kbdbuf:
            return self.kbdbuf.popleft() & 0x7F
        return 0

    def handle_events(self):

        while sdl2.SDL_PollEvent(self.event):
            if self.event.type == sdl2.SDL_QUIT:
                return False
            elif self.event.type == sdl2.SDL_KEYDOWN:
                sym = self.event.key.keysym.sym
                if sym == sdl2.SDLK_F9:
                    return False
                elif sym == sdl2.SDLK_F1:
                    print("F1 pressed!")
                elif sym == sdl2.SDLK_RETURN:
                    self._push_input(13)
            elif self.event.type == sdl2.SDL_TEXTINPUT:
                text = self.event.text.text.decode("utf-8")
                for ch in text:
                    print(f"Typed char: {ch} (ord={ord(ch)})")
                    self._push_input(ord(ch))
        return True






lastdebug = "x"


def DEBUG(s):
    global lastdebug
    if ALLOW_DEBUG:
        print(s)
        if cpu.r.pc in lst:
            if lastdebug != lst[cpu.r.pc]:
                lastdebug = lst[cpu.r.pc]
                print(lst[cpu.r.pc])


class MyIO(object):
    def read(self, addr):
        if addr == 0:
            return con.read_keyboard()
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
    db = {}
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
            if line[11] not in ("0123456789ABCDEF"):
                continue
            db[addr] = line
    return db


def run(arg):
    global cpu, con, mem, mmu, io
    if len(arg) != 2:
        raise RuntimeError("Bad usage.")
    lst = load_lst(arg[1])
    with open(arg[0], "rb") as rom:
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
        raise RuntimeError("Need SIMULATE target to set up in the source, ie REALIO must be 0")
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
    con = Console("MBASIC-6502 SIMULATOR")
    con.putstring(f"SIMULATION: ROM=${loc:04X}-${loc+len(rom)-1:04X} INIT=${init:04X} IO=${IO_PAGE_ADDR:04X}\r\n")
    running = True
    t0, t1, ops = sdl2.SDL_GetTicks(), 0, 0
    while running:
        cpu.step()
        ops += 1
        t2 = sdl2.SDL_GetTicks()
        if t2 - t1 >= 1000 // 25:
            t1 = t2
            running = con.handle_events()
            con.render()
    t0 = (sdl2.SDL_GetTicks() - t0) / 1000
    del con
    print(f"Running for {t0} seconds, {int(ops/t0)} ops/sec")


if __name__ == "__main__":
    run(sys.argv[1:])
    sys.exit(0)
