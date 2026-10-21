"""Genera drawings/terminals.svg: puntalino, forcella, faston F, taglio netto (scala 1:1, mm).

Vista dall'alto: terminale a sinistra, filo in uscita a destra (come il JST XH).
Dimensioni tipiche per filo 0.5-1.5 mm2:
  puntalino DIN 46228-4 0.5 mm2: L 15, tubetto 8 x d1.3, collare d3.0-3.5 (maggiorato)
  forcella M3 isolata rossa:      L 21, linguetta 6.4, fessura 3.7, isolante d3.5
  faston femmina 6.3 isolato:     L 20, larghezza 7.6, isolante ~d4.2

Uso: python drawings/gen_terminals.py drawings/terminals.svg
"""
import sys

INK = "#000"; METAL = "#e6e6e6"; SHADE = "#dcdcdc"; INSUL = "#f5f5f5"; WIRE = "#c8c8c8"
WIRE_W, WIRE_L = 1.3, 8.0

out = []
def add(s): out.append(s)
def f(v): return f"{v:.3f}"
def rect(x, y, w, h, fill, sw=0.2):
    add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def line(x1, y1, x2, y2, sw=0.12):
    add(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{INK}" stroke-width="{sw}"/>')
def poly(pts, fill, sw=0.2):
    add(f'<polygon points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def path(d, fill, sw=0.2):
    add(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def text(x, y, s, size=2.0, anchor="start", bold=False):
    w = ' font-weight="bold"' if bold else ""
    add(f'<text x="{f(x)}" y="{f(y)}" font-family="Arial" font-size="{size}" text-anchor="{anchor}" '
        f'dominant-baseline="middle"{w}>{s}</text>')

def wire(x, cy):
    rect(x, cy - WIRE_W / 2, WIRE_L, WIRE_W, WIRE, 0.12)

def sleeve(x0, x1, cy, r0, r1, rim):
    """Isolante a manicotto: raggio r0 a sinistra, svasato fino a r1 a destra, con bordo."""
    k = x0 + (x1 - x0) * 0.55
    path(f"M{f(x0)},{f(cy - r0)} L{f(k)},{f(cy - r0)} Q{f(x1 - rim)},{f(cy - r0)} {f(x1 - rim)},{f(cy - r1)} "
         f"L{f(x1)},{f(cy - r1)} L{f(x1)},{f(cy + r1)} L{f(x1 - rim)},{f(cy + r1)} "
         f"Q{f(x1 - rim)},{f(cy + r0)} {f(k)},{f(cy + r0)} L{f(x0)},{f(cy + r0)} Z", INSUL)
    line(x1 - rim, cy - r1, x1 - rim, cy + r1, 0.1)

def ferrule(x, cy):
    """Puntalino: tubetto metallico 8 mm + collare isolante 7 mm. Restituisce la x del lato filo."""
    rect(x, cy - 0.65, 8.0, 1.3, METAL)
    # collare: spalla conica, corpo, imbocco svasato
    r, rim = 1.5, 1.75
    path(f"M{f(x + 8)},{f(cy - 0.65)} L{f(x + 9)},{f(cy - r)} L{f(x + 14.2)},{f(cy - r)} "
         f"L{f(x + 14.4)},{f(cy - rim)} L{f(x + 15)},{f(cy - rim)} L{f(x + 15)},{f(cy + rim)} "
         f"L{f(x + 14.4)},{f(cy + rim)} L{f(x + 14.2)},{f(cy + r)} L{f(x + 9)},{f(cy + r)} "
         f"L{f(x + 8)},{f(cy + 0.65)} Z", INSUL)
    line(x + 14.4, cy - rim, x + 14.4, cy + rim, 0.1)
    return x + 15

def fork(x, cy):
    """Forcella M3 isolata: linguetta 6.4 con fessura 3.7, isolante d3.5. Restituisce la x del lato filo."""
    hw, sw_, tip, slot_end, neck = 3.2, 1.85, 0.8, 6.0, 9.5
    # linguetta con fessura aperta a sinistra e fondo arrotondato
    path(f"M{f(x + tip)},{f(cy - hw)} L{f(x + neck)},{f(cy - hw)} L{f(x + 11)},{f(cy - 1.0)} "
         f"L{f(x + 11)},{f(cy + 1.0)} L{f(x + neck)},{f(cy + hw)} L{f(x + tip)},{f(cy + hw)} "
         f"L{f(x)},{f(cy + hw - tip)} L{f(x)},{f(cy + sw_)} "
         f"L{f(x + slot_end - sw_)},{f(cy + sw_)} Q{f(x + slot_end)},{f(cy + sw_)} {f(x + slot_end)},{f(cy)} "
         f"Q{f(x + slot_end)},{f(cy - sw_)} {f(x + slot_end - sw_)},{f(cy - sw_)} "
         f"L{f(x)},{f(cy - sw_)} L{f(x)},{f(cy - hw + tip)} Z", METAL)
    sleeve(x + 11, x + 21, cy, 1.5, 1.75, 0.6)
    return x + 21

def faston_f(x, cy):
    """Faston femmina 6.3 isolato: bordi arrotolati, collo, manicotto. Restituisce la x del lato filo."""
    hw, roll, body = 3.8, 2.0, 10.0
    # base piana (visibile fra i due bordi arrotolati)
    rect(x + 0.4, cy - hw + roll, body - 0.4, 2 * (hw - roll), SHADE, 0.12)
    line(x + 4.0, cy - 0.6, x + 6.0, cy - 0.6, 0.1)  # finestrella di ritenzione
    line(x + 4.0, cy + 0.6, x + 6.0, cy + 0.6, 0.1)
    line(x + 6.0, cy - 0.6, x + 6.0, cy + 0.6, 0.1)
    # bordi arrotolati, con estremita' anteriori arrotondate
    for top in (cy - hw, cy + hw - roll):
        path(f"M{f(x + roll / 2)},{f(top)} L{f(x + body)},{f(top)} L{f(x + body)},{f(top + roll)} "
             f"L{f(x + roll / 2)},{f(top + roll)} Q{f(x)},{f(top + roll)} {f(x)},{f(top + roll / 2)} "
             f"Q{f(x)},{f(top)} {f(x + roll / 2)},{f(top)} Z", METAL)
    # collo verso il barilotto di crimpatura
    poly([(x + body, cy - hw), (x + 11.5, cy - 1.2), (x + 11.5, cy + 1.2), (x + body, cy + hw)], METAL)
    sleeve(x + 11.5, x + 20, cy, 1.9, 2.1, 0.6)
    # bordo del barilotto visibile all'imbocco dell'isolante
    line(x + 12.0, cy - 1.9, x + 12.0, cy + 1.9, 0.1)
    return x + 20

def flat_cut(x, cy):
    """Taglio netto: filo libero, estremita' tagliata a filo con il conduttore visibile."""
    rect(x, cy - WIRE_W / 2, 0.4, WIRE_W, METAL, 0.12)
    return x + 0.4

ITEMS = [("Puntalino", ferrule), ("Forcella", fork), ("Faston F 6.3", faston_f), ("Taglio netto", flat_cut)]

cell_w, cell_h = 36.0, 14.0
W = 2 * cell_w + 4
H = 2 * cell_h + 10
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * 8:.0f}" height="{H * 8:.0f}" viewBox="0 0 {W:.1f} {H:.1f}">')
add(f'<rect width="{W:.1f}" height="{H:.1f}" fill="#fff"/>')
text(3, 4, "Terminali — puntalino, forcella, faston F, taglio netto", 2.0, bold=True)
for k, (name, draw) in enumerate(ITEMS):
    r, c = divmod(k, 2)
    cx = 3 + c * cell_w; cy = 9 + r * cell_h
    text(cx, cy, name, 1.8, bold=True)
    mid = cy + 7.0
    x0 = cx + 2
    end = draw(x0, mid)
    wire(end, mid)
add("</svg>")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
