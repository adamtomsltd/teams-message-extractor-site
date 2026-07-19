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
<link rel="icon" href="{css_prefix}assets/icon.svg" type="image/svg+xml">
<link rel="icon" href="{css_prefix}assets/icon128.png" type="image/png">
{alts}
</head>
<body>"""

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
    css_prefix = "../" if LOCALES[code][0] else ""
    return f"""<main>
  <h1>{t['idx_title']}</h1>
  <figure class="hero"><img src="{css_prefix}assets/hero.png" alt="{esc(t['idx_title'])}" width="1400" height="560"></figure>
  <div class="card">{t['idx_card']}</div>
{render_listing(code)}
  <h2>{t['idx_shots_h']}</h2>
  <figure class="shot"><img src="{css_prefix}assets/popup.png" alt="{esc(t['idx_title'])}" width="640" height="400" loading="lazy"></figure>
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
    missing = set(load_cache["en"] if "en" in load_cache else []) - set(load_cache[c])
    if c != "en":
        missing = set(load_cache["en"]) - set(load_cache[c])
        assert not missing, f"{c} missing keys: {missing}"

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
            + RENDER[page](t, c)
            + foot(t, css_prefix)
        )
        assert "{{" not in html and "None" not in html.replace("noNone", "")
        with io.open(os.path.join(outdir, page), "w", encoding="utf-8") as f:
            f.write(html)
        count += 1
print(f"generated {count} pages for {len(LOCALES)} locales")
