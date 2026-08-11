"""Ensambla .qmd finales sustituyendo {{SVG:nombre}} por scratchpad/svg/nombre.svg."""

import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def build(template, dest):
    src = open(template).read()

    def sub(m):
        name = m.group(1)
        path = os.path.join(HERE, "svg", name + ".svg")
        return open(path).read()

    out = re.sub(r"\{\{SVG:([a-zA-Z0-9_\-]+)\}\}", sub, src)
    pending = re.findall(r"\{\{SVG:[^}]*\}\}", out)
    if pending:
        raise SystemExit(f"marcadores sin resolver: {pending}")
    with open(dest, "w") as f:
        f.write(out)
    print("build:", template, "->", dest)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
