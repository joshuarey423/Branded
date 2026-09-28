"""The packet cover.

One page, mostly air: the apex carried large behind the type, the wordmark, the
document title, and the plain statement of who holds the assets. Nothing on it
is an input.
"""

import apex
from brand import (
    BRONZE_DEEP,
    CONTENT_W,
    CUSTODIAN_ADDRESS,
    CUSTODIAN_EMAIL,
    CUSTODIAN_PHONE,
    ESPRESSO,
    GOLD,
    GRAY,
    INK_SOFT,
    LOGO_ASPECT,
    MARGIN_L,
    MARGIN_R,
    PAGE_H,
    PAGE_W,
    RULE,
    SERIF,
    SERIF_B,
    SERIF_I,
    alpha,
)
from layout import LOGO, gradient_rule, hairline, tracked, tracked_width


def render(c):
    # The apex sits larger and a touch stronger here than on the body pages.
    apex.stamp(c, width=548.0, center_y=506.0, alpha=0.075)

    # --- wordmark, centred high on the page ---------------------------------
    logo_h = 40.0
    logo_w = logo_h * LOGO_ASPECT
    c.drawImage(LOGO, (PAGE_W - logo_w) / 2.0, PAGE_H - 150.0,
                width=logo_w, height=logo_h, mask="auto",
                preserveAspectRatio=True, anchor="sw")

    # --- title block --------------------------------------------------------
    y = PAGE_H - 268.0
    rule_w = 168.0
    gradient_rule(c, (PAGE_W - rule_w) / 2.0, y, rule_w, 1.0)

    y -= 40.0
    label = "SELF-DIRECTED INDIVIDUAL RETIREMENT ACCOUNT"
    w = tracked_width(label, SERIF, 9.0, 3.4)
    tracked(c, (PAGE_W - w) / 2.0, y, label, SERIF, 9.0, BRONZE_DEEP, 3.4)

    y -= 44.0
    title = "APPLICATION PACKET"
    w = tracked_width(title, SERIF, 27.0, 4.5)
    tracked(c, (PAGE_W - w) / 2.0, y, title, SERIF, 27.0, ESPRESSO, 4.5)

    y -= 30.0
    sub = "Traditional IRA  ·  Roth IRA"
    c.setFont(SERIF_I, 12.0)
    c.setFillColor(GRAY)
    c.drawCentredString(PAGE_W / 2.0, y, sub)

    y -= 34.0
    gradient_rule(c, (PAGE_W - rule_w) / 2.0, y, rule_w, 1.0)

    # --- what is inside -----------------------------------------------------
    y -= 90.0
    contents = [
        "Application Instructions",
        "Account Application",
        "Fee Schedule",
        "Traditional IRA Custodial Account Agreement  ·  Form 5305-A",
        "Traditional IRA Account Disclosure Statement",
        "Roth IRA Custodial Account Agreement  ·  Form 5305-RA",
        "Roth IRA Account Disclosure Statement",
    ]
    heading = "CONTENTS"
    w = tracked_width(heading, SERIF, 6.6, 2.4)
    tracked(c, (PAGE_W - w) / 2.0, y, heading, SERIF, 6.6, GOLD, 2.4)
    y -= 19.0
    c.setFont(SERIF, 8.6)
    c.setFillColor(INK_SOFT)
    for line in contents:
        c.drawCentredString(PAGE_W / 2.0, y, line)
        y -= 13.4

    # --- foot: who holds the assets ----------------------------------------
    foot = 96.0
    hairline(c, MARGIN_L + 96.0, foot + 42.0, CONTENT_W - 192.0,
             alpha(RULE, 0.9), 0.4)

    line = "Custodial services provided by Digital Trust, LLC"
    c.setFont(SERIF, 8.2)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(PAGE_W / 2.0, foot + 28.0, line)

    c.setFont(SERIF, 7.4)
    c.setFillColor(GRAY)
    c.drawCentredString(PAGE_W / 2.0, foot + 15.0, CUSTODIAN_ADDRESS)
    c.drawCentredString(PAGE_W / 2.0, foot + 4.0,
                        f"{CUSTODIAN_PHONE}   ·   {CUSTODIAN_EMAIL}")
