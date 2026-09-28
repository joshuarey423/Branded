"""Where the source PDF's text layer needs help.

Extracting text from the original packet returns each page's body copy in
reading order, but hoists a page's section headings into one block (the
"ARTICLE V / ARTICLE VI / ARTICLE VII / ARTICLE VIII" clump at the top of
page 9 is typical) and, on two pages, emits an article out of sequence.

Rather than guess at run time, every page that needs it gets an explicit plan
below: an ordered list of headings and source segment ranges. Article bodies
were matched to their headings against the IRS model forms the agreements are
built on - Form 5305-A for the Traditional IRA and Form 5305-RA for the Roth.

Pages not listed here flow straight through in source order.
"""

# First content segment on each page. Pages that open a section carry a title
# block and contact line that the branded build re-renders itself, so they
# start later.
PAGE_START = {7: 8, 15: 6, 19: 8, 26: 6}
DEFAULT_START = 2

# ---------------------------------------------------------------------------
# Explicit plans. Items are ("h", text) headings, ("segs", first, last)
# inclusive source ranges, or ("table", key).
# ---------------------------------------------------------------------------
PAGE_PLANS = {
    # Traditional IRA custodial agreement - Form 5305-A front matter.
    7: [
        ("h", "PURPOSE OF THIS FORM"), ("segs", 8, 23),
        ("h", "DEFINITIONS"), ("segs", 29, 33),
        ("h", "TRADITIONAL IRA FOR NONWORKING SPOUSE"), ("segs", 34, 35),
        ("h", "SPECIFIC INSTRUCTIONS"), ("segs", 36, 44),
        ("h", "ARTICLE I"), ("segs", 45, 48),
    ],
    # Article II is emitted last by the extractor; 5305-A orders it II, III, IV.
    8: [
        ("h", "ARTICLE II"), ("segs", 76, 76),
        ("h", "ARTICLE III"), ("segs", 2, 7),
        ("h", "ARTICLE IV"), ("segs", 10, 74),
    ],
    9: [
        ("h", "ARTICLE V"), ("segs", 2, 6),
        ("h", "ARTICLE VI"), ("segs", 11, 12),
        ("h", "ARTICLE VII"), ("segs", 13, 14),
        ("h", "ARTICLE VIII"), ("segs", 15, 69),
    ],
    # Traditional IRA disclosure statement.
    15: [
        ("h", "PURPOSE OF THIS DISCLOSURE STATEMENT"), ("segs", 6, 12),
        ("h", "DISCLOSURES"), ("segs", 15, 78),
    ],
    16: [
        ("segs", 2, 2),
        ("table", "trad_deduction_covered"),
        ("segs", 28, 29),
        ("table", "trad_deduction_spouse"),
        ("segs", 57, 80),
    ],
    # Roth IRA custodial agreement - Form 5305-RA front matter.
    19: [
        ("h", "PURPOSE OF THIS FORM"), ("segs", 8, 24),
        ("h", "DEFINITIONS"), ("segs", 30, 34),
        ("h", "SPECIFIC INSTRUCTIONS"), ("segs", 35, 47),
        ("h", "ARTICLE I"), ("segs", 48, 50),
        ("h", "ARTICLE II"), ("segs", 51, 58),
    ],
    # All seven Roth articles are hoisted here, and III trails the clump.
    20: [
        ("h", "ARTICLE III"), ("segs", 2, 2),
        ("h", "ARTICLE IV"), ("segs", 10, 15),
        ("h", "ARTICLE V"), ("segs", 16, 31),
        ("h", "ARTICLE VI"), ("segs", 32, 36),
        ("h", "ARTICLE VII"), ("segs", 37, 38),
        ("h", "ARTICLE VIII"), ("segs", 39, 40),
        ("h", "ARTICLE IX"), ("segs", 41, 55),
    ],
    # Roth IRA disclosure statement.
    26: [
        ("h", "PURPOSE OF THIS DISCLOSURE STATEMENT"), ("segs", 6, 11),
        ("h", "DISCLOSURES"), ("segs", 12, 52),
        ("table", "roth_contribution"),
    ],
}

# ---------------------------------------------------------------------------
# The three IRS tables. The extractor returns these cell-by-cell with wrapped
# cells split across segments, so they are set out here as real rows.
# ---------------------------------------------------------------------------
TABLES = {
    "trad_deduction_covered": {
        "head": ["IF your tax filing status is ...",
                 "AND your modified AGI is ...",
                 "THEN you can take ..."],
        "rows": [
            ["single or head of household", "$66,000 or less", "a full deduction."],
            ["", "more than $66,000 but less than $76,000", "a partial deduction."],
            ["", "$76,000 or more", "no deduction."],
            ["married filing jointly or qualifying widow(er)", "$105,000 or less",
             "a full deduction."],
            ["", "more than $105,000 but less than $125,000", "a partial deduction."],
            ["", "$125,000 or more", "no deduction."],
            ["married filing separately^", "less than $10,000", "a partial deduction."],
            ["", "$10,000 or more", "no deduction."],
        ],
    },
    "trad_deduction_spouse": {
        "head": ["IF your filing status is ...",
                 "AND your modified AGI is ...",
                 "THEN you can take ..."],
        "rows": [
            ["Single, head of household, or qualifying widow(er)", "any amount",
             "a full deduction."],
            ["married filing jointly or separately with a spouse who isn’t covered "
             "by a plan at work", "any amount", "a full deduction."],
            ["married filing jointly with a spouse who is covered by a plan at work",
             "$198,000 or less", "a full deduction."],
            ["", "more than $198,000 but less than $208,000", "a partial deduction."],
            ["", "$208,000 or more", "no deduction."],
            ["married filing separately with a spouse who is covered by a plan at "
             "work. (You are entitled to the full deduction if you didn’t live with "
             "your spouse at any time during the year.)",
             "less than $10,000", "a partial deduction."],
            ["", "$10,000 or more", "no deduction."],
        ],
    },
    "roth_contribution": {
        "head": ["IF your filing status is ...",
                 "AND your modified AGI is ...",
                 "THEN you can take ..."],
        "rows": [
            ["married filing jointly or qualifying widow(er)", "less than $204,000",
             "up to the limit"],
            ["", "more than $204,000 but less than $214,000", "a reduced amount"],
            ["", "more than $214,000", "zero"],
            ["married filing separately and you lived with your spouse at any time "
             "during the year", "less than $10,000", "a reduced amount"],
            ["", "more than $10,000", "zero"],
            ["single, head of household, or married filing separately and you did not "
             "live with your spouse at any time during the year",
             "less than $129,000", "up to the limit"],
            ["", "more than $129,000 but less than $144,000", "a reduced amount"],
            ["", "more than $144,000", "zero"],
        ],
    },
}

# ---------------------------------------------------------------------------
# The four back-half sections.
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "key": "trad_agreement",
        "pages": range(7, 15),
        "title": "TRADITIONAL INDIVIDUAL RETIREMENT ACCOUNT",
        "subtitle": "Custodial Account Agreement",
        "meta": ["(Under section 408(a) of the Internal Revenue Code)",
                 "Form 5305-A (Revised April 2017)",
                 "Department of the Treasury – Internal Revenue Service"],
        "eyebrow": "FORTUITY INC",
        "header_title": "Traditional IRA Custodial Account Agreement",
        "header_sub": "Form 5305-A",
        "footer": "Traditional IRA — Custodial Account Agreement",
        "revision": "Rev 08.2022",
    },
    {
        "key": "trad_disclosure",
        "pages": range(15, 19),
        "title": "TRADITIONAL INDIVIDUAL RETIREMENT ACCOUNT",
        "subtitle": "Account Disclosure Statement",
        "meta": ["(Under section 408(a) of the Internal Revenue Code)"],
        "eyebrow": "FORTUITY INC",
        "header_title": "Traditional IRA Account Disclosure Statement",
        "header_sub": None,
        "footer": "Traditional IRA — Account Disclosure Statement",
        "revision": "Rev 06.2022",
    },
    {
        "key": "roth_agreement",
        "pages": range(19, 26),
        "title": "ROTH INDIVIDUAL RETIREMENT ACCOUNT",
        "subtitle": "Custodial Account Agreement",
        "meta": ["(Under section 408A of the Internal Revenue Code)",
                 "Form 5305-RA (Revised April 2017)",
                 "Department of the Treasury – Internal Revenue Service"],
        "eyebrow": "FORTUITY INC",
        "header_title": "Roth IRA Custodial Account Agreement",
        "header_sub": "Form 5305-RA",
        "footer": "Roth IRA — Custodial Account Agreement",
        "revision": "Rev 08.2022",
    },
    {
        "key": "roth_disclosure",
        "pages": range(26, 30),
        "title": "ROTH INDIVIDUAL RETIREMENT ACCOUNT",
        "subtitle": "Account Disclosure Statement",
        "meta": ["(Under section 408A of the Internal Revenue Code)"],
        "eyebrow": "FORTUITY INC",
        "header_title": "Roth IRA Account Disclosure Statement",
        "header_sub": None,
        "footer": "Roth IRA — Account Disclosure Statement",
        "revision": "Rev 05.2022",
    },
]
