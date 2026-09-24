"""Post-build check for a colour leak in the PDF.

Usage (from BGU-Calculus-Book/):  python3 tmp/pdf_colour_check.py [path/to.pdf]

Background: on 2026-09-24 every page after §8.6's .optional proof printed orange. XeTeX
reverses RTL lines, colour specials included, so an inline {\\color{..}..} could leave the
colour switched on (see CALCULUS-PROJECT.md, "Hebrew / RTL conventions", and audit check 13,
which catches the SOURCE pattern). This script catches the SYMPTOM, whatever the cause:
body text should be black, so a run of consecutive pages whose ink is mostly coloured means
something leaked.

Figures and box labels are coloured too, so a single colourful page is normal (the π
figure is ~47%). Only a RUN of heavily coloured pages is reported. Exit status 1 if found.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

THRESHOLD = 0.60   # share of ink that is coloured, above which a page counts as "coloured"
MIN_RUN = 2        # this many consecutive coloured pages = a leak

pdf = sys.argv[1] if len(sys.argv) > 1 else "_book/Book_Draft.pdf"
tmp = tempfile.mkdtemp()
try:
    subprocess.run(["pdftoppm", "-r", "30", "-png", pdf, os.path.join(tmp, "p")], check=True)
    shares = []
    for f in sorted(glob.glob(os.path.join(tmp, "p-*.png"))):
        page = int(f.rsplit("-", 1)[1][:-4])
        px = Image.open(f).convert("RGB").getdata()
        ink = [c for c in px if sum(c) < 450]                  # dark enough to be print
        col = [c for c in ink if max(c) - min(c) > 60]         # saturated, i.e. not grey/black
        shares.append((page, len(col) / max(1, len(ink))))
finally:
    shutil.rmtree(tmp)

runs, cur = [], []
for page, share in shares:
    if share > THRESHOLD:
        cur.append(page)
    else:
        if len(cur) >= MIN_RUN:
            runs.append(cur)
        cur = []
if len(cur) >= MIN_RUN:
    runs.append(cur)

print(f"{pdf}: {len(shares)} pages checked")
if not runs:
    print("OK: no run of coloured pages (no colour leak)")
    sys.exit(0)
for r in runs:
    print(f"LEAK? pages {r[0]}-{r[-1]} ({len(r)} pages) are mostly coloured. The cause is "
          f"usually just before page {r[0]}: look for an inline \\color there (audit check 13).")
sys.exit(1)
