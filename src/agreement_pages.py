"""Pages 7-29: the custodial agreements and disclosure statements.

The source text layer gives one line per segment, so the work here is to put
paragraphs, numbered lists and run-in headings back together, then flow them
into branded pages. Nothing on these pages is an input field.
"""

import os
import re

from reportlab.pdfbase.pdfmetrics import stringWidth

from brand import (
    BRONZE_DEEP,
    CONTENT_W,
    ESPRESSO,
    GOLD,
    GOLD_LIGHT,
    GRAY,
    INK,
    INK_SOFT,
    MARGIN_L,
    MARGIN_R,
    PAGE_H,
    PAGE_W,
    RULE,
    SANS,
    SANS_B,
    SANS_BO,
    SANS_O,
    SERIF,
    SERIF_B,
    SERIF_I,
    WASH,
    WASH_GOLD,
    WHITE,
    alpha,
)
from content_plan import DEFAULT_START, PAGE_PLANS, PAGE_START, SECTIONS, TABLES
from layout import gradient_rule, tracked, tracked_width, wrap, wrap_runs

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source_pages.txt")

BODY_SIZE = 8.4
BODY_LEAD = 11.4
TOP = PAGE_H - 88.0
BOTTOM = 76.0

MARKER_RE = re.compile(r"^(\d{1,2}\.|[a-z]\.|[ivx]{1,4}\.|[a-z]\)|\d\.\))$")
INDENT = {0: 0.0, 1: 18.0, 2: 36.0, 3: 54.0}
MARKER_W = {0: 18.0, 1: 17.0, 2: 18.0, 3: 19.0}


def _pages():
    with open(SRC, encoding="utf-8") as fh:
        return [ln.rstrip("\n") for ln in fh]


def _segments(page_text):
    return [p.strip() for p in re.split(r"\s{2,}", page_text.strip()) if p.strip()]


def _is_caps(s):
    letters = [ch for ch in s if ch.isalpha()]
    return bool(letters) and all(ch.isupper() for ch in letters)


def _marker_level(m):
    if re.match(r"^\d{1,2}\.$", m):
        return 0
    if re.match(r"^[a-z]\.$", m) and m[0] not in "ivx":
        return 1
    if re.match(r"^[ivx]{1,4}\.$", m):
        return 2
    if re.match(r"^[a-z]\.$", m):
        return 1
    return 2


# Source lines run 130-155 characters, so a short line that closes on a full
# stop is the last line of a paragraph rather than a mid-paragraph break.
FULL_LINE = 118


def _is_runin(s, prev_was_marker, next_seg=None):
    """A bold lead-in like 'Account.', 'Article IV.' or 'Uninvested Cash Funds.'

    Run-ins follow a list marker ('a.  Account.  The Custodian shall ...') but
    also open a paragraph straight after a heading, as the DEFINITIONS and
    SPECIFIC INSTRUCTIONS blocks do.
    """
    if _is_caps(s) and prev_was_marker:
        return True
    if not (len(s) < 62 and s.endswith(".") and s[:1].isupper()):
        return False
    if prev_was_marker:
        return True
    # opening a fresh block: only a run-in if real body copy follows it
    return next_seg is not None and len(next_seg) >= 45


# ---------------------------------------------------------------------------
# block model
# ---------------------------------------------------------------------------

class Block:
    def __init__(self, kind, text="", marker=None, runin=None, level=0, table=None):
        self.kind = kind          # heading | para | item | emphasis | table
        self.text = text
        self.marker = marker
        self.runin = runin
        self.level = level
        self.table = table


def _blocks_from_segs(segs, rng):
    """Turn an inclusive segment range into blocks."""
    out = []
    pending_marker = None
    pending_level = 0
    pending_runin = None
    buf = []
    prev_was_marker = False
    prev_was_emphasis = False

    def flush():
        """Emit the buffered paragraph.

        A paragraph that follows a list item without a marker of its own is a
        continuation of that item, so it keeps the item's indent instead of
        snapping back to the left margin.
        """
        nonlocal buf, pending_marker, pending_runin, pending_level
        if buf or pending_marker or pending_runin:
            text = " ".join(buf).strip()
            kind = "item" if pending_marker else "para"
            level = pending_level
            if pending_marker is None and out and out[-1].kind in ("item", "para"):
                level = out[-1].level
            out.append(Block(kind, text, pending_marker, pending_runin, level))
            pending_level = level
        buf, pending_marker, pending_runin = [], None, None

    for i in rng:
        if i >= len(segs):
            break
        s = segs[i]
        if MARKER_RE.match(s):
            flush()
            pending_marker = s
            pending_level = _marker_level(s)
            prev_was_marker = True
            prev_was_emphasis = False
            continue
        if _is_caps(s) and not prev_was_marker and len(s) > 45:
            # an all-caps emphasised passage, not a heading
            flush()
            out.append(Block("emphasis", s))
            prev_was_emphasis = True
            prev_was_marker = False
            continue
        if _is_caps(s) and prev_was_emphasis:
            # continuation line of the emphasised passage
            out[-1].text += " " + s
            continue
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        if (pending_runin is None and not buf
                and _is_runin(s, prev_was_marker, nxt)):
            pending_runin = s
            prev_was_marker = False
            prev_was_emphasis = False
            continue
        if _is_caps(s) and not prev_was_marker and len(s) <= 45:
            flush()
            out.append(Block("heading", s))
            pending_level = 0          # a heading restarts the indent context
            prev_was_emphasis = False
            prev_was_marker = False
            continue
        buf.append(s)
        prev_was_marker = False
        prev_was_emphasis = False
        # a short line closing on a full stop ends the paragraph
        if len(s) < FULL_LINE and s.endswith((".", ":", "”")):
            flush()
    flush()
    return [b for b in out if b.kind != "para" or b.text or b.runin]


def build_blocks(section):
    pages = _pages()
    blocks = []
    for pg in section["pages"]:
        segs = _segments(pages[pg - 1])
        start = PAGE_START.get(pg, DEFAULT_START)
        plan = PAGE_PLANS.get(pg)
        if plan is None:
            plan = [("segs", start, len(segs) - 1)]
        for item in plan:
            if item[0] == "h":
                blocks.append(Block("heading", item[1]))
            elif item[0] == "table":
                blocks.append(Block("table", table=TABLES[item[1]]))
            else:
                _, a, b = item
                blocks.extend(_blocks_from_segs(segs, range(a, b + 1)))
    return _merge_split_paragraphs(blocks)


def _merge_split_paragraphs(blocks):
    """A paragraph broken across a source page boundary arrives as two blocks."""
    out = []
    for b in blocks:
        if (out and b.kind == "para" and not b.marker and not b.runin
                and out[-1].kind in ("para", "item") and out[-1].text
                and not out[-1].text.rstrip().endswith((".", ":", "?", "”"))):
            out[-1].text = (out[-1].text + " " + b.text).strip()
            continue
        out.append(b)
    return out


# ---------------------------------------------------------------------------
# measuring and drawing
# ---------------------------------------------------------------------------

def _para_lines(b, width_for_level):
    width = width_for_level(b.level, bool(b.marker))
    runs = []
    if b.runin:
        runs.append((b.runin + "  ", SERIF_B, BODY_SIZE))
    if b.text:
        runs.append((b.text, SERIF, BODY_SIZE))
    if not runs:
        return []
    return wrap_runs(runs, width)


def _content_width(level, has_marker):
    w = CONTENT_W - INDENT[min(level, 3)]
    if has_marker:
        w -= MARKER_W[min(level, 3)]
    return w


def _table_geometry(tbl):
    cols = [CONTENT_W * 0.42, CONTENT_W * 0.31, CONTENT_W * 0.27]
    size = 7.6
    rows = []
    head_h = 0.0
    for cell, w in zip(tbl["head"], cols):
        head_h = max(head_h, len(wrap(cell, SERIF_B, size, w - 14.0)) * 9.8)
    head_h += 10.0
    for row in tbl["rows"]:
        h = 0.0
        for cell, w in zip(row, cols):
            if cell:
                h = max(h, len(wrap(cell, SERIF, size, w - 14.0)) * 9.6)
        rows.append(max(h + 8.0, 18.0))
    return cols, size, head_h, rows


PARA_GAP = 9.5


def _para_height(n_lines):
    """Height a paragraph of n lines consumes, matching what draw() advances."""
    if n_lines <= 0:
        return 0.0
    return BODY_SIZE + (n_lines - 1) * BODY_LEAD + PARA_GAP


def measure(b):
    if b.kind == "heading":
        return 32.0
    if b.kind == "table":
        cols, size, head_h, rows = _table_geometry(b.table)
        return head_h + sum(rows) + 14.0
    if b.kind == "emphasis":
        return len(wrap(b.text, SERIF_B, BODY_SIZE, CONTENT_W - 28.0)) * BODY_LEAD + 20.0
    return _para_height(len(_para_lines(b, _content_width)))


def draw(c, b, y):
    if b.kind == "heading":
        tracked(c, MARGIN_L, y - 15.0, b.text, SERIF_B, 9.4, BRONZE_DEEP, 1.6)
        gradient_rule(c, MARGIN_L, y - 21.0, CONTENT_W, 0.7,
                      c1=alpha(GOLD, 0.75), c2=alpha(BRONZE_DEEP, 0.3))
        return y - 32.0

    if b.kind == "emphasis":
        lines = wrap(b.text, SERIF_B, BODY_SIZE, CONTENT_W - 28.0)
        h = len(lines) * BODY_LEAD + 14.0
        c.setFillColor(WASH_GOLD)
        c.rect(MARGIN_L, y - h, CONTENT_W, h, stroke=0, fill=1)
        c.setFillColor(GOLD)
        c.rect(MARGIN_L, y - h, 2.4, h, stroke=0, fill=1)
        ty = y - 13.0
        c.setFont(SERIF_B, BODY_SIZE)
        c.setFillColor(ESPRESSO)
        for ln in lines:
            c.drawString(MARGIN_L + 14.0, ty, ln)
            ty -= BODY_LEAD
        return y - h - 8.0

    if b.kind == "table":
        return _draw_table(c, b.table, y)

    x = MARGIN_L + INDENT[min(b.level, 3)]
    if b.marker:
        c.setFont(SERIF_B, BODY_SIZE)
        c.setFillColor(BRONZE_DEEP)
        c.drawString(x, y - BODY_SIZE, b.marker)
        x += MARKER_W[min(b.level, 3)]

    lines = _para_lines(b, _content_width)
    ty = y - BODY_SIZE
    for line in lines:
        for text, font, size, dx in line:
            c.setFont(font, size)
            c.setFillColor(ESPRESSO if font == SERIF_B else INK_SOFT)
            c.drawString(x + dx, ty, text)
        ty -= BODY_LEAD
    return y - _para_height(len(lines))


def _draw_table(c, tbl, y):
    cols, size, head_h, row_hs = _table_geometry(tbl)
    xs, acc = [], MARGIN_L
    for w in cols:
        xs.append(acc)
        acc += w

    # header
    c.setFillColor(ESPRESSO)
    c.rect(MARGIN_L, y - head_h, CONTENT_W, head_h, stroke=0, fill=1)
    for cell, x, w in zip(tbl["head"], xs, cols):
        ty = y - 13.0
        c.setFont(SERIF_B, size)
        c.setFillColor(GOLD_LIGHT)
        for ln in wrap(cell, SERIF_B, size, w - 14.0):
            c.drawString(x + 7.0, ty, ln)
            ty -= 9.8
    cy = y - head_h

    for i, (row, h) in enumerate(zip(tbl["rows"], row_hs)):
        if i % 2 == 0:
            c.setFillColor(WASH)
            c.rect(MARGIN_L, cy - h, CONTENT_W, h, stroke=0, fill=1)
        for cell, x, w in zip(row, xs, cols):
            if not cell:
                continue
            ty = cy - 11.5
            c.setFont(SERIF, size)
            c.setFillColor(INK_SOFT)
            for ln in wrap(cell, SERIF, size, w - 14.0):
                c.drawString(x + 7.0, ty, ln)
                ty -= 9.6
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(MARGIN_L, cy - h, PAGE_W - MARGIN_R, cy - h)
        cy -= h

    gradient_rule(c, MARGIN_L, cy - 2.0, CONTENT_W, 1.4)
    return cy - 14.0


# ---------------------------------------------------------------------------
# section title block + pagination
# ---------------------------------------------------------------------------

def _section_title(c, section, y):
    tracked(c, MARGIN_L, y, section["title"], SERIF, 13.5, ESPRESSO, 2.0)
    y -= 18.0
    tracked(c, MARGIN_L, y, section["subtitle"].upper(), SERIF_B, 9.6,
            BRONZE_DEEP, 2.2)
    y -= 17.0
    c.setFont(SERIF_I, 7.4)
    c.setFillColor(GRAY)
    for m in section["meta"]:
        c.drawString(MARGIN_L, y, m)
        y -= 10.0
    y -= 6.0
    gradient_rule(c, MARGIN_L, y, CONTENT_W, 1.2)
    return y - 22.0


class BackPage:
    def __init__(self, section, items, first):
        self.section = section["footer"]
        self.revision = section["revision"]
        self.eyebrow = section["eyebrow"]
        self.title = section["header_title"]
        self.subtitle = section["header_sub"]
        self._section = section
        self._items = items
        self._first = first

    def render(self, c):
        y = TOP
        if self._first:
            y = _section_title(c, self._section, y)
        for b in self._items:
            y = draw(c, b, y)


def build_back_pages():
    pages = []
    for section in SECTIONS:
        blocks = build_blocks(section)
        first = True
        cur, y = [], TOP - (78.0 + 9.0 * len(section["meta"]))
        for b in blocks:
            h = measure(b)
            if y - h < BOTTOM and cur:
                pages.append(BackPage(section, cur, first))
                first = False
                cur, y = [], TOP
            # a heading should not be the last thing on a page
            if b.kind == "heading" and y - h - 40.0 < BOTTOM and cur:
                pages.append(BackPage(section, cur, first))
                first = False
                cur, y = [], TOP
            cur.append(b)
            y -= h
        if cur:
            pages.append(BackPage(section, cur, first))
    return pages
