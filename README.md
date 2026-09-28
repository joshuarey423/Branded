# Fortuity Inc — Self-Directed IRA Application Packet

A Fortuity-branded rebuild of the Digital Trust *Self-Directed Traditional IRA •
Roth IRA* application packet, with every input field blank.

**Output:** [`out/Fortuity_Self-Directed_IRA_Packet.pdf`](out/Fortuity_Self-Directed_IRA_Packet.pdf) — 33 pages, US Letter.

```bash
pip install reportlab pillow
python3 src/build.py                      # writes out/Fortuity_Self-Directed_IRA_Packet.pdf
python3 src/build.py path/to/other.pdf    # or somewhere else
```

---

## Every field is blank

The source template had values already sitting in its form layer. This packet is
composed from content rather than edited in place, so there is nothing for a
stale value to survive in — each widget is created empty and each checkbox
`/Off`. Verified on the built file:

| check | result |
| --- | --- |
| text field widgets | 82, all with an empty value |
| checkbox widgets | 29, all `/Off` |
| duplicate widget names | none (a shared name would make two fields fill in together) |
| personal data in the page artwork | none — no name, SSN, DOB or email appears anywhere outside Digital Trust's own contact details |

The fields are live AcroForm widgets, so the packet is still fillable on screen,
and each box is also drawn on the page so it prints correctly in a viewer that
ignores form fields.

## Branding

Colours are sampled directly from `FortuityInc_Logo_4C Transparent.png` — the
wordmark is a gradient, so the palette is its endpoints and midpoint rather than
a guess:

| token | hex | sampled at |
| --- | --- | --- |
| `GOLD_LIGHT` | `#F7C589` | gradient start |
| `GOLD_MID` | `#DFAF7C` | 25% across |
| `GOLD` | `#C8996D` | midpoint — the primary brand gold |
| `BRONZE` | `#B5875F` | 75% across |
| `BRONZE_DEEP` | `#A47753` | gradient end |

Supporting neutrals (`ESPRESSO #3A2E24`, `INK #221E1A`, `WASH #FAF6F1`,
`WASH_GOLD #F6EADC`) are tuned to sit under the gold. All of them live in
`src/brand.py`.

The logo ships in two forms in `assets/`: the four-colour wordmark trimmed to its
artwork bounds, and a white knockout for the dark closing panel. Both are
transparent PNGs derived from the OneDrive original.

Headings are set in tracked-out Helvetica to echo the wordmark's letter-spacing.
Tracking goes through the PDF character-spacing operator rather than one draw
call per glyph, so headings stay selectable and searchable.

## Custodian naming

Digital Trust is still named as custodian throughout. That is deliberate: pages
7–33 are the IRS model custodial agreements (Form 5305-A for the Traditional
IRA, Form 5305-RA for the Roth) and the custodian is a party to them, so the
name cannot be swapped without changing what the document is. Fortuity carries
the packet's identity — logo, palette, page furniture, footer — and the footer
says plainly that custodial services are provided by Digital Trust. Say the word
if you want it white-labelled further and it is a small change in `src/brand.py`
plus the footer in `src/layout.py`.

## How the source was read

The OneDrive connector serves a PDF as its extracted text layer; the original
bytes are not reachable from here. So the packet was rebuilt from that text:

- **Pages 1–6** (instructions, the four-page application, fee schedule) are
  hand-composed in `src/front_pages.py`, because they are positional forms that
  no reflow would reproduce.
- **Pages 7–33** (both custodial agreements, both disclosure statements) are
  reassembled in `src/agreement_pages.py`: one source line per segment, put back
  together into paragraphs, numbered lists and run-in headings, then flowed.

The extractor hoists a page's headings into one clump and, on two pages, emits
an article out of sequence. Every page that needs it therefore has an explicit
content plan in `src/content_plan.py` mapping headings and segment ranges,
matched against the IRS model forms. A coverage check confirms no source segment
is dropped: the only uncovered segments are the hoisted headings and the table
cells, both of which are re-emitted from the plan.

The original runs 29 pages; this one runs 33 because the body text is set larger
and looser. Content is complete — the extra pages are breathing room, not
additions.

### Worth a second pair of eyes

**The fee schedule.** The text layer returns the fee amounts as one block,
separate from their labels, so the label↔amount pairing on page 6 is
reconstructed rather than read off. It is well supported — the account section's
13 labels and the transaction section's 24 labels each match their amount count
exactly, and footnote [3] ("$75 re-registration fee applies to each asset")
independently confirms the row it lands on, as do `$150/hour` on Legal Action
Fee and `$25/month` on Late Fee. Still: check page 6 against the original before
this goes to a client.

## Layout

| file | what it holds |
| --- | --- |
| `src/brand.py` | palette, type, page geometry, custodian details |
| `src/layout.py` | page chrome and the form primitives (fields, checkboxes, callouts) |
| `src/front_pages.py` | pages 1–6, hand-composed |
| `src/content_plan.py` | per-page content plans, the three IRS tables, section definitions |
| `src/agreement_pages.py` | reassembly and flow for the agreements and disclosures |
| `src/build.py` | assembles the packet |
| `src/source_pages.txt` | extracted source text, one line per original page |
| `assets/` | Fortuity wordmark, four-colour and knockout |
