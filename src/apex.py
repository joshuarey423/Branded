"""The Fortuity apex triangle - watermark and small section glyph.

The mark is traced to vector (see `tools/trace_apex.py`), so it stays crisp at
any size and costs a few kilobytes rather than a bitmap on every page. The
watermark is registered once as a PDF form and stamped on each page, which
keeps the file small even though the outline runs to several hundred segments.
"""

from apex_path import ASPECT, CURVES
from brand import (
    GOLD_LIGHT,
    BRONZE_DEEP,
    PAGE_W,
    WATERMARK_ALPHA,
    WATERMARK_CENTER_Y,
    WATERMARK_WIDTH,
    mix,
)

FORM_NAME = "fortuity_apex"


def _build_path(c, x, y, width):
    """The outline, scaled into a box of `width` with its lower-left at (x, y)."""
    height = width / ASPECT
    p = c.beginPath()
    for curve in CURVES:
        for seg in curve:
            op = seg[0]
            if op == "m":
                p.moveTo(x + seg[1][0] * width, y + seg[1][1] * height)
            elif op == "l":
                p.lineTo(x + seg[1][0] * width, y + seg[1][1] * height)
            elif op == "c":
                p.curveTo(x + seg[1][0] * width, y + seg[1][1] * height,
                          x + seg[2][0] * width, y + seg[2][1] * height,
                          x + seg[3][0] * width, y + seg[3][1] * height)
            else:
                p.close()
    return p, height


def _paint_graded(c, x, y, width, height, c1, c2, steps=140):
    """Fill the current clip with a vertical ramp, light at the apex."""
    band = height / steps
    for i in range(steps):
        c.setFillColor(mix(c1, c2, i / (steps - 1.0)))
        c.rect(x - 1.0, y + height - (i + 1) * band, width + 2.0, band + 0.6,
               stroke=0, fill=1)


def register(c, width=WATERMARK_WIDTH):
    """Define the watermark once, before any page is written."""
    height = width / ASPECT
    c.beginForm(FORM_NAME, 0, 0, width, height)
    path, _ = _build_path(c, 0.0, 0.0, width)
    c.saveState()
    c.clipPath(path, stroke=0, fill=0)
    _paint_graded(c, 0.0, 0.0, width, height, GOLD_LIGHT, BRONZE_DEEP)
    c.restoreState()
    c.endForm()


def stamp(c, width=WATERMARK_WIDTH, center_y=WATERMARK_CENTER_Y,
          alpha=WATERMARK_ALPHA):
    """Lay the watermark on the current page, behind everything else."""
    height = width / ASPECT
    c.saveState()
    c.setFillAlpha(alpha)
    c.setStrokeAlpha(alpha)
    c.translate((PAGE_W - width) / 2.0, center_y - height / 2.0)
    if width != WATERMARK_WIDTH:
        c.scale(width / WATERMARK_WIDTH, width / WATERMARK_WIDTH)
    c.doForm(FORM_NAME)
    c.restoreState()


def glyph(c, x, y, size, color, alpha=1.0):
    """A small solid apex used as a section marker. `y` is the baseline."""
    path, height = _build_path(c, x, y, size)
    c.saveState()
    if alpha < 1.0:
        c.setFillAlpha(alpha)
    c.setFillColor(color)
    c.drawPath(path, stroke=0, fill=1)
    c.restoreState()
    return size
