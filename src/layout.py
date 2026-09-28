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


def header(c, eyebrow, title, subtitle=None):
    """Logo left, document title right, gold gradient hairline underneath."""
    logo_h = 26.0
    logo_w = logo_h * LOGO_ASPECT
    top = PAGE_H - 30.0
    c.drawImage(
        LOGO, MARGIN_L, top - logo_h, width=logo_w, height=logo_h,
        mask="auto", preserveAspectRatio=True, anchor="sw",
    )

    right = PAGE_W - MARGIN_R
    if eyebrow:
        w = tracked_width(eyebrow, SANS_B, 6.2, 1.5)
        tracked(c, right - w, top - 8.0, eyebrow, SANS_B, 6.2, GOLD, 1.5)
    if title:
        w = tracked_width(title, SANS, 8.4, 0.7)
        tracked(c, right - w, top - 20.0, title, SANS, 8.4, INK_SOFT, 0.7)
    if subtitle:
        w = stringWidth(subtitle, SANS, 7.0)
        c.setFont(SANS, 7.0)
        c.setFillColor(GRAY)
        c.drawString(right - w, top - 30.0, subtitle)

    gradient_rule(c, MARGIN_L, PAGE_H - 70.0, CONTENT_W, 1.6)


def footer(c, page_no, page_total, section_label, revision):
    y = 30.0
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(MARGIN_L, y + 13.0, PAGE_W - MARGIN_R, y + 13.0)

    c.setFont(SANS, 6.4)
    c.setFillColor(GRAY)
    c.drawString(MARGIN_L, y + 3.0, f"{section_label}  •  {revision}")

    right = PAGE_W - MARGIN_R
    label = f"Page {page_no} of {page_total}"
    c.setFont(SANS_B, 6.4)
    c.setFillColor(BRONZE_DEEP)
    c.drawRightString(right, y + 3.0, label)

    c.setFont(SANS, 6.0)
    c.setFillColor(GRAY)
    c.drawCentredString(PAGE_W / 2.0, y - 7.0,
                        "Fortuity Inc  •  Custodial services provided by Digital Trust")


def contact_strip(c, y):
    """Custodian contact line used on the cover-style pages."""
    from brand import CUSTODIAN_EMAIL, CUSTODIAN_FAX, CUSTODIAN_PHONE

    c.setFillColor(WASH)
    c.rect(MARGIN_L, y, CONTENT_W, 18.0, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(MARGIN_L, y, 2.4, 18.0, stroke=0, fill=1)
    c.setFont(SANS, 7.2)
    c.setFillColor(INK_SOFT)
    c.drawString(MARGIN_L + 12.0, y + 6.2,
                 f"Phone  {CUSTODIAN_PHONE}      Fax  {CUSTODIAN_FAX}      "
                 f"Email  {CUSTODIAN_EMAIL}")
    return y


# ---------------------------------------------------------------------------
# section furniture
# ---------------------------------------------------------------------------

def part_band(c, y, number, title, height=19.0):
    """PART 1. ACCOUNT OWNER INFORMATION - espresso band with gold cap."""
    c.setFillColor(ESPRESSO)
    c.rect(MARGIN_L, y, CONTENT_W, height, stroke=0, fill=1)
    gradient_rule(c, MARGIN_L, y + height - 2.0, CONTENT_W, 2.0)

    x = MARGIN_L + 11.0
    if number:
        w = tracked(c, x, y + 6.2, number, SANS_B, 8.0, GOLD_LIGHT, 1.0)
        x += w + 9.0
    tracked(c, x, y + 6.2, title, SANS_B, 8.0, WHITE, 1.4)
    return y - 10.0


def section_head(c, y, title, size=9.0):
    """Lighter heading used inside the agreements and disclosures."""
    tracked(c, MARGIN_L, y, title, SANS_B, size, BRONZE_DEEP, 1.1)
    c.setStrokeColor(alpha(GOLD, 0.55))
    c.setLineWidth(0.7)
    c.line(MARGIN_L, y - 4.5, PAGE_W - MARGIN_R, y - 4.5)
    return y - 14.0


def callout(c, y, text, width=None, pad=8.0, size=7.0):
    """The '!' notes from the source form, restyled as a gold-wash box."""
    width = width or CONTENT_W
    inner = width - pad * 2 - 14.0
    lines = wrap(text, SANS_O, size, inner)
    height = pad * 2 + len(lines) * (size + 2.0) - 2.0

    c.setFillColor(WASH_GOLD)
    c.rect(MARGIN_L, y - height, width, height, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(MARGIN_L, y - height, 2.4, height, stroke=0, fill=1)

    c.setFont(SANS_B, 9.0)
    c.setFillColor(BRONZE_DEEP)
    c.drawString(MARGIN_L + pad + 1.0, y - pad - size + 0.5, "!")

    ty = y - pad - size + 1.0
    c.setFont(SANS_O, size)
    c.setFillColor(INK_SOFT)
    for ln in lines:
        c.drawString(MARGIN_L + pad + 12.0, ty, ln)
        ty -= size + 2.0
    return y - height - 8.0


# ---------------------------------------------------------------------------
# form primitives - every one of these renders EMPTY
# ---------------------------------------------------------------------------

# A field occupies FIELD_H from the top of its row down to the rule; rows are
# spaced FIELD_H + FIELD_GAP apart. Callers pass the TOP of the row, never the
# rule, so a field row never backs into whatever sits above it.
FIELD_H = 16.0
FIELD_GAP = 13.0

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
    c.setFont(SANS, 6.2)
    c.setFillColor(GRAY)
    c.drawString(x, y - 6.0, label.upper())
    if hint:
        c.setFont(SANS_O, 5.6)
        c.setFillColor(alpha(GRAY, 0.75))
        c.drawString(x + stringWidth(label.upper(), SANS, 6.2) + 4.0,
                     y - 6.0, hint)
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
            fillColor=None, textColor=INK, fontName=SANS, fontSize=8,
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


def checkbox(c, x, y, size=8.0, label=None, label_font=SANS, label_size=7.4,
             label_color=INK, gap=5.0, fillable=True):
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


def pin_boxes(c, x, y, count=4, size=13.0, gap=4.0, fillable=True):
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
                textColor=INK, fontName=SANS, fontSize=9,
                tooltip=f"PIN digit {i + 1}",
            )
    return x + count * (size + gap)


def body(c, y, text, size=7.4, leading=None, color=INK, font=SANS,
         width=None, x=None, align="left"):
    """Plain wrapped body copy. Returns the new y cursor."""
    width = width or CONTENT_W
    x = MARGIN_L if x is None else x
    leading = leading or size + 2.6
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in wrap(text, font, size, width):
        if align == "center":
            c.drawCentredString(x + width / 2.0, y, ln)
        else:
            c.drawString(x, y, ln)
        y -= leading
    return y


def bullet(c, y, marker, text, x=None, width=None, size=7.4, leading=None,
           marker_w=16.0, color=INK, marker_color=BRONZE_DEEP,
           marker_font=SANS_B):
    x = MARGIN_L if x is None else x
    width = width or (CONTENT_W - marker_w)
    leading = leading or size + 2.6
    c.setFont(marker_font, size)
    c.setFillColor(marker_color)
    c.drawString(x, y, marker)
    return body(c, y, text, size=size, leading=leading, color=color,
                width=width, x=x + marker_w)
