#!/usr/bin/env python3
"""Generate the multilingual GitHub Pages site from i18n/*.json string files.

English renders at the site root; every other locale renders into a lowercase
hyphenated subdirectory (pt_BR -> pt-br/). Re-run after editing any i18n file.
"""
import io, json, os, sys

BASE = "/teams-message-extractor-site"  # project-pages path prefix
SITE = os.path.dirname(os.path.abspath(__file__))

# locale file code -> (url dir ('' = root), html lang tag, rtl?)
LOCALES = {
    "en":    ("",      "en",    False),
    "ar":    ("ar",    "ar",    True),
    "bn":    ("bn",    "bn",    False),
    "cs":    ("cs",    "cs",    False),
    "da":    ("da",    "da",    False),
    "de":    ("de",    "de",    False),
    "es":    ("es",    "es",    False),
    "fr":    ("fr",    "fr",    False),
    "hi":    ("hi",    "hi",    False),
    "it":    ("it",    "it",    False),
    "ja":    ("ja",    "ja",    False),
    "ko":    ("ko",    "ko",    False),
    "nl":    ("nl",    "nl",    False),
    "pl":    ("pl",    "pl",    False),
    "pt_BR": ("pt-br", "pt-BR", False),
    "ru":    ("ru",    "ru",    False),
    "uk":    ("uk",    "uk",    False),
    "ur":    ("ur",    "ur",    True),
    "zh_CN": ("zh-cn", "zh-CN", False),
    "zh_TW": ("zh-tw", "zh-TW", False),
}
PAGES = ["index.html", "privacy.html", "paid-model.html"]

def load(code):
    with io.open(os.path.join(SITE, "i18n", code + ".json"), encoding="utf-8") as f:
        return json.load(f)

def page_url(code, page):
    d = LOCALES[code][0]
    return f"{BASE}/{d}/{page}" if d else f"{BASE}/{page}"

def head(t, title, code, page, css_prefix):
    lang, rtl = LOCALES[code][1], LOCALES[code][2]
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{LOCALES[c][1]}" href="https://adamtomsltd.github.io{page_url(c, page)}">'
        for c in LOCALES
    ) + f'\n<link rel="alternate" hreflang="x-default" href="https://adamtomsltd.github.io{page_url("en", page)}">'
    return f"""<!DOCTYPE html>
<html lang="{lang}"{' dir="rtl"' if rtl else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{css_prefix}style.css">
{alts}
</head>
<body>"""

def nav(t, code, page, here_prefix):
    opts = []
    for c in sorted(LOCALES, key=lambda c: (c != "en", load_cache[c]["_lang_name"])):
        sel = " selected" if c == code else ""
        opts.append(f'<option value="{page_url(c, page)}"{sel}>{load_cache[c]["_lang_name"]}</option>')
    return f"""
<header class="site">
  <nav>
    <a class="brand" href="{here_prefix}./">Teams Message Extractor</a>
    <a href="{here_prefix}privacy.html">{t["nav_privacy"]}</a>
    <a href="{here_prefix}paid-model.html">{t["nav_faq"]}</a>
    <select class="lang" aria-label="{t["lang_label"]}" onchange="location.href=this.value">
      {chr(10).join(opts)}
    </select>
  </nav>
</header>"""

def foot(t):
    return f"\n<footer>{t['footer']}</footer>\n</body>\n</html>\n"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_listing(code):
    """Render the locale's Chrome Web Store detailed description (synced by
    sync_listing.py) as the body of the landing page."""
    path = os.path.join(SITE, "i18n", "listing", code + ".json")
    with io.open(path, encoding="utf-8") as f:
        sections = json.load(f)["sections"]
    out = []
    for s in sections:
        if s["type"] == "p":
            out.append(f"  <p>{esc(s['text'])}</p>")
        elif s["type"] == "h2":
            out.append(f"  <h2>{esc(s['text'])}</h2>")
        else:
            tag = s["type"]
            items = "\n".join(f"    <li>{esc(i)}</li>" for i in s["items"])
            out.append(f"  <{tag}>\n{items}\n  </{tag}>")
    return "\n".join(out)

def render_index(t, code):
    return f"""<main>
  <h1>{t['idx_title']}</h1>
  <div class="card">{t['idx_card']}</div>
{render_listing(code)}
  <h2>{t['idx_support_h']}</h2>
  <p>{t['idx_support']} <a href="mailto:adamltoms@gmail.com">adamltoms@gmail.com</a></p>
</main>"""

def render_privacy(t, code):
    return f"""<main>
  <h1>{t['pp_title']}</h1>
  <p class="meta">{t['pp_meta']}</p>
  <div class="card">{t['pp_summary']}</div>
  <h2>{t['pp_s1_h']}</h2>
  <p>{t['pp_s1_p']}</p>
  <h2>{t['pp_s2_h']}</h2>
  <ul>
    <li>{t['pp_s2_l1']}</li>
    <li>{t['pp_s2_l2']}</li>
    <li>{t['pp_s2_l3']}</li>
  </ul>
  <h2>{t['pp_s3_h']}</h2>
  <ul>
    <li>{t['pp_s3_l1']}</li>
    <li>{t['pp_s3_l2']}</li>
    <li>{t['pp_s3_l3']}</li>
    <li>{t['pp_s3_l4']}</li>
  </ul>
  <h2>{t['pp_s4_h']}</h2>
  <ul>
    <li>{t['pp_s4_l1']}</li>
    <li>{t['pp_s4_l2']}</li>
    <li>{t['pp_s4_l3']}</li>
    <li>{t['pp_s4_l4']}</li>
  </ul>
  <h2>{t['pp_s5_h']}</h2>
  <p>{t['pp_s5_p']}</p>
  <h2>{t['pp_s6_h']}</h2>
  <p>{t['pp_s6_p']}</p>
  <h2>{t['pp_s7_h']}</h2>
  <p>{t['pp_s7_p']}</p>
</main>"""

def render_faq(t, code):
    return f"""<main>
  <h1>{t['fq_title']}</h1>
  <p class="meta">{t['fq_meta']}</p>
  <div class="card">{t['fq_card']}</div>
  <h2>{t['fq_q1_h']}</h2>
  <p>{t['fq_q1_p']}</p>
  <h2>{t['fq_q2_h']}</h2>
  <p>{t['fq_q2_p']}</p>
  <h2>{t['fq_q3_h']}</h2>
  <p>{t['fq_q3_p']}</p>
  <h2>{t['fq_q4_h']}</h2>
  <p>{t['fq_q4_p']}</p>
  <h2>{t['fq_q5_h']}</h2>
  <p>{t['fq_q5_p']}</p>
</main>"""

RENDER = {"index.html": render_index, "privacy.html": render_privacy, "paid-model.html": render_faq}
TITLE = {
    "index.html": lambda t: t["idx_title"],
    "privacy.html": lambda t: f'{t["pp_title"]} — Teams Message Extractor',
    "paid-model.html": lambda t: f'{t["fq_title"]} — Teams Message Extractor',
}

load_cache = {}
for c in LOCALES:
    load_cache[c] = load(c)
    missing = set(load_cache["en"] if "en" in load_cache else []) - set(load_cache[c])
    if c != "en":
        missing = set(load_cache["en"]) - set(load_cache[c])
        assert not missing, f"{c} missing keys: {missing}"

count = 0
for c, (d, lang, rtl) in LOCALES.items():
    t = load_cache[c]
    outdir = os.path.join(SITE, d) if d else SITE
    os.makedirs(outdir, exist_ok=True)
    css_prefix = "../" if d else ""
    here_prefix = ""  # nav links are relative within the locale dir
    for page in PAGES:
        html = (
            head(t, TITLE[page](t), c, page, css_prefix)
            + nav(t, c, page, here_prefix)
            + RENDER[page](t, c)
            + foot(t)
        )
        assert "{{" not in html and "None" not in html.replace("noNone", "")
        with io.open(os.path.join(outdir, page), "w", encoding="utf-8") as f:
            f.write(html)
        count += 1
print(f"generated {count} pages for {len(LOCALES)} locales")
