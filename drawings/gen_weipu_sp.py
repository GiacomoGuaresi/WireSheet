"""Genera drawings/weipu_sp.svg: prese da pannello circolari tipo Weipu (fissaggio con dado
posteriore, codici GM-1312/S, GM-1712/S, GM-2112/S) + schema pin frontale per ogni configurazione.

Vista laterale (scala 1:1): faccia di innesto a sinistra, contatti a saldare e fili a destra.
Quote d'ingombro dalla scheda Hengzhan "Rear mount":
  GM-13: flangia d19.5, M13x1, sporgenza 10, totale 23
  GM-17: flangia d25,   M17,   sporgenza 12.2, totale 27
  GM-21: flangia d29,   M21x1, sporgenza 13.3, totale 27

Schema pin (scala 2:1): vista frontale del lato innesto della femmina /S, chiave in alto.
Le tabelle del fornitore mostrano il maschio; la femmina vista di fronte e' lo specchio
(verificato sulla foto di SP2112/S12: in alto 1-2, ultima fila 10-11-12).

Uso: python drawings/gen_weipu_sp.py drawings/weipu_sp.svg
"""
import sys

INK = "#000"; BODY = "#f5f5f5"; SHADE = "#dcdcdc"; METAL = "#e6e6e6"; WIRE = "#c8c8c8"
WIRE_W, WIRE_L = 1.3, 8.0
FACE_SCALE = 2.0

# Layout pin del MASCHIO dalle tabelle del fornitore: (numero, x, y, diametro contatto mm),
# coordinate normalizzate sul raggio dell'isolante (y verso il basso, chiave in alto).
def sym(*pins):
    return list(pins)

L13_17 = {
    "2P": [(1, 0.42, 0.0), (2, -0.42, 0.0)],
    "3P": [(1, 0.38, -0.25), (2, -0.38, -0.25), (3, 0.0, 0.39)],
    "4P": [(1, 0.31, -0.34), (2, -0.31, -0.34), (3, -0.31, 0.34), (4, 0.31, 0.34)],
    "5P": [(1, -0.29, -0.46), (5, 0.29, -0.46), (2, -0.48, 0.09), (4, 0.48, 0.09), (3, 0.0, 0.46)],
    "6P": [(1, 0.0, -0.58), (2, -0.47, -0.28), (3, -0.49, 0.29), (4, 0.0, 0.56), (5, 0.49, 0.29),
           (6, 0.47, -0.28)],
    "7P": [(1, -0.29, -0.5), (6, 0.29, -0.5), (2, -0.58, 0.0), (7, 0.0, 0.0), (5, 0.58, 0.0),
           (3, -0.29, 0.5), (4, 0.29, 0.5)],
    "9P": [(1, -0.22, -0.52), (8, 0.22, -0.52), (2, -0.52, -0.18), (7, 0.52, -0.18), (9, -0.08, 0.0),
           (3, -0.52, 0.22), (6, 0.52, 0.22), (4, -0.22, 0.55), (5, 0.22, 0.55)],
}
L21 = {
    "2P": [(1, 0.0, -0.41), (2, 0.0, 0.41)],
    "3P": [(1, 0.35, -0.2), (2, -0.35, -0.2), (3, 0.0, 0.41)],
    "4P": [(1, 0.0, -0.4), (2, 0.4, 0.0), (3, -0.4, 0.0), (4, 0.0, 0.4)],
    "5P-A": [(1, 0.25, -0.32), (2, -0.25, -0.32), (3, 0.4, 0.13), (4, -0.4, 0.13), (5, 0.0, 0.42)],
    "5P-B": [(1, 0.34, -0.3), (2, -0.34, -0.3), (3, 0.42, 0.31), (4, -0.42, 0.31), (5, 0.0, 0.53)],
    "5P-C": [(1, 0.33, -0.47), (2, -0.33, -0.47), (3, 0.54, 0.13), (4, -0.54, 0.13), (5, 0.0, 0.53)],
    "7P": [(1, 0.24, -0.41), (2, -0.24, -0.41), (3, 0.47, 0.0), (4, 0.0, 0.0), (5, -0.47, 0.0),
           (6, 0.24, 0.41), (7, -0.24, 0.41)],
    "9P": [(1, 0.22, -0.55), (2, -0.22, -0.55), (3, 0.56, -0.2), (4, -0.56, -0.2), (5, 0.0, 0.02),
           (6, 0.56, 0.25), (7, -0.56, 0.25), (8, 0.22, 0.58), (9, -0.22, 0.58)],
    "12P": [(1, 0.21, -0.59), (2, -0.21, -0.59), (3, 0.53, -0.34), (4, 0.0, -0.26), (5, -0.53, -0.34),
            (6, 0.6, 0.08), (7, 0.21, 0.1), (8, -0.21, 0.1), (9, -0.6, 0.08), (10, 0.38, 0.43),
            (11, 0.0, 0.56), (12, -0.38, 0.43)],
}

def contact_d(series, cfg, num):
    """Diametro contatto (mm) dalle tabelle del fornitore."""
    if series == "GM-13":
        return {"2P": 1.6, "3P": 1.6, "9P": 0.7}.get(cfg, 1.0)
    if series == "GM-17":
        return {"2P": 1.5, "3P": 1.5}.get(cfg, 1.0)
    if cfg == "5P-B":
        return 3.0 if num in (1, 2) else 1.0
    return {"2P": 3.0, "3P": 3.0, "4P": 3.0, "5P-A": 3.0, "5P-C": 2.0, "7P": 2.0}.get(cfg, 1.0)

# serie: (flangia, sporgenza, totale, filetto, d isolante, configurazioni)
SERIES = {
    "GM-13": (19.5, 10.0, 23.0, 13.0, 10.0, ["2P", "3P", "4P", "5P", "6P", "7P", "9P"], L13_17),
    "GM-17": (25.0, 12.2, 27.0, 17.0, 13.0, ["2P", "3P", "4P", "5P", "7P", "9P"], L13_17),
    "GM-21": (29.0, 13.3, 27.0, 21.0, 16.0, ["2P", "3P", "4P", "5P-A", "5P-B", "5P-C", "7P", "9P", "12P"], L21),
}

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
def path(d, fill, sw=0.2):
    add(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
def text(x, y, s, size=2.0, anchor="start", bold=False):
    w = ' font-weight="bold"' if bold else ""
    # testo scritto in decimi di mm: alcuni renderer (Qt) arrotondano font-size all'intero
    # baseline spostata a mano (Qt ignora dominant-baseline): y e' il centro del testo
    add(f'<text transform="translate({f(x)} {f(y + size * 0.36)}) scale(0.1)" font-family="Arial" '
        f'font-size="{size * 10:.1f}" text-anchor="{anchor}"{w}>{s}</text>')

def panel_socket(x0, cy, F, a, T, M):
    """Presa da pannello con dado posteriore; (x0, cy) = centro della faccia di innesto."""
    r = T - a
    def band(u0, u1, d, fill=BODY):
        rect(x0 + u0, cy - d / 2, u1 - u0, d, fill)
    # fili in uscita dai contatti a saldare
    for v in (-0.15, 0.0, 0.15):
        rect(x0 + T, cy + v * F - WIRE_W / 2, WIRE_L, WIRE_W, WIRE, 0.12)
    # parte anteriore filettata (accoppiamento con la ghiera della spina)
    band(0.0, 0.42 * a, 0.74 * F)
    for i in range(1, 6):
        u = 0.42 * a * i / 6
        line(x0 + u, cy - 0.37 * F, x0 + u, cy + 0.37 * F, 0.08)
    # corpo con chiave di polarizzazione in alto
    band(0.42 * a, 0.85 * a, 0.80 * F)
    rect(x0 + 0.5 * a, cy - 0.80 * F / 2 - 0.6, 0.3 * a, 0.6, SHADE, 0.12)
    # flangia di battuta sul pannello
    band(0.85 * a, a, F, SHADE)
    # filetto posteriore e dado esagonale
    band(a, a + 0.55 * r, M)
    for i in range(1, 8):
        u = a + 0.55 * r * i / 8
        line(x0 + u, cy - M / 2, x0 + u, cy + M / 2, 0.08)
    band(a + 0.18 * r, a + 0.40 * r, 0.95 * F)
    for v in (-0.25, 0.25):
        line(x0 + a + 0.18 * r, cy + v * F, x0 + a + 0.40 * r, cy + v * F, 0.1)
    # isolante posteriore arrotondato
    x1, x2, h = x0 + a + 0.55 * r, x0 + a + 0.78 * r, 0.30 * F
    path(f"M{f(x1)},{f(cy - h)} L{f(x2 - 1.0)},{f(cy - h)} Q{f(x2)},{f(cy - h)} {f(x2)},{f(cy - h + 1.0)} "
         f"L{f(x2)},{f(cy + h - 1.0)} Q{f(x2)},{f(cy + h)} {f(x2 - 1.0)},{f(cy + h)} L{f(x1)},{f(cy + h)} Z", BODY)
    # contatti a saldare
    for v in (-0.15, 0.0, 0.15):
        rect(x2, cy + v * F - 0.5, x0 + T - x2, 1.0, METAL, 0.12)

def dashed(x1, y1, x2, y2):
    add(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{INK}" stroke-width="0.1" '
        f'stroke-dasharray="3 0.8 0.6 0.8"/>')

def pin_face(cx, cy, series, cfg, layout, insert_d, thread_d):
    """Faccia frontale femmina lato innesto (specchio del maschio), scala FACE_SCALE.
    Dall'esterno: filetto di accoppiamento, cavita' per il manicotto della spina, isolante."""
    s = FACE_SCALE
    R = insert_d / 2 * s
    Ro = thread_d / 2 * s
    Rw = Ro - 0.7 * s            # parete interna del corpo
    # assi
    dashed(cx - Ro - 2, cy, cx + Ro + 2, cy)
    dashed(cx, cy - Ro - 2, cx, cy + Ro + 2)
    # filetto esterno (cresta e fondo) e corpo
    circle(cx, cy, Ro, SHADE, 0.2)
    add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(Ro - 0.35 * s)}" fill="none" stroke="{INK}" '
        f'stroke-width="0.08" stroke-dasharray="0.6 0.4"/>')
    circle(cx, cy, Rw, "#fff", 0.15)
    # chiave di polarizzazione sul corpo (in alto) e cava corrispondente sull'isolante
    kw = 0.9 * s
    rect(cx - kw / 2, cy - Rw - 0.05, kw, Rw - R + 0.7 * s, SHADE, 0.12)
    circle(cx, cy, R, BODY, 0.2)
    rect(cx - kw / 2 - 0.15, cy - R - 0.05, kw + 0.3, 0.7 * s + 0.05, "#fff", 0.12)
    rect(cx - kw / 2, cy - Rw - 0.05, kw, Rw - R + 0.7 * s, SHADE, 0.12)
    # numero dentro il cerchio del contatto: cerchio bianco, almeno grande quanto il numero
    lab, rmin = (2.2, 1.75) if insert_d < 12 else (2.6, 2.1)
    for num, x, y in layout[cfg]:
        px, py = cx - x * R, cy + y * R          # specchio orizzontale: femmina vista di fronte
        rc = max(rmin, contact_d(series, cfg, num) / 2 * s + 0.3)
        circle(px, py, rc, "#fff", 0.2)
        text(px, py, str(num), lab, "middle", True)

page_w = 210.0
rows = []
for name, (F, a, T, M, ins, cfgs, layout) in SERIES.items():
    cell = M * FACE_SCALE + 8
    per_row = int((page_w - 50) // cell)
    lines = (len(cfgs) + per_row - 1) // per_row
    rows.append((name, F, a, T, M, ins, cfgs, layout, cell, per_row, max(F + 10, lines * (cell + 3) + 6)))

SH = sum(r[-1] for r in rows) + 14
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_w * 5:.0f}" height="{SH * 5:.0f}" viewBox="0 0 {page_w:.1f} {SH:.1f}">')
add(f'<rect width="{page_w:.1f}" height="{SH:.1f}" fill="#fff"/>')
text(3, 4, "Prese da pannello tipo Weipu (dado posteriore) — GM-13 / GM-17 / GM-21 xx12/S", 2.0, bold=True)
text(3, 7.5, "Vista laterale 1:1 — schema pin 2:1, vista frontale lato innesto femmina, chiave in alto", 1.8)
top = 13
for name, F, a, T, M, ins, cfgs, layout, cell, per_row, h in rows:
    text(3, top, f"{name}12/S", 2.0, bold=True)
    panel_socket(4, top + 4 + F / 2, F, a, T, M)
    fx0 = 48
    for k, cfg in enumerate(cfgs):
        r, c = divmod(k, per_row)
        cx = fx0 + c * cell + cell / 2
        cy = top + 3 + r * (cell + 3) + cell / 2
        pin_face(cx, cy, name, cfg, layout, ins, M)
        text(cx, cy + M * FACE_SCALE / 2 + 3.2, cfg, 2.4, "middle", True)
    top += h
    line(3, top - 2, page_w - 3, top - 2, 0.08)
add("</svg>")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
