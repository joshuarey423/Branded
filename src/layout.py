"""Drawing primitives for the Fortuity-branded IRA packet.

Everything here works against a raw reportlab canvas rather than a Platypus
flowable tree - the application pages are positional forms, so a cursor-based
layout keeps the form pages and the agreement pages on one set of primitives.
"""

import os
import re

from reportlab.pdfbase.pdfmetrics import stringWidth

from brand import (
    BRONZE,
    BRONZE_DEEP,
    CONTENT_BOTTOM,
    CONTENT_W,
    ESPRESSO,
    GOLD,
    GOLD_LIGHT,
    GRAY,
    INK,
    INK_SOFT,
    LOGO_ASPECT,
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
    SERIF_BI,
    SERIF_I,
    WASH,
    WASH_GOLD,
    WHITE,
    alpha,
    mix,
)

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
LOGO = os.path.join(ASSETS, "fortuity_logo.png")
LOGO_KO = os.path.join(ASSETS, "fortuity_logo_knockout.png")


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------

def tracked(c, x, y, text, font, size, color, tracking=0.0):
    """Draw text with letter-spacing (the logo is heavily tracked out).

    Spacing goes through the PDF character-spacing operator rather than one
    drawString per glyph, so headings stay selectable and searchable.
    """
    c.setFillColor(color)
    if not tracking:
        c.setFont(font, size)
        c.drawString(x, y, text)
        return stringWidth(text, font, size)
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(tracking)
    t.textOut(text)
    # reset inside the same text object: Tc is part of the PDF text state and
    # would otherwise leak into every later drawString on the page
    t.setCharSpace(0)
    c.drawText(t)
    return tracked_width(text, font, size, tracking)


def tracked_width(text, font, size, tracking=0.0):
    return stringWidth(text, font, size) + tracking * max(len(text) - 1, 0)


def wrap(text, font, size, width):
    """Greedy word wrap returning a list of lines."""
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = w if not line else line + " " + w
        if stringWidth(trial, font, size) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            # a single word wider than the column still has to go somewhere
            while stringWidth(w, font, size) > width and len(w) > 1:
                cut = len(w)
                while cut > 1 and stringWidth(w[:cut], font, size) > width:
                    cut -= 1
                lines.append(w[:cut])
                w = w[cut:]
            line = w
    if line:
        lines.append(line)
    return lines


def wrap_runs(runs, width, first_indent=0.0):
    """Wrap a list of (text, font, size) runs into lines of positioned pieces.

    Returns [[(text, font, size, x_offset), ...], ...]. Used for paragraphs that
    open with a bold run-in heading, e.g. "Account.  The Custodian shall ...".
    """
    lines, cur, x = [], [], first_indent
    avail = width
    for text, font, size in runs:
        for i, word in enumerate(text.split()):
            piece = word
            w = stringWidth(piece, font, size)
            space = stringWidth(" ", font, size) if cur else 0.0
            if x + space + w > avail and cur:
                lines.append(cur)
                cur, x, avail = [], 0.0, width
                space = 0.0
            cur.append((piece, font, size, x + space))
            x += space + w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# page chrome
# ---------------------------------------------------------------------------

def gradient_rule(c, x, y, width, height=2.0, c1=GOLD_LIGHT, c2=BRONZE_DEEP, steps=90):
    """The signature Fortuity gold gradient, rendered as a fine step ramp."""
    seg = width / steps
    for i in range(steps):
        c.setFillColor(mix(c1, c2, i / (steps - 1.0)))
        c.rect(x + i * seg, y, seg + 0.4, height, stroke=0, fill=1)


def hairline(c, x, y, width, color=RULE, lw=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.line(x, y, x + width, y)


def header(c, eyebrow, title, subtitle=None):
    """Wordmark left, document title right, a graded gold rule beneath both."""
    logo_h = 25.0
    logo_w = logo_h * LOGO_ASPECT
    top = PAGE_H - 32.0
    c.drawImage(
        LOGO, MARGIN_L, top - logo_h, width=logo_w, height=logo_h,
        mask="auto", preserveAspectRatio=True, anchor="sw",
    )

    right = PAGE_W - MARGIN_R
    if eyebrow:
        w = tracked_width(eyebrow, SERIF, 6.0, 2.0)
        tracked(c, right - w, top - 7.0, eyebrow, SERIF, 6.0, GOLD, 2.0)
    if title:
        w = tracked_width(title, SERIF, 9.6, 0.5)
        tracked(c, right - w, top - 20.0, title, SERIF, 9.6, INK_SOFT, 0.5)
    if subtitle:
        w = stringWidth(subtitle, SERIF_I, 7.4)
        c.setFont(SERIF_I, 7.4)
        c.setFillColor(GRAY)
        c.drawString(right - w, top - 30.5, subtitle)

    # a graded rule over a hairline - the engraved double rule of a certificate
    gradient_rule(c, MARGIN_L, PAGE_H - 68.0, CONTENT_W, 1.2)
    hairline(c, MARGIN_L, PAGE_H - 71.6, CONTENT_W, alpha(GOLD, 0.35), 0.4)


def footer(c, page_no, page_total, section_label, revision):
    y = 30.0
    hairline(c, MARGIN_L, y + 15.0, CONTENT_W, alpha(RULE, 0.9), 0.4)

    c.setFont(SERIF_I, 7.0)
    c.setFillColor(GRAY)
    c.drawString(MARGIN_L, y + 4.0, f"{section_label}   \u2014   {revision}")

    right = PAGE_W - MARGIN_R
    c.setFont(SERIF, 7.2)
    c.setFillColor(BRONZE_DEEP)
    c.drawRightString(right, y + 4.0, f"{page_no} of {page_total}")

    label = "FORTUITY INC   \u00b7   CUSTODIAL SERVICES BY DIGITAL TRUST"
    w = tracked_width(label, SERIF, 5.8, 1.1)
    tracked(c, (PAGE_W - w) / 2.0, y - 7.0, label, SERIF, 5.8,
            alpha(GRAY, 0.85), 1.1)


def contact_strip(c, y):
    """Custodian contact line: hairline-ruled rather than boxed in."""
    from brand import CUSTODIAN_EMAIL, CUSTODIAN_FAX, CUSTODIAN_PHONE

    hairline(c, MARGIN_L, y + 16.0, CONTENT_W, alpha(RULE, 0.9), 0.4)
    hairline(c, MARGIN_L, y, CONTENT_W, alpha(RULE, 0.9), 0.4)

    parts = [("Telephone", CUSTODIAN_PHONE), ("Facsimile", CUSTODIAN_FAX),
             ("Email", CUSTODIAN_EMAIL)]
    x = MARGIN_L
    step = CONTENT_W / len(parts)
    for label, value in parts:
        w = tracked(c, x, y + 5.5, label.upper(), SERIF, 5.8, GOLD, 1.0)
        c.setFont(SERIF, 7.6)
        c.setFillColor(INK_SOFT)
        c.drawString(x + w + 7.0, y + 5.5, value)
        x += step
    return y


# ---------------------------------------------------------------------------
# section furniture
# ---------------------------------------------------------------------------

def part_band(c, y, number, title, height=21.0):
    """PART 1. ACCOUNT OWNER INFORMATION - espresso band under a gold cap."""
    import apex

    c.setFillColor(ESPRESSO)
    c.rect(MARGIN_L, y, CONTENT_W, height, stroke=0, fill=1)
    gradient_rule(c, MARGIN_L, y + height - 1.6, CONTENT_W, 1.6)

    base = y + 7.0
    x = MARGIN_L + 12.0
    apex.glyph(c, x, base - 1.5, 10.0, GOLD_LIGHT, alpha=0.95)
    x += 18.0
    if number:
        w = tracked(c, x, base, number, SERIF_B, 8.8, GOLD_LIGHT, 1.2)
        x += w + 10.0
    tracked(c, x, base, title, SERIF_B, 8.8, WHITE, 1.8)
    return y - 12.0


def section_head(c, y, title, size=9.4):
    """Lighter heading: tracked caps over a graded rule."""
    tracked(c, MARGIN_L, y, title, SERIF_B, size, BRONZE_DEEP, 1.5)
    gradient_rule(c, MARGIN_L, y - 5.5, CONTENT_W, 0.7,
                  c1=alpha(GOLD, 0.75), c2=alpha(BRONZE_DEEP, 0.35))
    return y - 17.0


def callout(c, y, text, width=None, pad=10.0, size=7.6):
    """The '!' notes from the source form, restyled as a ruled gold wash."""
    width = width or CONTENT_W
    inner = width - pad * 2 - 16.0
    lines = wrap(text, SERIF_I, size, inner)
    height = pad * 2 + len(lines) * (size + 3.0) - 3.0

    c.setFillColor(WASH_GOLD)
    c.rect(MARGIN_L, y - height, width, height, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(MARGIN_L, y - height, 1.8, height, stroke=0, fill=1)

    c.setFont(SERIF_B, 10.0)
    c.setFillColor(BRONZE_DEEP)
    c.drawString(MARGIN_L + pad + 2.0, y - pad - size + 0.5, "!")

    ty = y - pad - size + 1.0
    c.setFont(SERIF_I, size)
    c.setFillColor(INK_SOFT)
    for ln in lines:
        c.drawString(MARGIN_L + pad + 14.0, ty, ln)
        ty -= size + 3.0
    return y - height - 10.0


# ---------------------------------------------------------------------------
# form primitives - every one of these renders EMPTY
# ---------------------------------------------------------------------------

# A field occupies FIELD_H from the top of its row down to the rule; rows are
# spaced FIELD_H + FIELD_GAP apart. Callers pass the TOP of the row, never the
# rule, so a field row never backs into whatever sits above it.
FIELD_H = 17.0
FIELD_GAP = 15.0

# Widget names have to be unique: two widgets sharing a name in an AcroForm
# share a value, so the two "City" fields would fill in together.
_USED_NAMES = {}


def reset_field_names():
    _USED_NAMES.clear()


def _field_name(label):
    base = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_") or "field"
    _USED_NAMES[base] = _USED_NAMES.get(base, 0) + 1
    n = _USED_NAMES[base]
    return base if n == 1 else f"{base}_{n}"


def field(c, x, y, width, label, hint=None, fillable=True):
    """A blank entry field: small label, gold-tinted rule, and an empty widget.

    `y` is the top of the field; the rule lands at y - FIELD_H. The widget is
    created with no value, so the field opens blank in every reader.
    """
    rule_y = y - FIELD_H
    lw = tracked(c, x, y - 6.0, label.upper(), SERIF, 6.2, GRAY, 0.9)
    if hint:
        c.setFont(SERIF_I, 6.0)
        c.setFillColor(alpha(GRAY, 0.8))
        c.drawString(x + lw + 5.0, y - 6.0, hint)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.line(x, rule_y, x + width, rule_y)
    # gold tick at the left of every field rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(x, rule_y, x + 9.0, rule_y)

    if fillable:
        c.acroForm.textfield(
            name=_field_name(label), value="", x=x + 1.0, y=rule_y + 1.5,
            width=max(width - 2.0, 10.0), height=11.0,
            borderWidth=0, forceBorder=False, borderStyle="underlined",
            fillColor=None, textColor=INK, fontName=SERIF, fontSize=9,
            tooltip=f"{label}{' ' + hint if hint else ''}",
        )
    return rule_y


def field_row(c, y, specs, gap=12.0):
    """Lay a row of fields across the content width.

    specs: list of (label, hint_or_None, weight).  `y` is the top of the row;
    the returned value is the top of the next row.
    """
    total_weight = sum(s[2] for s in specs)
    avail = CONTENT_W - gap * (len(specs) - 1)
    x = MARGIN_L
    for label, hint, weight in specs:
        w = avail * weight / total_weight
        field(c, x, y, w, label, hint)
        x += w + gap
    return y - FIELD_H - FIELD_GAP


def checkbox(c, x, y, size=8.6, label=None, label_font=SERIF, label_size=8.4,
             label_color=INK, gap=6.0, fillable=True):
    """An unchecked box. The widget is created with checked=False."""
    # The box is drawn on the page so it always prints, and the widget sits on
    # top of it borderless - a viewer that ignores form fields still shows a
    # box to tick by hand.
    c.setStrokeColor(BRONZE)
    c.setLineWidth(0.8)
    c.rect(x, y, size, size, stroke=1, fill=0)
    if fillable:
        c.acroForm.checkbox(
            name=_field_name("cb_" + (label or "option")), checked=False,
            x=x, y=y, size=size, buttonStyle="check",
            borderColor=None, fillColor=None, textColor=ESPRESSO,
            borderWidth=0, tooltip=label or "",
        )
    if label:
        c.setFont(label_font, label_size)
        c.setFillColor(label_color)
        c.drawString(x + size + gap, y + 1.4, label)
        return x + size + gap + stringWidth(label, label_font, label_size)
    return x + size


def signature_row(c, y, name_label, date_label="Date", sig_label="Signature"):
    """Print-name / signature / date row, left blank. `y` is the row top."""
    gap = 14.0
    w_name = CONTENT_W * 0.40
    w_sig = CONTENT_W * 0.36
    w_date = CONTENT_W - w_name - w_sig - gap * 2

    field(c, MARGIN_L, y, w_name, name_label, "(Print or Type)")
    field(c, MARGIN_L + w_name + gap, y, w_sig, sig_label)
    field(c, MARGIN_L + w_name + w_sig + gap * 2, y, w_date, date_label, "(MM/DD/YYYY)")
    return y - FIELD_H - FIELD_GAP


def pin_boxes(c, x, y, count=4, size=14.0, gap=5.0, fillable=True):
    """Blank PIN boxes - one single-character widget per digit."""
    group = _field_name("pin")
    for i in range(count):
        bx = x + i * (size + gap)
        c.setStrokeColor(BRONZE)
        c.setLineWidth(0.8)
        c.rect(bx, y, size, size, stroke=1, fill=0)
        if fillable:
            c.acroForm.textfield(
                name=f"{group}_{i + 1}", value="", maxlen=1,
                x=bx + 1.0, y=y + 1.0, width=size - 2.0, height=size - 2.0,
                borderWidth=0, forceBorder=False, fillColor=None,
                textColor=INK, fontName=SERIF, fontSize=10,
                tooltip=f"PIN digit {i + 1}",
            )
    return x + count * (size + gap)


def body(c, y, text, size=8.4, leading=None, color=INK, font=SERIF,
         width=None, x=None, align="left"):
    """Plain wrapped body copy. Returns the new y cursor."""
    width = width or CONTENT_W
    x = MARGIN_L if x is None else x
    leading = leading or size + 3.2
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in wrap(text, font, size, width):
        if align == "center":
            c.drawCentredString(x + width / 2.0, y, ln)
        else:
            c.drawString(x, y, ln)
        y -= leading
    return y


def bullet(c, y, marker, text, x=None, width=None, size=8.4, leading=None,
           marker_w=18.0, color=INK, marker_color=BRONZE_DEEP,
           marker_font=SERIF_B):
    x = MARGIN_L if x is None else x
    width = width or (CONTENT_W - marker_w)
    leading = leading or size + 3.2
    c.setFont(marker_font, size)
    c.setFillColor(marker_color)
    c.drawString(x, y, marker)
    return body(c, y, text, size=size, leading=leading, color=color,
                width=width, x=x + marker_w)
