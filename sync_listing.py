#!/usr/bin/env python3
"""Sync the Chrome Web Store detailed descriptions onto the site.

Reads store-descriptions.txt from the (private) extension repo, parses each
locale's [START]..[END] block into structured sections, and writes
i18n/listing/<code>.json for gen.py to render into each locale's landing page.

Run whenever store-descriptions.txt changes, then gen.py, then commit.
"""
import io, json, os, re, sys

SITE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Documents/source/adamtomsltd/teams-message-extractor/store-descriptions.txt")

text = io.open(SRC, encoding="utf-8").read()
blocks = re.findall(r"=== (\w+) —.*?\[START\]\n(.*?)\n\[END\]", text, re.S)
assert len(blocks) == 20, f"expected 20 locale blocks, found {len(blocks)}"

# Numbered step lines look like "1. Open any Teams conversation" — one or two
# digits, a separator, then whitespace. The whitespace is required so version
# numbers at the start of a heading ("2.8.1 新功能：") don't match.
NUM = re.compile(r"^\d{1,2}[\.\)、]\s+\S")

def parse(body):
    sections, para = [], []

    def flush():
        nonlocal para
        if para:
            sections.append({"type": "p", "text": " ".join(para)})
            para = []

    lines = body.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            flush()
            i += 1
            continue
        if stripped.startswith(">"):
            flush()
            items = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                items.append(lines[i].strip()[1:].strip())
                i += 1
            sections.append({"type": "ul", "items": items})
            continue
        if NUM.match(stripped):
            flush()
            items = []
            while i < len(lines) and NUM.match(lines[i].strip()):
                items.append(re.sub(r"^\d+[\.\)、]\s*", "", lines[i].strip()))
                i += 1
            sections.append({"type": "ol", "items": items})
            continue
        # Section headings come in two shapes:
        #  (a) "Key features:" — ends with a colon (Latin or fullwidth)
        #  (b) "Disclaimer"    — short standalone line directly above a long
        #      paragraph line (only shape seen without a colon)
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if stripped.endswith((":", "：")) and len(stripped) < 80:
            flush()
            sections.append({"type": "h2", "text": stripped.rstrip(":：").rstrip()})
            i += 1
            continue
        if len(stripped) < 40 and not para and sections and len(nxt) > 80:
            flush()
            sections.append({"type": "h2", "text": stripped})
            i += 1
            continue
        para.append(stripped)
        i += 1
    flush()
    return sections

outdir = os.path.join(SITE, "i18n", "listing")
os.makedirs(outdir, exist_ok=True)
for code, body in blocks:
    sections = parse(body)
    kinds = [s["type"] for s in sections]
    assert kinds.count("ul") >= 3 and kinds.count("h2") >= 4, f"{code}: suspicious parse {kinds}"
    with io.open(os.path.join(outdir, code + ".json"), "w", encoding="utf-8") as f:
        json.dump({"sections": sections}, f, ensure_ascii=False, indent=1)
    print(f"{code}: {len(sections)} sections ({kinds.count('h2')} h2, {kinds.count('ul')} ul, {kinds.count('ol')} ol)")
