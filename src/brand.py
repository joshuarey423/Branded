"""Fortuity Inc brand tokens, sampled from FortuityInc_Logo_4C Transparent.png.

The wordmark is a left-to-right gradient that runs from a light champagne gold
into a deep bronze. Those two endpoints, plus the midpoint, are the palette the
rest of the packet is built from.
"""

from reportlab.lib.colors import Color, HexColor

# --- Logo gradient, sampled across the wordmark -------------------------------
GOLD_LIGHT = HexColor("#F7C589")   # gradient start  (top-left of the mark)
GOLD_MID = HexColor("#DFAF7C")     # 25% across
GOLD = HexColor("#C8996D")         # 50% across - the primary brand gold
BRONZE = HexColor("#B5875F")       # 75% across
BRONZE_DEEP = HexColor("#A47753")  # gradient end   (bottom-right of the mark)

# --- Supporting neutrals, tuned to sit under the gold -------------------------
INK = HexColor("#221E1A")          # body copy
INK_SOFT = HexColor("#4A433C")     # secondary copy
GRAY = HexColor("#6E655C")         # field labels, metadata
RULE = HexColor("#DCD2C6")         # hairlines and field underlines
WASH = HexColor("#FAF6F1")         # section wash
WASH_GOLD = HexColor("#F6EADC")    # callout wash
ESPRESSO = HexColor("#3A2E24")     # dark band behind knockout logo
WHITE = HexColor("#FFFFFF")

# --- Type ---------------------------------------------------------------------
# Times throughout. The old names are kept so the rest of the packet did not
# have to be rewritten around the change; they now point at the serif faces.
SERIF = "Times-Roman"
SERIF_B = "Times-Bold"
SERIF_I = "Times-Italic"
SERIF_BI = "Times-BoldItalic"

SANS = SERIF
SANS_B = SERIF_B
SANS_O = SERIF_I
SANS_BO = SERIF_BI

# Times carries a smaller x-height than Helvetica, so every size steps up and
# leading opens out to keep the page comfortable rather than cramped.
BODY = 8.6
BODY_LEAD = 11.6
SMALL = 7.4
LABEL = 6.8
MICRO = 6.2

# --- Page geometry ------------------------------------------------------------
PAGE_W, PAGE_H = 612.0, 792.0      # US Letter
MARGIN_L = 54.0
MARGIN_R = 54.0
HEADER_H = 74.0
FOOTER_H = 44.0
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R
CONTENT_TOP = PAGE_H - HEADER_H
CONTENT_BOTTOM = FOOTER_H

LOGO_ASPECT = 2414.0 / 552.0       # trimmed wordmark

# --- Fixed contact block ------------------------------------------------------
# Digital Trust remains the named custodian throughout: the custodial agreements
# are IRS model forms (5305-A / 5305-RA) and the custodian is a party to them.
CUSTODIAN_NAME = "Digital Trust"
CUSTODIAN_PHONE = "(800) 777-9878"
CUSTODIAN_FAX = "(800) 867-7668"
CUSTODIAN_EMAIL = "operations@digitaltrust.com"
CUSTODIAN_ADDRESS = "7336 W. Post Rd., Suite 111, Las Vegas, NV 89113"

PRESENTER_NAME = "Fortuity Inc"

# --- Apex watermark -----------------------------------------------------------
# The nested-delta mark sits behind the type on every page. Kept faint enough
# that it never competes with the body copy, large enough to read as a
# deliberate ground rather than a stamp.
WATERMARK_WIDTH = 470.0      # points, on a 612pt page
WATERMARK_ALPHA = 0.048
WATERMARK_CENTER_Y = 372.0   # a shade below the optical centre of the block


def alpha(color: Color, a: float) -> Color:
    """Same hue, reduced opacity - used for gradient fades and tint bands."""
    return Color(color.red, color.green, color.blue, alpha=a)


def mix(c1: Color, c2: Color, t: float) -> Color:
    """Linear blend between two brand colors; t=0 returns c1, t=1 returns c2."""
    return Color(
        c1.red + (c2.red - c1.red) * t,
        c1.green + (c2.green - c1.green) * t,
        c1.blue + (c2.blue - c1.blue) * t,
    )
