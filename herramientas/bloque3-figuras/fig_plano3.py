"""Figuras del Tema 3 (el plano en planta, intersecciones, vaguadas y divisorias)."""

import os
import math
import numpy as np
from terreno import z, grad_z, rdp
from svgkit import (SVG, SIENA, TOSTADO, VERDE, ROJO, GRIS, NARANJA2, TEAL,
                    AZUL, AZUL_BORDE, marker_defs, plan_contours,
                    label_on_contour, streamline, r1, CONTORNOS, DOM_Y)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "svg")


def save(name, markup):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(markup)
    print("ok", name)


# ----------------------------------------------------------------------
# Base: plano graduado en planta (traza + horizontales + lmp)
# ----------------------------------------------------------------------

TH = math.radians(-10)
DX, DY = math.cos(TH), -math.sin(TH)
NX, NY = -math.sin(TH), math.cos(TH)
STEP = 60.0
OX, OY = 120, 55
L = 400


def hpt(k, t):
    """Punto en la horizontal k (0=traza), parametro t en [0,1] a lo largo."""
    return (OX + NX * STEP * k + DX * L * t, OY + NY * STEP * k + DY * L * t)


def dibuja_horizontales(svg, cotas=True, con_traza=True, k_ini=0):
    for k in range(k_ini, 5):
        a, b = hpt(k, 0), hpt(k, 1)
        if k == 0 and con_traza:
            svg.line(*a, *b, stroke="#1a1a1a", w=3.2)
            if cotas:
                svg.text(b[0] - 4, b[1] - 8, "traza (0)", size=12.5, weight="700", anchor="end")
        else:
            svg.line(*a, *b, stroke="#2e9e40", w=2.4)
            if cotas:
                svg.text(b[0] + 5, b[1] + 4, str(2 * k), size=12.5, weight="700", fill="#d00000")


# ----------------------------------------------------------------------
# Recta pertenece a plano: cotas por pertenencia
# ----------------------------------------------------------------------

def pertenencia(deck=True):
    svg = SVG("0 0 560 400", width_style="78%", deck=deck)
    dibuja_horizontales(svg)
    # lmp graduada
    s = hpt(0, 0.5)
    e = hpt(4.45, 0.5 - 0.0)
    svg.line(*hpt(-0.3, 0.5), *e, stroke=ROJO, w=2.6)
    for k in range(0, 5):
        svg.circle(*hpt(k, 0.5), r=3.2)
    svg.text(e[0] + 6, e[1] + 2, "l.m.p.", size=12, fill=ROJO, weight="700", style="italic")
    # recta oblicua contenida en el plano (proyeccion cualquiera)
    svg.frag(1 if deck else None)
    ra, rb = hpt(-0.5, 0.86), hpt(5.0, 0.62)
    svg.line(*ra, *rb, stroke="#6a4a92", w=2.8)
    svg.text(ra[0] + 10, ra[1] + 2, "s", size=14, fill="#6a4a92", weight="700", style="italic")
    svg.end_frag()
    # puntos de cruce con las horizontales -> cota por pertenencia
    svg.frag(2 if deck else None)
    for k in (1, 3):
        # interseccion recta s con horizontal k
        # parametrizar: p = ra + u*(rb-ra); q = hpt(k,0) + t*(hpt(k,1)-hpt(k,0))
        p0 = np.array(ra); p1 = np.array(rb)
        q0 = np.array(hpt(k, 0)); q1 = np.array(hpt(k, 1))
        A = np.array([[p1[0] - p0[0], -(q1[0] - q0[0])], [p1[1] - p0[1], -(q1[1] - q0[1])]])
        b = q0 - p0
        u, t = np.linalg.solve(A, b)
        P = p0 + u * (p1 - p0)
        svg.circle(P[0], P[1], r=3.6)
        svg.text(P[0] + 7, P[1] + 16, f"({2 * k})", size=12.5, weight="700", fill="#2d2d8a")
    svg.text(60, 372, "En los cruces con las líneas de nivel, la cota de la recta es la del plano", size=12.5, fill="#2d2d8a", weight="700")
    svg.end_frag()
    svg.text(60, 392, "Equidistancia = 2 m", size=12, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# Formas de definir un plano
# ----------------------------------------------------------------------

def definir1(deck=True):
    """Dato: una linea de nivel (cota 2) y la pendiente del plano (30%)."""
    svg = SVG("0 0 560 400", width_style="78%", deck=deck)
    # dato: la horizontal de cota 2
    a, b = hpt(1, 0), hpt(1, 1)
    svg.line(*a, *b, stroke="#2e9e40", w=3)
    svg.text(b[0] + 5, b[1] + 4, "2", size=12.5, weight="700", fill="#d00000")
    svg.text(60, 34, "dato: una línea de nivel y la pendiente (30 %)", size=12.5, fill="#444", style="italic")
    # calculo intervalo y graduo la lmp
    svg.frag(1 if deck else None)
    svg.line(*hpt(0.7, 0.5), *hpt(4.45, 0.5), stroke=ROJO, w=2.6)
    for k in range(1, 5):
        svg.circle(*hpt(k, 0.5), r=3.2)
    p2 = hpt(2, 0.5)
    svg.text(p2[0] + 10, p2[1] - 8, "i = e / pte = 2 / 0,30 = 6,67 m", size=12.5, fill=ROJO, weight="700")
    svg.end_frag()
    # resto de horizontales
    svg.frag(2 if deck else None)
    for k in (2, 3, 4):
        a2, b2 = hpt(k, 0), hpt(k, 1)
        svg.line(*a2, *b2, stroke="#2e9e40", w=2.4, dash=None)
        svg.text(b2[0] + 5, b2[1] + 4, str(2 * k), size=12.5, weight="700", fill="#d00000")
    a0, b0 = hpt(0, 0), hpt(0, 1)
    svg.line(*a0, *b0, stroke="#1a1a1a", w=3.2)
    svg.text(b0[0] - 4, b0[1] - 8, "traza (0)", size=12.5, weight="700", anchor="end")
    svg.end_frag()
    svg.text(60, 392, "Equidistancia = 2 m · Escala 1:500", size=12, fill="#555")
    return svg.render()


def definir2(deck=True):
    """Dato: una recta graduada y un punto exterior con cota."""
    svg = SVG("0 0 560 400", width_style="78%", deck=deck)
    # recta graduada cualquiera (no lmp): con puntos de cota 2,4,6,8
    ra, rb = hpt(-0.4, 0.28), hpt(5.0, 0.52)
    svg.line(*ra, *rb, stroke="#1a1a1a", w=2.6)
    svg.text(ra[0] - 8, ra[1] - 8, "recta graduada", size=12, fill="#444", style="italic")
    # sus puntos de cota estan donde cruza las horizontales
    cruces = {}
    p0 = np.array(ra); p1 = np.array(rb)
    for k in range(0, 5):
        q0 = np.array(hpt(k, 0)); q1 = np.array(hpt(k, 1))
        A = np.array([[p1[0] - p0[0], -(q1[0] - q0[0])], [p1[1] - p0[1], -(q1[1] - q0[1])]])
        b = q0 - p0
        u, t = np.linalg.solve(A, b)
        P = p0 + u * (p1 - p0)
        cruces[k] = P
        svg.circle(P[0], P[1], r=3.4)
        svg.text(P[0] - 4, P[1] + 18, f"{2 * k}", size=12, weight="700", fill="#2d2d8a")
    # punto exterior con cota 2
    M = hpt(1, 0.88)
    svg.circle(*M, r=3.6)
    svg.text(M[0] + 7, M[1] - 6, "m(2)", size=12.5, weight="700", fill="#2d2d8a")
    # frag: linea de nivel por el punto y la cota igual de la recta
    svg.frag(1 if deck else None)
    P2 = cruces[1]
    svg.line(P2[0], P2[1], M[0] + (M[0] - P2[0]) * 0.18, M[1] + (M[1] - P2[1]) * 0.18, stroke="#2e9e40", w=3)
    svg.text((P2[0] + M[0]) / 2, (P2[1] + M[1]) / 2 - 10, "línea de nivel 2", size=12, fill="#2e9e40", weight="700")
    svg.end_frag()
    # frag: las demas horizontales paralelas por los puntos de cota
    svg.frag(2 if deck else None)
    d = (M[0] - P2[0], M[1] - P2[1])
    nrm = math.hypot(*d)
    dxu, dyu = d[0] / nrm, d[1] / nrm
    for k in (0, 2, 3, 4):
        P = cruces[k]
        tmax = (500.0 - P[0]) / dxu
        svg.line(P[0] - dxu * 40, P[1] - dyu * 40, P[0] + dxu * tmax, P[1] + dyu * tmax,
                 stroke="#2e9e40" if k else "#1a1a1a", w=2.2 if k else 3)
        svg.text(P[0] + dxu * tmax + 6, P[1] + dyu * tmax + 4, str(2 * k) if k else "traza (0)",
                 size=12, weight="700", fill="#d00000" if k else "#1a1a1a")
    svg.text(60, 372, "Las demás líneas de nivel: paralelas por los puntos de cota de la recta", size=12.5, fill="#2d2d8a", weight="700")
    svg.end_frag()
    svg.text(60, 392, "Equidistancia = 2 m", size=12, fill="#555")
    return svg.render()


def definir3(deck=True):
    """Dato: tres puntos no alineados."""
    svg = SVG("0 0 560 400", width_style="78%", deck=deck)
    A = (140, 300); B = (430, 120); C = (410, 330)
    for (p, lab) in [(A, "a(2)"), (B, "b(8)"), (C, "c(4)")]:
        svg.circle(*p, r=3.8)
        dx_l, dy_l = (8, 16) if lab != "c(4)" else (-40, 22)
        svg.text(p[0] + dx_l, p[1] + dy_l, lab, size=13, weight="700", fill="#2d2d8a")
    svg.text(70, 60, "dato: tres puntos no alineados", size=12.5, fill="#444", style="italic")
    # frag 1: uno dos puntos -> recta, la graduo
    svg.frag(1 if deck else None)
    svg.line(*A, *B, stroke="#1a1a1a", w=2.6)
    # puntos de cota 4 y 6 sobre ab (de 2 a 8: tercios)
    for k, cota in [(1, 4), (2, 6)]:
        P = (A[0] + (B[0] - A[0]) * k / 3.0, A[1] + (B[1] - A[1]) * k / 3.0)
        svg.circle(*P, r=3.4)
        svg.text(P[0] - 6, P[1] + 18, f"({cota})", size=12, weight="700", fill="#2d2d8a")
    svg.text(150, 130, "uno a y b, y gradúo ab", size=12, fill="#555", style="italic")
    svg.end_frag()
    # frag 2: recta + punto -> caso anterior: linea de nivel 4 por c
    svg.frag(2 if deck else None)
    P4 = (A[0] + (B[0] - A[0]) / 3.0, A[1] + (B[1] - A[1]) / 3.0)
    dx4, dy4 = C[0] - P4[0], C[1] - P4[1]
    nn = math.hypot(dx4, dy4)
    dxu, dyu = dx4 / nn, dy4 / nn
    svg.line(P4[0] - dxu * 30, P4[1] - dyu * 30, C[0] + dxu * 50, C[1] + dyu * 50, stroke="#2e9e40", w=3)
    svg.text(C[0] + dxu * 56 + 4, C[1] + dyu * 56 + 4, "línea de nivel 4", size=12, fill="#2e9e40", weight="700")
    svg.text(70, 372, "…y ya es el caso anterior: recta graduada + punto", size=12.5, fill="#2d2d8a", weight="700")
    svg.end_frag()
    svg.text(70, 392, "Equidistancia = 2 m", size=12, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# Interseccion de dos planos
# ----------------------------------------------------------------------

def interseccion(deck=True):
    svg = SVG("0 0 620 420", width_style="80%", deck=deck)
    # plano verde: horizontales casi horizontales; plano rosa: casi verticales
    # verde: y = 340 - 55*k (cotas 1215+5k?) usemos cotas 100,105,110,115
    svg.frag(1 if deck else None)
    for k in range(0, 4):
        y = 330 - 62 * k
        svg.line(60, y + 14, 420, y - 14, stroke="#2e9e40", w=2.4)
        svg.text(52, y + 18, str(100 + 5 * k), size=12, weight="700", fill="#2e9e40", anchor="end")
    svg.text(120, 396, "plano verde: gradúo sus líneas de nivel", size=12.5, fill="#2e9e40", weight="700")
    svg.end_frag()
    svg.frag(2 if deck else None)
    for k in range(0, 4):
        x = 200 + 88 * k
        svg.line(x - 20, 60, x + 26, 400, stroke="#c05ad0", w=2.4)
        svg.text(x - 22, 52, str(100 + 5 * k), size=12, weight="700", fill="#a03ab0")
    svg.text(480, 90, "plano rosa:", size=12.5, fill="#a03ab0", weight="700")
    svg.text(480, 106, "gradúo", size=12.5, fill="#a03ab0", weight="700")
    svg.end_frag()
    # interseccion: puntos de igual cota
    svg.frag(3 if deck else None)
    pts = []
    for k in range(0, 4):
        y = 330 - 62 * k
        x = 200 + 88 * k
        g0 = np.array([60.0, y + 14]); g1 = np.array([420.0, y - 14])
        r0 = np.array([x - 20.0, 60.0]); r1_ = np.array([x + 26.0, 400.0])
        A = np.array([[g1[0] - g0[0], -(r1_[0] - r0[0])], [g1[1] - g0[1], -(r1_[1] - r0[1])]])
        b = r0 - g0
        u, t = np.linalg.solve(A, b)
        P = g0 + u * (g1 - g0)
        pts.append(P)
        svg.circle(P[0], P[1], r=4)
    svg.line(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], stroke=TOSTADO, w=5, cap="round")
    for P in pts:
        svg.circle(P[0], P[1], r=4)
    svg.text(608, 386, "intersección: puntos de igual cota", size=13, fill="#8a6a30", weight="700", anchor="end")
    svg.end_frag()
    svg.text(52, 416, "Equidistancia = 5 m", size=12, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# Vaguadas y divisorias sobre el terreno conductor
# ----------------------------------------------------------------------

def vaguadas(deck=True):
    svg = SVG("-10 -14 500 400", width_style="76%", deck=deck)
    svg.raw(marker_defs("vg", colors=(("azul", "#1d6fd0"), ("rojo", ROJO))))
    svg.raw('<rect x="-10" y="-14" width="500" height="400" fill="#fdfbf7"/>')
    plan_contours(svg)
    label_on_contour(svg, 160, 0.2, dy=4)
    label_on_contour(svg, 140, 0.62, dy=4)
    label_on_contour(svg, 120, 0.34, dy=4)
    label_on_contour(svg, 100, 0.6, dy=4, poly_idx=1)
    label_on_contour(svg, 130, 0.5, dy=4, poly_idx=1)
    label_on_contour(svg, 110, 0.55, dy=4, poly_idx=1)

    # vaguadas: descensos desde cerca del collado (270,180) hacia NE y SW
    svg.frag(1 if deck else None)
    for x0, y0 in [(276, 192), (262, 168)]:
        sl = streamline(x0, y0, direction=-1, step=2.5)
        pts = [(p[0], DOM_Y - p[1]) for p in sl]
        d = "M " + " L ".join(f"{r1(a)},{r1(b)}" for a, b in pts)
        svg.path(d, stroke="#1d6fd0", w=3)
    svg.text(430, 40, "vaguada", size=14, fill="#1d6fd0", weight="700", anchor="end", halo=True)
    svg.text(150, 330, "vaguada", size=14, fill="#1d6fd0", weight="700", halo=True)
    svg.end_frag()

    # divisorias: ascensos desde el collado hacia las dos cimas
    svg.frag(2 if deck else None)
    for x0, y0 in [(255, 185), (283, 172)]:
        sl = streamline(x0, y0, direction=1, step=2.5)
        pts = [(p[0], DOM_Y - p[1]) for p in sl]
        d = "M " + " L ".join(f"{r1(a)},{r1(b)}" for a, b in pts)
        svg.path(d, stroke=ROJO, w=3, dash="8,4")
    svg.text(205, 152, "divisoria", size=14, fill=ROJO, weight="700", halo=True)
    svg.text(352, 196, "divisoria", size=14, fill=ROJO, weight="700", halo=True)
    svg.end_frag()

    # collado y lectura de las curvas
    svg.frag(3 if deck else None)
    svg.circle(270, DOM_Y - 180, r=5, fill="#fff", stroke="#1a1a1a", w=2)
    svg.text(282, DOM_Y - 180 + 4, "collado", size=13, weight="700", halo=True)
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Interpolacion lineal en un triangulo (para el capitulo de curvado)
# ----------------------------------------------------------------------

def interp_triangulo(deck=False):
    svg = SVG("0 0 560 340", width_style="72%", deck=deck)
    A = (80, 290); B = (300, 60); C = (500, 250)
    va, vb, vc = 18.0, 42.0, 31.0
    svg.poly([A, B, C], stroke="#1a1a1a", w=2.4, closed=True)
    for (p, v, dx, dy) in [(A, va, -34, 18), (B, vb, -10, -12), (C, vc, 14, 16)]:
        svg.circle(*p, r=4)
        svg.text(p[0] + dx, p[1] + dy, f"{v:g}", size=13.5, weight="700", fill="#2d2d8a")
    # graduar cada lado para los multiplos de 5: 20,25,30,35,40
    niveles = [20, 25, 30, 35, 40]
    cortes = {n: [] for n in niveles}
    for (P, vp, Q, vq) in [(A, va, B, vb), (B, vb, C, vc), (A, va, C, vc)]:
        for n in niveles:
            if min(vp, vq) < n < max(vp, vq):
                t = (n - vp) / (vq - vp)
                X = (P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t)
                cortes[n].append(X)
                svg.circle(X[0], X[1], r=2.8, fill="#e8a33d", stroke="#7a5510", w=1.2)
    for n in niveles:
        if len(cortes[n]) == 2:
            (x0, y0), (x1, y1) = cortes[n]
            svg.line(x0, y0, x1, y1, stroke=SIENA, w=2)
            svg.text((x0 + x1) / 2 + 6, (y0 + y1) / 2 - 6, str(n), size=11.5, weight="700", fill=SIENA)
    svg.text(30, 328, "Graduando los lados (interpolación lineal) y uniendo puntos de igual valor", size=12.5, fill="#555")
    return svg.render()


if __name__ == "__main__":
    save("pl3_pertenencia", pertenencia(True)); save("pl3_pertenencia_static", pertenencia(False))
    save("pl3_definir1", definir1(True)); save("pl3_definir1_static", definir1(False))
    save("pl3_definir2", definir2(True)); save("pl3_definir2_static", definir2(False))
    save("pl3_definir3", definir3(True)); save("pl3_definir3_static", definir3(False))
    save("pl3_interseccion", interseccion(True)); save("pl3_interseccion_static", interseccion(False))
    save("pl3_vaguadas", vaguadas(True)); save("pl3_vaguadas_static", vaguadas(False))
    save("pl3_interp_tri", interp_triangulo())


# ----------------------------------------------------------------------
# Quiz: ¿vaguada o divisoria? (tintas + linea negra; con cotas se revela)
# ----------------------------------------------------------------------

def quiz(deck=True):
    svg = SVG("-10 -14 500 400", width_style="76%", deck=deck)
    svg.raw('<rect x="-10" y="-14" width="500" height="400" fill="#fdfbf7"/>')
    plan_contours(svg)
    # linea negra: la vaguada NE (sin decir cual es)
    sl = streamline(272, 184, direction=-1, step=2.5)
    pts = [(p[0], DOM_Y - p[1]) for p in sl]
    d = "M " + " L ".join(f"{r1(a)},{r1(b)}" for a, b in pts)
    svg.path(d, stroke="#111", w=3.6)
    svg.text(240, 372, "¿La línea negra es vaguada o divisoria?", size=14, fill="#111", weight="700", anchor="middle", halo=True)
    # frag: aparecen las cotas y la respuesta
    svg.frag(1 if deck else None)
    label_on_contour(svg, 160, 0.2, dy=4, size=13)
    label_on_contour(svg, 140, 0.62, dy=4, size=13)
    label_on_contour(svg, 120, 0.34, dy=4, size=13)
    label_on_contour(svg, 100, 0.6, dy=4, poly_idx=1, size=13)
    label_on_contour(svg, 130, 0.5, dy=4, poly_idx=1, size=13)
    label_on_contour(svg, 110, 0.55, dy=4, poly_idx=1, size=13)
    label_on_contour(svg, 110, 0.3, dy=4, size=13)
    svg.text(468, 196, "con las cotas: el terreno baja hacia el NE", size=13, fill="#1d6fd0", weight="700", anchor="end", halo=True)
    svg.text(468, 214, "y las curvas apuntan aguas arriba: VAGUADA", size=13, fill="#1d6fd0", weight="700", anchor="end", halo=True)
    svg.end_frag()
    return svg.render()


if __name__ == "__main__":
    save("pl3_quiz", quiz(True))
    save("pl3_quiz_static", quiz(False))
