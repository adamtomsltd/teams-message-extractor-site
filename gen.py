#!/usr/bin/env python3
"""Generate the multilingual GitHub Pages site from i18n/*.json string files.

English renders at the site root; every other locale renders into a lowercase
hyphenated subdirectory (pt_BR -> pt-br/). Re-run after editing any i18n file.
"""
import io, json, os, sys

BASE = "/teams-message-extractor-site"  # project-pages path prefix
SITE = os.path.dirname(os.path.abspath(__file__))

# locale file code -> (url dir ('' = root), html lang tag, rtl?, flag emoji)
# Flags are a pragmatic UI hint, not a statement that language == country;
# the most-associated flag is used for each locale.
LOCALES = {
    "en":    ("",      "en",    False, "\U0001F1EC\U0001F1E7"),  # 🇬🇧
    "ar":    ("ar",    "ar",    True,  "\U0001F1F8\U0001F1E6"),  # 🇸🇦
    "bn":    ("bn",    "bn",    False, "\U0001F1E7\U0001F1E9"),  # 🇧🇩
    "cs":    ("cs",    "cs",    False, "\U0001F1E8\U0001F1FF"),  # 🇨🇿
    "da":    ("da",    "da",    False, "\U0001F1E9\U0001F1F0"),  # 🇩🇰
    "de":    ("de",    "de",    False, "\U0001F1E9\U0001F1EA"),  # 🇩🇪
    "es":    ("es",    "es",    False, "\U0001F1EA\U0001F1F8"),  # 🇪🇸
    "fr":    ("fr",    "fr",    False, "\U0001F1EB\U0001F1F7"),  # 🇫🇷
    "hi":    ("hi",    "hi",    False, "\U0001F1EE\U0001F1F3"),  # 🇮🇳
    "it":    ("it",    "it",    False, "\U0001F1EE\U0001F1F9"),  # 🇮🇹
    "ja":    ("ja",    "ja",    False, "\U0001F1EF\U0001F1F5"),  # 🇯🇵
    "ko":    ("ko",    "ko",    False, "\U0001F1F0\U0001F1F7"),  # 🇰🇷
    "nl":    ("nl",    "nl",    False, "\U0001F1F3\U0001F1F1"),  # 🇳🇱
    "pl":    ("pl",    "pl",    False, "\U0001F1F5\U0001F1F1"),  # 🇵🇱
    "pt_BR": ("pt-br", "pt-BR", False, "\U0001F1E7\U0001F1F7"),  # 🇧🇷
    "ru":    ("ru",    "ru",    False, "\U0001F1F7\U0001F1FA"),  # 🇷🇺
    "uk":    ("uk",    "uk",    False, "\U0001F1FA\U0001F1E6"),  # 🇺🇦
    "ur":    ("ur",    "ur",    True,  "\U0001F1F5\U0001F1F0"),  # 🇵🇰
    "zh_CN": ("zh-cn", "zh-CN", False, "\U0001F1E8\U0001F1F3"),  # 🇨🇳
    "zh_TW": ("zh-tw", "zh-TW", False, "\U0001F1F9\U0001F1FC"),  # 🇹🇼
}
PAGES = ["index.html", "privacy.html", "paid-model.html"]

def load(code):
    with io.open(os.path.join(SITE, "i18n", code + ".json"), encoding="utf-8") as f:
        return json.load(f)

def page_url(code, page):
    d = LOCALES[code][0]
    return f"{BASE}/{d}/{page}" if d else f"{BASE}/{page}"

import re as _re
def strip_tags(html):
    return _re.sub(r'<[^>]+>', '', html).replace('"', '&quot;').strip()

def meta_desc_for(t, page):
    if page == 'index.html':
        return strip_tags(t.get('idx_intro', ''))[:300]
    if page == 'privacy.html':
        return strip_tags(t.get('pp_summary', ''))[:300]
    return strip_tags(t.get('fq_card', ''))[:300]

def head(t, title, code, page, css_prefix):
    meta_desc = meta_desc_for(t, page)
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
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="https://adamtomsltd.github.io{page_url(code, page)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:url" content="https://adamtomsltd.github.io{page_url(code, page)}">
<meta property="og:image" content="https://adamtomsltd.github.io/teams-message-extractor-site/assets/hero.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#45477e">
{faq_jsonld(t) if page == "index.html" else ""}
<link rel="stylesheet" href="{css_prefix}style.css">
<link rel="icon" href="{css_prefix}assets/icon.svg" type="image/svg+xml">
<link rel="icon" href="{css_prefix}assets/icon128.png" type="image/png">
{alts}
</head>
<body>
<a class="skiplink" href="#main">{t.get('a11y_skip', 'Skip to content')}</a>"""

def nav(t, code, page, here_prefix, css_prefix):
    opts = []
    for c in sorted(LOCALES, key=lambda c: (c != "en", load_cache[c]["_lang_name"])):
        sel = " selected" if c == code else ""
        flag = LOCALES[c][3]
        opts.append(f'<option value="{page_url(c, page)}"{sel}>{flag} {load_cache[c]["_lang_name"]}</option>')
    return f"""
<header class="site">
  <nav>
    <a class="brand" href="{here_prefix}./"><img class="brandicon" src="{css_prefix}assets/icon.svg" alt="" width="22" height="22">Teams Message Extractor</a>
    <a href="{here_prefix}privacy.html">{t["nav_privacy"]}</a>
    <a href="{here_prefix}paid-model.html">{t["nav_faq"]}</a>
    <select class="lang" aria-label="{t["lang_label"]}" onchange="location.href=this.value">
      {chr(10).join(opts)}
    </select>
  </nav>
</header>"""

def consent_ui(t):
    """Localized cookie banner + settings modal, wired up by consent.js.
    Hidden by default; consent.js shows the banner only when no valid
    consent cookie exists."""
    return f"""
<div id="cc-banner" class="cc-banner" hidden role="region" aria-label="{esc(t['cc_title'])}">
  <div class="cc-inner">
    <p class="cc-text"><strong>{t['cc_title']}</strong><br>{t['cc_desc']} <a href="privacy.html#cookies">{t['cc_policy']}</a></p>
    <div class="cc-actions">
      <button id="cc-accept" class="cc-btn cc-primary" type="button">{t['cc_accept']}</button>
      <button id="cc-essential" class="cc-btn" type="button">{t['cc_essential']}</button>
      <button id="cc-more" class="cc-btn" type="button">{t['cc_more']}</button>
    </div>
  </div>
</div>
<div id="cc-modal" class="cc-overlay" hidden role="dialog" aria-modal="true" aria-labelledby="cc-modal-title">
  <div class="cc-dialog">
    <h2 id="cc-modal-title">{t['cc_modal_title']}</h2>
    <p>{t['cc_modal_desc']}</p>
    <div class="cc-group">
      <div class="cc-group-head"><strong>{t['cc_nec_name']}</strong><span class="cc-always">{t['cc_always']}</span></div>
      <p>{t['cc_nec_desc']}</p>
    </div>
    <div class="cc-group">
      <div class="cc-group-head"><strong>{t['cc_stats_name']}</strong><label class="cc-switch"><input type="checkbox" id="cc-stats" aria-label="{esc(t['cc_stats_name'])}"><span></span></label></div>
      <p>{t['cc_stats_desc']}</p>
    </div>
    <div class="cc-actions">
      <button id="cc-save" class="cc-btn cc-primary" type="button">{t['cc_save']}</button>
    </div>
  </div>
</div>"""

def foot(t, css_prefix):
    return (
        f"\n<footer>{t['footer']} · <button id=\"cc-open\" class=\"cc-footer-link\" type=\"button\">{t['cc_footer']}</button></footer>"
        + consent_ui(t)
        + f'\n<script src="{css_prefix}consent.js" defer></script>\n</body>\n</html>\n'
    )

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ── Icon glyphs (stroke, currentColor) + English-keyword assignment.
# Listing structure is identical across locales (same sections, same item
# order), so icons chosen from the EN text apply position-wise everywhere.
GLYPHS = {
 "chat":    '<path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z"/>',
 "user":    '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 5-6 8-6s6.5 2 8 6"/>',
 "smile":   '<circle cx="12" cy="12" r="9"/><path d="M8.5 14a4.5 4.5 0 0 0 7 0M9 9.5h.01M15 9.5h.01"/>',
 "clip":    '<path d="M21 12.5l-8.2 8.2a5.8 5.8 0 0 1-8.2-8.2L12.8 4.3a3.9 3.9 0 0 1 5.5 5.5L10 18a1.95 1.95 0 0 1-2.8-2.8l7.3-7.3"/>',
 "image":   '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8.5" cy="10" r="1.5"/><path d="M21 16l-5-5-4 4-2-2-5 5"/>',
 "branch":  '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="9" r="2"/><path d="M6 7v10M18 11c0 4-5 4-9 6"/>',
 "globe":   '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14 0 18M12 3c-3 3.5-3 14 0 18"/>',
 "shield":  '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
 "zap":     '<path d="M13 2L5 13h5l-1 9 8-11h-5z"/>',
 "archive": '<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8M10 12h4"/>',
 "file":    '<path d="M14 3H7a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/>',
 "download":'<path d="M12 4v11M7 10l5 5 5-5M4 20h16"/>',
 "scroll":  '<path d="M7 5l5 5 5-5M7 13l5 5 5-5"/>',
 "search":  '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M20 20l-4.5-4.5"/>',
 "table":   '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M9 4v16M15 4v16"/>',
 "code":    '<path d="M8 8L4 12l4 4M16 8l4 4-4 4"/>',
 "mdmark":  '<path d="M4 17V7l4 5 4-5v10M17 8v6M14.5 12l2.5 2.5L19.5 12"/>',
 "clock":   '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "check":   '<path d="M5 12.5l4 4L19 7"/>',
}
def glyph(name, size=20):
    return (f'<span class="cardico" aria-hidden="true"><svg viewBox="0 0 24 24" width="{size}" height="{size}" '
            f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'{GLYPHS.get(name, GLYPHS["check"])}</svg></span>')

KEYWORD_GLYPHS = [
 ("channel","branch"),("thread","branch"),("csv","table"),("excel","table"),
 ("markdown","mdmark"),("screenshot","image"),("image","image"),
 ("scroll","scroll"),("zip","archive"),("archiv","archive"),("backup","archive"),("backing","archive"),
 ("timestamp","clock"),("sender","user"),("author","user"),
 ("emoji","smile"),("reaction","smile"),("attachment","clip"),("file","clip"),
 ("search","search"),("compliance","shield"),("audit","shield"),("legal","shield"),
 ("hr ","shield"),("privacy","shield"),("private","shield"),("local","shield"),
 ("domain","globe"),("everywhere","globe"),("language","globe"),
 ("download","download"),("popup","download"),("migrat","file"),("record","file"),
 ("fast","zap"),("light","zap"),
 ("message","chat"),("chat","chat"),("conversation","chat"),
]
def glyph_for(en_text):
    t = (en_text or "").lower()
    for kw, g in KEYWORD_GLYPHS:
        if kw in t:
            return g
    return "check"

_EN_LISTING = None
def en_listing_sections():
    global _EN_LISTING
    if _EN_LISTING is None:
        with io.open(os.path.join(SITE, "i18n", "listing", "en.json"), encoding="utf-8") as f:
            _EN_LISTING = json.load(f)["sections"]
    return _EN_LISTING

def render_listing_grouped(code):
    """The store description (synced by sync_listing.py), grouped into
    (intro_html, [(title, body_html), ...]) so the landing can render each
    h2-section as its own full-width band. Bullet lists become card grids;
    numbered lists become step tiles — the two changes that turn a text
    document into a landing page."""
    path = os.path.join(SITE, "i18n", "listing", code + ".json")
    with io.open(path, encoding="utf-8") as f:
        sections = json.load(f)["sections"]
    en_secs = en_listing_sections()
    structure_matches = (len(en_secs) == len(sections)
        and all(a["type"] == b["type"] for a, b in zip(en_secs, sections)))

    ul_seen = [0]  # mutable counter shared with block_html
    UL_VARIANTS = ["timeline", "pillgrid", "usecases", ""]

    def block_html(s, en_s=None):
        if s["type"] == "p":
            return f'<p>{esc(s["text"])}</p>'
        if s["type"] == "ol":
            items = "".join(f'<li><span>{esc(i)}</span></li>' for i in s["items"])
            return f'<ol class="steps">{items}</ol>'
        # ul → card grid. "Title: rest" bullets become a composed card:
        # icon tile, title line, muted description. Unsplittable bullets stay
        # a single line under the icon.
        en_items = (en_s or {}).get("items", [])
        cards = []
        for idx, i in enumerate(s["items"]):
            ICON = glyph(glyph_for(en_items[idx] if idx < len(en_items) else i))
            txt = esc(i)
            lead = rest = None
            for sep in (": ", "، ", "：", " – "):
                if sep in txt and len(txt.split(sep)[0]) < 60:
                    lead, rest = txt.split(sep, 1)
                    break
            if lead:
                cards.append(f'<li>{ICON}<h3>{lead}</h3><p>{rest}</p></li>')
            else:
                cards.append(f'<li>{ICON}<p class="solo">{txt}</p></li>')
        variant = UL_VARIANTS[ul_seen[0]] if ul_seen[0] < len(UL_VARIANTS) else ""
        ul_seen[0] += 1
        variant_cls = f" {variant}" if variant else ""
        return f'<ul class="cardgrid{variant_cls}">{"".join(cards)}</ul>' 

    intro, groups, cur = [], [], None
    for i, s in enumerate(sections):
        en_s = en_secs[i] if structure_matches else None
        if s["type"] == "h2":
            cur = {"title": esc(s["text"]), "body": []}
            groups.append(cur)
        else:
            (cur["body"] if cur else intro).append(block_html(s, en_s))
    return "\n".join(intro), [(g["title"], "\n".join(g["body"])) for g in groups]

STORE_URL = "https://chromewebstore.google.com/detail/teams-message-extractor-c/hemdpkoomkdphclendigjhelkaknjddb"

CHROME_ICON = ('<svg class="ctaicon" aria-hidden="true" viewBox="0 0 48 48" width="22" height="22">'
    '<circle cx="24" cy="24" r="20" fill="#fff"/>'
    '<path fill="#EA4335" d="M24 8a16 16 0 0 1 13.86 8H24a8 8 0 0 0-7.4 4.94L9.7 12.7A16 16 0 0 1 24 8z"/>'
    '<path fill="#34A853" d="M9.7 12.7l6.9 8.24A8 8 0 0 0 24 32c.6 0 1.18-.07 1.74-.19L18.8 39.9A16 16 0 0 1 9.7 12.7z"/>'
    '<path fill="#FBBC05" d="M37.86 16A16 16 0 0 1 18.8 39.9l6.94-8.1A8 8 0 0 0 32 24c0-1.42-.37-2.76-1.02-3.92L37.86 16z"/>'
    '<circle cx="24" cy="24" r="6.5" fill="#4285F4" stroke="#fff" stroke-width="1.6"/></svg>')

def faq_jsonld(t):
    items = []
    for i in range(1, 6):
        items.append({
            "@type": "Question", "name": t[f"faq_q{i}"],
            "acceptedAnswer": {"@type": "Answer", "text": t[f"faq_a{i}"]}
        })
    import json as _json
    return ('<script type="application/ld+json">'
            + _json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}, ensure_ascii=False)
            + '</script>')

def render_index(t, code):
    css_prefix = "../" if LOCALES[code][0] else ""
    stats = "".join(f'<span class="chip">{t[k]}</span>' for k in ("stat_formats", "stat_langs", "stat_trackers", "stat_proxy"))
    FMT_GLYPH = {"CSV": "table", "HTML": "code", "Markdown": "mdmark", "ZIP": "archive"}
    fmt_rows = "".join(
        f'<tr><td class="fmtname">{glyph(FMT_GLYPH[name], 18)}{name}</td><td>{t[key]}</td></tr>'
        for name, key in (("CSV", "fmt_csv"), ("HTML", "fmt_html"), ("Markdown", "fmt_md"), ("ZIP", "fmt_zip")))
    faq_items = "".join(
        f'<details><summary>{t[f"faq_q{i}"]}</summary><p>{t[f"faq_a{i}"]}</p></details>'
        for i in range(1, 6))
    intro_html, groups = render_listing_grouped(code)

    bands = []
    def band(inner, cls=""):
        bands.append(f'<section class="band {cls}"><div class="wrap">{inner}</div></section>')

    band(f"""<h1>{t['hero_h']}</h1>
      <p class="herosub">{t['hero_sub']}</p>
      <p class="ctarow"><a class="cta" href="{STORE_URL}" rel="noopener">{CHROME_ICON}{t['cta_install']}</a>
      <span class="ctausers">{t['cta_users']}</span></p>
      <div class="stats">{stats}</div>""", "heroband")

    band(f"""<figure class="hero browser"><img src="{css_prefix}assets/hero.png" alt="{esc(t['idx_title'])}" width="1400" height="560"></figure>
      <div class="card">{t['idx_card']}</div>
      <div class="prose">{intro_html}</div>""")

    for i, (title, body) in enumerate(groups):
        band(f'<h2>{title}</h2>{body}', "alt" if i % 2 == 0 else "")

    band(f'<h2>{t["fmt_h"]}</h2><div class="fmtwrap"><table class="fmt">{fmt_rows}</table></div>',
         "alt" if len(groups) % 2 == 0 else "")
    band(f"""<h2>{t['smpl_h']}</h2>
      <p class="prose">{t['smpl_note']}</p>
      <p class="samplerow">
        <a class="samplelink" href="{css_prefix}assets/sample.csv" download>{glyph("table", 18)}CSV</a>
        <a class="samplelink" href="{css_prefix}assets/sample.html" download>{glyph("code", 18)}HTML</a>
        <a class="samplelink" href="{css_prefix}assets/sample.md" download>{glyph("mdmark", 18)}Markdown</a>
      </p>""")
    band(f'<h2>{t["faq_h"]}</h2><div class="faq">{faq_items}</div>', "alt")
    band(f"""<h2>{t['idx_shots_h']}</h2>
      <figure class="shot"><img src="{css_prefix}assets/popup.png" alt="{esc(t['idx_title'])}" width="640" height="400" loading="lazy"></figure>""", "alt")
    band(f"""<h2>{t['idx_support_h']}</h2>
      <p>{t['idx_support']} <a href="mailto:adamltoms@gmail.com">adamltoms@gmail.com</a></p>
      <p class="ctarow"><a class="cta" href="{STORE_URL}" rel="noopener">{CHROME_ICON}{t['cta_install']}</a></p>""")

    return '<main class="landing">' + "".join(bands) + '</main>'

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
  <h2 id="cookies">{t['pp_s8_h']}</h2>
  <p>{t['pp_s8_p']}</p>
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
    "privacy.html": lambda t: f'{t["pp_title"]} - Teams Message Extractor',
    "paid-model.html": lambda t: f'{t["fq_title"]} - Teams Message Extractor',
}

load_cache = {}
for c in LOCALES:
    load_cache[c] = load(c)
_en = load('en') if 'en' not in load_cache else load_cache.get('en') or load('en')
class _Fallback(dict):
    def __init__(self, d, en): super().__init__(d); self._en = en
    def __missing__(self, k): return self._en.get(k, '')
    def get(self, k, default=None):
        v = super().get(k, None)
        return v if v is not None else self._en.get(k, default)
for c in LOCALES:
    en_d = load_cache['en'] if 'en' in load_cache else _en
    load_cache[c] = _Fallback(load_cache[c], en_d)
    missing = set(load_cache["en"] if "en" in load_cache else []) - set(load_cache[c])
    if c != "en":
        missing = set(load_cache["en"]) - set(load_cache[c])
        if missing:
            print(f"note: {c} falls back to English for {len(missing)} key(s)")

count = 0
for c, (d, lang, rtl, flag) in LOCALES.items():
    t = load_cache[c]
    outdir = os.path.join(SITE, d) if d else SITE
    os.makedirs(outdir, exist_ok=True)
    css_prefix = "../" if d else ""
    here_prefix = ""  # nav links are relative within the locale dir
    for page in PAGES:
        html = (
            head(t, TITLE[page](t), c, page, css_prefix)
            + nav(t, c, page, here_prefix, css_prefix)
            + RENDER[page](t, c).replace('<main', '<main id="main"', 1)
            + foot(t, css_prefix)
        )
        assert "{{" not in html and "None" not in html.replace("noNone", "")
        with io.open(os.path.join(outdir, page), "w", encoding="utf-8") as f:
            f.write(html)
        count += 1
urls = []
for c, (d, lang, rtl, flag) in LOCALES.items():
    for page in PAGES:
        urls.append(f"https://adamtomsltd.github.io{page_url(c, page)}")
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap += "".join(f"<url><loc>{u}</loc></url>\n" for u in urls)
sitemap += "</urlset>\n"
io.open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)
io.open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\nSitemap: https://adamtomsltd.github.io/teams-message-extractor-site/sitemap.xml\n")
print(f"generated {count} pages for {len(LOCALES)} locales + sitemap ({len(urls)} urls) + robots.txt")
