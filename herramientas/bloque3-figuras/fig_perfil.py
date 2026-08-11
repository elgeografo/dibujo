"""Figuras del Tema 4 (perfiles longitudinales) sobre el terreno conductor."""

import os
import math
import numpy as np
from terreno import z, rdp
from svgkit import (SVG, SIENA, TOSTADO, VERDE, ROJO, GRIS, NARANJA2, TEAL,
                    AZUL, AZUL_BORDE, marker_defs, plan_contours,
                    label_on_contour, r1, CONTORNOS, DOM_Y)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "svg")


def save(name, markup):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(markup)
    print("ok", name)


# Perfil A-B a traves de las dos cimas y el collado
A = np.array([45.0, 308.0])
B = np.array([445.0, 50.0])
LAB = float(np.hypot(*(B - A)))


def z_al(s):
    """Cota del terreno a distancia s de A sobre la recta AB."""
    t = s / LAB
    p = A + t * (B - A)
    return float(z(p[0], p[1]))


S = np.linspace(0, LAB, 480)
ZS = np.array([z_al(s) for s in S])


def crossings(levels=range(100, 161, 10)):
    """Distancias s donde el perfil cruza cada cota entera."""
    out = []
    for lev in levels:
        d = ZS - lev
        idx = np.where(np.sign(d[:-1]) * np.sign(d[1:]) < 0)[0]
        for i in idx:
            s0, s1 = S[i], S[i + 1]
            f0, f1 = d[i], d[i + 1]
            s = s0 - f0 * (s1 - s0) / (f1 - f0)
            out.append((float(s), float(lev)))
    out.sort()
    return out


CROSS = crossings()


# ----------------------------------------------------------------------
# Traza del perfil en planta
# ----------------------------------------------------------------------

def traza(deck=True):
    svg = SVG("-10 -14 500 390", width_style="82%", deck=deck)
    svg.raw('<rect x="-10" y="-14" width="500" height="390" fill="#fdfbf7"/>')
    plan_contours(svg)
    label_on_contour(svg, 160, 0.2, dy=4)
    label_on_contour(svg, 140, 0.62, dy=4)
    label_on_contour(svg, 120, 0.34, dy=4)
    label_on_contour(svg, 100, 0.6, dy=4, poly_idx=1)
    label_on_contour(svg, 130, 0.5, dy=4, poly_idx=1)
    svg.frag(1 if deck else None)
    svg.line(A[0], DOM_Y - A[1], B[0], DOM_Y - B[1], stroke=ROJO, w=2.6)
    svg.circle(A[0], DOM_Y - A[1], r=4)
    svg.circle(B[0], DOM_Y - B[1], r=4)
    svg.text(A[0] - 12, DOM_Y - A[1] - 10, "A", size=15, weight="700")
    svg.text(B[0] + 8, DOM_Y - B[1] + 6, "B", size=15, weight="700")
    svg.end_frag()
    svg.frag(2 if deck else None)
    for s, lev in CROSS:
        t = s / LAB
        p = A + t * (B - A)
        svg.circle(p[0], DOM_Y - p[1], r=3)
    svg.text(240, 372, "marco los cruces de AB con cada curva de nivel", size=13, fill="#2d2d8a", weight="700", anchor="middle", halo=True)
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Levantar el perfil
# ----------------------------------------------------------------------

EH = 580.0 / LAB          # px por metro en horizontal
X0 = 40.0


def perfil_path(ev, ybase, zbase=95.0, color=VERDE, w=3):
    pts = [(X0 + s * EH, ybase - (zz - zbase) * ev) for s, zz in zip(S, ZS)]
    simp = rdp(np.array(pts), 0.4)
    return "M " + " L ".join(f"{r1(p[0])},{r1(p[1])}" for p in simp)


def levantar(deck=True):
    svg = SVG("0 0 660 420", width_style="94%", deck=deck)
    EV = 2.2
    YB = 395.0            # linea de cota 95
    # banda superior: la linea AB con los cruces
    svg.line(X0, 40, X0 + LAB * EH, 40, stroke="#1a1a1a", w=2.4)
    svg.text(X0 - 6, 32, "A", size=14, weight="700", anchor="end")
    svg.text(X0 + LAB * EH + 6, 32, "B", size=14, weight="700")
    svg.frag(1 if deck else None)
    for s, lev in CROSS:
        x = X0 + s * EH
        svg.line(x, 34, x, 46, stroke=SIENA, w=1.8)
    svg.text(X0 + 8, 22, "cruces con las curvas de nivel (con su cota)", size=11.5, fill=SIENA, style="italic")
    svg.end_frag()
    # guias horizontales de cota
    svg.frag(2 if deck else None)
    for lev in range(100, 161, 10):
        y = YB - (lev - 95.0) * EV
        svg.line(X0, y, X0 + LAB * EH, y, stroke="#c9c9c9", w=0.9)
        svg.text(X0 - 6, y + 4, str(lev), size=11, fill="#777", anchor="end")
    svg.end_frag()
    # verticales desde los cruces
    svg.frag(3 if deck else None)
    for s, lev in CROSS:
        x = X0 + s * EH
        y = YB - (lev - 95.0) * EV
        svg.line(x, 46, x, y, stroke=GRIS, w=0.9, dash="4,3")
        svg.circle(x, y, r=2.8)
    svg.end_frag()
    # perfil
    svg.frag(4 if deck else None)
    svg.path(perfil_path(EV, YB), stroke=VERDE, w=3)
    svg.text(X0 + 200, YB - (ZS.max() - 95) * EV - 10, "el perfil del terreno", size=13, fill=VERDE, weight="700")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Natural vs realzado
# ----------------------------------------------------------------------

def natural_realzado(deck=True):
    svg = SVG("0 0 660 400", width_style="94%", deck=deck)
    eh2 = 0.58
    global EH, X0
    EH_old, X0_old = EH, X0
    EH, X0 = eh2, 60.0
    # natural: Ev = Eh
    svg.frag(1 if deck else None)
    svg.text(40, 28, "Perfil NATURAL: Ev = Eh", size=13.5, fill="#2d2d8a", weight="700")
    svg.line(X0, 118, X0 + LAB * eh2, 118, stroke="#999", w=1)
    svg.path(perfil_path(eh2, 118), stroke=VERDE, w=2.6)
    svg.text(X0 + LAB * eh2 + 12, 96, "queda demasiado", size=11.5, fill="#666", style="italic")
    svg.text(X0 + LAB * eh2 + 12, 110, "“suave”", size=11.5, fill="#666", style="italic")
    svg.end_frag()
    # realzado: Ev = 4 Eh
    svg.frag(2 if deck else None)
    svg.text(40, 168, "Perfil REALZADO: Ev = 4 × Eh (p. ej. Eh 1:8000, Ev 1:2000)", size=13.5, fill="#2d2d8a", weight="700")
    svg.line(X0, 388, X0 + LAB * eh2, 388, stroke="#999", w=1)
    svg.path(perfil_path(eh2 * 4, 388), stroke=VERDE, w=2.6)
    svg.end_frag()
    EH, X0 = EH_old, X0_old
    return svg.render()


# ----------------------------------------------------------------------
# La guitarra
# ----------------------------------------------------------------------

def guitarra(deck=True):
    svg = SVG("0 0 660 430", width_style="94%", deck=deck)
    EV = 1.7
    YB = 220.0
    svg.path(perfil_path(EV, YB), stroke=VERDE, w=2.6)
    for s, lev in CROSS:
        x = X0 + s * EH
        y = YB - (lev - 95.0) * EV
        svg.circle(x, y, r=2.4)
        svg.line(x, y, x, 240, stroke="#bbb", w=0.7)
    svg.line(X0, 240, X0 + LAB * EH, 240, stroke="#1a1a1a", w=1.6)
    # filas de la guitarra
    filas = [("Plano de comparación 95 m", None, 240),
             ("Ordenadas del terreno", "cota", 300),
             ("Distancias al origen", "orig", 360),
             ("Distancias parciales", "parc", 420)]
    svg.frag(1 if deck else None)
    prev_y = 240
    for nombre, tipo, ybot in filas:
        svg.text(8, (prev_y + ybot) / 2 + 4 if tipo else prev_y + 14, nombre, size=10.5, fill="#333")
        svg.line(X0, ybot, X0 + LAB * EH, ybot, stroke="#1a1a1a", w=1.1)
        prev_y = ybot
    prev_s = 0.0
    cols = [(0.0, round(z_al(0), 1))] + [(s, lev) for s, lev in CROSS if 10 < s < LAB - 10] + [(LAB, round(z_al(LAB), 1))]
    for k, (s, lev) in enumerate(cols):
        x = X0 + s * EH
        svg.line(x, 240, x, 420, stroke="#ccc", w=0.6)
        svg.raw(f'<text x="{r1(x + 3)}" y="296" font-size="9.5" fill="#1a1a1a" transform="rotate(-90 {r1(x + 3)} 296)">{lev:g}</text>')
        svg.raw(f'<text x="{r1(x + 3)}" y="356" font-size="9.5" fill="#1a1a1a" transform="rotate(-90 {r1(x + 3)} 356)">{s:.0f}</text>')
        if k > 0:
            svg.raw(f'<text x="{r1((xprev + x) / 2 + 3)}" y="416" font-size="9.5" fill="#555" transform="rotate(-90 {r1((xprev + x) / 2 + 3)} 416)">{s - prev_s:.0f}</text>')
        xprev = x
        prev_s = s
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Perfil desarrollado (dos alineaciones)
# ----------------------------------------------------------------------

V = np.array([270.0, 180.0])   # vertice en el collado


def desarrollado(deck=True):
    svg = SVG("0 0 680 430", width_style="94%", deck=deck)
    # plan reducido arriba a la izquierda
    sc = 0.42
    ox, oy = 30, 20

    def m(p):
        return (ox + p[0] * sc, oy + (DOM_Y - p[1]) * sc)

    svg.raw(f'<g opacity="0.95">')
    for lev in range(100, 161, 10):
        for poly in CONTORNOS[lev]:
            pts = [m((p[0], p[1])) for p in poly]
            d = "M " + " L ".join(f"{r1(a)},{r1(b)}" for a, b in pts)
            svg.path(d, stroke=SIENA, w=1.4 if lev % 50 == 0 else 0.7)
    A2 = np.array([80.0, 300.0]); B2 = np.array([430.0, 60.0])
    svg.line(*m(A2), *m(V), stroke=ROJO, w=2.2)
    svg.line(*m(V), *m(B2), stroke=ROJO, w=2.2)
    svg.circle(*m(A2), r=3.2); svg.circle(*m(V), r=3.2); svg.circle(*m(B2), r=3.2)
    svg.text(m(A2)[0] - 14, m(A2)[1] + 4, "A", size=13, weight="700")
    svg.text(m(V)[0] + 2, m(V)[1] - 8, "V", size=13, weight="700")
    svg.text(m(B2)[0] + 6, m(B2)[1] + 4, "B", size=13, weight="700")
    svg.raw("</g>")
    svg.text(240, 30, "dos alineaciones: A–V y V–B", size=12.5, fill="#444", style="italic")

    # perfil desarrollado abajo
    svg.frag(1 if deck else None)
    L1 = float(np.hypot(*(V - A2))); L2 = float(np.hypot(*(B2 - V)))
    LT = L1 + L2
    eh = 600.0 / LT
    x0 = 40.0
    EV = 2.0
    YB = 405.0

    def z_seg(P, Q, Lseg, s):
        t = s / Lseg
        p = P + t * (Q - P)
        return float(z(p[0], p[1]))

    pts = []
    for s in np.linspace(0, L1, 240):
        pts.append((x0 + s * eh, YB - (z_seg(A2, V, L1, s) - 95.0) * EV))
    for s in np.linspace(0, L2, 240):
        pts.append((x0 + (L1 + s) * eh, YB - (z_seg(V, B2, L2, s) - 95.0) * EV))
    simp = rdp(np.array(pts), 0.4)
    d = "M " + " L ".join(f"{r1(p[0])},{r1(p[1])}" for p in simp)
    svg.line(x0, YB, x0 + LT * eh, YB, stroke="#999", w=1)
    svg.path(d, stroke=VERDE, w=2.8)
    # marca del vertice
    xv = x0 + L1 * eh
    svg.line(xv, YB, xv, 230, stroke=ROJO, w=1.4, dash="6,4")
    svg.circle(xv, 222, r=9, fill="none", stroke=ROJO, w=1.6)
    svg.text(xv, 226, "V", size=11, weight="700", fill=ROJO, anchor="middle")
    svg.text(xv + 14, 240, "el desarrollo “endereza” el eje: giro en V", size=11.5, fill=ROJO, style="italic")
    svg.text(x0, 236, "A", size=13, weight="700")
    svg.text(x0 + LT * eh - 4, 236, "B", size=13, weight="700")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Perfil del terreno con rasante: desmonte y terraplen
# ----------------------------------------------------------------------

def rasante(deck=True):
    svg = SVG("0 0 660 340", width_style="94%", deck=deck)
    EV = 2.0
    YB = 315.0
    zr0, zr1 = 128.0, 106.0

    def zr(s):
        return zr0 + (zr1 - zr0) * s / LAB

    # rellenos desmonte/terraplen
    svg.frag(2 if deck else None)
    above = ZS > np.array([zr(s) for s in S])
    i = 0
    while i < len(S) - 1:
        j = i
        while j < len(S) - 1 and above[j] == above[i]:
            j += 1
        seg_s = S[i:j + 1]
        top = [(X0 + s * EH, YB - (zz - 95.0) * EV) for s, zz in zip(seg_s, ZS[i:j + 1])]
        bot = [(X0 + s * EH, YB - (zr(s) - 95.0) * EV) for s in seg_s[::-1]]
        pts = top + bot
        dpo = "M " + " L ".join(f"{r1(p[0])},{r1(p[1])}" for p in pts) + " Z"
        col = "#e07a7a" if above[i] else "#7ac07a"
        svg.path(dpo, stroke="none", w=0, fill=col, fill_opacity=0.55)
        i = j
    svg.text(150, 120, "DESMONTE (quito tierra)", size=12.5, fill="#b03030", weight="700")
    svg.text(300, 300, "TERRAPLÉN (aporto tierra)", size=12.5, fill="#2a7a2a", weight="700")
    svg.end_frag()
    # perfil y rasante
    svg.path(perfil_path(EV, YB), stroke=VERDE, w=2.8)
    svg.frag(1 if deck else None)
    svg.line(X0, YB - (zr0 - 95) * EV, X0 + LAB * EH, YB - (zr1 - 95) * EV, stroke="#1a1a1a", w=2.6)
    svg.text(X0 + 8, YB - (zr0 - 95) * EV - 10, "rasante de la obra", size=12.5, weight="700")
    svg.text(X0 + LAB * EH - 4, YB - (z_al(LAB) - 95.0) * EV - 12, "terreno", size=12.5, fill=VERDE, weight="700", anchor="end")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Perfiles transversales (concepto, en planta)
# ----------------------------------------------------------------------

def transversales(deck=False):
    svg = SVG("0 0 560 300", width_style="80%", deck=deck)
    # eje con dos alineaciones
    P0, P1, P2 = (60, 240), (280, 140), (500, 180)
    svg.line(*P0, *P1, stroke=ROJO, w=2.6)
    svg.line(*P1, *P2, stroke=ROJO, w=2.6)
    svg.text(30, 222, "eje de la obra", size=12.5, fill=ROJO, weight="700")
    k = 1
    for (Pa, Pb, n) in [(P0, P1, 4), (P1, P2, 3)]:
        vx, vy = Pb[0] - Pa[0], Pb[1] - Pa[1]
        nrm = math.hypot(vx, vy)
        ux, uy = vx / nrm, vy / nrm
        px, py = -uy, ux
        for j in range(n):
            t = (j + 0.5) / n
            cx, cy = Pa[0] + vx * t, Pa[1] + vy * t
            svg.line(cx - px * 34, cy - py * 34, cx + px * 34, cy + py * 34, stroke=TEAL, w=2)
            svg.text(cx + px * 44, cy + py * 44 + 4, f"T{k}", size=11.5, fill=TEAL, weight="700", anchor="middle")
            k += 1
    svg.text(280, 292, "Perfiles perpendiculares al eje: la sección cambia en cada punto", size=12.5, fill="#555", anchor="middle")
    return svg.render()


if __name__ == "__main__":
    print("A:", round(z_al(0), 1), "B:", round(z_al(LAB), 1), "L:", round(LAB, 1))
    print("cruces:", [(round(s), lev) for s, lev in CROSS])
    save("perf_traza", traza(True)); save("perf_traza_static", traza(False))
    save("perf_levantar", levantar(True)); save("perf_levantar_static", levantar(False))
    save("perf_natural", natural_realzado(True)); save("perf_natural_static", natural_realzado(False))
    save("perf_guitarra", guitarra(True)); save("perf_guitarra_static", guitarra(False))
    save("perf_desarrollado", desarrollado(True)); save("perf_desarrollado_static", desarrollado(False))
    save("perf_rasante", rasante(True)); save("perf_rasante_static", rasante(False))
    save("perf_transversales", transversales())
