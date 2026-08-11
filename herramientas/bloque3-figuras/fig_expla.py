"""Figuras del Tema 5 (explanaciones: plataformas horizontales y en pendiente)."""

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


# ----------------------------------------------------------------------
# Plataforma horizontal en el collado del terreno conductor
# ----------------------------------------------------------------------

RX0, RX1 = 235.0, 315.0
RY0, RY1 = 140.0, 215.0
Z0 = 108.0
PD = 1.0        # pendiente talud desmonte (1:1)
PT = 2.0 / 3.0  # pendiente talud terraplen (2:3)


def boundary_samples(n_edge=46, n_corner=13):
    """(punto, normal exterior) recorriendo el borde con esquinas en abanico."""
    out = []
    corners = [((RX1, RY1), (1, 0), (0, 1)),
               ((RX0, RY1), (0, 1), (-1, 0)),
               ((RX0, RY0), (-1, 0), (0, -1)),
               ((RX1, RY0), (0, -1), (1, 0))]
    edges = [(((RX1, RY0), (RX1, RY1)), (1, 0)),
             (((RX1, RY1), (RX0, RY1)), (0, 1)),
             (((RX0, RY1), (RX0, RY0)), (-1, 0)),
             (((RX0, RY0), (RX1, RY0)), (0, -1))]
    for (P0, P1), nrm in edges:
        for t in np.linspace(0, 1, n_edge):
            p = (P0[0] + (P1[0] - P0[0]) * t, P0[1] + (P1[1] - P0[1]) * t)
            out.append((p, nrm))
        # esquina al final del borde
        (c, n1, n2) = [x for x in corners if x[0] == P1][0]
        a1 = math.atan2(n1[1], n1[0])
        a2 = math.atan2(n2[1], n2[0])
        while a2 < a1:
            a2 += 2 * math.pi
        for a in np.linspace(a1, a2, n_corner)[1:-1]:
            out.append((c, (math.cos(a), math.sin(a))))
    return out


def d_encuentro(p, nrm):
    """Distancia horizontal hasta el encuentro talud-terreno; signo del lado."""
    zp = float(z(p[0], p[1]))
    lado = 1 if zp > Z0 else -1   # 1 = desmonte, -1 = terraplen
    pend = PD if lado == 1 else PT
    prev_d, prev_f = 0.0, 0.0 - (zp - Z0) * lado  # f(d) = talud - terreno (con signo)
    for d in np.arange(0.5, 140.0, 0.5):
        q = (p[0] + nrm[0] * d, p[1] + nrm[1] * d)
        if not (-40 <= q[0] <= 520 and -40 <= q[1] <= 400):
            break
        zq = float(z(q[0], q[1]))
        f = (Z0 + lado * pend * d - zq) * lado   # >0 cuando el talud supera al terreno
        if f >= 0:
            # interpola
            if f == prev_f:
                return d, lado
            dd = prev_d + (0 - prev_f) * (d - prev_d) / (f - prev_f)
            return dd, lado
        prev_d, prev_f = d, f
    return None, lado


SAMPLES = boundary_samples()
ENC = []
for p, nrm in SAMPLES:
    d, lado = d_encuentro(p, nrm)
    ENC.append((p, nrm, d, lado))


def sv(p):
    return (p[0], DOM_Y - p[1])


def planta_horizontal(deck=True):
    svg = SVG("150 70 290 240", width_style="94%", deck=deck)
    svg.raw('<rect x="150" y="70" width="290" height="240" fill="#fdfbf7"/>')
    plan_contours(svg, w_master=1.8, w_normal=0.9)
    # rotulos de curva dentro de la ventana de zoom
    usados = set()
    for lev in (100, 110, 120, 130):
        for pi, poly in enumerate(CONTORNOS.get(lev, [])):
            for frac in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9):
                i = int(frac * (len(poly) - 1))
                x, y = poly[i][0], DOM_Y - poly[i][1]
                if not (170 <= x <= 420 and 90 <= y <= 290):
                    continue
                if RX0 - 26 <= x <= RX1 + 26 and DOM_Y - RY1 - 26 <= y <= DOM_Y - RY0 + 26:
                    continue
                if any(abs(x - a) < 40 and abs(y - b) < 24 for a, b in usados):
                    continue
                usados.add((x, y))
                svg.text(x, y + 4, str(lev), size=11, fill=SIENA, weight="700", anchor="middle", halo=True)
                break
            else:
                continue
            break

    # frag 1: plataforma y linea de paso
    svg.frag(1 if deck else None)
    svg.poly([sv((RX0, RY0)), sv((RX1, RY0)), sv((RX1, RY1)), sv((RX0, RY1))],
             stroke="#1a1a1a", w=2.6, fill="#d9d9d9", fill_opacity=0.75, closed=True)
    cxp, cyp = sv(((RX0 + RX1) / 2, (RY0 + RY1) / 2))
    svg.text(cxp, cyp - 4, "plataforma", size=12, weight="700", anchor="middle")
    svg.text(cxp, cyp + 12, "(cota 108)", size=12, weight="700", anchor="middle")
    paso = [p for (p, nrm, d, lado) in ENC if d is not None and d < 1.2]
    for p in paso:
        svg.circle(*sv(p), r=3.2, fill="#2d6fd0", stroke="#123a70", w=1.4)
    svg.text(sv((RX0 + 30, RY0))[0], sv((RX0 + 30, RY0))[1] + 20, "línea de paso", size=11.5, fill="#2d6fd0", weight="700", halo=True)
    svg.end_frag()

    # frag 2 y 3: horizontales de los taludes
    for lado_obj, frag, col, pend, iv in [(1, 2, "#d06060", PD, 10.0 / PD), (-1, 3, "#3f9e3f", PT, 10.0 / PT)]:
        svg.frag(frag if deck else None)
        for kc in (1, 2, 3, 4, 5):
            c = Z0 + lado_obj * 5.0 * kc
            dc = abs(c - Z0) / pend
            pts = []
            for (p, nrm, d, lado) in ENC:
                if lado == lado_obj and d is not None and dc <= d:
                    pts.append(sv((p[0] + nrm[0] * dc, p[1] + nrm[1] * dc)))
                else:
                    if len(pts) > 1:
                        svg.poly(pts, stroke=col, w=1.1)
                    pts = []
            if len(pts) > 1:
                svg.poly(pts, stroke=col, w=1.1)
        svg.end_frag()

    # frag 4: lineas de encuentro con el terreno
    svg.frag(4 if deck else None)
    for lado_obj, col, w in [(1, ROJO, 2.6), (-1, "#1a7a1a", 2.6)]:
        pts = []
        for (p, nrm, d, lado) in ENC:
            if lado == lado_obj and d is not None and d > 1.2:
                pts.append(sv((p[0] + nrm[0] * d, p[1] + nrm[1] * d)))
            else:
                if len(pts) > 1:
                    svg.poly(pts, stroke=col, w=w)
                pts = []
        if len(pts) > 1:
            svg.poly(pts, stroke=col, w=w)
    svg.text(213, 128, "encuentro del", size=12, fill=ROJO, weight="700", halo=True, anchor="middle")
    svg.text(213, 143, "desmonte (1:1)", size=12, fill=ROJO, weight="700", halo=True, anchor="middle")
    svg.text(370, 253, "encuentro del", size=12, fill="#1a7a1a", weight="700", halo=True, anchor="middle")
    svg.text(370, 268, "terraplén (2:3)", size=12, fill="#1a7a1a", weight="700", halo=True, anchor="middle")
    svg.end_frag()
    svg.text(158, 304, "Plataforma a cota 108 · líneas de talud cada 5 m", size=11, fill="#555")
    return svg.render()


# ----------------------------------------------------------------------
# Seccion tipo: desmonte, plataforma, terraplen
# ----------------------------------------------------------------------

def seccion(deck=True):
    svg = SVG("0 0 640 300", width_style="92%", deck=deck)

    def terr(x):
        return 100.0 + 145.0 / (1.0 + math.exp(-(x - 320.0) / 80.0))

    xs = np.linspace(0, 640, 240)
    pts = [(float(x), terr(float(x))) for x in xs]
    simp = rdp(np.array(pts), 0.4)
    d = "M " + " L ".join(f"{r1(p[0])},{r1(p[1])}" for p in simp)
    px0, px1, py = 240.0, 420.0, 180.0
    # talud desmonte 1:1 hacia la izquierda (sube)
    xd = px0
    while xd > 0 and py - (px0 - xd) > terr(xd):
        xd -= 0.5
    yd = py - (px0 - xd)
    # talud terraplen 2:3 hacia la derecha (baja)
    xt = px1
    while xt < 640 and py + (xt - px1) * (2.0 / 3.0) < terr(xt):
        xt += 0.5
    yt = py + (xt - px1) * (2.0 / 3.0)
    svg.frag(2 if deck else None)
    svg.poly([(xd, yd), (px0, py), (px0, terr(px0))], stroke="none", fill="#e07a7a", fill_opacity=0.5, closed=True)
    svg.line(xd, yd, px0, py, stroke=ROJO, w=2.6)
    svg.text(xd - 6, yd - 12, "talud de desmonte (1:1)", size=12.5, fill=ROJO, weight="700")
    svg.end_frag()
    svg.frag(3 if deck else None)
    svg.poly([(px1, py), (xt, yt), (px1, terr(px1))], stroke="none", fill="#7ac07a", fill_opacity=0.5, closed=True)
    svg.line(px1, py, xt, yt, stroke="#1a7a1a", w=2.6)
    svg.text(px1 + 30, yt + 20, "talud de terraplén (2:3)", size=12.5, fill="#1a7a1a", weight="700")
    svg.end_frag()
    svg.path(d, stroke=SIENA, w=2.8)
    svg.text(30, 92, "terreno", size=13, fill=SIENA, weight="700")
    svg.frag(1 if deck else None)
    svg.line(px0, py, px1, py, stroke="#1a1a1a", w=3.4)
    svg.text((px0 + px1) / 2, py - 10, "plataforma", size=13, weight="700", anchor="middle")
    svg.end_frag()
    svg.frag(4 if deck else None)
    svg.text(320, 282, "desmonte: quito tierra · terraplén: aporto tierra · el perfil ayuda a verlo", size=12, fill="#555", anchor="middle")
    svg.end_frag()
    return svg.render()


# ----------------------------------------------------------------------
# Plataforma en pendiente: metodo de los conos (esquema)
# ----------------------------------------------------------------------

def conos_esquema(deck=True):
    svg = SVG("0 0 640 380", width_style="88%", deck=deck)
    # borde de la plataforma con pendiente: recta graduada con puntos 10, 10.5, 11
    A = (120, 300); B = (520, 120)
    ux, uy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    px, py = -uy, ux   # normal (hacia abajo-derecha del borde)
    svg.line(A[0] - ux * 30, A[1] - uy * 30, B[0] + ux * 30, B[1] + uy * 30, stroke="#1a1a1a", w=3)
    ptos = []
    for k, cota in [(0, 10), (1, 10.5), (2, 11)]:
        t = 0.15 + k * 0.35
        p = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t)
        ptos.append((p, cota))
        svg.circle(*p, r=3.6)
        svg.text(p[0] + 8, p[1] + 18, f"({cota:g})", size=12.5, weight="700", fill="#2d2d8a")
    svg.text(A[0] - 24, A[1] + 26, "borde de la plataforma (graduado)", size=12, fill="#444", style="italic")

    # frag 1: cono en el punto intermedio: circunferencia de radio i
    R = 62.0
    svg.frag(1 if deck else None)
    pc = ptos[1][0]
    svg.circle(pc[0], pc[1], r=R, fill="none", stroke=NARANJA2, w=2)
    svg.line(pc[0], pc[1], pc[0] + R * 0.7071, pc[1] + R * 0.7071, stroke=NARANJA2, w=1.4, dash="5,3")
    svg.text(pc[0] + R * 0.75, pc[1] + R * 0.75 + 18, "radio = intervalo del talud", size=11.5, fill=NARANJA2, weight="700")
    svg.text(pc[0] - R - 10, pc[1] - R * 0.6, "cono de talud", size=11.5, fill=NARANJA2, weight="700", anchor="end")
    svg.text(pc[0] - R - 10, pc[1] - R * 0.6 + 15, "con vértice en (10,5)", size=11.5, fill=NARANJA2, weight="700", anchor="end")
    svg.end_frag()

    # frag 2: linea de nivel del talud = tangente desde el punto anterior
    svg.frag(2 if deck else None)
    p0 = ptos[0][0]
    # tangente desde p0 a la circunferencia (pc, R), lado exterior (down-slope)
    dx, dy = pc[0] - p0[0], pc[1] - p0[1]
    dist = math.hypot(dx, dy)
    alpha = math.asin(R / dist)
    base = math.atan2(dy, dx)
    for sgn, w, col in [(1, 2.6, "#3f9e3f")]:
        ang = base + sgn * alpha
        tl = dist * math.cos(alpha)
        q = (p0[0] + math.cos(ang) * (tl + 130), p0[1] + math.sin(ang) * (tl + 130))
        svg.line(p0[0], p0[1], q[0], q[1], stroke=col, w=w)
    svg.text(p0[0] + 150, p0[1] + 44, "línea de nivel 10 del talud:", size=12, fill="#3f9e3f", weight="700")
    svg.text(p0[0] + 150, p0[1] + 60, "tangente a la base del cono", size=12, fill="#3f9e3f", weight="700")
    svg.end_frag()

    # frag 3: las demas horizontales del talud, paralelas
    svg.frag(3 if deck else None)
    ang = math.atan2(pc[1] - p0[1], pc[0] - p0[0]) + math.asin(R / math.hypot(pc[0] - p0[0], pc[1] - p0[1]))
    tx, ty = math.cos(ang), math.sin(ang)
    for k, cota in [(1, 10.5), (2, 11)]:
        p = ptos[k][0]
        svg.line(p[0] - tx * 40, p[1] - ty * 40, p[0] + tx * 230, p[1] + ty * 230, stroke="#3f9e3f", w=1.6, dash="7,4" if k == 2 else None)
        svg.text(p[0] + tx * 236, p[1] + ty * 236 + 4, f"{cota:g}", size=11.5, fill="#3f9e3f", weight="700")
    svg.text(30, 360, "El talud del borde en pendiente es la superficie tangente a los conos: sus líneas", size=11.5, fill="#555")
    svg.text(30, 375, "de nivel son las tangentes comunes a las circunferencias de igual cota", size=11.5, fill="#555")
    svg.end_frag()
    return svg.render()


if __name__ == "__main__":
    print("z esquinas:", [round(float(z(x, y)), 1) for x, y in [(RX0, RY0), (RX1, RY0), (RX0, RY1), (RX1, RY1)]])
    save("exp_planta", planta_horizontal(True)); save("exp_planta_static", planta_horizontal(False))
    save("exp_seccion", seccion(True)); save("exp_seccion_static", seccion(False))
    save("exp_conos", conos_esquema(True)); save("exp_conos_static", conos_esquema(False))
