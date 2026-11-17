#!/usr/bin/env python3
"""Generate the profile dashboard (assets/dashboard-light.svg and -dark.svg).

Edit the numbers below, then run:  python3 assets/make_dashboard.py
"""

from pathlib import Path

# ---- Data: update these ---------------------------------------------------
AS_OF = "November 2026"
TILES = [
    ("Publications", "20", "peer-reviewed"),
    ("Citations", "165", "Google Scholar"),
    ("h-index", "8", "Google Scholar"),
    ("MD simulations since", "2019", "all-atom, GROMACS"),
]
PAPERS_PER_YEAR = [(2020, 1), (2021, 1), (2022, 3), (2023, 6), (2024, 3),
                   (2025, 4), (2026, 2)]
TOOLBOX = [
    ("Simulation", ["GROMACS", "PLUMED", "MM-PBSA"]),
    ("Analysis and ML", ["Python", "MDTraj", "PyTorch"]),
    ("Design and structure", ["Schrödinger", "CryoSPARC", "Docking"]),
]

# ---- Themes ---------------------------------------------------------------
THEMES = {
    "light": dict(surface="#fcfcfb", border="#0b0b0b", border_op="0.10",
                  primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", baseline="#c3c2b7", series="#2a78d6"),
    "dark": dict(surface="#1a1a19", border="#ffffff", border_op="0.10",
                 primary="#f0efec", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", baseline="#383835", series="#3987e5"),
}

FONT = 'system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
W, GAP = 840, 12
TILE_H = 92
ROW2_Y = TILE_H + GAP
ROW2_H = 268
H = ROW2_Y + ROW2_H


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;")


def card(x, y, w, h, t):
    return (f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="10" '
            f'fill="{t["surface"]}" stroke="{t["border"]}" stroke-opacity="{t["border_op"]}"/>')


def text(x, y, s, size, fill, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


def tiles(t):
    out = []
    w = (W - GAP * (len(TILES) - 1)) / len(TILES)
    for i, (label, value, caption) in enumerate(TILES):
        x = round(i * (w + GAP), 1)
        out.append(card(x, 0, w, TILE_H, t))
        out.append(text(x + 16, 26, label, 12.5, t["secondary"]))
        out.append(text(x + 16, 62, value, 30, t["primary"], 600))
        out.append(text(x + 16, 80, caption, 11.5, t["muted"]))
    return out


def chart(x0, y0, w, h, t):
    out = [card(x0, y0, w, h, t),
           text(x0 + 16, y0 + 28, "Publications per year", 14, t["primary"], 600),
           text(x0 + 16, y0 + 46, f"Peer-reviewed papers; 2026 counted to {AS_OF}",
                11.5, t["muted"])]
    left, right = x0 + 44, x0 + w - 20
    top, base = y0 + 76, y0 + h - 38
    ymax = 6
    scale = (base - top) / ymax
    for tick in (2, 4, 6):
        y = base - tick * scale
        out.append(f'<line x1="{left}" x2="{right}" y1="{y}" y2="{y}" stroke="{t["grid"]}"/>')
    for tick in (0, 2, 4, 6):
        out.append(text(left - 10, base - tick * scale + 4, str(tick), 11.5,
                        t["muted"], anchor="end"))
    slot = (right - left) / len(PAPERS_PER_YEAR)
    bar_w, r = 24, 4
    peak = max(n for _, n in PAPERS_PER_YEAR)
    for i, (year, n) in enumerate(PAPERS_PER_YEAR):
        cx = left + slot * (i + 0.5)
        x, bh = cx - bar_w / 2, n * scale
        ytop = base - bh
        # column: rounded at the data end, square at the baseline
        out.append(
            f'<path d="M{x},{base} V{ytop + r} Q{x},{ytop} {x + r},{ytop} '
            f'H{x + bar_w - r} Q{x + bar_w},{ytop} {x + bar_w},{ytop + r} V{base} Z" '
            f'fill="{t["series"]}"/>')
        out.append(text(cx, base + 18, str(year), 11.5, t["muted"], anchor="middle"))
        if n == peak:
            out.append(text(cx, ytop - 7, str(n), 12, t["primary"], 600, "middle"))
    out.append(f'<line x1="{left}" x2="{right}" y1="{base}" y2="{base}" stroke="{t["baseline"]}"/>')
    return out


def toolbox(x0, y0, w, h, t):
    out = [card(x0, y0, w, h, t),
           text(x0 + 16, y0 + 28, "Toolbox", 14, t["primary"], 600),
           text(x0 + 16, y0 + 46, "What the simulations and models run on",
                11.5, t["muted"])]
    y = y0 + 76
    for group, items in TOOLBOX:
        out.append(text(x0 + 16, y, group, 11.5, t["secondary"], 600))
        x = x0 + 16
        for item in items:
            chip_w = round(sum(9.2 if c.isupper() else 7.0 for c in item) + 26)
            out.append(f'<rect x="{x + 0.5}" y="{y + 10.5}" width="{chip_w}" height="26" rx="13" '
                       f'fill="none" stroke="{t["baseline"]}"/>')
            out.append(text(x + chip_w / 2 + 0.5, y + 28, item, 12.5, t["primary"],
                            anchor="middle"))
            x += chip_w + 8
        y += 62
    return out


def build(theme):
    t = THEMES[theme]
    chart_w = 500
    body = tiles(t)
    body += chart(0, ROW2_Y, chart_w, ROW2_H, t)
    body += toolbox(chart_w + GAP, ROW2_Y, W - chart_w - GAP, ROW2_H, t)
    summary = ("Research dashboard: " +
               "; ".join(f"{label} {value}" for label, value, _ in TILES) +
               ". Publications per year: " +
               ", ".join(f"{y}: {n}" for y, n in PAPERS_PER_YEAR) + ".")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" font-family=\'{FONT}\'>\n'
            f'<title>{esc(summary)}</title>\n' + "\n".join(body) + "\n</svg>\n")


if __name__ == "__main__":
    here = Path(__file__).parent
    for theme in THEMES:
        path = here / f"dashboard-{theme}.svg"
        path.write_text(build(theme), encoding="utf-8")
        print(f"Wrote {path}")
