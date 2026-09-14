import re, glob, html

# 1. CITATION AUDIT -----------------------------------------------------------
# Every rendered box id, NUMBERED OR NOT (numbered="false" and the .thmkey/.thmwarn
# classes produce ids with no number in the label — they are still link targets).
ids = set()
for f in glob.glob("_book/*.html"):
    ids |= set(re.findall(r'<div id="(box-[^"]+)"', open(f, encoding="utf-8").read()))
bad = []
for q in sorted(glob.glob("*.qmd")):
    src = open(q, encoding="utf-8").read()
    for m in re.finditer(r'\[([^\]]*?)\]\(([^)]*?)#(box-[^)\s]+)\)', src):
        if m.group(3) not in ids:
            bad.append(f"{q}: DANGLING #{m.group(3)}  (text: {m.group(1).strip()})")
        # link text must NAME the target, never carry the filter's number
        if re.search(r'\d+\.\d+\.\d+', m.group(1)):
            bad.append(f"{q}: NUMBER IN LINK TEXT  {m.group(1).strip()} -> #{m.group(3)}")
print(f"1. citation audit          : {len(bad)}")
for b in bad: print("     " + b)

# 2. em-dash straight after math ----------------------------------------------
hits = [f"{q}:{i}" for q in sorted(glob.glob("*.qmd"))
        for i, l in enumerate(open(q, encoding="utf-8"), 1) if re.search(r'\$ *—', l)]
print(f"2. '$ —' after math        : {len(hits)}")
for h in hits: print("     " + h)

# 3. bullets inside a .thmproof / .thmsol fence -------------------------------
hits = []
for q in sorted(glob.glob("*.qmd")):
    depth, inbox = 0, None
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        o = re.match(r'^(:{3,})\s*(\{.*\}|\w.*)?$', l.rstrip())
        if o and o.group(2):
            depth += 1
            if inbox is None and re.search(r'thmproof|thmsol', o.group(2)): inbox = depth
        elif re.match(r'^:{3,}\s*$', l.rstrip()):
            if inbox is not None and depth == inbox: inbox = None
            depth = max(0, depth - 1)
        elif inbox is not None and re.match(r'^\s*- ', l):
            hits.append(f"{q}:{i}")
print(f"3. bullets in proof/sol    : {len(hits)}")
for h in hits: print("     " + h)

# 4. centred caption div with no enclosing when-format="pdf" ------------------
# Tracks the fence stack; a 6-line proximity test gives false positives, because the
# guard sits above a ```{=latex}``` block and is 7+ lines up.
hits = []
for q in sorted(glob.glob("*.qmd")):
    stack = []
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        m = re.match(r'^(:{3,})(\s*\{.*\}|\s+\w.*)?\s*$', l.rstrip())
        if not m: continue
        attrs = (m.group(2) or "").strip()
        if attrs:
            if attrs == '{style="text-align:center"}' and \
               not any('when-format="pdf"' in a for a in stack):
                hits.append(f"{q}:{i}")
            stack.append(attrs)
        elif stack:
            stack.pop()
print(f"4. unguarded centred div   : {len(hits)}")
for h in hits: print("     " + h)

# 5. every #box- id defined exactly once book-wide --------------------------
# Check 1 only tests link -> id, so a duplicated DEFINITION slips past it. Duplicates are
# invalid HTML in the merged PDF pass and make the [] resolver ambiguous, silently.
seen = {}
for q in sorted(glob.glob("*.qmd")):
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        m = re.match(r'^:{3,}\s*\{#(box-[\w-]+)', l)
        if m:
            seen.setdefault(m.group(1), []).append(f"{q}:{i}")
dups = {k: v for k, v in seen.items() if len(v) > 1}
print(f"5. duplicate box ids       : {len(dups)}")
for k, v in sorted(dups.items()):
    print(f"     {k}  ->  {', '.join(v)}")

# 6. empty-link citation of a box the filter never records ---------------------
# theorem-numbering.lua calls record() only for boxes it NUMBERS. The UNNUMBERED classes
# below, and anything carrying numbered="false", are skipped — so an empty [](#box-...)
# pointing at one renders a literal "??". Such a box must be cited with NAMED link text
# instead (which is the house convention anyway), or opt in with numbered="true".
UNNUMBERED = ("thmexpl", "thmwarn", "thmkey", "thmchk")
unrecorded = set()
for q in sorted(glob.glob("*.qmd")):
    for l in open(q, encoding="utf-8"):
        m = re.match(r'^:{3,}\s*\{#(box-[\w-]+)([^}]*)\}', l)
        if not m:
            continue
        bid, attrs = m.group(1), m.group(2)
        opts_in = 'numbered="true"' in attrs
        if 'numbered="false"' in attrs and not opts_in:
            unrecorded.add(bid)
        elif any(f".{c}" in attrs for c in UNNUMBERED) and not opts_in:
            unrecorded.add(bid)
hits = []
for q in sorted(glob.glob("*.qmd")):
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        for m in re.finditer(r'\[\]\(([^)]*?)#(box-[^)\s]+)\)', l):
            if m.group(2) in unrecorded:
                hits.append(f"{q}:{i}  [](#{m.group(2)}) -> renders ??")
print(f"6. empty ref to unnumbered : {len(hits)}")
for h in hits: print("     " + h)
