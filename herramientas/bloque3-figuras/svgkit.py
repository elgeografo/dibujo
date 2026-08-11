"""Utilidades comunes para generar los SVG del Bloque 3."""

import json
import os
import numpy as np
from terreno import z, grad_z, to_svg_path, rdp

HERE = os.path.dirname(os.path.abspath(__file__))

# Paleta del libro
AZUL = "#6f9fd8"; AZUL_BORDE = "#24537a"; TOSTADO = "#d2b077"
VERDE = "#14532d"; ROJO = "#d00000"; NARANJA = "#d97706"; NARANJA2 = "#e8862c"
TEAL = "#0f766e"; GRIS = "#909090"; SIENA = "#8a5a2a"
AZULCAJA = "#2d2d8a"; VERDECAJA = "#1a6e1a"

with open(os.path.join(HERE, "contornos.json")) as f:
    CONTORNOS = {int(k): v for k, v in json.load(f).items()}

DOM_X, DOM_Y = 480.0, 360.0


class SVG:
    """Acumulador simple de markup SVG con soporte de fragmentos Reveal."""

    def __init__(self, viewbox, width_style="100%", deck=True, extra_style=""):
        self.parts = []
        self.viewbox = viewbox
        self.width_style = width_style
        self.deck = deck  # si False, ignora los indices de fragmento
        self.extra_style = extra_style
        self._open_frag = False

    def frag(self, idx):
        self.end_frag()
        if self.deck and idx is not None:
            self.parts.append(f'<g class="fragment" data-fragment-index="{idx}">')
            self._open_frag = True
        return self

    def end_frag(self):
        if self._open_frag:
            self.parts.append("</g>")
            self._open_frag = False

    def raw(self, s):
        self.parts.append(s)
        return self

    def line(self, x1, y1, x2, y2, stroke="#1a1a1a", w=2, dash=None, cap=None, marker=None, opacity=None):
        a = f'<line x1="{r1(x1)}" y1="{r1(y1)}" x2="{r1(x2)}" y2="{r1(y2)}" stroke="{stroke}" stroke-width="{w}"'
        if dash: a += f' stroke-dasharray="{dash}"'
        if cap: a += f' stroke-linecap="{cap}"'
        if marker: a += f' marker-end="url(#{marker})"'
        if opacity: a += f' stroke-opacity="{opacity}"'
        self.parts.append(a + "/>")
        return self

    def path(self, d, stroke="#1a1a1a", w=2, fill="none", dash=None, opacity=None, fill_opacity=None, join="round"):
        a = f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="{join}"'
        if dash: a += f' stroke-dasharray="{dash}"'
        if opacity: a += f' stroke-opacity="{opacity}"'
        if fill_opacity is not None: a += f' fill-opacity="{fill_opacity}"'
        self.parts.append(a + "/>")
        return self

    def poly(self, pts, stroke="#1a1a1a", w=2, fill="none", dash=None, closed=False, fill_opacity=None):
        s = " ".join(f"{r1(p[0])},{r1(p[1])}" for p in pts)
        tag = "polygon" if closed else "polyline"
        a = f'<{tag} points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"'
        if dash: a += f' stroke-dasharray="{dash}"'
        if fill_opacity is not None: a += f' fill-opacity="{fill_opacity}"'
        self.parts.append(a + "/>")
        return self

    def circle(self, cx, cy, r=3.4, fill="#fff", stroke="#1a1a1a", w=1.6):
        self.parts.append(f'<circle cx="{r1(cx)}" cy="{r1(cy)}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')
        return self

    def text(self, x, y, s, size=13, fill="#1a1a1a", weight=None, anchor=None, style=None, halo=False):
        a = f'font-size="{size}" fill="{fill}"'
        if weight: a += f' font-weight="{weight}"'
        if anchor: a += f' text-anchor="{anchor}"'
        if style: a += f' font-style="{style}"'
        if halo:
            self.parts.append(f'<text x="{r1(x)}" y="{r1(y)}" {a} stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round" opacity="0.9">{s}</text>')
        self.parts.append(f'<text x="{r1(x)}" y="{r1(y)}" {a}>{s}</text>')
        return self

    def render(self):
        self.end_frag()
        style = f"width:{self.width_style}; display:block; margin:0 auto;"
        if self.extra_style:
            style += " " + self.extra_style
        body = "\n".join(self.parts)
        return (f'<svg viewBox="{self.viewbox}" xmlns="http://www.w3.org/2000/svg" style="{style}">\n{body}\n</svg>')


def r1(v):
    v = round(float(v), 1)
    return int(v) if v == int(v) else v


def marker_defs(prefix, colors=(("rojo", ROJO), ("verde", VERDE), ("naranja", NARANJA2), ("gris", GRIS), ("negro", "#1a1a1a"), ("teal", TEAL))):
    """Marcadores de flecha con ids unicos por pagina: <prefix>-flecha-<color>."""
    out = ["<defs>"]
    for name, col in colors:
        out.append(
            f'<marker id="{prefix}-flecha-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{col}"/></marker>'
        )
    out.append("</defs>")
    return "".join(out)


def plan_contours(svg, levels=range(100, 161, 10), stroke=SIENA, w_master=2.2, w_normal=1.1, master_every=50, flip=DOM_Y):
    """Dibuja las curvas de nivel del terreno conductor en planta."""
    for lev in levels:
        for poly in CONTORNOS.get(lev, []):
            d = to_svg_path(poly, flip_y=flip)
            w = w_master if lev % master_every == 0 else w_normal
            svg.path(d, stroke=stroke, w=w)
    return svg


def streamline(x0, y0, direction=-1, step=2.0, n=400, stop_z=None):
    """Linea de maxima pendiente desde (x0,y0): direction=-1 desciende, +1 asciende."""
    pts = [(x0, y0)]
    x, y = x0, y0
    for _ in range(n):
        gx, gy = grad_z(x, y)
        norm = float(np.hypot(gx, gy))
        if norm < 1e-4:
            break
        x += direction * step * gx / norm
        y += direction * step * gy / norm
        if not (0 <= x <= DOM_X and 0 <= y <= DOM_Y):
            break
        pts.append((float(x), float(y)))
        if stop_z is not None:
            zz = float(z(x, y))
            if (direction < 0 and zz < stop_z) or (direction > 0 and zz > stop_z):
                break
    return rdp(np.array(pts), 1.0).tolist()


def label_on_contour(svg, lev, frac, dx=0, dy=0, size=11, poly_idx=0, halo=True, fill=SIENA):
    """Rotula la cota `lev` en la posicion fraccional `frac` de su polilinea."""
    polys = CONTORNOS.get(lev, [])
    if not polys or poly_idx >= len(polys):
        return
    poly = polys[poly_idx]
    i = int(frac * (len(poly) - 1))
    x, y = poly[i][0], DOM_Y - poly[i][1]
    svg.text(x + dx, y + dy, str(lev), size=size, fill=fill, weight="700", anchor="middle", halo=halo)
