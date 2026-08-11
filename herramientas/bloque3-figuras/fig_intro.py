"""Figuras del Tema 1 (introduccion al sistema de planos acotados)."""

import os
import numpy as np
from terreno import z, to_svg_path, rdp
from svgkit import (SVG, CONTORNOS, DOM_X, DOM_Y, SIENA, TOSTADO, VERDE, ROJO,
                    GRIS, NARANJA2, TEAL, AZUL, AZUL_BORDE, marker_defs,
                    plan_contours, label_on_contour, r1)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, markup):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(markup)
    print("ok", name)


# ----------------------------------------------------------------------
# Proyeccion iso para la figura heroe
# ----------------------------------------------------------------------
S = 0.62
KZ = 1.7
ZPLAN = 52.0   # cota (ficticia) del plano del dibujo, bien separado del terreno


def iso(x, y, zz):
    u = (x - y) * 0.866 * S
    v = (x + y) * 0.30 * S - KZ * (zz - 100.0)
    return u, v


def iso_path(poly, zz, dec=1):
    pts = [iso(p[0], p[1], zz) for p in poly]
    if len(pts) < 2:
        return ""
    d = [f"M {r1(pts[0][0])},{r1(pts[0][1])}"]
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (r1(p1[0] + (p2[0] - p0[0]) / 6.0), r1(p1[1] + (p2[1] - p0[1]) / 6.0))
        c2 = (r1(p2[0] - (p3[0] - p1[0]) / 6.0), r1(p2[1] - (p3[1] - p1[1]) / 6.0))
        d.append(f"C {c1[0]},{c1[1]} {c2[0]},{c2[1]} {r1(p2[0])},{r1(p2[1])}")
    return " ".join(d)


def rhombus(zz):
    corners = [(0, 0), (DOM_X, 0), (DOM_X, DOM_Y), (0, DOM_Y)]
    return [iso(x, y, zz) for x, y in corners]


def boundary_profile(edge, n=140):
    """Perfil del terreno a lo largo de un borde del dominio."""
    if edge == "y0":
        xs = np.linspace(0, DOM_X, n); ys = np.zeros(n)
    elif edge == "x480":
        ys = np.linspace(0, DOM_Y, n); xs = np.full(n, DOM_X)
    elif edge == "y360":
        xs = np.linspace(0, DOM_X, n); ys = np.full(n, DOM_Y)
    else:
        ys = np.linspace(0, DOM_Y, n); xs = np.zeros(n)
    zz = z(xs, ys)
    pts = [iso(x, y, h) for x, y, h in zip(xs, ys, zz)]
    return rdp(np.array(pts), 0.6).tolist()


def hero(deck=True):
    svg = SVG("-378 -150 708 425", width_style="100%", deck=deck)
    svg.raw(marker_defs("axoh"))

    # ---- base: silueta del terreno (perfiles del borde del dominio)
    for edge, dash, w, col in [("x0", None, 1.6, "#4a4a4a"), ("y0", None, 1.6, "#4a4a4a"),
                               ("y360", "5,4", 1.0, "#c0c0c0"), ("x480", None, 1.6, "#4a4a4a")]:
        pts = boundary_profile(edge)
        d = "M " + " L ".join(f"{r1(p[0])},{r1(p[1])}" for p in pts)
        svg.path(d, stroke=col, w=w, dash=dash)
    svg.text(-373, -138, "El terreno", size=14, weight="700", fill="#4a4a4a")

    # ---- frag 1: dos planos horizontales de corte + equidistancia
    svg.frag(1 if deck else None)
    for lev in (130, 140):
        pts = rhombus(lev)
        svg.poly(pts, stroke="#5b7ba0", w=1.1, dash="7,5", closed=True,
                 fill=AZUL, fill_opacity=0.12)
        ux, vx = iso(DOM_X, 0, lev)
        svg.text(ux + 8, vx + 4, str(lev), size=12, fill="#5b7ba0", weight="700")
    ul, vl0 = iso(0, DOM_Y, 130)
    _, vl1 = iso(0, DOM_Y, 140)
    xd = ul - 14
    svg.line(xd, vl0, xd, vl1, stroke=ROJO, w=2)
    svg.line(xd - 5, vl0, xd + 5, vl0, stroke=ROJO, w=2)
    svg.line(xd - 5, vl1, xd + 5, vl1, stroke=ROJO, w=2)
    svg.text(xd - 10, (vl0 + vl1) / 2 + 4, "EQUIDISTANCIA = 10 m", size=12.5, fill=ROJO,
             weight="700", anchor="end")
    svg.text(-373, -120, "1. Corto el terreno con planos", size=12.5, fill="#3f5a78")
    svg.text(-373, -105, "horizontales cada 10 m", size=12.5, fill="#3f5a78")
    svg.end_frag()

    # ---- frag 2: curvas de nivel en 3D
    svg.frag(2 if deck else None)
    for lev in range(100, 161, 10):
        for poly in CONTORNOS[lev]:
            svg.path(iso_path(poly, lev), stroke=SIENA, w=1.9)
    svg.text(-373, -82, "2. Cada corte es una curva de nivel:", size=12.5, fill=SIENA)
    svg.text(-373, -67, "todos sus puntos tienen la misma cota", size=12.5, fill=SIENA)
    svg.end_frag()

    # ---- frag 3: plano de comparacion + proyeccion
    svg.frag(3 if deck else None)
    pts = rhombus(ZPLAN)
    svg.poly(pts, stroke="#1a1a1a", w=1.6, fill=TOSTADO, fill_opacity=0.85, closed=True)
    # rayos de proyeccion desde puntos de las curvas 130 y 110
    for lev, fracs in [(130, (0.15, 0.55)), (110, (0.3,))]:
        for fr in fracs:
            poly = CONTORNOS[lev][0]
            p = poly[int(fr * (len(poly) - 1))]
            u1, v1 = iso(p[0], p[1], lev)
            u2, v2 = iso(p[0], p[1], ZPLAN)
            svg.line(u1, v1, u2, v2, stroke=GRIS, w=1.1, dash="4,3")
    # curvas proyectadas sobre el plano
    for lev in range(100, 161, 10):
        for poly in CONTORNOS[lev]:
            svg.path(iso_path(poly, ZPLAN), stroke=SIENA, w=1.2)
    uc, vc = iso(DOM_X, DOM_Y, ZPLAN)
    svg.text(uc, vc + 22, "PLANO DE COMPARACIÓN (cota 0)", size=13, weight="700",
             fill="#6a5335", anchor="middle")
    svg.text(-373, -44, "3. Proyecto las curvas sobre un plano", size=12.5, fill="#2f4f2f")
    svg.text(-373, -29, "horizontal: el plano acotado", size=12.5, fill="#2f4f2f")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Plan del terreno conductor, rotulado
# ----------------------------------------------------------------------

def terreno_plan(deck=True, labels=True, name="intro_terreno_plan"):
    svg = SVG("-10 -14 500 390", width_style="88%", deck=deck)
    svg.raw(marker_defs("plan1", colors=(("negro", "#1a1a1a"),)))
    svg.raw(f'<rect x="-10" y="-14" width="500" height="390" fill="#fdfbf7"/>')
    plan_contours(svg)
    if labels:
        label_on_contour(svg, 160, 0.45, dy=4)
        label_on_contour(svg, 150, 0.42, dy=4)
        label_on_contour(svg, 140, 0.40, dy=4)
        label_on_contour(svg, 130, 0.38, dy=4)
        label_on_contour(svg, 120, 0.34, dy=4)
        label_on_contour(svg, 110, 0.30, dy=4)
        label_on_contour(svg, 130, 0.5, dy=4, poly_idx=1)
        label_on_contour(svg, 120, 0.5, dy=4, poly_idx=1)
        label_on_contour(svg, 110, 0.55, dy=4, poly_idx=1)
        label_on_contour(svg, 100, 0.6, dy=4, poly_idx=1)
        # norte
        svg.line(468, 40, 468, 10, stroke="#1a1a1a", w=2, marker="plan1-flecha-negro")
        svg.text(461, 54, "N", size=15, weight="700")
        svg.text(6, 371, "Equidistancia = 10 m", size=12.5, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# ¿Que falta en este plano? (tintas hipsometricas, sin rotulos)
# ----------------------------------------------------------------------

def quefalta(deck=True):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xs = np.linspace(0, DOM_X, 481); ys = np.linspace(0, DOM_Y, 361)
    X, Y = np.meshgrid(xs, ys)
    Z = z(X, Y)
    fig, ax = plt.subplots()
    colores = ["#2e8b57", "#63b06a", "#a8cf82", "#e8dc9a", "#dfb35e", "#c9834a", "#a85f38"]
    niveles = [90, 100, 110, 120, 130, 140, 150, 170]
    cf = ax.contourf(X, Y, Z, levels=niveles, colors=colores)
    svg = SVG("-10 -14 500 390", width_style="80%", deck=deck)
    svg.raw('<rect x="-10" y="-14" width="500" height="390" fill="#fdfbf7"/>')
    for col, segs in zip(colores, cf.allsegs):
        for seg in segs:
            if len(seg) < 3:
                continue
            simp = rdp(seg, 1.5)
            pts = [(round(p[0], 1), round(360.0 - p[1], 1)) for p in simp.tolist()]
            d = "M " + " L ".join(f"{a},{b}" for a, b in pts) + " Z"
            svg.path(d, stroke="none", w=0, fill=col, fill_opacity=0.9)
    plt.close(fig)
    plan_contours(svg, stroke="#6a4a22", w_master=1.4, w_normal=0.8)
    return svg.render()


# ----------------------------------------------------------------------
# La equidistancia no se ve: se lee. Intervalos en planta.
# ----------------------------------------------------------------------

def leer_plano(deck=True):
    svg = SVG("-10 -14 500 390", width_style="84%", deck=deck)
    svg.raw(marker_defs("plan2"))
    svg.raw('<rect x="-10" y="-14" width="500" height="390" fill="#fdfbf7"/>')
    plan_contours(svg)
    label_on_contour(svg, 160, 0.2, dy=4)
    label_on_contour(svg, 150, 0.55, dy=4)
    label_on_contour(svg, 140, 0.58, dy=4)
    label_on_contour(svg, 130, 0.38, dy=4)
    label_on_contour(svg, 120, 0.34, dy=4)
    label_on_contour(svg, 110, 0.30, dy=4)
    label_on_contour(svg, 130, 0.8, dy=4, poly_idx=1)
    label_on_contour(svg, 120, 0.85, dy=4, poly_idx=1)
    # frag 1: donde LEO la equidistancia (rodear dos rotulos consecutivos)
    svg.frag(1 if deck else None)
    for lev, fr, pi in [(150, 0.55, 0), (140, 0.58, 0)]:
        poly = CONTORNOS[lev][pi]
        p = poly[int(fr * (len(poly) - 1))]
        svg.raw(f'<ellipse cx="{r1(p[0])}" cy="{r1(DOM_Y - p[1])}" rx="15" ry="9.5" fill="none" stroke="{ROJO}" stroke-width="2"/>')
    svg.text(126, 96, "150 − 140 = 10 m: la equidistancia", size=13.5, fill=ROJO, weight="700", halo=True)
    svg.text(126, 113, "no la VEO, la LEO", size=13.5, fill=ROJO, weight="700", halo=True)
    svg.end_frag()
    # frag 2: intervalos (flechas verdes) en zona junta y zona separada
    svg.frag(2 if deck else None)
    # ladera N del Cerro Mayor: curvas juntas (mucha pendiente)
    svg.raw(f'<line x1="150" y1="40" x2="152.5" y2="6" stroke="{VERDE}" stroke-width="2.4" '
            f'marker-start="url(#plan2-flecha-verde)" marker-end="url(#plan2-flecha-verde)"/>')
    # zona del collado: curvas separadas (poca pendiente)
    svg.raw(f'<line x1="268" y1="208" x2="331" y2="245" stroke="{VERDE}" stroke-width="2.4" '
            f'marker-start="url(#plan2-flecha-verde)" marker-end="url(#plan2-flecha-verde)"/>')
    svg.text(163, 14, "curvas juntas = mucha pendiente", size=13, fill=VERDE, weight="700", halo=True)
    svg.text(310, 278, "curvas separadas =", size=13, fill=VERDE, weight="700", halo=True)
    svg.text(310, 294, "poca pendiente", size=13, fill=VERDE, weight="700", halo=True)
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Pendiente: concepto (plano tostado + dos rectas)
# ----------------------------------------------------------------------

def pendiente(deck=True):
    svg = SVG("0 0 460 250", width_style="78%", deck=deck)
    # plano tostado en perspectiva
    svg.poly([(20, 225), (120, 140), (445, 140), (345, 225)], stroke="#1a1a1a", w=1.6,
             fill=TOSTADO, fill_opacity=0.9, closed=True)
    # recta de poca pendiente (naranja): de (90,205) sube poco
    svg.frag(1 if deck else None)
    svg.line(70, 214, 250, 168, stroke=NARANJA2, w=3.5, cap="round")
    svg.line(190, 183, 190, 168, stroke=ROJO, w=2)          # dV
    svg.line(96, 207, 190, 183, stroke=VERDE, w=2)          # dH sobre el plano
    svg.text(48, 244, "Poca pendiente", size=13, fill="#8a5a10", weight="700")
    svg.end_frag()
    # recta de mucha pendiente (teal)
    svg.frag(2 if deck else None)
    svg.line(255, 210, 360, 30, stroke=TEAL, w=3.5, cap="round")
    svg.line(330, 132, 330, 81, stroke=ROJO, w=2)
    svg.line(272, 181, 330, 132, stroke=VERDE, w=2)
    svg.text(368, 22, "Mucha", size=13, fill=TEAL, weight="700")
    svg.text(368, 38, "pendiente", size=13, fill=TEAL, weight="700")
    svg.end_frag()
    svg.frag(3 if deck else None)
    svg.text(30, 30, "dV", size=13, fill=ROJO, weight="700")
    svg.text(58, 30, "= distancia vertical", size=12, fill="#444")
    svg.text(30, 50, "dH", size=13, fill=VERDE, weight="700")
    svg.text(58, 50, "= distancia horizontal", size=12, fill="#444")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Practica de los conos (dos conos graduados en planta y alzado)
# ----------------------------------------------------------------------

def conos(deck=True):
    svg = SVG("0 0 560 300", width_style="92%", deck=deck)
    esc = 3.2  # px por metro
    for cx, r_m, label, frag in [(120, 20, "Cono 1: R = 20 m, h = 10 m", 1),
                                 (400, 40, "Cono 2: R = 40 m, h = 10 m", 2)]:
        svg.frag(frag if deck else None)
        cy = 150
        # planta: circunferencias cotas 0,2,4,6,8 y vertice cota 10
        rotula = (0, 2) if r_m <= 20 else (0, 1, 2, 3, 4)
        for k in range(0, 5):
            rr = r_m * esc * (1 - k / 5.0)
            svg.circle(cx, cy, r=rr, fill="none", stroke=SIENA, w=1.6 if k else 2.2)
            if k in rotula:
                svg.text(cx + rr * 0.7071 + 3, cy - rr * 0.7071 - 3, str(2 * k), size=10.5, fill=SIENA, weight="700")
        svg.circle(cx, cy, r=2.6, fill="#1a1a1a", stroke="#1a1a1a")
        svg.text(cx + 6, cy - 5, "10", size=10.5, fill="#1a1a1a", weight="700")
        # intervalo marcado en rojo sobre un radio
        x0 = cx + r_m * esc * (3 / 5.0); x1 = cx + r_m * esc * (4 / 5.0)
        svg.line(x0, cy, x1, cy, stroke=ROJO, w=3)
        svg.text((x0 + x1) / 2 - 4, cy + 16, "i", size=13, fill=ROJO, weight="700", style="italic")
        svg.text(cx - 78, 288, label, size=13, fill="#2d2d8a", weight="700")
        svg.end_frag()
    return svg.render()


if __name__ == "__main__":
    save("intro_hero", hero(deck=True))
    save("intro_hero_static", hero(deck=False))
    save("intro_terreno_plan", terreno_plan())
    save("intro_quefalta", quefalta())
    save("intro_leer", leer_plano(deck=True))
    save("intro_leer_static", leer_plano(deck=False))
    save("intro_pendiente", pendiente(deck=True))
    save("intro_pendiente_static", pendiente(deck=False))
    save("intro_conos", conos(deck=True))
    save("intro_conos_static", conos(deck=False))
