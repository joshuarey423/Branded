"""Build the Fortuity-branded Self-Directed IRA application packet.

    python3 src/build.py [out/Fortuity_Self-Directed_IRA_Packet.pdf]

Every field in the output is blank by construction: the packet is composed from
text content, not from the source PDF's form layer, so no pre-filled value can
survive into it.
"""

import os
import sys

from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agreement_pages  # noqa: E402
import apex  # noqa: E402
import cover  # noqa: E402
import front_pages  # noqa: E402
from brand import PAGE_H, PAGE_W  # noqa: E402
from layout import footer, header  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "out", "Fortuity_Self-Directed_IRA_Packet.pdf")

# (eyebrow, title, section label for the footer, revision)
FRONT_CHROME = [
    ("FORTUITY INC", "Application Instructions", "Application Instructions", "Rev 05.2022"),
    ("FORTUITY INC", "Account Application", "Account Application  —  1 of 4", "Rev 05.2022"),
    ("FORTUITY INC", "Account Application", "Account Application  —  2 of 4", "Rev 05.2022"),
    ("FORTUITY INC", "Account Application", "Account Application  —  3 of 4", "Rev 05.2022"),
    ("FORTUITY INC", "Account Application", "Account Application  —  4 of 4", "Rev 05.2022"),
    ("FORTUITY INC", "Fee Schedule", "Fee Schedule  —  Self-Directed Retirement Accounts", "Rev 03.2023"),
]

FRONT_SUBTITLE = [
    "Traditional IRA • Roth IRA",
    "Traditional IRA • Roth IRA",
    "Traditional IRA • Roth IRA",
    "Traditional IRA • Roth IRA",
    "Traditional IRA • Roth IRA",
    "Self-Directed Retirement Accounts",
]

FRONT_RENDERERS = [
    front_pages.page_instructions,
    front_pages.page_application_1,
    front_pages.page_application_2,
    front_pages.page_application_3,
    front_pages.page_application_4,
    front_pages.page_fee_schedule,
]


def build(out_path=DEFAULT_OUT):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Fortuity Inc — Self-Directed IRA Application Packet")
    c.setAuthor("Fortuity Inc")
    c.setSubject("Traditional IRA • Roth IRA — application, fee schedule, "
                 "custodial agreements and disclosures")

    # the watermark is defined once and stamped per page, so the outline costs
    # a few KB rather than repeating on all 30-odd pages
    apex.register(c)

    back = agreement_pages.build_back_pages()
    total = len(FRONT_RENDERERS) + len(back)

    cover.render(c)
    c.showPage()

    page_no = 0
    for i, render in enumerate(FRONT_RENDERERS):
        page_no += 1
        apex.stamp(c)
        eyebrow, title, section, rev = FRONT_CHROME[i]
        header(c, eyebrow, title, FRONT_SUBTITLE[i])
        render(c)
        footer(c, page_no, total, section, rev)
        c.showPage()

    for page in back:
        page_no += 1
        apex.stamp(c)
        header(c, page.eyebrow, page.title, page.subtitle)
        page.render(c)
        footer(c, page_no, total, page.section, page.revision)
        c.showPage()

    c.save()
    return out_path, total


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    path, total = build(out)
    print(f"wrote {path}  ({total} pages)")
