# Teams Message Extractor — website

Public GitHub Pages site for the [Teams Message Extractor](https://github.com/adamtomsltd/teams-message-extractor) browser extension: landing page, privacy policy, and paid-model FAQ, in 20 languages.

Live at: **https://adamtomsltd.github.io/teams-message-extractor-site/**

## How the site is built

All 60 HTML pages (3 pages × 20 locales) are **generated** — never edit them by hand.

- `i18n/<locale>.json` — every translatable string, one file per locale. English is the reference; `gen.py` asserts key parity for all other locales.
- `i18n/listing/<locale>.json` — the Chrome Web Store detailed description per locale, synced from `store-descriptions.txt` in the extension repo by `sync_listing.py`; rendered as the landing-page body.
- `gen.py` — renders `index.html`, `privacy.html`, `paid-model.html` for every locale (English at the root, others in `de/`, `fr/`, `pt-br/`, …). Also renders the cookie banner + settings modal into every page.

Workflow: edit the i18n JSON (and/or `gen.py`), then

```bash
python3 gen.py   # regenerates all 60 pages
```

and commit everything. **Pushing `main` deploys** (GitHub Pages serves the `main` branch root).

## Analytics & cookie consent

- `consent.js` — vanilla-JS consent manager, a port of the `gdpr-cookie` CMP used on barracudas.co.uk (Google Consent Mode v2). It sets all-denied consent defaults (restoring any prior choice from the `cookieConsent` cookie — base64 JSON `{v: 2, ts, d}`) **before** injecting Google Tag Manager, and pushes `consent update` + a `cookie_consent_update` dataLayer event whenever the visitor decides. Two consent groups: strictly necessary (always on) and statistics (`analytics_storage`).
- The banner/modal markup is rendered per-locale by `gen.py` (`consent_ui()`); the strings are the `cc_*` keys in `i18n/*.json`. The privacy policy's cookies section is `pp_s8_*` (anchor `#cookies`).
- **GTM container: `GTM-PWQWZPZM`** — baked into `consent.js`. The GA4 measurement ID (`G-T87CX665RS`) lives in the container's Google Tag, *not* in this repo, so analytics changes are made in the GTM UI and published as a new container version — no site deploy needed.
- The Google Tag carries `cookie_domain=adamtomsltd.github.io`: `github.io` is on the Public Suffix List, so GA4's automatic cookie-domain detection fails there and browsers reject the `_ga` cookies without it.
- Store-listing traffic is separate: the Chrome Web Store's "Opt in to Google Analytics" auto-created its own restricted GA4 property (Marketer role, 2-month retention). It cannot be merged with the website property.

No consent = no cookies: visitors who decline or ignore the banner send only anonymous, cookieless Consent Mode pings.
