"""Pages 1-6 of the packet: instructions, the 4-page application, fee schedule.

These are the pages that carry real layout in the source document, so they are
hand-composed rather than reflowed. Every input on them renders EMPTY - there
are no pre-filled values anywhere in this build.
"""

from reportlab.pdfbase.pdfmetrics import stringWidth

from brand import (
    BRONZE,
    BRONZE_DEEP,
    CONTENT_W,
    CUSTODIAN_ADDRESS,
    CUSTODIAN_EMAIL,
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
from layout import (
    body,
    bullet,
    callout,
    checkbox,
    contact_strip,
    field,
    field_row,
    gradient_rule,
    part_band,
    pin_boxes,
    section_head,
    signature_row,
    tracked,
    tracked_width,
    wrap,
)

TOP = PAGE_H - 88.0          # first page of a document: title block sits here
TOP_BAND = PAGE_H - 106.0    # continuation page opening with a PART band
TOP_CONT = PAGE_H - 92.0     # continuation page opening with a heading


def _doc_title(c, y, title, subtitle):
    tracked(c, MARGIN_L, y, title, SERIF_B, 17.0, ESPRESSO, 2.6)
    y -= 17.0
    tracked(c, MARGIN_L, y, subtitle, SERIF, 9.6, BRONZE_DEEP, 2.2)
    return y - 18.0


def _step_header(c, y, step, title):
    """STEP 1. OPEN YOUR ACCOUNT - numbered gold chip plus rule."""
    size = 19.0
    c.setFillColor(ESPRESSO)
    c.rect(MARGIN_L, y - 4.0, size, size, stroke=0, fill=1)
    c.setFont(SERIF_B, 10.0)
    c.setFillColor(GOLD_LIGHT)
    c.drawCentredString(MARGIN_L + size / 2.0, y + 1.5, str(step))

    x = MARGIN_L + size + 11.0
    w = tracked(c, x, y + 2.0, title, SERIF_B, 10.0, ESPRESSO, 2.0)
    gradient_rule(c, x + w + 10.0, y + 4.5, PAGE_W - MARGIN_R - x - w - 10.0,
                  0.7, c1=alpha(GOLD, 0.7), c2=alpha(BRONZE_DEEP, 0.3))
    return y - 19.0


def _check_item(c, y, text, sub=None, indent=0.0):
    x = MARGIN_L + 8.0 + indent
    checkbox(c, x, y - 2.0, 8.6)
    y2 = body(c, y, text, size=8.4, x=x + 16.0, width=CONTENT_W - 24.0 - indent)
    if sub:
        for s in sub:
            c.setFillColor(GOLD)
            c.circle(x + 23.0, y2 + 2.6, 1.3, stroke=0, fill=1)
            y2 = body(c, y2, s, size=7.6, color=GRAY, x=x + 29.0,
                      width=CONTENT_W - 40.0 - indent)
        y2 -= 2.0
    return y2 - 5.0


# ---------------------------------------------------------------------------
# PAGE 1 - APPLICATION INSTRUCTIONS
# ---------------------------------------------------------------------------

def page_instructions(c):
    y = _doc_title(c, TOP, "APPLICATION INSTRUCTIONS", "Traditional IRA  •  Roth IRA")
    contact_strip(c, y - 9.0)
    y -= 40.0

    y = body(c, y, "To ensure your account is established in a timely manner, verify "
                   "that the following items have been completed and submitted:",
             size=8.4, color=INK_SOFT)
    y -= 10.0

    y = _step_header(c, y, 1, "OPEN YOUR ACCOUNT")
    y -= 4.0
    tracked(c, MARGIN_L + 8.0, y, "ACCOUNT CHECKLIST", SERIF, 7.0, GRAY, 1.8)
    y -= 16.0
    for item in [
        "Self-Directed Account Application",
        "Copy of Valid Government-Issued Photo ID",
        "Review IRA Fee Schedule",
        "Review Account Disclosure Information",
    ]:
        y = _check_item(c, y, item)
        y -= 4.0
    y -= 12.0

    y = _step_header(c, y, 2, "FUND YOUR ACCOUNT")
    y -= 4.0
    y = body(c, y, "Once your account has been successfully established, fund your "
                   "account through one or more options:", size=8.2, color=GRAY)
    y -= 10.0
    y = _check_item(
        c, y, "New Contribution",
        ["See Deposit Submission Form or ACH Contribution Form"])
    y = _check_item(
        c, y, "IRA-to-IRA Transfer  (See IRA-to-IRA Transfer Request Form)",
        ["For Traditional IRAs: A direct movement of assets from a Traditional IRA "
         "or SEP IRA into a Traditional IRA",
         "For Roth IRAs: A direct movement of assets from a Roth IRA into a Roth IRA"])
    y = _check_item(
        c, y, "Eligible Rollover  (See IRA Rollover Certification Form)",
        ["For Traditional IRAs: A distribution from a Traditional IRA, SEP IRA, "
         "SIMPLE IRA or Employer-Sponsored Plan deposited into a Traditional IRA",
         "For Roth IRAs: A distribution from a Roth or Employer-Sponsored Plan "
         "deposited into a Roth IRA"])
    y -= 12.0

    y = _step_header(c, y, 3, "DIRECT YOUR INVESTMENT")
    y -= 4.0
    y = body(c, y, "After your account has been funded, contact Digital Trust to "
                   "discuss your Direction of Investment — we’ll work with you to "
                   "ensure all necessary documents are completed to process your "
                   "asset purchase.", size=8.4, color=INK_SOFT)

    # --- submit block, anchored above the footer ------------------------
    box_h = 82.0
    y = 132.0 + box_h
    c.setFillColor(WASH)
    c.rect(MARGIN_L, y - box_h, CONTENT_W, box_h, stroke=0, fill=1)
    gradient_rule(c, MARGIN_L, y - 2.0, CONTENT_W, 2.0)

    tx = MARGIN_L + 16.0
    ty = y - 22.0
    tracked(c, tx, ty, "SUBMIT YOUR APPLICATION", SERIF_B, 9.0, ESPRESSO, 2.0)
    ty -= 13.0
    c.setFont(SERIF_I, 8.0)
    c.setFillColor(GRAY)
    c.drawString(tx, ty, "Verify all completed information and submit your "
                         "application to Digital Trust.")

    col = MARGIN_L + CONTENT_W * 0.06
    ty2 = y - 53.0
    tracked(c, col, ty2, "VIA MAIL", SERIF, 6.6, BRONZE_DEEP, 1.8)
    c.setFont(SERIF, 8.0)
    c.setFillColor(INK)
    c.drawString(col, ty2 - 12.0, "Digital Trust")
    c.setFillColor(INK_SOFT)
    c.drawString(col, ty2 - 22.0, CUSTODIAN_ADDRESS)

    col2 = MARGIN_L + CONTENT_W * 0.62
    tracked(c, col2, ty2, "VIA EMAIL", SERIF, 6.6, BRONZE_DEEP, 1.8)
    c.setFont(SERIF, 8.0)
    c.setFillColor(INK)
    c.drawString(col2, ty2 - 12.0, CUSTODIAN_EMAIL)


# ---------------------------------------------------------------------------
# PAGE 2 - ACCOUNT APPLICATION 1 of 4
# ---------------------------------------------------------------------------

def page_application_1(c):
    y = _doc_title(c, TOP, "ACCOUNT APPLICATION", "Traditional IRA  •  Roth IRA")
    contact_strip(c, y - 9.0)
    y -= 42.0

    y = part_band(c, y - 8.0, "PART 1.", "ACCOUNT OWNER INFORMATION")
    y -= 4.0

    # account type election
    tracked(c, MARGIN_L, y, "TYPE OF ACCOUNT TO ESTABLISH", SERIF, 7.0, GRAY, 1.8)
    y -= 14.0
    x = checkbox(c, MARGIN_L, y, 9.0, "Traditional IRA", SERIF, 8.6)
    checkbox(c, x + 34.0, y, 9.0, "Roth IRA", SERIF, 8.6)
    y -= 16.0
    y = callout(c, y, "If no option is selected, this application will NOT be processed.")

    y = field_row(c, y, [("First Name", None, 34), ("M.I.", None, 9),
                         ("Last Name", None, 34), ("Suffix", None, 11),
                         ("Title", None, 12)])
    y = field_row(c, y, [("Social Security Number", "(###-##-####)", 34),
                         ("Date of Birth", "(MM/DD/YYYY)", 30),
                         ("Email Address", None, 36)])
    y = field_row(c, y, [("Legal Address", None, 100)])
    y = field_row(c, y, [("City", None, 44), ("State", None, 18), ("Zip", None, 20),
                         ("Primary Phone", None, 30), ("Type", None, 16)])
    y = field_row(c, y, [("Mailing Address", "(If different than above)", 100)])
    y = field_row(c, y, [("City", None, 44), ("State", None, 18), ("Zip", None, 20),
                         ("Alt Phone", None, 30), ("Type", None, 16)])

    # PIN
    y -= 8.0
    tracked(c, MARGIN_L, y, "PLEASE CREATE A 4-DIGIT PIN", SERIF, 7.0, GRAY, 1.8)
    pin_boxes(c, MARGIN_L + 132.0, y - 4.0)
    y -= 24.0
    y = callout(c, y, "PIN numbers should be kept confidential as they can be used "
                      "in place of verifying personal information.")

    y = part_band(c, y - 14.0, "PART 2.", "ACCOUNT SETUP")
    y -= 6.0
    y = body(c, y, "Choose your preferred method for paying the fees associated with "
                   "your account. Refer to your Fee Schedule for all fees applicable "
                   "to your account.", size=8.3, color=INK_SOFT)
    y -= 6.0
    checkbox(c, MARGIN_L, y - 1.0, 9.0,
             "Deduct the fees due from the cash available in my account.", SERIF, 8.6)
    y -= 15.0
    checkbox(c, MARGIN_L, y - 1.0, 9.0,
             "Deduct fees using a Credit or Debit Card.", SERIF, 8.6)
    y -= 17.0
    y = callout(c, y, "If this option is selected, you will receive a secure link "
                      "upon signing to provide your card information.")

    # funding & check titling
    y -= 12.0
    y = section_head(c, y, "FUNDING & CHECK TITLING", 7.6)
    y = body(c, y, "Please see the below example for correct check and asset titling "
                   "information. The account and assets must be titled in this way to "
                   "reflect your IRA being the legal owner of the investments and "
                   "assets. Incorrect titling may cause delays in processing your "
                   "request or taxable consequences. The correct titling should be as "
                   "follows:", size=7.9, color=GRAY)
    y -= 6.0

    box_h = 30.0
    c.setFillColor(WASH_GOLD)
    c.rect(MARGIN_L, y - box_h, CONTENT_W, box_h, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(MARGIN_L, y - box_h, 2.4, box_h, stroke=0, fill=1)
    c.setFont(SERIF_B, 9.4)
    c.setFillColor(ESPRESSO)
    c.drawString(MARGIN_L + 14.0, y - 14.0,
                 "“Digital Trust FBO: (Your Name) (Account Type)”")
    c.setFont(SERIF_I, 8.0)
    c.setFillColor(GRAY)
    c.drawString(MARGIN_L + 14.0, y - 26.0,
                 "Example:  Digital Trust FBO: Jane Doe Inherited Roth IRA")


# ---------------------------------------------------------------------------
# PAGE 3 - ACCOUNT APPLICATION 2 of 4
# ---------------------------------------------------------------------------

def _yes_no_row(c, y, question):
    """Question with blank Yes / No checkboxes. `y` is the top of the row."""
    right_edge = PAGE_W - MARGIN_R
    no_x = right_edge - 36.0
    yes_x = no_x - 46.0
    lines = wrap(question, SERIF, 8.4, yes_x - MARGIN_L - 16.0)

    ty = y - 10.0
    c.setFont(SERIF, 8.4)
    c.setFillColor(INK)
    for ln in lines:
        c.drawString(MARGIN_L, ty, ln)
        ty -= 11.0
    checkbox(c, yes_x, y - 12.0, 8.6, "Yes", SERIF, 8.4)
    checkbox(c, no_x, y - 12.0, 8.6, "No", SERIF, 8.4)

    bottom = min(ty + 11.0 - 6.0, y - 24.0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(MARGIN_L, bottom, right_edge, bottom)
    return bottom - 4.0


def _beneficiary_block(c, y, index):
    """One blank beneficiary block. `y` is the top of the block."""
    ty = y - 8.0
    tracked(c, MARGIN_L, ty, f"BENEFICIARY {index}.", SERIF_B, 8.2, BRONZE_DEEP, 1.6)
    x = MARGIN_L + 94.0
    x = checkbox(c, x, ty - 2.0, 8.6, "Primary Beneficiary", SERIF, 8.2)
    checkbox(c, x + 20.0, ty - 2.0, 8.6, "Contingent Beneficiary", SERIF, 8.2)
    c.setStrokeColor(alpha(GOLD, 0.5))
    c.setLineWidth(0.6)
    c.line(MARGIN_L, ty - 7.0, PAGE_W - MARGIN_R, ty - 7.0)
    y = ty - 13.0

    y = field_row(c, y, [("First Name or Trust/Charity Name", None, 50),
                         ("Last Name or Trust/Charity Type", None, 50)])
    y = field_row(c, y, [("SSN or EIN", None, 26),
                         ("Date of Birth or Trust Establishment Date", None, 40),
                         ("Relationship", None, 20), ("Share %", None, 14)])
    y = field_row(c, y, [("Address", None, 46), ("City", None, 24),
                         ("State", None, 14), ("Zip", None, 16)])
    return y - 2.0


def page_application_2(c):
    y = part_band(c, TOP_BAND, "PART 3.", "SPOUSAL CONSENT")
    y -= 4.0

    y = body(c, y, "Account owners who are married and live in the following states: "
                   "AK, AZ, CA, ID, LA, NV, NM, TX, WA, or WI are subject to the laws "
                   "of community property. Community property requires that the "
                   "married account owner list their spouse as the primary beneficiary "
                   "with a share percentage of 100%. Should the account owner choose to "
                   "list someone other than their spouse, spousal consent is required.",
             size=8.1, color=INK_SOFT)
    y -= 6.0
    y = body(c, y, "Please complete the questions below to determine if spousal "
                   "consent is required:", size=8.1, color=GRAY)
    y -= 12.0

    y = _yes_no_row(c, y, "Are you currently married?")
    y = _yes_no_row(c, y, "Do you reside in a community property state?  "
                          "(AK, AZ, CA, ID, LA, NV, NM, TX, WA, WI)")
    y = _yes_no_row(c, y, "Did you name someone other than your spouse as the primary "
                          "beneficiary with a share percentage of 100%?")
    y -= 4.0
    y = callout(c, y, "Spousal consent is required if you have answered “Yes” to all "
                      "of the questions listed above. If the answer to any of the "
                      "questions is “No,” spousal consent is not required.")

    y -= 10.0
    y = section_head(c, y, "CONSENT OF SPOUSE", 7.6)
    y = body(c, y, "I acknowledge that I am the spouse of the Account Owner. I "
                   "understand that as a spouse living in a community property state, "
                   "I may have a property interest in the account and a right to "
                   "relinquish my interest. I understand that I must provide consent "
                   "for the Account Owner to designate a beneficiary other than or in "
                   "addition to myself. I have been advised to consult a competent "
                   "legal or tax advisor prior to consenting to the beneficiary "
                   "designation below.", size=7.9, color=INK_SOFT)
    y -= 14.0
    y = signature_row(c, y, "Spouse Name", sig_label="Signature of Spouse")

    y = part_band(c, y - 16.0, "PART 4.", "BENEFICIARY DESIGNATION")
    y -= 4.0
    y = body(c, y, "Upon the death of the account owner, the assets held in this "
                   "account are to be paid to the beneficiaries listed below. The "
                   "distributions are as follows: individuals or entities listed as the "
                   "primary beneficiary will inherit first. Should the individuals or "
                   "entities listed as primary beneficiary predecease the account "
                   "owner, the assets will then be divided on a pro rata basis to the "
                   "remaining primary beneficiaries or go to the then listed contingent "
                   "beneficiaries if there is no primary beneficiary remaining. Should "
                   "all listed beneficiaries predecease the account owner or if no "
                   "beneficiaries are listed, the assets will be paid to the account "
                   "owner’s estate. If the account owner fails to list a share "
                   "percentage, the beneficiaries are deemed to all receive equal "
                   "shares. Account owners who are married and live in the following "
                   "states: AK, AZ, CA, ID, LA, NV, NM, TX, WA, or WI are subject to "
                   "the laws of community property requiring the account owner to list "
                   "their spouse as primary beneficiary with a share of 100% or obtain "
                   "spousal consent.", size=7.8, color=INK_SOFT)
    y -= 8.0
    checkbox(c, MARGIN_L, y - 1.0, 9.0,
             "I elect not to designate beneficiaries at this time and understand that "
             "I may designate beneficiaries at a later date.", SERIF, 8.4)
    y -= 18.0
    y = callout(c, y, "The total share percentage for primary beneficiaries must total "
                      "100% and the total share percentage for contingent beneficiaries "
                      "must total 100%. Partial percentages will not be accepted.")
    _beneficiary_block(c, y, 1)


# ---------------------------------------------------------------------------
# PAGE 4 - ACCOUNT APPLICATION 3 of 4
# ---------------------------------------------------------------------------

def page_application_3(c):
    y = TOP_CONT
    tracked(c, MARGIN_L, y, "PART 4.  BENEFICIARY DESIGNATION",
            SERIF_B, 8.6, BRONZE_DEEP, 1.8)
    tracked(c, PAGE_W - MARGIN_R - tracked_width("CONTINUED", SERIF, 7.0, 1.8),
            y, "CONTINUED", SERIF, 7.0, GRAY, 1.8)
    c.setStrokeColor(alpha(GOLD, 0.6))
    c.setLineWidth(0.7)
    c.line(MARGIN_L, y - 5.0, PAGE_W - MARGIN_R, y - 5.0)
    y -= 20.0

    for i in (2, 3, 4):
        y = _beneficiary_block(c, y, i)
        y -= 6.0

    y -= 6.0
    checkbox(c, MARGIN_L, y - 1.0, 9.0,
             "Check here if additional beneficiaries are listed on an attached "
             "addendum.", SERIF, 8.4)
    x = MARGIN_L + 318.0
    # the field rule lands on the checkbox baseline, so pass the row top
    field(c, x, y + 15.0, PAGE_W - MARGIN_R - x,
          "Total number of addendums attached")
    y -= 34.0

    y = part_band(c, y, "PART 5.", "ADDITIONAL AUTHORIZED INDIVIDUAL INFORMATION")
    y -= 4.0
    y = body(c, y, "Account owners may grant individuals or advisors permission to act "
                   "as agents on their account for the limited purpose of obtaining "
                   "information pertaining to their account. Digital Trust will not "
                   "take direction from authorized agents for purposes of directing "
                   "investments, disbursements of funds, or any other changes to the "
                   "client’s account. Digital Trust reserves the right to contact the "
                   "account owner regarding agent information requests.",
             size=7.2, leading=10.2, color=INK_SOFT)
    y -= 20.0

    y = field_row(c, y, [("Full Name", None, 40), ("Email", None, 36),
                         ("Phone", None, 24)])
    y = field_row(c, y, [("Address", None, 46), ("City", None, 24),
                         ("State", None, 14), ("Zip", None, 16)])

    y -= 8.0
    tracked(c, MARGIN_L, y, "PLEASE CREATE A 4-DIGIT PIN", SANS_B, 6.6, GRAY, 1.0)
    pin_boxes(c, MARGIN_L + 132.0, y - 4.0)
    y -= 26.0
    callout(c, y, "PIN numbers should be kept confidential as they can be used in "
                  "place of verifying personal information.")


# ---------------------------------------------------------------------------
# PAGE 5 - ACCOUNT APPLICATION 4 of 4
# ---------------------------------------------------------------------------

def page_application_4(c):
    y = part_band(c, TOP_BAND, "PART 6.", "ACCOUNT OWNER AUTHORIZATION")
    y -= 10.0

    tracked(c, MARGIN_L, y, "IMPORTANT: PLEASE READ BEFORE SIGNING.",
            SERIF_B, 9.6, ESPRESSO, 1.8)
    y -= 24.0

    y = section_head(c, y, "USA PATRIOT ACT", 7.6)
    y = body(c, y, "To cooperate with the US Government’s efforts to combat the "
                   "funding of terrorism and money laundering activities, Federal Law "
                   "requires all financial institutions to obtain, verify, and record "
                   "the identity of each individual who opens an account. Accordingly, "
                   "when you open an account, we will request your name, address, date "
                   "of birth, a copy of your driver’s license or passport, and other "
                   "information that will help us to identify you.",
             size=8.5, leading=12.0, color=INK_SOFT)
    y -= 24.0

    checkbox(c, MARGIN_L, y - 1.0, 9.0,
             "I have reviewed the Digital Trust Fee Schedule.", SERIF, 9.0)
    y -= 20.0
    checkbox(c, MARGIN_L, y - 1.0, 9.0,
             "I have reviewed the Digital Trust disclosures associated with opening "
             "this account.", SERIF, 9.0)
    y -= 30.0

    y = body(c, y, "By signing below, I certify that all information provided in this "
                   "Application is true and accurate. I understand the terms and "
                   "conditions that apply to this account and agree to be bound by "
                   "them.", size=8.8, leading=12.4, color=INK)
    y -= 30.0
    y = signature_row(c, y, "IRA Owner Name", sig_label="Signature of IRA Owner")

    # closing brand block, anchored above the footer
    box_h = 58.0
    y = 96.0 + box_h
    c.setFillColor(ESPRESSO)
    c.rect(MARGIN_L, y - box_h, CONTENT_W, box_h, stroke=0, fill=1)
    gradient_rule(c, MARGIN_L, y - 2.0, CONTENT_W, 2.0)
    from layout import LOGO_KO
    from brand import LOGO_ASPECT
    lh = 20.0
    c.drawImage(LOGO_KO, MARGIN_L + 16.0, y - 34.0, width=lh * LOGO_ASPECT,
                height=lh, mask="auto", preserveAspectRatio=True, anchor="sw")
    c.setFont(SERIF, 7.6)
    c.setFillColor(alpha(WHITE, 0.8))
    c.drawString(MARGIN_L + 16.0, y - 46.0,
                 "Submit to  " + CUSTODIAN_EMAIL + "   or   " + CUSTODIAN_ADDRESS)


# ---------------------------------------------------------------------------
# PAGE 6 - FEE SCHEDULE
# ---------------------------------------------------------------------------

ACCOUNT_FEES = [
    ("row", "Traditional IRA & Roth IRA", "$375"),
    ("sub", "Per Additional Asset [1]", "$75"),
    ("row", "SEP IRA & SIMPLE IRA", "$475"),
    ("sub", "Additional Participant", "$75"),
    ("sub", "Per Additional Asset [1]", "$75"),
    ("row", "Inherited Traditional IRA & Inherited Roth IRA", "$375"),
    ("sub", "Full Distribution (No Account Setup)", "$250"),
    ("row", "Individual 401(k) Plan", "$475"),
    ("sub", "Additional Participant", "$150"),
    ("sub", "Per Additional Asset [1]", "$75"),
    ("group", "Custodial Accounts", None),
    ("row", "Qualified Funds Account", "$375"),
    ("row", "Non-Qualified Funds Account", "$375"),
]

TRANSACTION_FEES = [
    ("Outgoing Domestic Wire", "$35"),
    ("Outgoing International Wire", "$50"),
    ("Check", "$35"),
    ("Cashier’s Check", "$50"),
    ("ACH", "$35"),
    ("Stop Payment, Return Check/Wire", "$50"),
    ("Credit Card Declined, Chargeback", "$50"),
    ("Duplicate Page Statements", "$30"),
    ("EIN Creation", "$25"),
    ("Loan Setup Fee  (Individual 401(k) Plans Only)", "$225"),
    ("Loan Default Fee  (Individual 401(k) Plans Only)", "$150"),
    ("Plan Amendment  (Individual 401(k) Plans Only)", "$150"),
    ("Next-Day Processing  (Within 24 hours)", "$100"),
    ("Same-Day Processing  (Received by 10AM)", "$250"),
    ("Medallion Stamp", "$35"),
    ("Overnight Mail", "$35"),
    ("Roth Conversion or Recharacterization [2]", "$100"),
    ("Re-Registration  (Per Asset) [3]", "$75"),
    ("IRS Form Facilitation / Preparation Fee", "$100/each"),
    ("Legal Action Fee [4]", "$150/hour"),
    ("Corrective Reporting Fee", "$250/each"),
    ("Late Fee", "$25/month"),
    ("Partial Termination  (50% or more of Account)", "$150"),
    ("Complete Termination", "$300"),
]

ASSET_FEES = [
    ("group", "Crypto Assets", None),
    ("row", "Setup Fee  (Collected from all fund deposits)", "5.99%"),
    ("row", "Trading Fee  (Buy/Sell)", "2.0%"),
    ("row", "Annual Fee  (Billed monthly)", "0.08%"),
    ("row", "In-Kind Transfer Out", "1.0%"),
    ("group", "Other Assets", None),
    ("row", "Real Estate  (Buy / Sell)", "$150"),
    ("row", "Precious Metals  (Buy / Sell)", "$50"),
]


def _fee_rows(c, y, rows, x, width, size=7.7):
    for kind, label, amount in rows:
        if kind == "group":
            y -= 4.0
            tracked(c, x, y, label.upper(), SERIF, 6.8, BRONZE_DEEP, 1.6)
            y -= 12.0
            continue
        indent = 11.0 if kind == "sub" else 0.0
        c.setFont(SERIF_I if kind == "sub" else SERIF, size)
        c.setFillColor(GRAY if kind == "sub" else INK)
        c.drawString(x + indent, y, label)
        c.setFont(SERIF_B, size)
        c.setFillColor(ESPRESSO)
        c.drawRightString(x + width, y, amount)
        c.setStrokeColor(alpha(RULE, 0.8))
        c.setLineWidth(0.4)
        c.line(x + indent, y - 3.8, x + width, y - 3.8)
        y -= 13.0
    return y


def page_fee_schedule(c):
    y = _doc_title(c, TOP, "FEE SCHEDULE", "Self-Directed Retirement Accounts")
    contact_strip(c, y - 9.0)
    y -= 40.0

    gap = 22.0
    colw = (CONTENT_W - gap) / 2.0
    left_x, right_x = MARGIN_L, MARGIN_L + colw + gap

    # --- left column: account fees + asset purchase fees ---------------
    ly = y
    c.setFillColor(ESPRESSO)
    c.rect(left_x, ly - 4.0, colw, 17.0, stroke=0, fill=1)
    tracked(c, left_x + 9.0, ly + 1.5, "ACCOUNT FEES", SERIF_B, 8.0, GOLD_LIGHT, 2.0)
    ly -= 27.0

    c.setFont(SERIF, 7.7)
    c.setFillColor(INK)
    c.drawString(left_x, ly, "Setup Fee  (One-Time)")
    c.setFont(SERIF_B, 7.7)
    c.setFillColor(ESPRESSO)
    c.drawRightString(left_x + colw, ly, "$50")
    c.setStrokeColor(alpha(GOLD, 0.7))
    c.setLineWidth(0.6)
    c.line(left_x, ly - 3.8, left_x + colw, ly - 3.8)
    ly -= 17.0

    tracked(c, left_x, ly, "ANNUAL FEE", SERIF, 6.8, GRAY, 1.6)
    ly -= 13.0
    ly = _fee_rows(c, ly, ACCOUNT_FEES, left_x, colw)

    ly -= 12.0
    c.setFillColor(ESPRESSO)
    c.rect(left_x, ly - 4.0, colw, 17.0, stroke=0, fill=1)
    tracked(c, left_x + 9.0, ly + 1.5, "ASSET PURCHASE FEES", SERIF_B, 8.0,
            GOLD_LIGHT, 2.0)
    ly -= 27.0
    ly = _fee_rows(c, ly, ASSET_FEES, left_x, colw)

    # --- right column: transaction fees --------------------------------
    ry = y
    c.setFillColor(ESPRESSO)
    c.rect(right_x, ry - 4.0, colw, 17.0, stroke=0, fill=1)
    tracked(c, right_x + 9.0, ry + 1.5, "TRANSACTION FEES", SERIF_B, 8.0,
            GOLD_LIGHT, 2.0)
    ry -= 27.0
    ry = _fee_rows(c, ry, [("row", a, b) for a, b in TRANSACTION_FEES],
                   right_x, colw)

    # --- footnotes ------------------------------------------------------
    fy = min(ly, ry) - 10.0
    fy = max(fy, 96.0)
    c.setFillColor(WASH)
    notes = [
        "Fees are subject to change with written notice. The annual fee is invoiced "
        "in the anniversary month each year.",
        "[1] If you are signed up on a platform, the platform will count as one asset "
        "for account fee purposes.",
        "[2] Recharacterizations may only be in cash. Roth conversions may not be "
        "recharacterized.",
        "[3] Any re-registration fees charged by third-parties will be additionally "
        "assessed. $75 re-registration fee applies to each asset.",
        "[4] Relating to production of documents related to subpoena or legal action.",
    ]
    lines = []
    for n in notes:
        lines.extend(wrap(n, SERIF, 6.8, CONTENT_W - 24.0))
    box_h = len(lines) * 8.8 + 18.0
    c.rect(MARGIN_L, fy - box_h, CONTENT_W, box_h, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(MARGIN_L, fy - box_h, 2.4, box_h, stroke=0, fill=1)
    ty = fy - 14.0
    c.setFont(SERIF, 6.8)
    c.setFillColor(GRAY)
    for ln in lines:
        c.drawString(MARGIN_L + 14.0, ty, ln)
        ty -= 8.8
