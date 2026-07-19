/* Cookie consent + Google Tag Manager loader.
 *
 * Vanilla port of the Barracudas gdpr-cookie CMP (Google Consent Mode v2).
 * Same stored-consent format: base64(JSON {v, ts, d}) in a "cookieConsent"
 * cookie, all consent types denied by default, prior consent restored
 * synchronously BEFORE GTM is injected, and `consent update` plus a
 * `cookie_consent_update` dataLayer event on every user decision.
 *
 * The GA4 measurement ID lives inside the GTM container (GA4 tag), not in
 * this file — swap analytics behaviour in the GTM UI without redeploying.
 */
(function () {
  "use strict";

  var GTM_ID = "GTM-PWQWZPZM";
  var CONSENT_VERSION = 2;
  var COOKIE_NAME = "cookieConsent";
  var COOKIE_DAYS = 365;
  // Consent groups: which Google consent types an accepted group grants.
  var GROUPS = [
    { id: "necessary", optional: false, types: [] },
    { id: "statistics", optional: true, types: ["analytics_storage"] }
  ];

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  function allTypes() {
    var out = [];
    GROUPS.forEach(function (g) {
      g.types.forEach(function (t) { if (out.indexOf(t) < 0) out.push(t); });
    });
    return out;
  }

  function readCookie() {
    var m = document.cookie.match(new RegExp("(?:^|; )" + COOKIE_NAME + "=([^;]*)"));
    return m ? m[1] : null;
  }

  function writeCookie(value) {
    var expires = new Date(Date.now() + COOKIE_DAYS * 864e5).toUTCString();
    var secure = location.protocol === "https:" ? "; Secure" : "";
    document.cookie = COOKIE_NAME + "=" + value + "; expires=" + expires + "; path=/; SameSite=Lax" + secure;
  }

  function deserialize(raw) {
    try {
      var bytes = Uint8Array.from(atob(raw), function (c) { return c.charCodeAt(0); });
      var parsed = JSON.parse(new TextDecoder().decode(bytes));
      if (!parsed || parsed.v !== CONSENT_VERSION || typeof parsed.d !== "object" || parsed.d === null) {
        return null;
      }
      var decisions = {};
      GROUPS.forEach(function (g) {
        decisions[g.id] = typeof parsed.d[g.id] === "boolean" ? parsed.d[g.id] : !g.optional;
      });
      return decisions;
    } catch (e) {
      return null;
    }
  }

  function serialize(decisions) {
    var json = JSON.stringify({ v: CONSENT_VERSION, ts: Math.floor(Date.now() / 1000), d: decisions });
    var bytes = new TextEncoder().encode(json);
    var bin = "";
    for (var i = 0; i < bytes.length; i++) { bin += String.fromCharCode(bytes[i]); }
    return btoa(bin);
  }

  function deriveState(decisions) {
    var state = {};
    allTypes().forEach(function (t) { state[t] = "denied"; });
    GROUPS.forEach(function (g) {
      if (decisions && decisions[g.id]) {
        g.types.forEach(function (t) { state[t] = "granted"; });
      }
    });
    return state;
  }

  var raw = readCookie();
  var stored = raw ? deserialize(raw) : null;

  // Consent Mode v2 defaults, set before gtag.js is injected. A returning
  // consenter starts the page already "granted"; everyone else (and any
  // malformed cookie) starts all-denied.
  gtag("consent", "default", deriveState(stored));
  gtag("set", "ads_data_redaction", true);
  gtag("set", "url_passthrough", true);

  window.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
  var tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtm.js?id=" + GTM_ID;
  document.head.appendChild(tag);

  // --- Banner / settings-modal wiring (markup is rendered per-locale by gen.py) ---
  function $(id) { return document.getElementById(id); }
  var banner = $("cc-banner");
  var modal = $("cc-modal");
  var statsToggle = $("cc-stats");
  if (!banner || !modal || !statsToggle) { return; }

  function decide(decisions) {
    stored = decisions;
    writeCookie(serialize(decisions));
    gtag("consent", "update", deriveState(decisions));
    window.dataLayer.push({ event: "cookie_consent_update" });
    banner.hidden = true;
    modal.hidden = true;
  }

  if (!stored) { banner.hidden = false; }

  function openModal() {
    statsToggle.checked = stored ? !!stored.statistics : false;
    modal.hidden = false;
  }

  $("cc-accept").addEventListener("click", function () {
    var d = {};
    GROUPS.forEach(function (g) { d[g.id] = true; });
    decide(d);
  });
  $("cc-essential").addEventListener("click", function () {
    var d = {};
    GROUPS.forEach(function (g) { d[g.id] = !g.optional; });
    decide(d);
  });
  $("cc-more").addEventListener("click", openModal);
  $("cc-open").addEventListener("click", openModal);
  $("cc-save").addEventListener("click", function () {
    decide({ necessary: true, statistics: statsToggle.checked });
  });
  modal.addEventListener("click", function (e) {
    if (e.target === modal) { modal.hidden = true; }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modal.hidden) { modal.hidden = true; }
  });
})();
