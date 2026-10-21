"""Genera drawings/terminal_block_2-8p.svg: morsettiera a innesto passo 5.08 (tipo Phoenix
MSTB 2,5/n-ST-5,08), 2..8 poli, scala 1:1 (unita' = mm).

Vista dall'alto (lato viti): parte di innesto a sinistra, corpo con viti e uscita fili a destra.
Le posizioni sono impilate in verticale (No.1 in basso). Larghezza = n * 5.08; corpo con viti accorciato per il disegno.

Uso: python drawings/gen_terminal_block.py drawings/terminal_block_2-8p.svg
"""
import sys

PITCH, NOSE, STEP = 5.08, 7.3, 7.6  # innesto, corpo con viti
DEPTH = NOSE + STEP
INK = "#000"; BODY = "#f5f5f5"; SHADE = "#dcdcdc"; METAL = "#e6e6e6"; WIRE = "#c8c8c8"
WIRE_W, WIRE_L = 1.3, 8.0

def W(n): return PITCH * n

out = []
def add(s): out.append(s)
def f(v): return f"{v:.3f}"
def rect(x, y, w, h, fill, sw=0.2, rx=0.0):
    r = f' rx="{f(rx)}"' if rx else ""
    add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r} fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def line(x1, y1, x2, y2, sw=0.12):
    add(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{INK}" stroke-width="{sw}"/>')
def circle(cx, cy, r, fill, sw=0.15):
    add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def poly(pts, fill, sw=0.2):
    add(f'<polygon points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def text(x, y, s, size=2.0, anchor="start", bold=False):
    w = ' font-weight="bold"' if bold else ""
    add(f'<text x="{f(x)}" y="{f(y)}" font-family="Arial" font-size="{size}" text-anchor="{anchor}" '
        f'dominant-baseline="middle"{w}>{s}</text>')

def terminal_block(x0, y0, n):
    w = W(n)
    nose = NOSE  # parte bassa che si innesta nell'header
    # innesto a sinistra (gradino), corpo con le viti a destra, fili in uscita a destra
    rect(x0, y0, nose, w, SHADE)
    rect(x0 + nose, y0, STEP, w, BODY)
    for i in range(n):
        cy = y0 + w - (i + 0.5) * PITCH  # No.1 in basso
        # tubetto della presa che entra nell'header
        rect(x0, cy - 2.0, nose - 0.6, 4.0, BODY, 0.12, 0.8)
        # vite con taglio
        circle(x0 + nose + 3.0, cy, 1.8, "#fff")
        circle(x0 + nose + 3.0, cy, 1.3, METAL, 0.1)
        sx, sy = 1.3 * 0.5, 1.3 * 0.866  # taglio inclinato di 30 gradi
        line(x0 + nose + 3.0 + sx, cy - sy, x0 + nose + 3.0 - sx, cy + sy, 0.25)
        # foro quadro di sblocco/prova
        rect(x0 + nose + 5.8, cy - 0.75, 0.75, 1.5, "#fff", 0.12)
        # filo
        rect(x0 + DEPTH, cy - WIRE_W / 2, WIRE_L, WIRE_W, WIRE, 0.12)
    # marcatore No.1
    tx = x0 - 0.4; ty = y0 + w - 0.5 * PITCH
    poly([(tx, ty), (tx - 1.2, ty - 0.7), (tx - 1.2, ty + 0.7)], INK, 0.05)
    text(tx - 2.6, ty, "1", 1.4, "middle", True)

cols, cell_w = 4, 34.0
row_h = W(8) + 8
SW = cols * cell_w + 4
SH = 2 * row_h + 8
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SW * 6:.0f}" height="{SH * 6:.0f}" viewBox="0 0 {SW:.1f} {SH:.1f}">')
add(f'<rect width="{SW:.1f}" height="{SH:.1f}" fill="#fff"/>')
text(3, 4, "Morsettiera a innesto — 2P … 8P (passo 5.08 mm)", 2.0, bold=True)
for k, n in enumerate(range(2, 9)):
    r, c = divmod(k, cols)
    cx = 3 + c * cell_w; cy = 10 + r * row_h
    text(cx, cy, f"{n}P", 2.0, bold=True)
    terminal_block(cx + 4, cy + 3 + (W(8) - W(n)) / 2, n)
add("</svg>")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
