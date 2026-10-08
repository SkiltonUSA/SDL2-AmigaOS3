SDL ZZFractal 0.2 - A4000TX / ZZ9000 preview

Interactive SDL2 Mandelbrot explorer with a separate Cortex-A9 compute worker.
The 68k owns SDL, input, drawing and AmigaOS calls. Firmware is not included.

REQUIREMENTS
AmigaOS 3.2.x, 68030+ (tested on TF4060/68060), ZZ9000 with its 256 MB Fast
RAM enabled, tested XX19c / XACP 1.7 firmware, P96 and a compatible
cybergraphics.library V40+. Tested machine has cybergraphics.library 42.7.
Only one ZZ9000 ARM app may run. Close ZZQuake, Doom, Dark Forces, ZZReSid,
other fractal apps and ARM debuggers before starting. Even CPU mode keeps
this app's worker alive. The firmware register cannot identify XX19c safely;
Workbench startup asks you to confirm the required configuration.

INSTALL / RUN
Extract the drawer anywhere and double-click SDLZZFractal.
No Mac, MCP bridge, network, ARexx or separate ARM payload is needed.
The icon uses a 131072-byte stack. From Shell:
  Protect SDLZZFractal +e
  Stack 131072
  SDLZZFractal
Do not copy libSDL2.a to LIBS:; SDL is linked into this executable.
No startup files, drivers, Workbench preferences or firmware are changed.

CONTROLS
A / ARM button          render on ARM
C / CPU button          render on the 68k
Left click image        center and zoom 2x
Right click             zoom out (Q14 rounding applies)
Arrow keys              pan by a quarter of the image
I / O                   increase / decrease iterations (32, 64, 128, 256)
R / Reset               restore initial view and 128 iterations
X / Escape / Cancel     cancel; pending shared-memory work is drained
M                       iconify to a Workbench application icon
Double-click app icon   restore; rendering can continue while iconified
Q / close gadget        quit and return ARM before releasing shared memory
F5 / F6 / F7             Workbench / temporary 16-bit / temporary 32-bit
                        screen, when idle; rerender on selected screen

The image is 320x240. Fixed-point zoom stops at step 2 (six zoom levels from
initial view). The center is bounded; a pan/zoom outside it is ignored.
Temporary test screens require a suitable mode and are closed on exit.

TIMING
Wall time includes event handling, cooperative scheduling, transfer and
presentation. ARM compute is an estimate based on the read-only Zynq global
timer calibrated against the Amiga E-clock. Transfer includes request/result
cache synchronization and pixel copying on the 68k; colour mapping and SDL
updates have separate measurements. ARM request roundtrip includes waiting
and overlaps compute/transfer; do not add these columns together.
The 68k yields one OS tick between bounded work slices. Scheduling differs
between CPU and ARM modes, so total render ratios are NOT raw CPU speed ratios.
The ARM worker's MMU and caches remain disabled. CPU and ARM builds also use
different compilers/options. The SDK library retains -O0.

LIMITS
Preview for the tested configuration. No audio, arbitrary window resizing,
SDL texture-renderer, generic ARM runtime or instruction stepping is implied.
No firmware/cache policy changes. Test records and source:
https://github.com/SkiltonUSA/SDL2-AmigaOS3
