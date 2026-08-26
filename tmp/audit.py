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
