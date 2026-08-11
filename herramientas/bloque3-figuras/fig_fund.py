"""Figuras del Tema 2 (fundamentos: punto, recta, plano; graduacion)."""

import os
import math
from svgkit import (SVG, SIENA, TOSTADO, VERDE, ROJO, GRIS, NARANJA2, TEAL,
                    AZUL, AZUL_BORDE, marker_defs, plan_contours,
                    label_on_contour, r1, CONTORNOS, DOM_Y)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "svg")


def save(name, markup):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(markup)
    print("ok", name)


# Proyeccion oblicua para escenas pequenas: terreno (x,y) con y en profundidad
def ob(x, y, z=0.0, v0=250.0, kz=9.0):
    return x + 0.42 * y, v0 - 0.30 * y - kz * z


def parallelogram(svg, x0, x1, y0, y1, v0, fill=TOSTADO, opacity=0.9, stroke="#1a1a1a", w=1.6):
    pts = [ob(x0, y0, 0, v0), ob(x1, y0, 0, v0), ob(x1, y1, 0, v0), ob(x0, y1, 0, v0)]
    svg.poly(pts, stroke=stroke, w=w, fill=fill, fill_opacity=opacity, closed=True)
    return pts


# ----------------------------------------------------------------------
# El punto: cotas positivas, negativas, nulas; desnivel
# ----------------------------------------------------------------------

def punto(deck=True):
    svg = SVG("0 0 640 300", width_style="96%", deck=deck)
    V0 = 262
    parallelogram(svg, 20, 380, 20, 200, V0)
    svg.text(*[c + o for c, o in zip(ob(30, 32, 0, V0), (4, -4))], "PC (cota 0)", size=11.5,
             fill="#6a5335", style="italic")

    def vert(xg, yg, cota, nombre, frag=None, kz=9.0, lab_dx=6, lab_dy=15):
        u0, v0p = ob(xg, yg, 0, V0)
        u1, v1p = ob(xg, yg, cota, V0, kz)
        svg.frag(frag if deck else None)
        if cota > 0:
            svg.line(u0, v0p, u1, v1p, stroke=GRIS, w=1.3, dash="4,3")
        elif cota < 0:
            svg.line(u0, v0p, u1, v1p, stroke=GRIS, w=1.3, dash="4,3")
        svg.circle(u1, v1p, r=3.6)
        svg.text(u1 + 7, v1p - 5, nombre, size=14, weight="700")
        svg.circle(u0, v0p, r=3.2, fill="#e8a33d", stroke="#7a5510", w=1.4)
        svg.text(u0 + lab_dx, v0p + lab_dy, f"{nombre.lower()}({cota:g})", size=12.5, weight="700", fill="#2d2d8a")
        svg.end_frag()
        return (u0, v0p), (u1, v1p)

    # A(4) y C(5): por encima del plano
    (_, _), (ua, va) = vert(150, 120, 4, "A", frag=1)
    (_, _), (uc, vc) = vert(255, 150, 5, "C", frag=1)
    # D(0): en el plano
    svg.frag(2 if deck else None)
    u0, v0p = ob(90, 165, 0, V0)
    svg.circle(u0, v0p, r=3.6)
    svg.text(u0 + 6, v0p + 15, "d(0)", size=12.5, weight="700", fill="#2d2d8a")
    svg.text(u0 - 4, v0p - 10, "D", size=14, weight="700")
    svg.end_frag()
    # B(-2): por debajo
    vert(352, 68, -2, "B", frag=3, lab_dx=8, lab_dy=-9)
    # desnivel C-A
    svg.frag(4 if deck else None)
    svg.line(ua, va, uc, vc - (vc - va), stroke=ROJO, w=1.2, dash="5,3")
    svg.line(uc, vc, uc, vc - (vc - va) if False else va, stroke=ROJO, w=2.2)
    svg.text(uc + 8, (va + vc) / 2 + 4, "desnivel = 5 − 4 = 1 m", size=12.5, fill=ROJO, weight="700")
    svg.end_frag()

    # panel derecho: lo que queda en el papel
    svg.frag(5 if deck else None)
    svg.raw('<rect x="480" y="30" width="150" height="220" fill="#ffffff" stroke="#b8a37e" stroke-width="2"/>')
    svg.text(555, 50, "El papel", size=12, fill="#6a5335", style="italic", anchor="middle")
    for nombre, cota, xg, yg in [("a", 4, 150, 120), ("c", 5, 255, 150), ("d", 0, 90, 165), ("b", -2, 352, 68)]:
        px = 480 + (xg - 20.0) / 360.0 * 150.0
        py = 250 - (yg - 20.0) / 180.0 * 220.0
        svg.circle(px, py, r=3.2, fill="#e8a33d", stroke="#7a5510", w=1.4)
        if nombre == "b":
            svg.text(px - 6, py + 13, f"{nombre}({cota:g})", size=12, weight="700", fill="#2d2d8a", anchor="end")
        else:
            svg.text(px + 5, py + 13, f"{nombre}({cota:g})", size=12, weight="700", fill="#2d2d8a")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# La recta: proyeccion, traza y pendiente
# ----------------------------------------------------------------------

def recta(deck=True):
    svg = SVG("0 0 640 320", width_style="96%", deck=deck)
    svg.raw(marker_defs("fr"))
    V0 = 285
    KZ = 26.0
    parallelogram(svg, 20, 420, 20, 200, V0)
    # T en el plano, A elevado cota 3
    T = (80, 55); A = (330, 160)
    ut, vt = ob(*T, 0, V0)
    ua0, va0 = ob(*A, 0, V0)
    ua, va = ob(*A, 3, V0, KZ)
    # recta espacio R y proyeccion r
    svg.frag(1 if deck else None)
    svg.circle(ua, va, r=3.6)
    svg.text(ua + 8, va - 4, "A", size=14, weight="700")
    svg.line(ua0, va0, ua, va, stroke=GRIS, w=1.3, dash="4,3")
    svg.circle(ua0, va0, r=3.2, fill="#e8a33d", stroke="#7a5510", w=1.4)
    svg.text(ua0 + 7, va0 + 14, "a(3)", size=12.5, weight="700", fill="#2d2d8a")
    svg.end_frag()
    svg.frag(2 if deck else None)
    svg.line(ut, vt, ua, va, stroke="#1a1a1a", w=2.6)
    svg.text((ut + ua) / 2 - 14, (vt + va) / 2 - 10, "R", size=14, weight="700", style="italic")
    svg.line(ut, vt, ua0, va0, stroke=VERDE, w=2.6)
    svg.text((ut + ua0) / 2, (vt + va0) / 2 + 16, "r", size=14, weight="700", fill=VERDE, style="italic")
    svg.end_frag()
    # traza
    svg.frag(3 if deck else None)
    svg.circle(ut, vt, r=3.6)
    svg.text(ut - 6, vt + 18, "t(0)", size=12.5, weight="700", fill="#2d2d8a")
    svg.text(ut - 10, vt - 10, "T", size=14, weight="700")
    svg.end_frag()
    # pendiente: dV y dH
    svg.frag(4 if deck else None)
    svg.line(ua0, va0, ua, va, stroke=ROJO, w=2.4)
    svg.text(ua0 + 10, (va0 + va) / 2 + 4, "dV = 3 m", size=12.5, fill=ROJO, weight="700")
    svg.text((ut + ua0) / 2 - 40, (vt + va0) / 2 + 26, "dH = 300 m", size=12.5, fill=VERDE, weight="700")
    # arco del angulo alfa en t sobre el plano
    ang1 = math.atan2(va - vt, ua - ut)
    ang0 = math.atan2(va0 - vt, ua0 - ut)
    rr = 52
    x0_, y0_ = ut + rr * math.cos(ang0), vt + rr * math.sin(ang0)
    x1_, y1_ = ut + rr * math.cos(ang1), vt + rr * math.sin(ang1)
    svg.raw(f'<path d="M {r1(x0_)},{r1(y0_)} A {rr} {rr} 0 0 0 {r1(x1_)},{r1(y1_)}" fill="none" stroke="{NARANJA2}" stroke-width="2"/>')
    svg.text(ut + 62, vt - 6, "α", size=14, fill=NARANJA2, weight="700")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Posiciones particulares de la recta
# ----------------------------------------------------------------------

def posiciones(deck=True):
    svg = SVG("0 0 660 240", width_style="98%", deck=deck)
    for k, (titulo, sub) in enumerate([("OBLICUA", "posición general"),
                                       ("HORIZONTAL", "pendiente = 0 · proyección en V.M."),
                                       ("VERTICAL", "pendiente = ∞ · proyección: un punto")]):
        x0 = 10 + k * 220
        svg.frag(k + 1 if deck else None)
        pts = [(x0 + 8, 190), (x0 + 68, 130), (x0 + 208, 130), (x0 + 148, 190)]
        svg.poly(pts, stroke="#1a1a1a", w=1.4, fill=TOSTADO, fill_opacity=0.85, closed=True)
        cx = x0 + 108
        if k == 0:
            svg.line(cx - 55, 175, cx + 62, 52, stroke="#1a1a1a", w=2.4)
            svg.line(cx - 55, 175, cx + 62, 145, stroke=VERDE, w=2.4)
            svg.line(cx + 62, 52, cx + 62, 145, stroke=GRIS, w=1.2, dash="4,3")
            svg.circle(cx - 55, 175, r=3.2)
            svg.text(cx - 68, 172, "t", size=12, weight="700", style="italic")
        elif k == 1:
            svg.line(cx - 62, 92, cx + 58, 74, stroke="#1a1a1a", w=2.4)
            svg.line(cx - 47, 172, cx + 73, 154, stroke=VERDE, w=2.4)
            svg.line(cx - 62, 92, cx - 47, 172, stroke=GRIS, w=1.1, dash="4,3")
            svg.line(cx + 58, 74, cx + 73, 154, stroke=GRIS, w=1.1, dash="4,3")
            svg.text(cx - 12, 66, "A", size=11.5, weight="700")
            svg.text(cx + 66, 62, "B", size=11.5, weight="700")
            svg.text(cx - 6, 186, "a(3)  b(3)", size=11, weight="700", fill="#2d2d8a")
        else:
            svg.line(cx, 40, cx, 158, stroke="#1a1a1a", w=2.4)
            svg.circle(cx, 158, r=3.4, fill="#e8a33d", stroke="#7a5510", w=1.4)
            svg.text(cx + 7, 172, "r = un punto", size=11, weight="700", fill="#2d2d8a")
        svg.text(x0 + 108, 216, titulo, size=13, weight="700", fill="#2d2d8a", anchor="middle")
        svg.text(x0 + 108, 232, sub, size=10.5, fill="#666", anchor="middle")
        svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# El plano: rectas singulares (vista oblicua)
# ----------------------------------------------------------------------

def plano(deck=True):
    svg = SVG("0 168 660 178", width_style="100%", deck=deck)
    svg.raw(marker_defs("fp"))
    V0 = 330
    KZ = 9.0
    ESC = 6.0        # px por metro sobre el terreno
    PEND = 0.30      # pendiente del plano P
    E = 2.0          # equidistancia (m)
    y_traza = 30.0
    dy = E / PEND * ESC   # 40 px de recesion por curva
    x0, x1 = 130, 480

    # plano de proyeccion
    parallelogram(svg, 15, 560, 5, 230, V0, opacity=0.55)

    # ---- frag 1: plano P y su traza
    svg.frag(1 if deck else None)
    c0 = ob(x0, y_traza, 0, V0, KZ)
    c1 = ob(x1, y_traza, 0, V0, KZ)
    c2 = ob(x1, y_traza + 4 * dy / ESC * ESC, 8, V0, KZ)
    c3 = ob(x0, y_traza + 4 * dy, 8, V0, KZ)
    # ojo: y en unidades "terreno px": la horizontal de cota c esta en y = y_traza + (c/PEND)*ESC
    c2 = ob(x1, y_traza + 4 * dy, 8, V0, KZ)
    svg.poly([c0, c1, c2, c3], stroke=AZUL_BORDE, w=1.8, fill=AZUL, fill_opacity=0.22, closed=True)
    svg.text(c2[0] - 26, c2[1] + 16, "P", size=16, weight="700", fill=AZUL_BORDE)
    svg.line(*c0, *c1, stroke="#1a1a1a", w=3.4)
    svg.text((c0[0] + c1[0]) / 2 + 40, (c0[1] + c1[1]) / 2 + 18, "traza de P (cota 0)", size=12.5, weight="700")
    svg.end_frag()

    # ---- frag 2: horizontales (lineas de nivel) del plano
    svg.frag(2 if deck else None)
    for c in (2, 4, 6, 8):
        yg = y_traza + (c / PEND) * ESC / 1.0
        p0 = ob(x0, yg, c, V0, KZ)
        p1 = ob(x1, yg, c, V0, KZ)
        svg.line(*p0, *p1, stroke="#2e9e40", w=3)
        svg.text(p1[0] + 8, p1[1] + 4, str(c), size=12.5, weight="700", fill="#d00000")
        if c == 2:
            svg.text(c1[0] + 8, c1[1] + 4, "0", size=12.5, weight="700", fill="#d00000")
        # proyeccion en el plano de comparacion
        q0 = ob(x0, yg, 0, V0, KZ)
        q1 = ob(x1, yg, 0, V0, KZ)
        svg.line(*q0, *q1, stroke=GRIS, w=1.0, dash="5,4")
    p8 = ob(x0, y_traza + 4 * dy, 8, V0, KZ)
    svg.text(p8[0] - 4, p8[1] - 10, "líneas de nivel del plano", size=12, fill="#2e9e40", weight="700")
    svg.end_frag()

    # ---- frag 3: linea de maxima pendiente
    svg.frag(3 if deck else None)
    xm = 300
    m0 = ob(xm, y_traza, 0, V0, KZ)
    m1 = ob(xm, y_traza + 4 * dy, 8, V0, KZ)
    svg.line(*m0, *m1, stroke=ROJO, w=3)
    mm = ((m0[0] + m1[0]) / 2, (m0[1] + m1[1]) / 2)
    svg.text(mm[0] + 10, mm[1] + 2, "l.m.p.", size=12.5, fill=ROJO, weight="700", style="italic")
    # su proyeccion
    mp = ob(xm, y_traza + 4 * dy, 0, V0, KZ)
    svg.line(*m0, *mp, stroke=ROJO, w=1.4, dash="5,4")
    # angulo alfa
    svg.text(m0[0] + 12, m0[1] - 14, "α", size=14, fill=NARANJA2, weight="700")
    svg.end_frag()

    # ---- frag 4: equidistancia e intervalo en el borde izquierdo
    svg.frag(4 if deck else None)
    for c in (2, 4):
        yg = y_traza + (c / PEND) * ESC
        a0 = ob(x0, yg, c, V0, KZ)
        a1 = ob(x0, yg, c - 2, V0, KZ)
        svg.line(a0[0], a0[1], a1[0], a1[1], stroke=ROJO, w=2.6)
    e0 = ob(x0, y_traza + (2 / PEND) * ESC, 0, V0, KZ)
    svg.line(*c0, e0[0], e0[1], stroke=VERDE, w=2.6)
    svg.text(c0[0] - 8, c0[1] - 30, "equidistancia (dV)", size=12, fill=ROJO, weight="700", anchor="end")
    svg.text(c0[0] - 8, c0[1] - 14, "intervalo (dH)", size=12, fill=VERDE, weight="700", anchor="end")
    svg.raw(f'<line x1="{r1(c0[0] - 10)}" y1="{r1(c0[1] - 26)}" x2="{r1((ob(x0, y_traza + 6.67, 1, V0, KZ))[0])}" '
            f'y2="{r1((ob(x0, y_traza + 6.67, 1, V0, KZ))[1])}" stroke="{GRIS}" stroke-width="0"/>')
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# El plano en planta: representacion graduada
# ----------------------------------------------------------------------

def plano_planta(deck=True, pendiente=0.30, e=2.0, esc_px=9.0):
    svg = SVG("0 0 560 400", width_style="80%", deck=deck)
    i_m = e / pendiente          # 6.67 m
    step = i_m * esc_px          # px entre horizontales
    th = math.radians(-10)       # las horizontales bajan levemente a la derecha
    dx, dy = math.cos(th), -math.sin(th)
    nx, ny = -math.sin(th), math.cos(th)  # normal (hacia abajo)
    ox, oy = 120, 60
    L = 400

    def hline(k):
        px, py = ox + nx * step * k, oy + ny * step * k
        return (px, py), (px + dx * L, py + dy * L)

    svg.frag(1 if deck else None)
    (a, b) = hline(0)
    svg.line(*a, *b, stroke="#1a1a1a", w=3.2)
    svg.text(b[0] - 8, b[1] - 8, "traza (0)", size=12.5, weight="700")
    for k in range(1, 5):
        (a2, b2) = hline(k)
        svg.line(*a2, *b2, stroke="#2e9e40", w=2.4)
        svg.text(b2[0] + 4, b2[1] + 4, str(2 * k), size=12.5, weight="700", fill="#d00000")
    svg.end_frag()

    # LMP graduada, perpendicular a las horizontales
    svg.frag(2 if deck else None)
    t = 0.55
    sx, sy = ox + dx * L * t, oy + dy * L * t
    ex, ey = sx + nx * step * 4.45, sy + ny * step * 4.45
    svg.line(sx - nx * step * 0.35, sy - ny * step * 0.35, ex, ey, stroke=ROJO, w=3)
    svg.text(ex + 6, ey + 2, "l.m.p.", size=12.5, fill=ROJO, weight="700", style="italic")
    for k in range(0, 5):
        px, py = sx + nx * step * k, sy + ny * step * k
        svg.circle(px, py, r=3.4)
    svg.end_frag()

    # medir el intervalo
    svg.frag(3 if deck else None)
    k0, k1 = 2, 3
    p0 = (sx + nx * step * k0 + dx * 16, sy + ny * step * k0 + dy * 16)
    p1 = (sx + nx * step * k1 + dx * 16, sy + ny * step * k1 + dy * 16)
    svg.line(*p0, *p1, stroke=VERDE, w=3)
    svg.text((p0[0] + p1[0]) / 2 + 12, (p0[1] + p1[1]) / 2 + 2, "i = 6,67 m", size=13, fill=VERDE, weight="700")
    svg.end_frag()
    svg.text(40, 390, "Equidistancia = 2 m · Pendiente del plano = 30 % · Escala 1:500", size=12.5, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# Reglas de las curvas de nivel sobre el terreno conductor
# ----------------------------------------------------------------------

def reglas(deck=True):
    svg = SVG("-10 -14 500 390", width_style="80%", deck=deck)
    svg.raw('<rect x="-10" y="-14" width="500" height="390" fill="#fdfbf7"/>')
    plan_contours(svg)
    label_on_contour(svg, 160, 0.45, dy=4)
    label_on_contour(svg, 150, 0.55, dy=4)
    label_on_contour(svg, 110, 0.30, dy=4)
    label_on_contour(svg, 100, 0.6, dy=4, poly_idx=1)
    # cima
    svg.frag(1 if deck else None)
    svg.raw(f'<ellipse cx="122" cy="102" rx="52" ry="36" fill="none" stroke="{TEAL}" stroke-width="2.2" stroke-dasharray="6,4"/>')
    svg.text(250, 44, "cima: curvas cerradas, cota crece hacia dentro", size=13, fill=TEAL, weight="700", anchor="middle", halo=True)
    svg.end_frag()
    # collado: cotas repetidas
    svg.frag(2 if deck else None)
    for lev, fr, pi in [(100, 0.6, 1), (100, 0.35, 2)]:
        polys = CONTORNOS[lev]
        if pi >= len(polys):
            continue
        poly = polys[pi]
        p = poly[int(fr * (len(poly) - 1))]
        svg.raw(f'<ellipse cx="{r1(p[0])}" cy="{r1(DOM_Y - p[1])}" rx="16" ry="11" fill="none" stroke="{ROJO}" stroke-width="2.2"/>')
    label_on_contour(svg, 100, 0.35, dy=4, poly_idx=2)
    svg.text(300, 330, "collado: la misma cota aparece a ambos lados", size=13, fill=ROJO, weight="700", anchor="middle", halo=True)
    svg.end_frag()
    # nunca se cortan
    svg.frag(3 if deck else None)
    svg.text(245, 370, "y dos curvas de nivel nunca se cortan", size=13.5, fill="#2d2d8a", weight="700", anchor="middle")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Graduacion de rectas: casos 1, 2 y 3
# ----------------------------------------------------------------------

def _linea_base(svg, x0, y0, x1, y1, extra=0.12):
    """Recta soporte en blanco-hueso prolongada por ambos extremos."""
    vx, vy = x1 - x0, y1 - y0
    svg.line(x0 - vx * extra, y0 - vy * extra, x1 + vx * extra, y1 + vy * extra,
             stroke="#c9c9c9", w=4, cap="round")


def caso1(deck=True):
    # A(500) - B(540), e = 10 m: dividir en 4 partes iguales (Thales)
    svg = SVG("0 0 620 330", width_style="94%", deck=deck)
    svg.raw(marker_defs("g1", colors=(("gris", GRIS), ("verde", VERDE))))
    A = (90, 268); B = (530, 92)
    _linea_base(svg, *A, *B)
    svg.frag(1 if deck else None)
    for (px, py), lab in [(A, "a(500)"), (B, "b(540)")]:
        svg.circle(px, py, r=4)
        svg.text(px - 12, py + 22, lab, size=13.5, weight="700", fill="#2d2d8a")
    svg.end_frag()
    # construccion de Thales
    svg.frag(2 if deck else None)
    aux = (A[0] + 320, A[1] + 40)   # rayo auxiliar
    svg.line(*A, *aux, stroke=GRIS, w=1.3, marker="g1-flecha-gris")
    for k in range(1, 5):
        px, py = A[0] + (aux[0] - A[0]) * k / 4.5, A[1] + (aux[1] - A[1]) * k / 4.5
        svg.circle(px, py, r=2.4, fill=GRIS, stroke=GRIS)
        if k == 4:
            svg.line(px, py, *B, stroke=GRIS, w=1.3)
        # paralelas
    for k in range(1, 4):
        px, py = A[0] + (aux[0] - A[0]) * k / 4.5, A[1] + (aux[1] - A[1]) * k / 4.5
        qx, qy = A[0] + (B[0] - A[0]) * k / 4.0, A[1] + (B[1] - A[1]) * k / 4.0
        svg.line(px, py, qx, qy, stroke=GRIS, w=1.1, dash="4,3")
    svg.text(aux[0] + 10, aux[1] - 10, "divido en 4 partes iguales", size=12, fill="#777", style="italic")
    svg.end_frag()
    # puntos graduados
    svg.frag(3 if deck else None)
    for k, cota in [(1, 510), (2, 520), (3, 530)]:
        qx, qy = A[0] + (B[0] - A[0]) * k / 4.0, A[1] + (B[1] - A[1]) * k / 4.0
        svg.circle(qx, qy, r=3.6)
        svg.text(qx - 10, qy + 22, f"({cota})", size=12.5, weight="700", fill="#2d2d8a")
    svg.end_frag()
    # intervalo
    svg.frag(4 if deck else None)
    k0x, k0y = A[0] + (B[0] - A[0]) * 0.25, A[1] + (B[1] - A[1]) * 0.25
    k1x, k1y = A[0] + (B[0] - A[0]) * 0.5, A[1] + (B[1] - A[1]) * 0.5
    svg.raw(f'<line x1="{r1(k0x)}" y1="{r1(k0y - 14)}" x2="{r1(k1x)}" y2="{r1(k1y - 14)}" stroke="{VERDE}" '
            f'stroke-width="2.4" marker-start="url(#g1-flecha-verde)" marker-end="url(#g1-flecha-verde)"/>')
    svg.text((k0x + k1x) / 2 - 26, (k0y + k1y) / 2 - 34, "i = 35 m", size=13.5, fill=VERDE, weight="700")
    svg.end_frag()
    svg.text(16, 318, "Equidistancia = 10 m · Las cotas de a y b pertenecen a la serie", size=12.5, fill="#555")
    return svg.render()


def caso2(deck=True):
    # A(509) - B(516), e = 2 m: buscar la cota 510 con regla de tres
    svg = SVG("0 0 620 330", width_style="94%", deck=deck)
    svg.raw(marker_defs("g2", colors=(("verde", VERDE), ("naranja", NARANJA2))))
    A = (70, 262); B = (555, 78)
    _linea_base(svg, *A, *B)
    svg.frag(1 if deck else None)
    for (px, py), lab in [(A, "a(509)"), (B, "b(516)")]:
        svg.circle(px, py, r=4)
        svg.text(px - 12, py + 22, lab, size=13.5, weight="700", fill="#2d2d8a")
    svg.raw(f'<line x1="{r1(A[0]+10)}" y1="{r1(A[1]-18)}" x2="{r1(B[0]-16)}" y2="{r1(B[1]-20)}" stroke="{VERDE}" '
            f'stroke-width="2" marker-start="url(#g2-flecha-verde)" marker-end="url(#g2-flecha-verde)"/>')
    svg.text((A[0] + B[0]) / 2 - 40, (A[1] + B[1]) / 2 - 34, "dH = 2.212 m", size=13, fill=VERDE, weight="700")
    svg.end_frag()
    # x hasta la cota 510
    svg.frag(2 if deck else None)
    t = 1.0 / 7.0
    P = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t)
    svg.line(*A, *P, stroke=NARANJA2, w=3.4, cap="round")
    svg.circle(*P, r=3.6)
    svg.text(P[0] - 12, P[1] + 22, "(510)", size=12.5, weight="700", fill="#2d2d8a")
    svg.text(P[0] - 46, P[1] - 12, "¿x?", size=13.5, fill=NARANJA2, weight="700")
    svg.end_frag()
    # ya estamos en el caso 1: graduar desde 510
    svg.frag(3 if deck else None)
    for k, cota in [(1, 512), (2, 514)]:
        q = (P[0] + (B[0] - P[0]) * k / 3.0, P[1] + (B[1] - P[1]) * k / 3.0)
        svg.circle(*q, r=3.6)
        svg.text(q[0] - 10, q[1] + 22, f"({cota})", size=12.5, weight="700", fill="#2d2d8a")
    svg.text(B[0] - 130, B[1] + 46, "…y sigo como en el caso 1", size=12, fill="#777", style="italic")
    svg.end_frag()
    svg.text(16, 318, "Equidistancia = 2 m · La cota de a no pertenece a la serie", size=12.5, fill="#555")
    return svg.render()


def caso3(deck=True):
    # A(610), pendiente 35%, e = 2 m: intervalo i = 5,71 m
    svg = SVG("0 0 620 330", width_style="94%", deck=deck)
    svg.raw(marker_defs("g3", colors=(("verde", VERDE), ("naranja", NARANJA2))))
    A = (85, 262); B = (555, 80)
    _linea_base(svg, *A, *B)
    svg.frag(1 if deck else None)
    svg.circle(*A, r=4)
    svg.text(A[0] - 12, A[1] + 22, "a(610)", size=13.5, weight="700", fill="#2d2d8a")
    ux, uy = (B[0] - A[0]), (B[1] - A[1])
    nx, ny = ux / math.hypot(ux, uy), uy / math.hypot(ux, uy)
    svg.raw(f'<line x1="{r1(A[0]+nx*40)}" y1="{r1(A[1]+ny*40-30)}" x2="{r1(A[0]+nx*130)}" y2="{r1(A[1]+ny*130-30)}" '
            f'stroke="{NARANJA2}" stroke-width="2.6" marker-end="url(#g3-flecha-naranja)"/>')
    svg.text(40, 172, "pendiente 35 % (ascendente)", size=12.5, fill=NARANJA2, weight="700")
    svg.end_frag()
    # el intervalo calculado se lleva sucesivamente
    svg.frag(2 if deck else None)
    step = 150.0
    for k, cota in [(1, 612), (2, 614), (3, 616)]:
        q = (A[0] + nx * step * k, A[1] + ny * step * k)
        svg.circle(*q, r=3.6)
        svg.text(q[0] - 10, q[1] + 22, f"({cota})", size=12.5, weight="700", fill="#2d2d8a")
    q0 = (A[0] + nx * step, A[1] + ny * step)
    q1 = (A[0] + nx * step * 2, A[1] + ny * step * 2)
    svg.raw(f'<line x1="{r1(q0[0])}" y1="{r1(q0[1] - 14)}" x2="{r1(q1[0])}" y2="{r1(q1[1] - 14)}" stroke="{VERDE}" '
            f'stroke-width="2.4" marker-start="url(#g3-flecha-verde)" marker-end="url(#g3-flecha-verde)"/>')
    svg.text((q0[0] + q1[0]) / 2 - 24, (q0[1] + q1[1]) / 2 - 34, "i = 5,71 m", size=13.5, fill=VERDE, weight="700")
    svg.end_frag()
    svg.text(16, 318, "Equidistancia = 2 m · Conozco un punto y la pendiente", size=12.5, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# Ejemplo de pendiente para el capitulo de fundamentos
# ----------------------------------------------------------------------

def pendiente_ej(deck=False):
    svg = SVG("0 0 560 190", width_style="80%", deck=deck)
    svg.raw(marker_defs("pe", colors=(("verde", VERDE),)))
    A = (60, 150); B = (500, 62)
    _linea_base(svg, *A, *B)
    for k, cota in [(0, 500), (1, 502), (2, 504), (3, 506)]:
        q = (A[0] + (B[0] - A[0]) * k / 3.0, A[1] + (B[1] - A[1]) * k / 3.0)
        svg.circle(*q, r=3.6)
        svg.text(q[0] - 12, q[1] + 20, f"({cota})", size=12.5, weight="700", fill="#2d2d8a")
    q0 = (A[0] + (B[0] - A[0]) / 3.0, A[1] + (B[1] - A[1]) / 3.0)
    q1 = (A[0] + (B[0] - A[0]) * 2 / 3.0, A[1] + (B[1] - A[1]) * 2 / 3.0)
    svg.raw(f'<line x1="{r1(q0[0])}" y1="{r1(q0[1] - 13)}" x2="{r1(q1[0])}" y2="{r1(q1[1] - 13)}" stroke="{VERDE}" '
            f'stroke-width="2.4" marker-start="url(#pe-flecha-verde)" marker-end="url(#pe-flecha-verde)"/>')
    svg.text((q0[0] + q1[0]) / 2 - 20, (q0[1] + q1[1]) / 2 - 32, "i = 6 m", size=13, fill=VERDE, weight="700")
    svg.text(16, 182, "Equidistancia = 2 m: pendiente = 2/6 = 33,3 %", size=12.5, fill="#555")
    return svg.render()


if __name__ == "__main__":
    save("fund_punto", punto(True)); save("fund_punto_static", punto(False))
    save("fund_recta", recta(True)); save("fund_recta_static", recta(False))
    save("fund_posiciones", posiciones(True)); save("fund_posiciones_static", posiciones(False))
    save("fund_plano", plano(True)); save("fund_plano_static", plano(False))
    save("fund_plano_planta", plano_planta(True)); save("fund_plano_planta_static", plano_planta(False))
    save("fund_reglas", reglas(True)); save("fund_reglas_static", reglas(False))
    save("grad_caso1", caso1(True)); save("grad_caso1_static", caso1(False))
    save("grad_caso2", caso2(True)); save("grad_caso2_static", caso2(False))
    save("grad_caso3", caso3(True)); save("grad_caso3_static", caso3(False))
    save("fund_pendiente_ej", pendiente_ej())
