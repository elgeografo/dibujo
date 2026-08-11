"""Terreno conductor del Bloque 3 (planos acotados).

Dominio: x en [0, 480] m, y en [0, 360] m (y crece hacia el norte).
Dos cerros (Cerro Mayor al NO, Cerro Menor al SE) separados por un
collado; una vaguada drena desde el collado hacia el este.
Equidistancia de referencia: 10 m; curvas 100..160.

En los SVG del plano usamos u = x, v = 360 - y (el eje SVG-y crece
hacia abajo), de modo que el norte queda arriba.
"""

import json
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Superficie del terreno
# ----------------------------------------------------------------------

def z(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    # Cerro Mayor (NO): elipse rotada ~ -20 grados
    ca, sa = np.cos(np.radians(-20)), np.sin(np.radians(-20))
    xm, ym = x - 125.0, y - 255.0
    xr = ca * xm - sa * ym
    yr = sa * xm + ca * ym
    cerro_mayor = 72.0 * np.exp(-((xr / 118.0) ** 2 + (yr / 88.0) ** 2))
    # espolon hacia el S del Cerro Mayor (rompe la simetria)
    espolon = 20.0 * np.exp(-(((x - 85.0) / 68.0) ** 2 + ((y - 118.0) / 72.0) ** 2))
    # Cerro Menor (SE): elipse rotada ~ +30 grados
    cb, sb = np.cos(np.radians(30)), np.sin(np.radians(30))
    xn, yn = x - 380.0, y - 92.0
    xs = cb * xn - sb * yn
    ys = sb * xn + cb * yn
    cerro_menor = 46.0 * np.exp(-((xs / 98.0) ** 2 + (ys / 70.0) ** 2))
    # base inclinada suave que drena hacia el E/SE
    base = 96.0 - 0.006 * x - 0.004 * (360.0 - y)
    return base + cerro_mayor + espolon + cerro_menor


def grad_z(x, y, h=0.01):
    gx = (z(x + h, y) - z(x - h, y)) / (2 * h)
    gy = (z(x, y + h) - z(x, y - h)) / (2 * h)
    return gx, gy


# ----------------------------------------------------------------------
# Extraccion de curvas de nivel -> polilineas simplificadas
# ----------------------------------------------------------------------

def rdp(points, tol):
    """Ramer-Douglas-Peucker sobre una polilinea Nx2."""
    pts = np.asarray(points)
    if len(pts) < 3:
        return pts
    keep = np.zeros(len(pts), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i0, i1 = stack.pop()
        if i1 <= i0 + 1:
            continue
        a, b = pts[i0], pts[i1]
        ab = b - a
        lab = np.hypot(*ab)
        if lab == 0:
            d = np.hypot(*(pts[i0 + 1 : i1] - a).T)
        else:
            d = np.abs(np.cross(ab, pts[i0 + 1 : i1] - a)) / lab
        imax = int(np.argmax(d)) + i0 + 1
        if d[imax - i0 - 1] > tol:
            keep[imax] = True
            stack.append((i0, imax))
            stack.append((imax, i1))
    return pts[keep]


def contour_polylines(levels, xlim=(0, 480), ylim=(0, 360), n=481, tol=1.2):
    xs = np.linspace(xlim[0], xlim[1], n)
    ys = np.linspace(ylim[0], ylim[1], int(n * (ylim[1] - ylim[0]) / (xlim[0] - xlim[1] if False else (xlim[1] - xlim[0]))) or 361)
    X, Y = np.meshgrid(xs, ys)
    Z = z(X, Y)
    fig, ax = plt.subplots()
    cs = ax.contour(X, Y, Z, levels=levels)
    out = {}
    for lev, segs in zip(cs.levels, cs.allsegs):
        polys = []
        for seg in segs:
            if len(seg) < 2:
                continue
            simp = rdp(seg, tol)
            polys.append(np.round(simp, 1).tolist())
        out[float(lev)] = polys
    plt.close(fig)
    return out


def to_svg_path(poly, flip_y=360.0, dec=1):
    """Polilinea [[x,y],...] -> atributo d de path SVG con suavizado
    Catmull-Rom -> Bezier cubica (coordenadas plano: v = flip_y - y)."""
    pts = [(round(p[0], dec), round(flip_y - p[1], dec)) for p in poly]
    if len(pts) < 2:
        return ""
    if len(pts) == 2:
        return f"M {pts[0][0]},{pts[0][1]} L {pts[1][0]},{pts[1][1]}"
    d = [f"M {pts[0][0]},{pts[0][1]}"]
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (round(p1[0] + (p2[0] - p0[0]) / 6.0, dec), round(p1[1] + (p2[1] - p0[1]) / 6.0, dec))
        c2 = (round(p2[0] - (p3[0] - p1[0]) / 6.0, dec), round(p2[1] - (p3[1] - p1[1]) / 6.0, dec))
        d.append(f"C {c1[0]},{c1[1]} {c2[0]},{c2[1]} {p2[0]},{p2[1]}")
    return " ".join(d)


# ----------------------------------------------------------------------
# Proyeccion axonometrica (para las figuras "3D" del fundamento)
# ----------------------------------------------------------------------

def iso(x, y, zz, scale=1.0, kz=1.0):
    """Proyeccion isometrica-ish: devuelve (u, v) SVG (v hacia abajo)."""
    u = (x - y) * 0.866 * scale
    v = (x + y) * 0.35 * scale - kz * zz
    return u, v


if __name__ == "__main__":
    levels = list(range(100, 171, 10))
    data = contour_polylines(levels)
    with open("contornos.json", "w") as f:
        json.dump({str(int(k)): v for k, v in data.items()}, f)
    # resumen
    for k in sorted(data, key=float):
        polys = data[k]
        print(int(k), "->", len(polys), "polilineas,", sum(len(p) for p in polys), "pts")
    # vista rapida para inspeccion visual
    xs = np.linspace(0, 480, 481)
    ys = np.linspace(0, 360, 361)
    X, Y = np.meshgrid(xs, ys)
    Z = z(X, Y)
    fig, ax = plt.subplots(figsize=(8, 6))
    cs = ax.contour(X, Y, Z, levels=list(range(96, 172, 2)), linewidths=0.4, colors="#999")
    cs2 = ax.contour(X, Y, Z, levels=levels, linewidths=1.2, colors="#8a5a2a")
    ax.clabel(cs2, fmt="%d")
    ax.set_aspect("equal")
    ax.set_title(f"terreno conductor  zmax={Z.max():.1f}")
    fig.savefig("terreno_preview.png", dpi=110)
    print("preview -> terreno_preview.png, zmax", round(float(Z.max()), 2), "zmin", round(float(Z.min()), 2))
