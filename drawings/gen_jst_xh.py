"""Genera drawings/jst_xh_2-7p.svg: JST XHP-2..7 in scala 1:1 (unita' = mm).

Uso: python drawings/gen_jst_xh.py drawings/jst_xh_2-7p.svg
"""
import sys

PITCH, LEN, DEPTH, FLANGE = 2.5, 7.5, 5.7, 0.25
INK = "#000"; BODY = "#f5f5f5"; SHADE = "#dcdcdc"; METAL = "#e6e6e6"

def B(n): return PITCH * (n - 1) + 4.8
def A(n): return PITCH * (n - 1)

out = []
def add(s): out.append(s)
def rect(x, y, w, h, fill=BODY, sw=0.2, extra=""):
    add(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" {extra}/>')
def line(x1, y1, x2, y2, sw=0.15, extra=""):
    add(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{INK}" stroke-width="{sw}" {extra}/>')
def poly(pts, fill=BODY, sw=0.2):
    p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
    add(f'<polygon points="{p}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def text(x, y, s, size=1.6, anchor="middle", bold=False):
    w = ' font-weight="bold"' if bold else ""
    add(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Arial" font-size="{size}" text-anchor="{anchor}" dominant-baseline="middle"{w}>{s}</text>')

def side_view(x0, y0, n, wire=8.0):
    """Vista dal lato aggancio: faccia di accoppiamento a sinistra, collarino e fili a destra.
    Le posizioni sono impilate in verticale (No.1 in basso)."""
    b = B(n); off = (b - A(n)) / 2
    body_l = LEN - 0.6
    flange_x = x0 + body_l
    end_x = flange_x + FLANGE + 0.6
    # corpo (lato accoppiamento)
    rect(x0, y0 + 0.3, body_l, b - 0.6)
    # pareti di testa
    line(x0, y0 + 1.0, flange_x, y0 + 1.0, 0.12)
    line(x0, y0 + b - 1.0, flange_x, y0 + b - 1.0, 0.12)
    for i in range(n):
        cy = y0 + off + i * PITCH
        # finestra della linguetta di ritenzione del contatto
        wx = x0 + 0.5
        rect(wx, cy - 0.6, 2.2, 1.2, "#fff", 0.12)
        poly([(wx + 2.2, cy - 0.6), (wx + 1.2, cy), (wx + 2.2, cy + 0.6)], SHADE, 0.08)
        # filo uscente dal collarino
        rect(end_x, cy - 0.65, wire, 1.3, "#c8c8c8", 0.12)
    # collarino sul lato fili
    rect(flange_x, y0, FLANGE + 0.6, b, SHADE)
    # marcatore No.1 (in basso)
    tx = x0 - 0.4; ty = y0 + off + A(n)
    poly([(tx, ty), (tx - 1.2, ty - 0.7), (tx - 1.2, ty + 0.7)], INK, 0.05)
    text(tx - 2.6, ty, "1", 1.4, bold=True)

cols, cell_w = 3, 32.0
row_h = [B(7) + 8, B(7) + 8]
W = cols * cell_w + 4
H = sum(row_h) + 8
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*6:.0f}" height="{H*6:.0f}" viewBox="0 0 {W:.1f} {H:.1f}">')
add(f'<rect width="{W:.1f}" height="{H:.1f}" fill="#fff"/>')
text(3, 5, "JST XH — XHP-2 … XHP-7 (passo 2.5 mm)", 2.0, "start", True)
for k, n in enumerate(range(2, 8)):
    r, c = divmod(k, cols)
    cx = 3 + c * cell_w; cy = 10 + sum(row_h[:r])
    text(cx + 2, cy, f"XHP-{n}", 2.0, "start", True)
    oy = cy + 3 + (B(7) - B(n)) / 2
    side_view(cx + 5, oy, n)
add("</svg>")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
