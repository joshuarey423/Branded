# Fortuity Inc — Self-Directed IRA Application Packet

A Fortuity-branded rebuild of the Digital Trust *Self-Directed Traditional IRA •
Roth IRA* application packet: set in Times, carried on the apex triangle, with
every input field blank.

**Output:** [`out/Fortuity_Self-Directed_IRA_Packet.pdf`](out/Fortuity_Self-Directed_IRA_Packet.pdf) — cover plus 41 numbered pages, US Letter.

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

## The apex watermark

The nested-delta mark sits behind the type on every page, and larger and a
shade stronger on the cover.

It ships as a 914 × 661 PNG — fine on screen, soft blown up to seven inches —
so `tools/trace_apex.py` traces it once into vector outlines
(`src/apex_path.py`). That keeps the edges crisp at any size and costs a few
kilobytes instead of a bitmap on every page. The outline is registered as a
single PDF form and stamped per page, then filled through a clip with a vertical
gold ramp that runs light at the apex into bronze at the base.

Body pages carry it at 470pt wide and 4.8% opacity; the cover at 548pt and
7.5%. Both live in `src/brand.py` if you want it louder or quieter — it is one
number.

To re-trace after a logo revision:

```bash
pip install potracer numpy pillow
python3 tools/trace_apex.py fortuity_triangle_4C_transparent.png src/apex_path.py
```

## Type

Times throughout — `Times-Roman`, `Times-Bold`, `Times-Italic` — with headings
tracked out to echo the wordmark's letter-spacing. Tracking goes through the PDF
character-spacing operator rather than one draw call per glyph, so headings stay
selectable and searchable.

Times carries a smaller x-height than the sans it replaced, so every size steps
up and the leading opens out: body copy is 8.4pt on 11.4, which is why the
packet runs longer than the 29-page original. The content is complete — the
extra pages are breathing room, not additions.

## Colour

Sampled directly from `FortuityInc_Logo_4C Transparent.png`. The wordmark is a
gradient, so the palette is its endpoints and midpoint rather than a guess:

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

Pages stay white rather than taking a paper tint: this is a form that gets
printed and signed, and a full-bleed background is a liability on a print
driver.

The logo ships in two forms in `assets/`: the four-colour wordmark trimmed to
its artwork bounds, and a white knockout for the dark closing panel.

## Custodian naming

Digital Trust is still named as custodian throughout. That is deliberate: the
back half is the IRS model custodial agreements (Form 5305-A for the Traditional
IRA, Form 5305-RA for the Roth) and the custodian is a party to them, so the
name cannot be swapped without changing what the document is. Fortuity carries
the packet's identity — logo, palette, page furniture, footer — and the footer
says plainly that custodial services are provided by Digital Trust. Say the word
if you want it white-labelled further and it is a small change in `src/brand.py`
plus the footer in `src/layout.py`.

## How the source was read

The OneDrive connector serves a PDF as its extracted text layer; the original
bytes are not reachable from here. So the packet was rebuilt from that text:

- **The instructions, four-page application and fee schedule** are
  hand-composed in `src/front_pages.py`, because they are positional forms that
  no reflow would reproduce.
- **Both custodial agreements and both disclosure statements** are reassembled
  in `src/agreement_pages.py`: one source line per segment, put back together
  into paragraphs, numbered lists and run-in headings, then flowed.

The extractor hoists a page's headings into one clump and, on two pages, emits
an article out of sequence. Every page that needs it therefore has an explicit
content plan in `src/content_plan.py` mapping headings and segment ranges,
matched against the IRS model forms. A coverage check confirms no source segment
is dropped: the only uncovered segments are the hoisted headings and the table
cells, both of which are re-emitted from the plan.

### Worth a second pair of eyes

**The fee schedule.** The text layer returns the fee amounts as one block,
separate from their labels, so the label↔amount pairing on the fee schedule is
reconstructed rather than read off. It is well supported — the account section's
13 labels and the transaction section's 24 labels each match their amount count
exactly, and footnote [3] ("$75 re-registration fee applies to each asset")
independently confirms the row it lands on, as do `$150/hour` on Legal Action
Fee and `$25/month` on Late Fee. Still: check that page against the original
before this goes to a client.

## Layout

| file | what it holds |
| --- | --- |
| `src/brand.py` | palette, type scale, page geometry, watermark settings, custodian details |
| `src/apex.py` | the apex watermark and the small section glyph |
| `src/apex_path.py` | generated vector outline — do not hand-edit |
| `src/layout.py` | page chrome and the form primitives (fields, checkboxes, callouts) |
| `src/cover.py` | the cover |
| `src/front_pages.py` | instructions, application, fee schedule — hand-composed |
| `src/content_plan.py` | per-page content plans, the three IRS tables, section definitions |
| `src/agreement_pages.py` | reassembly and flow for the agreements and disclosures |
| `src/build.py` | assembles the packet |
| `src/source_pages.txt` | extracted source text, one line per original page |
| `tools/trace_apex.py` | re-traces the apex mark from its PNG |
| `assets/` | Fortuity wordmark, four-colour and knockout |
