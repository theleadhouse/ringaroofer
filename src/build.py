"""RingaRoofer v2 static site generator -> ../public  (python3 build.py)
Photo-led, call-first roofing referral site for Google/Microsoft paid search (inbound calls). Same URLs as v1 so ads, Search Console and links keep working.
Adds: real photos, app-style mobile bar, roof-problem picker, 60 Roof Questions answers (reviews removed), search-style FAQs, roof inspection + 'roofers near me' pages, Thumbtack backup link."""
import json, rr_problems as RP
import rr_more as RM
import rr_faq2
import os, re, json, shutil
from html import escape as esc
from content import *
import legal
import faqs as FQ
from rr_state_detail import detail
from questions import Q as QS, CATS as QCATS
QBY = {q[0]: q for q in QS}

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.normpath(os.path.join(ROOT, "..", "public"))
V = "20261127b"; UPDATED = "2026-11-20"
GSC_META = "xz9ncKiRn5z77EkCuE-lelMPzNC5h_5giCsF33PhNyk"
for _s in SERVICES: _s["faqs"] = _s["faqs"][:-1] + FQ.EXTRA.get(_s["slug"], []) + _s["faqs"][-1:] if _s["faqs"] and _s["faqs"][-1][0].startswith("Do you do") else _s["faqs"] + FQ.EXTRA.get(_s["slug"], [])
TOPIC = {"roof-repair": "Roof repair", "roof-leak-repair": "Roof leak", "emergency-roof-repair": "Emergency repair or tarp", "roof-tarping": "Emergency repair or tarp",
         "storm-roof-repair": "Storm or wind", "hail-roof-repair": "Hail", "roof-replacement": "Roof replacement or new roof", "new-roof": "Roof replacement or new roof", "roof-inspection": "Roof inspection"}

I = {
 "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>', "arrow": '<path d="M5 12h14M13 5l7 7-7 7"/>',
 "hammer": '<path d="m15 12-8.4 8.4a2.1 2.1 0 0 1-3-3L12 9"/><path d="M17.6 15 22 10.6M20.9 11.7l-1.3-1.3a2 2 0 0 1 0-2.8l.5-.5-3.6-3.6a5 5 0 0 0-7 0L9 4l4 1v2.3l2.4 2.4a2 2 0 0 1 2.8 0l1.3 1.3"/>',
 "drop": '<path d="M12 2.7s-6 6.3-6 11.3a6 6 0 0 0 12 0c0-5-6-11.3-6-11.3z"/>',
 "siren": '<path d="M7 18v-6a5 5 0 0 1 10 0v6"/><path d="M5 21a1 1 0 0 1-1-1v-1a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v1a1 1 0 0 1-1 1zM12 2v2M4.2 5.2l1.4 1.4M19.8 5.2l-1.4 1.4"/>',
 "tarp": '<path d="M3 11 12 4l9 7"/><path d="M5 10.5 12 15l7-4.5"/><path d="M5 10v9h14v-9"/>',
 "storm": '<path d="M19 16.9A5 5 0 0 0 18 7h-1.3a8 8 0 1 0-11.7 9"/><path d="m13 11-4 6h6l-4 6"/>',
 "hail": '<path d="M20 16.6A5 5 0 0 0 18 7h-1.3a8 8 0 1 0-12.7 8.9"/><circle cx="8" cy="19" r="1"/><circle cx="12" cy="21" r="1"/><circle cx="16" cy="19" r="1"/>',
 "house": '<path d="M3 10.5 12 3l9 7.5V21H3z"/><path d="M9 21v-7h6v7"/>',
 "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5M2 17l10 5 10-5"/>',
 "shingle": '<path d="M2 12 12 4l10 8"/><path d="M5 11h14M4 14h16M3 17h18"/>', "metal": '<path d="M2 12 12 4l10 8"/><path d="M7 8v12M12 4v16M17 8v12"/>',
 "flat": '<rect x="3" y="8" width="18" height="12" rx="1"/><path d="M3 8h18l-1-3H4z"/>', "tile": '<path d="M2 12 12 4l10 8"/><path d="M4 15a2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0"/>',
 "slate": '<path d="M2 12 12 4l10 8"/><path d="M5 12h4v4H5zM10 12h4v4h-4zM15 12h4v4h-4z"/>', "shake": '<path d="M2 12 12 4l10 8"/><path d="M6 11v7M10 10v9M14 10v9M18 11v7"/>',
 "map": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>', "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>', "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>', "chev": '<path d="m6 9 6 6 6-6"/>', "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
 "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>', "ext": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
 "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21v-6h6v6"/>', "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
 "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L3 21l1.9-6.4A8 8 0 1 1 21 12z"/>', "help": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
 "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
}
I.setdefault("x", '<path d="M18 6 6 18M6 6l12 12"/>')
I.setdefault("chev", '<path d="m6 9 6 6 6-6"/>')
def ic(n, s=22): return f'<svg class="ic" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[n]}</svg>'
def call_btn(cls="btn btn-call", label=None, place=""):
    return f'<a class="{cls}" href="tel:{TEL}" data-call="{place}">{ic("phone",19)}<span>{label or "Call " + PHONE}</span></a>'
def tt_link(campaign, label="Rather book online? Compare roofers on Thumbtack, our partner", cls="tt-text"):
    return f'<a class="{cls}" href="{tt(campaign)}" target="_blank" rel="sponsored noopener" data-tt="{campaign}">{label} {ic("ext",14)}</a>'
def pic(key, w=900, h=None, eager=False, cls=""):
    src, alt, _ = P[key]
    ld = 'fetchpriority="high"' if eager else 'loading="lazy"'
    hh = h or int(w * .7)
    return (f'<img class="{cls}" src="{img(src, w, hh)}" srcset="{img(src, w // 2, hh // 2)} {w // 2}w, {img(src, w, hh)} {w}w, {img(src, int(w * 1.5), int(hh * 1.5))} {int(w * 1.5)}w" '
            f'sizes="(max-width: 700px) 100vw, {w}px" width="{w}" height="{hh}" alt="{esc(alt)}" {ld} decoding="async">')

LOGO = ('<svg class="logo-mark" width="42" height="42" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#13233A"/>'
        '<path d="M8 22 20 12l12 10" fill="none" stroke="#F26B1D" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M12 21v9h16v-9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
        '<path d="M26.5 7.5a6 6 0 0 1 3.5 3.5M28 4.5a9.5 9.5 0 0 1 5.5 5.5" fill="none" stroke="#F26B1D" stroke-width="2" stroke-linecap="round"/></svg>')
BRANDH = f'{LOGO}<span class="wm"><span>Ringa<em>Roofer</em></span><small>Roofers near you, one call</small></span>'
NAV = [("Roof Problems", "/roof-problems/", [(n, f"/roof-problems/{k}/") for k, n in RP.CATS] + [("Roof dictionary", "/roof-dictionary/"), ("Roof tools", "/tools/")]), ("Services", "/services/", [(s["name"], f"/services/{s['slug']}/") for s in SERVICES]), ("Roof Types", "/roof-types/", [(t["name"], f"/roof-types/{t['slug']}/") for t in TYPES]),
       ("Coverage", "/coverage/", None), ("Roof Questions", "/questions/", None)]
SOLO = ("/services/roof-leak-repair/",)

def header(active):
    li = []
    for t, h, sub in NAV:
        cur = ' aria-current="page"' if active == h or (sub and active.startswith(h) and active not in SOLO) else ""
        if sub:
            dd = "".join(f'<a href="{u}">{n}</a>' for n, u in sub)
            li.append(f'<li class="has-dd"><a href="{h}"{cur}>{t}</a><button class="dd-btn" aria-label="{t} menu" aria-expanded="false">{ic("chev",16)}</button><div class="dd">{dd}</div></li>')
        else:
            li.append(f'<li><a href="{h}"{cur}>{t}</a></li>')
    mob = "".join(f'<a href="{h}">{t}</a>' + ("".join(f'<a class="sub" href="{u}">{n}</a>' for n, u in sub) if sub else "") for t, h, sub in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap tb-in"><span>{ic("storm",15)} Leaks, storm-hit roofs, new roofs and re-roofs · Roofing companies across the U.S.</span><a href="tel:{TEL}" data-call="topbar">Call {PHONE}</a></div></div>
<header class="hdr"><div class="wrap hdr-in">
 <a class="brand" href="/" aria-label="RingaRoofer home">{BRANDH}</a>
 <nav class="nav" aria-label="Main"><ul>{"".join(li)}</ul></nav>
 <div class="hdr-cta">{call_btn("btn btn-call hdr-call", PHONE, "header")}<button class="menu" aria-label="Open menu" aria-expanded="false" aria-controls="mnav">{ic("menu",26)}</button></div>
</div>
<div class="mnav" id="mnav" hidden><nav aria-label="Mobile">{mob}<a href="/roofers-near-me/">Roofers Near Me</a><a href="/library/">Roof Library</a><a href="/community/">Real Roof Problems</a><a href="/how-it-works/">How It Works</a><a href="/contact/">Request a Callback</a></nav>{call_btn("btn btn-call block", None, "mobile-menu")}</div>
</header>'''

DISCLAIMER = ("RingaRoofer.com is a referral service that connects homeowners with independent local roofing contractors. RingaRoofer does not charge homeowners and does not perform roofing work. "
              "All contractors are independent, and RingaRoofer does not warrant or guarantee any work performed. Homeowners should confirm that any contractor they hire holds the credentials and coverage required for the work in their area. "
              "RingaRoofer is a Thumbtack partner and may be paid when you use Thumbtack through links on this site. Thumbtack is a separate company. "
              "Photos are real photographs from Pexels and Unsplash shown for illustration; they do not show specific companies or jobs. Images are for illustration only. Any people shown are actors or models, not actual contractors, technicians or customers. Same-day service is subject to availability and is not guaranteed; timing depends on the provider, your location and local demand. Calls may be recorded for quality purposes.")
def footer():
    svc = "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    typ = "".join(f'<li><a href="/roof-types/{t["slug"]}/">{t["name"]}</a></li>' for t in TYPES)
    return f'''<section class="cta-final"><div class="cta-bg">{pic("newroof", 1600, 700)}</div><div class="wrap cta-in"><p class="kick">Roof problem?</p><h2>Talk to a roofer today.</h2><p>One call connects you with an independent roofing company that serves your area: repairs, leaks, new roofs, re-roofs and emergency service.</p>
<div class="btns">{call_btn("btn btn-call xl", None, "footer-cta")}<a class="btn btn-ghost light xl" href="/contact/">Request a callback</a></div>{tt_link("footer", cls="tt-text light")}</div></section>
<footer class="ftr"><div class="wrap">
 <div class="f-grid">
  <div class="f-brand"><a class="brand" href="/">{BRANDH}</a><p>Connecting homeowners with independent roofing companies across the United States.</p>
   <p><a class="f-phone" href="tel:{TEL}" data-call="footer">{ic("phone",18)} {PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
  <div><h2>Services</h2><ul>{svc}</ul></div>
  <div><h2>Roof Types</h2><ul>{typ}</ul></div>
  <div><h2>RingaRoofer</h2><ul><li><a href="/roofers-near-me/">Roofers Near Me</a></li><li><a href="/questions/">Roof Questions</a></li><li><a href="/roof-problem-guide/">Roof Problem Guide</a></li><li><a href="/assets/guides/roof-problem-guide.pdf" download>Download the Guide (PDF)</a></li><li><a href="/how-it-works/">How It Works</a></li><li><a href="/coverage/">Coverage by State</a></li><li><a href="/community/">Real Roof Problems</a></li><li><a href="/library/">Roof Library</a></li><li><a href="/roof-dictionary/">Roof Dictionary</a></li><li><a href="/tools/">Roof Tools</a></li><li><a href="/for-roofing-pros/">For Roofing Pros</a></li><li><a href="/contact/">Request a Callback</a></li><li><a href="/sitemap/">Site Map</a></li></ul></div>
 </div>
 <p class="disc">{DISCLAIMER}</p>
 <div class="f-legal"><nav aria-label="Legal"><a href="/privacy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/referral-disclosure/">Referral Disclosure</a><a href="/california-privacy/">California Privacy</a><a href="/california-privacy/#opt-out">Do Not Sell or Share My Personal Information</a><a href="/do-not-call/">Do Not Call</a><a href="/accessibility/">Accessibility</a></nav>
 <p>&copy; 2026 RingaRoofer.com</p></div>
</div></footer>
<nav class="tabbar" aria-label="Quick actions"><a href="/" class="tb-i">{ic("home",21)}<span>Home</span></a><a href="/services/" class="tb-i">{ic("grid",21)}<span>Services</span></a><a href="tel:{TEL}" class="tb-call" data-call="tabbar" aria-label="Call {PHONE}">{ic("phone",24)}<span>Call</span></a><a href="/questions/" class="tb-i">{ic("help",21)}<span>Questions</span></a><button type="button" class="tb-i tb-menu" aria-controls="mnav">{ic("menu",21)}<span>Menu</span></button></nav>
<a class="fcall" href="tel:{TEL}" data-call="float-desktop" aria-label="Call a roofer at {PHONE}">{ic("phone",20)}<span><b>Need a roofer?</b><small>Call {PHONE}</small></span></a>'''

def crumbs(trail):
    if not trail: return ""
    items = [("Home", "/")] + trail
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
        f'<li><a href="{u}">{n}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{n}</li>' for i, (n, u) in enumerate(items)) + '</ol></nav>'

def schema(p):
    g = [{"@type": "Organization", "@id": URL + "/#org", "name": BRAND, "url": URL + "/", "logo": URL + "/assets/img/logo-512.png", "email": EMAIL, "telephone": TEL,
          "areaServed": {"@type": "Country", "name": "United States"}, "description": "RingaRoofer is a roofing referral service that connects homeowners with independent local roofing companies.",
          "contactPoint": {"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service", "areaServed": "US", "availableLanguage": "en"}},
         {"@type": "WebSite", "@id": URL + "/#site", "url": URL + "/", "name": BRAND, "publisher": {"@id": URL + "/#org"}},
         {"@type": p.get("stype", "WebPage"), "@id": URL + p["url"] + "#page", "url": URL + p["url"], "name": p["title"], "description": p["desc"], "isPartOf": {"@id": URL + "/#site"}, "dateModified": UPDATED, "inLanguage": "en-US"}]
    if p.get("ogimg"): g[-1]["primaryImageOfPage"] = {"@type": "ImageObject", "url": p["ogimg"]}
    if p.get("trail"):
        items = [("Home", "/")] + p["trail"]
        g.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": URL + u} for i, (n, u) in enumerate(items)]})
    if p.get("faqs"):
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": re.sub("<[^>]+>", "", q), "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in p["faqs"]]})
    if p.get("service"):
        g.append({"@type": "Service", "name": p["service"], "serviceType": p["service"], "provider": {"@id": URL + "/#org"},
                  "areaServed": {"@type": "State", "name": p["state"]} if p.get("state") else {"@type": "Country", "name": "United States"}, "description": p["desc"]})
    if p.get("article"):
        g.append({"@type": "Article", "headline": p["h1"], "description": p["desc"], "datePublished": UPDATED, "dateModified": UPDATED, "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@id": URL + "/#org"}, "mainEntityOfPage": URL + p["url"]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, separators=(",", ":"))

import quote_funnel, funnel_cfg
_QFS = {}
def qmode(p=None): return "leads" if (p and p.get("leads_preview")) else funnel_cfg.MODE
def qcfg(p=None):
    """Form settings for this page: the live mode from funnel_cfg.MODE, or 'leads' on the /preview/ page."""
    return funnel_cfg._cfg(V, DISCLAIMER) if qmode(p) == "leads" else funnel_cfg.cfg(V, DISCLAIMER)
def qf(p=None):
    """Smart quote form pieces: (section, head, end-of-body, bottom band)."""
    m = qmode(p)
    if m not in _QFS: _QFS[m] = quote_funnel.embed(qcfg(p), check)
    return _QFS[m]
def hero_form(p):
    """The same smart form as a card for the hero (one form per page: the page then skips the lower form section)."""
    c = qcfg(p)
    cfgjs = json.dumps({"vertical": c["vertical"], "labels": c["labels"], "trade": c["trade"], "mode": c.get("mode", "leads"), "tt": c.get("tt", "")})
    head = ('Get roofing help in 30 seconds' if c.get("mode") != "thumbtack" else 'Find roofers near you in 30 seconds')
    return (f'<!--qf--><div class="lp-card hcard" style="--brand:{c["brand_color"]};--brand2:{c["brand_color2"]};--dark:{c["dark"]}">'
            f'<p class="hc-k">{head}</p>{quote_funnel.form_html(c)}<script type="application/json" id="qf-cfg">{cfgjs}</script></div><!--/qf-->')
def qf_body(p):
    """Expert-first order (Nov 2026): the quote funnel sits further down the page (before the FAQ), not right under the hero."""
    b = p["body"]
    if not qf_on(p) or p.get("hero_form"): return b
    i = b.find(" id=faq>")
    j = b.rfind("<section", 0, i) if i > -1 else -1
    return (b[:j] + qf(p)[0] + b[j:]) if j > -1 else (b + qf(p)[0])
def qf_on(p): return bool(p.get("hero_form")) or not (p.get("legal") or p.get("noindex") or p.get("form") or p["url"] in ("/sitemap/", "/404/"))

def page(p):
    og = p.get("ogimg") or URL + "/assets/img/og.png"
    return f'''<!doctype html>
<html lang="en-US"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["desc"])}">
<link rel="canonical" href="{URL}{p["url"]}">
<meta name="robots" content="{"noindex, follow" if p.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"}">
<meta name="google-site-verification" content="{GSC_META}">
<meta property="og:type" content="{"article" if p.get("article") else "website"}"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(p["title"])}"><meta property="og:description" content="{esc(p["desc"])}"><meta property="og:url" content="{URL}{p["url"]}">
<meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13233A"><meta name="format-detection" content="telephone=yes">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/img/logo-192.png">
<link rel="preconnect" href="https://images.pexels.com"><link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="/assets/site.css?v={V}">{qf(p)[1] if qf_on(p) else ""}
<script type="application/ld+json">{schema(p)}</script>
<script src="/assets/config.js?v={V}"></script>
<script src="/assets/site.js?v={V}" defer></script>
</head>
<body class="{p.get("cls","")}">
{header(p["url"])}
<main id="main">
{p["hero"]}
{qf_body(p)}
{qf(p)[3] if qf_on(p) and not p.get("hero_form") else ""}
</main>
{footer()}
{legal.TF_SCRIPT if p.get("form") else ""}
{qf(p)[2] if qf_on(p) else ""}
</body></html>
'''

# ---------------------------------------------------------------- blocks
def sec(inner, cls="", title=None, kicker=None, intro=None, id_=None):
    if not inner: return ""
    head = f'<div class="sec-h">{f"<p class=kick>{kicker}</p>" if kicker else ""}<h2>{title}</h2>{f"<p>{intro}</p>" if intro else ""}</div>' if title else ""
    return f'<section class="sec {cls}"{f" id={id_}" if id_ else ""}><div class="wrap">{head}{inner}</div></section>'
def svc_cards(items=SERVICES):
    cta = (f'<div class="pcard card-cta"><p class="kick">Not sure what\'s wrong?</p><h3>Just call and describe it</h3><p>Tell us what your roof is doing. We\'ll connect you with a local roofing company.</p>{call_btn("btn btn-call block", None, "services-grid")}</div>' if len(items) % 3 == 2 else "")
    return '<div class="pgrid">' + "".join(
        f'<a class="pcard" href="/services/{s["slug"]}/"><div class="pc-img">{pic(s["photo"], 640, 440)}<span class="pc-ic">{ic(s["icon"],22)}</span></div><div class="pc-body"><h3>{s["name"]}</h3><p>{s["short"]}</p><span class="more">Get a roofer {ic("arrow",16)}</span></div></a>' for s in items) + cta + '</div>'
def type_cards():
    return '<div class="pgrid">' + "".join(
        f'<a class="pcard" href="/roof-types/{t["slug"]}/"><div class="pc-img">{pic(t["photo"], 640, 440)}<span class="pc-ic">{ic(t["icon"],22)}</span></div><div class="pc-body"><h3>{t["name"]}</h3><p>{t["lead"]}</p><span class="more">Roofers for this {ic("arrow",16)}</span></div></a>' for t in TYPES) + '</div>'
def steps():
    return ('<ol class="steps">'
            f'<li><span>1</span><h3>Call {PHONE}</h3><p>Tell us what\'s going on with your roof and your ZIP code. It takes about a minute.</p></li>'
            '<li><span>2</span><h3>Talk to a local roofer</h3><p>We connect your call to an independent roofing company that serves your area.</p></li>'
            '<li><span>3</span><h3>You decide</h3><p>Talk it through, set up a visit, and choose whether to go ahead. No obligation.</p></li></ol>')
def faq_html(faqs):
    return '<div class="faq">' + "".join(f'<details><summary>{q}{ic("chev",18)}</summary><p>{a}</p></details>' for q, a in faqs) + '</div>'
def tt_btn(campaign, label="See roofers on Thumbtack", cls="btn btn-tt"):
    return f'<a class="{cls}" href="{tt(campaign)}" target="_blank" rel="sponsored noopener" data-tt="{campaign}">{ic("calendar",18)}<span>{label}</span></a>'
def ttbox(campaign):
    return (f'<div class="ttbox"><div><p class="kick">Our partner</p><h3>Rather book online?</h3><p>Compare local roofers, see their reviews and past jobs, and book online through Thumbtack. If the roof is leaking now, calling is quickest.</p></div>'
            f'{tt_btn(campaign)}</div>')
def now_box():
    return (f'<div class="nowbox"><p class="kick">{ic("drop",16)} Roof leaking right now?</p><h3>Do these while you call</h3><ol>'
            '<li><b>Catch the water</b> and move belongings away.</li><li><b>Keep out</b> of rooms with a sagging ceiling.</li>'
            '<li><b>Take photos</b> of the ceiling and the roof from the ground.</li><li><b>Stay off the roof</b>, especially when it\'s wet.</li></ol>'
            f'{call_btn("btn btn-call block", None, "now-box")}</div>')
def phero(h1, lead, trail, campaign, photo, alerts=None, qs=None, kick=""):
    """Expert-first hero (Nov 2026): photo, title, lead, then 'What you're probably wondering' links."""
    if qs is None: qs = [(RPB[k]["h1"], f"/roof-problems/{k}/") for k in DEFQ]
    return ehero(h1, lead, trail, photo, kick, "", qs)
def lhero(h1, trail, sub=""):
    return f'<section class="phero lg"><div class="wrap">{crumbs(trail)}<h1>{h1}</h1>{f"<p class=lead>{sub}</p>" if sub else ""}</div></section>'
def st_slug(n): return n.lower().replace(" ", "-").replace(",", "").replace(".", "")
def problems():
    return '<div class="scenes six">' + "".join(f'<a class="scene" href="{u}"><div class="sc-img">{pic(k, 520, 620)}</div><div class="sc-cap"><h3>{t}</h3><span>{ic("arrow",16)}</span></div></a>' for t, k, u in PROBLEMS) + '</div>'
def matcher():
    chips = "".join(f'<button type="button" class="mchip" aria-pressed="false" data-k="{k}" data-route="{r}" data-url="{u}" data-name="{esc(t)}" data-msg="{esc(m)}" data-photo="{img(P[ph][0], 900, 640)}">{ic("check",15)}<span>{t}</span></button>' for k, t, ph, u, r, m in PROJECTS)
    return (f'<div class="match" id="match"><div class="m-left"><p class="kick">Step 1 of 2</p><h2>What\'s going on with your roof?</h2><p class="m-sub">Pick the one that fits and we\'ll show you the quickest way to get it handled.</p><div class="m-chips">{chips}</div></div>'
            f'<div class="m-right" aria-live="polite"><div class="m-img"><img data-mimg src="{img(P["roofer"][0], 900, 640)}" alt="Roofer installing shingles on a home" width="900" height="640" loading="lazy"></div>'
            f'<div class="m-card"><p class="kick">Step 2 of 2</p><h3 data-mtitle>Choose what fits</h3><p data-mtext>Every option is a quick call: we connect you with a local roofing company that handles it.</p>'
            f'<div class="btns m-call">{call_btn("btn btn-call", None, "matcher")}<a class="btn btn-ghost" data-mlink href="/services/">See details</a></div>'
            f'<div class="btns m-tt" hidden>{tt_btn("matcher", "Compare roofers on Thumbtack")}{call_btn("btn btn-ghost", "Or call", "matcher-alt")}</div></div></div></div>')
def pro_strip():
    items = [("roofer2", "Shingle roofs"), ("metal", "Metal roofs"), ("flat", "Flat roofs"), ("tile", "Tile roofs")]
    return '<div class="pros">' + "".join(f'<figure>{pic(k, 520, 620)}<figcaption>{t}</figcaption></figure>' for k, t in items) + '</div><p class="small center">Real photos, shown for illustration. They don\'t show a specific company.</p>'
def straight_talk():
    pts = [("Local roofing companies", "Your call goes to an independent roofing company that works in your area."),
           ("Straight answers", "Describe what your roof is doing. They'll tell you what it likely is and when they can come."),
           ("You're in charge", "No obligation. Agree any work directly with the roofing company."),
           ("Every kind of roof", "Asphalt shingle, metal, flat, tile, slate and cedar shake.")]
    return '<div class="talk">' + "".join(f'<div><span class="pipe-dot"></span><h3>{t}</h3><p>{d}</p></div>' for t, d in pts) + '</div>'
def marquee():
    row = "".join(f'<span>{ic("house",15)} {c}</span>' for c in NEIGHBORHOODS)
    return f'<div class="marq" aria-label="Some of the cities we connect homeowners in"><div class="marq-in">{row}{row}</div></div>'
def seasons():
    return '<div class="seasons">' + "".join(f'<div class="season{" now" if i == 0 else ""}"><h3>{n}</h3><p>{d}</p></div>' for i, (n, d) in enumerate(SEASONS)) + '</div>'
def story_cards(items=STORIES):
    return '<div class="stories">' + "".join(
        f'<article class="story"><div class="st-img">{pic(ph, 560, 360)}</div><div class="st-body"><p class="tag">Common situation</p><h3>{t}</h3><p>{what}</p><p class="tip"><b>What helps:</b> {tip}</p><a class="more" href="{u}">Get help with this {ic("arrow",16)}</a></div></article>'
        for t, ph, what, tip, u in items) + '</div>'
def q_cards(items, more=True):
    return ('<div class="qlist">' + "".join(f'<a class="qcard" href="/questions/{q[0]}/"><span class="qc-ic">{ic("help",20)}</span><span><b>{q[1]}</b><small>{q[5][:118].rsplit(" ", 1)[0].rstrip(".,:;")}…</small></span>{ic("arrow",16)}</a>' for q in items) + '</div>'
            + ('<p class="center"><a class="btn btn-ghost" href="/questions/">All 60 roof questions</a></p>' if more else ""))
def related_q(url, n=4):
    hits = [q for q in QS if q[4] == url]
    return (hits + [q for q in QS if q not in hits])[:n]
def jump(items):
    return '<nav class="jump" aria-label="On this page">' + "".join(f'<a href="#{i}">{t}</a>' for t, i in items) + f'<a class="j-call" href="tel:{TEL}" data-call="jump">{ic("phone",15)} Call</a></nav>'
def trust():
    return ('<div class="trust"><div>' + ic("users") + '<span><b>One call, one roofer</b>A company that serves your area</span></div><div>' + ic("siren") + '<span><b>Emergency service</b>Leaks and storm-hit roofs</span></div><div>'
            + ic("house") + '<span><b>Full service roofing</b>Repairs, new roofs, re-roofs</span></div><div>' + ic("map") + '<span><b>Nationwide</b>Availability varies by ZIP</span></div></div>')

PAGES = []
def add(**p): PAGES.append(p)

# ---------------------------------------------------------------- expert roof problem pages (Nov 2026)
RPB = {x["slug"]: x for x in RP.P}
ULV = {3: ("Get help today", "u3"), 2: ("Book a visit this week", "u2"), 1: ("Check first, plan ahead", "u1")}
def ulv(n, big=False): return f'<span class="ulv {ULV[n][1]}{" big" if big else ""}"><i></i><i></i><i></i><b>{ULV[n][0]}</b></span>'
def rp_url(x): return f"/roof-problems/{x['slug']}/"
def ticks2(items, cls="ticks"): return f'<ul class="{cls}">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
def qlist(qs):
    return ('<div class="eh-q"><p class="eh-qh">What you\'re probably wondering</p><ul>' + "".join(f'<li><a href="{k if k.startswith("/") else "#" + k}"><span>{q}</span>{ic("arrow" if k.startswith("/") else "chev",18)}</a></li>' for q, k in qs) + '</ul></div>') if qs else ""
def ehero(name, lead, trail, photo, kick="", extra="", qs=None):
    return (f'<section class="ehero"><div class="wrap eh-in"><div class="eh-img">{pic(photo, 720, 520, eager=True)}</div><div class="eh-txt">{crumbs(trail)}{f"<p class=kick>{kick}</p>" if kick else ""}<h1>{name}</h1><p class="lead">{lead}</p>{extra}{qlist(qs)}'
            f'<p class="eh-call">{ic("phone",16)} Need a roofer? <a href="tel:{TEL}" data-call="problem-hero">Call {PHONE}</a> to reach an independent local roofing company.</p></div></div></section>')
def chk(items): return '<ol class="chk">' + "".join(f'<li><span>{i+1}</span><p>{x}</p></li>' for i, x in enumerate(items)) + '</ol>'
def pat(rows): return '<div class="pat"><div class="pat-h"><span>If you see</span><span>It usually means</span><span>Next step</span></div>' + "".join(f'<div class="pat-row"><div><small>If you see</small><b>{a}</b></div><div><small>It usually means</small>{b}</div><div><small>Next step</small>{c}</div></div>' for a, b, c in rows) + '</div>'
def callcard(when, place):
    return (f'<div class="callcard2"><div><p class="kick">{ic("phone",16)} When to call a roofer</p><p>{when}</p></div>'
            f'<div class="cc2-btn">{call_btn("btn btn-call", None, place)}<small>Independent local roofing companies · No obligation</small></div></div>')
def srclist(keys): return '<ul class="srcs">' + "".join(f'<li><a href="{RP.SRC[k][2]}" target="_blank" rel="noopener">{RP.SRC[k][1]}</a> <span>{RP.SRC[k][0]}</span></li>' for k in keys) + '</ul>'
def pcards(items):
    return '<div class="tcards">' + "".join(f'<a class="tcard" href="{rp_url(x)}">{ulv(x["lv"])}<h3>{x["h1"]}</h3><p>{x["lead"].split(". ")[0].rstrip(".")}.</p><span class="more">See what to check {ic("arrow",16)}</span></a>' for x in items) + '</div>'
URG = [("u3", "Get help today", "Water coming in, a bulging ceiling, bare roof deck after wind, a tree on the roof, or a sagging roof line.", ["roof-leaking-right-now", "shingles-blown-off", "tree-fell-on-roof"]),
       ("u2", "Book a visit this week", "Leaks only in heavy rain, a growing ceiling stain, hail dents, ice dams, or water pooling on a flat roof.", ["roof-leaks-only-in-heavy-rain", "hail-hit-my-roof", "ice-dams"]),
       ("u1", "Check first, plan ahead", "Shingle grit, curling shingles, moss, nail pops, or deciding between repair and a new roof.", ["granules-in-downspouts", "curling-or-cracked-shingles", "repair-or-replace-roof"])]
def urgency():
    return '<div class="urg three">' + "".join(f'<div class="ur {k}"><h3>{t}</h3><p>{d}</p>' + "".join(f'<a href="/roof-problems/{sl}/">{RPB[sl]["h1"].rstrip("?")} {ic("arrow",14)}</a>' for sl in links) + '</div>' for k, t, d, links in URG) + '</div>'
RCN = dict(RP.CATS)
def cat_url(k): return f"/roof-problems/{k}/"
def dlink(l): return l if l.startswith("/") else (cat_url(l) if l in RCN else (f"/roof-problems/{l}/" if l else ""))
DB = {d[0]: d for d in RM.D}
def words_for(slug, cat):
    w = [d for d in RM.D if d[3] == slug]
    return (w + [d for d in RM.D if d[3] == cat and d not in w])[:6]
def words_box(ws):
    if not ws: return ""
    return ('<div class="wordsbox"><h3>' + ic("book",18) + ' Words you may hear</h3><dl>' + "".join(f'<div><dt><a href="/roof-dictionary/#{k}">{t}</a></dt><dd>{d}</dd></div>' for k, t, d, l in ws)
            + '</dl><p class="small"><a href="/roof-dictionary/">Open the full roof dictionary</a></p></div>')
def say_box(say, fix):
    s2 = re.sub(r"\[([^\]]+)\]", r'<mark>\1</mark>', say)
    return (f'<div class="two"><div class="col"><h3>{ic("check",18)} What a roofer usually does</h3>{ticks2(fix)}</div>'
            f'<div class="col saybox"><h3>{ic("phone",18)} What to tell the roofer</h3><p class="say">&ldquo;{s2}&rdquo;</p><p class="small">Fill in the highlighted parts. A clear description helps the roofer tell you what it likely involves.</p></div></div>')
def catcards(keys=None):
    keys = keys or [k for k, n in RP.CATS]
    return '<div class="catgrid">' + "".join(f'<a class="catc" href="{cat_url(k)}"><div class="cc-img">{pic(RM.CAT[k]["photo"], 480, 300)}</div><div class="cc-b"><h3>{RCN[k]}</h3><p>{RM.CAT[k]["short"]}</p><span class="more">{sum(1 for x in RP.P if x["cat"] == k)} problems explained {ic("arrow",16)}</span></div></a>' for k in keys) + '</div>'
DEFQ = ["roof-leaking-right-now", "water-stain-on-ceiling", "shingles-blown-off", "hail-hit-my-roof", "repair-or-replace-roof", "door-to-door-roofer"]

# ---------------------------------------------------------------- home
def make_home_hero(p):
    return f'''<section class="hero hero-form">
 <div class="hero-bg">{pic("roofer2", 1900, 1100, eager=True)}</div>
 <div class="wrap hero-in">
  <div class="hero-txt">
   <p class="kick live"><span class="dot"></span>Roofers near you · Nationwide</p>
   <h1>Need a roofer near you? <em>Get matched in minutes.</em></h1>
   <p class="lead">Roof leaks, storm and hail repair, new roofs and re-roofs, from independent roofing companies that serve your area.</p>
   <ul class="hero-ticks"><li>{ic("check",18)} Repairs, leaks and full replacements</li><li>{ic("check",18)} Local roofing companies near you</li><li>{ic("check",18)} No obligation to hire anyone</li></ul>
   <p class="hero-alt"><a href="#problems">What's wrong with my roof?</a><span>·</span><a href="tel:{TEL}" data-call="home-hero">Rather talk? {PHONE}</a></p>
  </div>
  <div class="hero-side">{hero_form(p)}</div>
 </div>
</section>
{marquee()}'''
home_hero = None
HOME_FAQS = [
 ("What is RingaRoofer?", "A roofing referral service. When you call, we connect you with an independent roofing company that serves your area. We don't do roofing work ourselves."),
 ("Is there a charge to call?", "No. RingaRoofer doesn't charge homeowners. You agree any work and terms directly with the roofing company."),
 ("What roofing work is covered?", "Full service roofing: repairs, leak repairs, inspections, new roofs, re-roofs and emergency service, on asphalt shingle, metal, flat, tile, slate and cedar shake roofs."),
 ("Do you cover my area?", "Our network includes independent roofing companies across the country. Availability can vary by ZIP code and type of work, so call and we'll check for you."),
 ("Are the photos your jobs?", "No. They're real photographs from Pexels and Unsplash. Ask the roofer you speak with about their own work.")] + FQ.HOME
home_body = (
 sec(trust(), "tight trustsec")
 + sec(f'<div class="nowwrap">{now_box()}</div>', "tight")
 + sec(pcards([RPB[k] for k in DEFQ]) + f'<p class="center"><a class="btn btn-ghost" href="/roof-problems/">All {len(RP.P)} roof problems {ic("arrow",16)}</a></p>', "soft", "What's going on with your roof?", "Start here", "Tap the one that matches for what to check from the ground, what it usually means and when to call.", id_="problems")
 + "__TOOLS__"
 + sec(urgency(), "", "How urgent is it?", "An honest answer", "Most roof problems aren't emergencies. Here's how roofers sort them.", id_="urgency")
 + sec(matcher(), "soft", None, id_="match-sec")
 + sec(svc_cards(), "", "Full service roofing", "Services", "From a few missing shingles to a complete re-roof, one call puts you in touch with a roofer who handles it.", id_="help")
 + sec(steps(), "soft", "How it works", "Simple", id_="how-it-works")
 + sec(type_cards(), "", "Every type of roof", "Roof types", "Asphalt shingle, metal, flat, tile, slate and cedar shake.")
 + f'<section class="band"><div class="band-bg">{pic("storm", 1800, 800)}</div><div class="wrap band-in"><p class="kick">Storm season</p><h2>Storm last night? Get the roof checked.</h2><p>High wind lifts shingles and hail bruises them, often without anything visible from the ground. Stay off the roof, photograph what you can see, and call. We\'ll connect you with a local roofer.</p><div class="btns">{call_btn("btn btn-call xl", None, "storm-band")}<a class="btn btn-ghost light" href="/services/storm-roof-repair/">Storm roof repair {ic("arrow",16)}</a></div></div></section>'
 + sec(straight_talk(), "", "Straight talk, local roofers", "Why call us")
 + sec(seasons(), "soft", "Roofing through the year", "Seasonal")
 + sec(pro_strip(), "", "Real roofs, real work", "Photos")
 + sec(story_cards(STORIES[:3]) + '<p class="center"><a class="btn btn-ghost" href="/community/">More real roof problems</a></p>', "soft", "Roof problems homeowners call about", "Sound familiar?", "Typical situations and what helps. These are examples, not reviews.")
 + sec(q_cards([QBY[k] for k in ("why-is-my-roof-leaking", "repair-or-replace-roof", "signs-you-need-a-new-roof", "how-to-tell-if-hail-hit-roof", "asphalt-shingles-vs-metal", "how-to-find-a-roofer-near-me")]), "", "Roof questions homeowners ask", "Roof Questions", "Straight answers to the questions homeowners search most.", id_="questions")
 + sec(ttbox("home"), "tight soft")
 + sec('<div class="states">' + "".join(f'<a href="/coverage/{st_slug(s[1])}/">{s[1]}</a>' for s in STATES) + '</div>', "", "Roofing help in every state", "Coverage", "Availability can vary by ZIP code.", id_="coverage")
 + sec(faq_html(HOME_FAQS), "soft", "Common questions", "FAQ", id_="faq"))
add(url="/", title="Roofers Near You | Roof Repair & New Roofs · Call (888) 261-1486 | RingaRoofer", desc="Need a roofer near you? Call (888) 261-1486 to connect with a local roofing company for roof repair, leaks, storm and hail repair, new roofs and re-roofs.",
    h1="Need a roofer near you?", hero=make_home_hero({}), body=home_body, faqs=HOME_FAQS, cls="home", ogimg=img(P["roofer2"][0], 1200, 630), hero_form=True)
# Preview of the homepage with the form in lead mode (sends to the buyer; test server until SBB_LIVE=1). Not indexed.
add(url="/preview/", title="Preview: RingaRoofer homepage with lead form", desc="Internal preview.", h1="Need a roofer near you?", hero=make_home_hero({"leads_preview": True}),
    body=home_body, faqs=[], cls="home", noindex=True, hero_form=True, leads_preview=True)

# ---------------------------------------------------------------- roofers near me (head-term ad landing page)
RNM_FAQ = [("How do I find a roofer near me?", f"Call {PHONE}. Tell us your ZIP code and what's going on with your roof, and we'll connect you with an independent roofing company that serves your area."),
           ("What should I ask a roofer before hiring?", "How long they've worked locally, who will be on the roof, what the written scope of work includes, how they protect your property, and the credentials your state requires."),
           ("Can a roofer come out this week?", "Often, yes. It depends on your area and recent weather. After storms, roofers book up quickly, so call early.")]
add(url="/roofers-near-me/", title="Roofers Near Me | Local Roofing Companies · Call (888) 261-1486 | RingaRoofer", desc="Looking for roofers near you? One call to (888) 261-1486 connects you with an independent local roofing company for repairs, leaks, inspections, new roofs and re-roofs.",
    h1="Roofers near you", trail=[("Roofers Near Me", "/roofers-near-me/")], faqs=RNM_FAQ, service="Roofing referral",
    hero=phero("Roofers near you, one call away", "Repairs, leaks, storm and hail, inspections, new roofs and re-roofs. Start with what's going on, or call and we'll connect you with an independent roofing company that serves your area.", [("Roofers Near Me", "/roofers-near-me/")], "roofers-near-me", "aerial",
               qs=[("What's going on with my roof?", "problems"), ("Is it urgent?", "urgency"), ("What do local roofers handle?", "services"), ("Before I hire a roofer", "questions"), ("Questions people ask", "faq")]),
    body=sec(pcards([RPB[k] for k in DEFQ]), "soft", "What's going on with your roof?", "Start here", "Tap the one that matches for what to check first and when to call.", id_="problems")
         + sec(urgency(), "", "How urgent is it?", "An honest answer", id_="urgency")
         + sec(svc_cards(), "soft", "What local roofers handle", "Services", id_="services") + sec(steps(), "", "How it works", "Simple")
         + sec(q_cards([QBY[k] for k in ("how-to-find-a-roofer-near-me", "questions-to-ask-a-roofer", "how-fast-can-a-roofer-come", "roofer-door-to-door")]), "", "Before you hire", "Roof Questions", id_="questions") + sec(faq_html(RNM_FAQ), "soft", "Questions", "FAQ", id_="faq") + sec(ttbox("roofers-near-me"), "tight"))

# ---------------------------------------------------------------- services
add(url="/services/", title="Roofing Services: Repair, Leaks, Inspection, Replacement & Emergency | RingaRoofer", desc="Full service roofing: roof repair, leak repair, inspections, emergency roofing, storm and hail repair, roof replacement, new roofs and re-roofs. Call (888) 261-1486.",
    h1="Roofing services", trail=[("Services", "/services/")], hero=phero("Full service roofing, one call away", "Repairs, inspections, new roofs, re-roofs and emergency service. Choose your problem below, or just call.", [("Services", "/services/")], "services", "roofer"),
    body=sec(svc_cards()) + sec(steps(), "soft", "How it works") + sec(ttbox("services"), "tight"))
GAL = ["roofer", "shingles2", "storm2", "hail", "tearoff", "inspect", "aerial", "flat2", "newroof"]
STORMY = ("storm-roof-repair", "hail-roof-repair", "emergency-roof-repair", "roof-tarping")
for s in SERVICES:
    u = f'/services/{s["slug"]}/'
    rel = [x for x in SERVICES if x is not s][:3]
    gal = [k for k in GAL if k != s["photo"]][(len(s["slug"]) % 5):][:3]
    side = f'<aside class="doc-side"><div class="sticky">{now_box()}</div></aside>'
    body = (sec(jump([("What to know", "about"), ("Photos", "photos"), ("FAQ", "faq"), ("Questions", "questions")]), "jumpsec")
            + sec('<div class="doc">' + "".join(f'<h2>{h}</h2>{b}' for h, b in s["sections"]) + '</div>' + side, "doc-wrap", id_="about")
            + sec('<div class="gal">' + "".join(f'<figure>{pic(k, 600, 440)}<figcaption>{P[k][1]}</figcaption></figure>' for k in gal) + '</div>', "soft", "Real roofs, real problems", "Photos", id_="photos")
            + sec(steps(), "", "How it works", "Simple")
            + sec(faq_html(s["faqs"]), "soft", f'{s["name"]}: common questions', "FAQ", id_="faq")
            + sec(q_cards(related_q(u)), "", "Homeowners also ask", "Roof Questions", id_="questions")
            + sec(ttbox(s["slug"] + "-box"), "tight")
            + sec(svc_cards(rel), "soft", "Related roofing services"))
    add(url=u, title=s["title"], desc=s["desc"], h1=s["h1"], trail=[("Services", "/services/"), (s["name"], u)],
        hero=phero(s["h1"], s["lead"], [("Services", "/services/"), (s["name"], u)], s["slug"], s["photo"], alerts="US" if s["slug"] in STORMY else None),
        body=body, faqs=s["faqs"], service=s["name"], ogimg=img(P[s["photo"]][0], 1200, 630))

# ---------------------------------------------------------------- roof types
add(url="/roof-types/", title="Roof Types: Shingle, Metal, Flat, Tile, Slate & Cedar | RingaRoofer", desc="Asphalt shingle, metal, flat (TPO, EPDM), tile, slate and cedar shake roofs: repairs and replacements from roofers near you. Call (888) 261-1486.",
    h1="Roof types", trail=[("Roof Types", "/roof-types/")], hero=phero("Every type of roof", "Whatever your roof is made of, one call connects you with a roofer who works with it.", [("Roof Types", "/roof-types/")], "roof-types", "shingles"),
    body=sec(type_cards()) + sec('<p class="center"><a class="btn btn-ghost" href="/library/choosing-a-roofing-material/">Compare roofing materials</a></p>', "tight"))
for t in TYPES:
    u = f'/roof-types/{t["slug"]}/'; fq = FQ.TYPES_EXTRA.get(t["slug"], [])
    add(url=u, title=t["title"], desc=t["desc"], h1=t["h1"], trail=[("Roof Types", "/roof-types/"), (t["name"], u)], faqs=fq or None, ogimg=img(P[t["photo"]][0], 1200, 630),
        hero=phero(t["h1"], t["lead"], [("Roof Types", "/roof-types/"), (t["name"], u)], "type-" + t["slug"], t["photo"]),
        body=sec(f'<div class="doc">{t["body"]}</div><aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap")
             + (sec(faq_html(fq), "soft", "Questions", "FAQ") if fq else "") + sec(svc_cards(SERVICES[:3]), "", "Popular services"), service=f'{t["name"]} repair and replacement')

# ---------------------------------------------------------------- coverage
RPHOTO = {"Northeast": "shingles2", "Southeast": "storm2", "Midwest": "hail", "South Central": "storm", "Mountain West": "metal", "West": "tile"}
by_region = {}
for code, name, reg, cities, extra in STATES: by_region.setdefault(reg, []).append(name)
cov = "".join(f'<div class="region"><div class="rg-img">{pic(RPHOTO[r], 520, 340)}</div><div><h3>{r}</h3><p>{REGIONS[r]}</p><div class="states">' + "".join(f'<a href="/coverage/{st_slug(n)}/">{n}</a>' for n in v) + '</div></div></div>' for r, v in by_region.items())
add(url="/coverage/", title="Roofers Near You, State by State | RingaRoofer Coverage", desc="RingaRoofer connects homeowners with independent roofing companies across the U.S. Find roofing help in your state. Call (888) 261-1486.",
    h1="Coverage", trail=[("Coverage", "/coverage/")], hero=phero("Roofers near you, nationwide", "Our network connects homeowners with independent roofing companies across the country. Availability can vary by ZIP code.", [("Coverage", "/coverage/")], "coverage", "aerial2", alerts="US"),
    body=sec(cov))
for code, name, reg, cities, extra in STATES:
    u = f"/coverage/{st_slug(name)}/"
    fq = [(f"Do you have roofers in {name}?", f"Yes. Our network connects homeowners across {name} with independent roofing companies. Availability can vary by ZIP code and type of work."),
          (f"How fast can a roofer come out in {name}?", "It depends on your location, the season and recent weather. After major storms roofers book up quickly, so call early.")]
    _dh, _dq = detail(code, name, cities); fq = fq + _dq
    body = (sec(f'<div class="doc"><h2>Roofing in {name}</h2><p>{extra} {REGIONS[reg]}</p>{_dh}<h2>Roofing help we connect {name} homeowners with</h2><ul class="ticks">'
                + "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a>: {s["short"]}</li>' for s in SERVICES) + '</ul>'
                + f'<h2>Areas served in {name}</h2><p>Homeowners across {name} call us, including in and around ' + ", ".join(cities[:-1]) + f' and {cities[-1]}. Call and we\'ll check availability for your ZIP code.</p>'
                + f'<h2 id="hire">Before you hire a roofer in {name}</h2><ul class="ticks"><li>Ask how long they\'ve worked in {name} and for local references.</li><li>Confirm they hold the credentials and coverage {name} requires for roofing work.</li><li>Get the scope of work in writing before work starts.</li><li>After big storms, be cautious with door-to-door crews.</li></ul></div>'
                f'<aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap")
            + sec(svc_cards(SERVICES[:3]), "soft", f"Popular roofing services in {name}") + sec(ttbox("state-" + code.lower()), "tight") + sec(faq_html(fq), "", "Questions", id_="faq"))
    body = sec(pcards([RPB[k] for k in DEFQ]), "soft", f"What's going on with your roof?", "Start here", f"The roof problems {name} homeowners search most. Tap yours for what to check and when to call.", id_="problems") + body
    # Nov 24: Search Console shows state pages ranking for "roof replacement", "roof repair", "roofer near me", "roofing contractor"
    _t = f"Roofers in {name}: Roof Repair & Replacement | RingaRoofer"
    if len(_t) > 64: _t = f"Roofers in {name}: Roof Repair & Replacement"
    add(url=u, title=_t, desc=f"Roof leaking or storm-hit in {name}? Call {PHONE} to reach a local roofer serving {cities[0]}, {cities[1]}, {cities[2]} and nearby for roof repair, leaks, storm repairs and roof replacement.",
        h1=f"Roofers in {name}", trail=[("Coverage", "/coverage/"), (name, u)],
        hero=phero(f"Roofers in {name}: what to know first", f"Roof leak, storm-hit roof or thinking about a new roof in {name}? Here's what to check, the main roof risks in {name}, and how to find a roofer who serves your area.", [("Coverage", "/coverage/"), (name, u)], "state-" + code.lower(), RPHOTO[reg],
                   qs=[("What's going on with my roof?", "problems"), (f"What are the main roof risks in {name}?", "risks"), ("What can I check from the ground?", "check-ground"), (f"Before I hire a roofer in {name}", "hire"), ("Questions people ask", "faq")], kick=name),
        body=body, faqs=fq, service="Roofing referral", state=name)

# ---------------------------------------------------------------- roof problems hub + pages
JUMPP = [("check", "Check first"), ("if-you-see", "If you see"), ("what-to-do", "What to do"), ("roofer", "What a roofer does"), ("example", "Example"), ("faq", "Questions"), ("words", "Words")]
hub = "".join(sec(f'<p class="catlead">{RM.CAT[k]["short"]} <a href="{cat_url(k)}">How this part of your roof works {ic("arrow",14)}</a></p>' + pcards([x for x in RP.P if x["cat"] == k]), "soft" if i % 2 else "", n, None, None, k) for i, (k, n) in enumerate(RP.CATS))
add(url="/roof-problems/", title="Roof Problems: Leaks, Missing Shingles, Hail, Ice Dams & More | RingaRoofer", desc="Roof leaking, shingles blown off, hail, ice dams, sagging, moss, flat-roof ponding: what to check from the ground, what it usually means and when to call a roofer.",
    h1="Roof problems", trail=[("Roof Problems", "/roof-problems/")], cls="pestpage",
    hero=ehero("What's going on with your roof?", "Pick the problem that matches. Each page shows what to check from the ground, what the signs usually mean, an example situation, and when to call a roofer. Based on public guidance from the FTC, FEMA, the Department of Energy and ENERGY STAR.", [("Roof Problems", "/roof-problems/")], "ceiling", "Roof problems",
               qs=[(n, cat_url(k)) for k, n in RP.CATS]),
    body=sec(urgency(), "tight") + hub + sec(f'<div class="dteaser"><div><p class="kick">{ic("book",16)} Roof dictionary</p><h3>Flashing? Underlayment? Pipe boot?</h3><p>{len(RM.D)} roofing words in plain English.</p></div><a class="btn btn-dark" href="/roof-dictionary/">Open the dictionary {ic("arrow",16)}</a></div>', "tight") + sec(f'<div class="srcbox"><h3>Where our information comes from</h3>{srclist(list(RP.SRC.keys()))}<p class="small">{RP.NOTE}</p></div>', "soft"))
for x in RP.P:
    u = rp_url(x); h1 = x["h1"]; trail = [("Roof Problems", "/roof-problems/"), (RCN[x["cat"]], cat_url(x["cat"])), (h1.rstrip("?"), u)]
    mx = RM.MORE.get(x["slug"], {})
    _seen = set(); allfaq = []
    for _q, _a in x["faq"] + rr_faq2.F.get(x["slug"], []):
        if _q.lower() not in _seen: _seen.add(_q.lower()); allfaq.append((_q, _a))
    rel = [y for y in RP.P if y["cat"] == x["cat"] and y["slug"] != x["slug"]][:3]
    if len(rel) < 3: rel += [y for y in RP.P if y["slug"] != x["slug"] and y not in rel][:3 - len(rel)]
    short = '<div class="shortans"><p class="kick">The short answer</p><ul>' + "".join(f"<li>{t}</li>" for t in x["short"]) + '</ul></div>'
    jump = '<nav class="jump" aria-label="On this page">' + "".join(f'<a href="#{k}">{n}</a>' for k, n in JUMPP) + '</nav>'
    body = (sec(jump, "jumpsec") + sec(short, "tight", id_="short")
            + sec(chk(x["check"]), "", "What to check first", "From the ground", "Stay off the roof. Everything here can be done from the ground, inside, or from a safe spot in the attic.", id_="check")
            + sec(pat(x["patterns"]), "soft", "If you see this, it usually means…", "Read the signs", id_="if-you-see")
            + sec(f'<div class="cols2"><div class="col"><h3>{ic("check",18)} What you can do</h3>{ticks2(x["do"])}</div><div class="col warn"><h3>{ic("x",18)} What to avoid</h3>{ticks2(x["avoid"], "xs")}</div></div>', "", "What to do now", "Practical steps", id_="what-to-do")
            + (sec(say_box(mx["say"], mx["fix"]), "soft", "What a roofer does, and what to tell them", "When you call", id_="roofer") if mx else "")
            + sec(f'<div class="story1"><p class="kick">A typical situation</p><p>{x["story"]}</p><p class="small">An example to help you recognize your own situation, not a customer review.</p></div>', "tight", id_="example")
            + sec(callcard(x["when"], "when-" + x["slug"]), "tight", id_="pro")
            + sec(faq_html(allfaq), "soft", f'{h1.rstrip("?")}: {len(allfaq)} questions people ask', "Questions people ask", id_="faq")
            + sec(words_box(words_for(x["slug"], x["cat"])), "", None, None, None, "words")
            + sec(pcards(rel), "soft", f'More about {RCN[x["cat"]].lower()}', "Keep reading", f'<a href="{cat_url(x["cat"])}">See all {RCN[x["cat"]].lower()} problems and how this part of your roof works</a>')
            + sec(f'<div class="srcbox"><h3>Sources</h3>{srclist(x["src"])}<p class="small">{RP.NOTE}</p></div>', "tight soft"))
    add(url=u, title=(f"{h1.rstrip('?')}? What to Check and When to Call | RingaRoofer" if h1.endswith("?") else f"{h1} | RingaRoofer"), desc=x["lead"][:155].rsplit(" ", 1)[0] + ("…" if len(x["lead"]) > 155 else ""),
        h1=h1, trail=trail, faqs=allfaq, cls="pestpage", article=True,
        hero=ehero(h1, x["lead"], trail, x["photo"], dict(RP.CATS)[x["cat"]], ulv(x["lv"], True),
                   qs=[("The short answer", "short"), ("What should I check first?", "check"), ("What do the signs mean?", "if-you-see"), ("What can I do right now?", "what-to-do"), ("What will a roofer do?", "roofer"), ("When do I need a roofer?", "pro"), ("Questions people ask", "faq")]),
        body=body)

# ---------------------------------------------------------------- community, library, how it works, contact
add(url="/community/", title="Real Roof Problems Homeowners Call About | RingaRoofer", desc="Common roof problems, from ceiling stains and wind-blown shingles to hail and worn-out roofs, and what helps in each.",
    h1="Real roof problems", trail=[("Real Problems", "/community/")], hero=phero("Real roof problems homeowners call about", "Typical situations and what helps. These are examples to help you recognize your own, not customer reviews.", [("Real Problems", "/community/")], "community", "oldroof"),
    body=sec(story_cards()) + sec(seasons(), "soft", "Roofing through the year", "Seasonal"))
add(url="/how-it-works/", title="How RingaRoofer Works | One Call, One Local Roofer", desc="How RingaRoofer works: call, describe your roof problem and ZIP code, and we connect you with an independent roofing company serving your area.",
    h1="How it works", trail=[("How It Works", "/how-it-works/")], hero=phero("One call, one local roofer", "Here's exactly what happens when you call RingaRoofer.", [("How It Works", "/how-it-works/")], "how-it-works", "edge"),
    body=sec(steps()) + sec(straight_talk(), "soft") + sec('<div class="doc"><h2>What RingaRoofer is</h2><p>A referral service. We don\'t do roofing work, and we don\'t charge homeowners. Roofing companies in our network pay us for connecting them with homeowners who need roofing help.</p>'
        '<h2>Who you\'ll speak with</h2><p>An independent roofing company that serves your area. They discuss the job, set up a visit, and agree any work and terms directly with you.</p>'
        '<h2>Booking online</h2><p>If you\'d rather book online, you can compare roofers on Thumbtack, our partner. RingaRoofer may be paid when you use Thumbtack through our links. Thumbtack is a separate company.</p>'
        '<h2>Your choice, always</h2><p>You\'re never obliged to hire anyone. To stop calls, see our <a href="/do-not-call/">Do Not Call</a> page.</p></div>'), stype="AboutPage")
add(url="/library/", title="Roof Library: Leaks, New Roofs, Materials & Hail | RingaRoofer", desc="Plain-English roofing help: what to do when the roof leaks, signs you need a new roof, how long roofs last, repair or replace, materials and hail checklists.",
    h1="Roof Library", trail=[("Roof Library", "/library/")], hero=phero("Roof Library", "Plain-English roofing help for homeowners.", [("Roof Library", "/library/")], "library", "shingles2"),
    body=sec('<div class="pgrid">' + "".join(f'<a class="pcard" href="/library/{a["slug"]}/"><div class="pc-img">{pic(a["photo"], 640, 440)}</div><div class="pc-body"><h3>{a["h1"]}</h3><p>{a["lead"]}</p><span class="more">Read {ic("arrow",16)}</span></div></a>' for a in ARTICLES) + '</div>'))
for a in ARTICLES:
    u = f'/library/{a["slug"]}/'
    add(url=u, title=a["title"], desc=a["desc"], h1=a["h1"], trail=[("Roof Library", "/library/"), (a["h1"], u)], article=True, ogimg=img(P[a["photo"]][0], 1200, 630),
        hero=phero(a["h1"], a["lead"], [("Roof Library", "/library/"), (a["h1"], u)], "library-" + a["slug"], a["photo"]),
        body=sec(f'<div class="doc">{a["body"]}</div><aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap"))
add(url="/contact/", title="Request a Callback From a Roofer | RingaRoofer", desc="Call (888) 261-1486 or request a callback. RingaRoofer connects you with an independent roofing company serving your area.",
    h1="Request a callback", trail=[("Request a Callback", "/contact/")], form=True,
    hero=lhero("Request a callback", [("Request a Callback", "/contact/")], "The quickest way is to call. Prefer a callback? Fill in the form and a roofing company serving your area will reach out."),
    body=sec(legal.FORM, "soft"))

# ---------------------------------------------------------------- roof questions (our editorial answers)
qhub = "".join(sec(q_cards([q for q in QS if q[2] == k], more=False), "soft" if i % 2 else "", n, None, None, k) for i, (k, n) in enumerate(QCATS))
qnav = '<nav class="jump qjump" aria-label="Topics">' + "".join(f'<a href="#{k}">{n}</a>' for k, n in QCATS) + '</nav>'
add(url="/questions/", title="Roof Questions: Straight Answers for Homeowners | RingaRoofer", desc="Answers to the roofing questions homeowners search most: leaks, repair or replace, new roofs, storms and hail, materials, inspections and hiring a roofer.",
    h1="Roof Questions", trail=[("Roof Questions", "/questions/")], hero=lhero("Roof questions, straight answers", [("Roof Questions", "/questions/")], "60 answers to the questions homeowners search most. Need a roofer now? Call " + PHONE + "."),
    body=sec(qnav, "jumpsec") + qhub)
CATN = dict(QCATS)
for slug, qq, cat, ph, link, short, pts in QS:
    u = f"/questions/{slug}/"
    same = [q for q in QS if q[2] == cat and q[0] != slug][:4]
    svc_name = next((x["name"] for x in SERVICES if f'/services/{x["slug"]}/' == link), None) or next((t["name"] for t in TYPES if f'/roof-types/{t["slug"]}/' == link), None) or ("Roofers near you" if link == "/roofers-near-me/" else "Roof Library")
    body = sec(f'<div class="doc qa"><p class="qa-tag">{ic("chat",16)} Answered by RingaRoofer · {CATN[cat]}</p><p class="qa-short">{short}</p><h2>What to know</h2><ul class="ticks">' + "".join(f"<li>{p}</li>" for p in pts) + '</ul>'
               f'<div class="qa-cta"><div><b>Need a roofer for this?</b><span>One call connects you with an independent roofing company that serves your area.</span></div>{call_btn("btn btn-call", None, "question-" + slug)}</div>'
               f'<p class="small">General information for homeowners, not a substitute for a roofer looking at your roof. More on this: <a href="{link}">{svc_name}</a>.</p></div>'
               f'<aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap") + sec(q_cards(same, more=True), "soft", f"More about {CATN[cat].lower()}", "Roof Questions")
    add(url=u, title=f"{qq} | RingaRoofer", desc=(short[:155].rsplit(" ", 1)[0] + "…") if len(short) > 155 else short, h1=qq, trail=[("Roof Questions", "/questions/"), (qq, u)], article=True,
        faqs=[(qq, short)], ogimg=img(P[ph][0], 1200, 630),
        hero=phero(qq, short, [("Roof Questions", "/questions/"), (qq, u)], "question-" + slug, ph), body=body)

for lp in legal.PAGES:
    add(url=lp["url"], title=lp["title"] + " | RingaRoofer", desc=lp["desc"], h1=lp["h1"], trail=[(lp["h1"], lp["url"])], legal=True,
        hero=lhero(lp["h1"], [(lp["h1"], lp["url"])], "Last updated October 3, 2026"), body=sec(f'<div class="doc legal">{lp["body"]}</div>'))

# ---------------------------------------------------------------- category pages, roof dictionary, tools, roofing pros (Nov 2026)
for k, n in RP.CATS:
    c = RM.CAT[k]; u = cat_url(k); items = [x for x in RP.P if x["cat"] == k]; trail = [("Roof Problems", "/roof-problems/"), (n, u)]
    ws = [d for d in RM.D if d[3] == k or d[3] in {x["slug"] for x in items}][:8]
    body = (sec('<nav class="jump" aria-label="On this page"><a href="#problems">Problems</a><a href="#how">How it works</a><a href="#faq">Questions</a><a href="#words">Words</a></nav>', "jumpsec")
            + sec(pcards(items), "", f"{n}: pick your problem", "Start here", "Each one shows what to check from the ground, what it usually means, what a roofer does, and when to call.", id_="problems")
            + sec('<div class="doc howdoc">' + "".join(f"<p>{t}</p>" for t in c["how"]) + '</div>', "soft", "How this part of your roof works", "The basics", id_="how")
            + sec(callcard("Call when water is coming in, shingles or panels are missing, something hit the roof, or a problem keeps coming back.", "cat-" + k), "tight")
            + sec(faq_html(c["faq"]), "soft", f"{n}: questions people ask", "FAQ", id_="faq")
            + sec(words_box(ws), "", None, None, None, "words")
            + sec(catcards([o for o, _ in RP.CATS if o != k]), "soft", "Other roof problems", "Keep exploring"))
    add(url=u, title=f"{n}: Roof Problems, Checks and When to Call | RingaRoofer", desc=c["lead"][:155].rsplit(" ", 1)[0] + ("…" if len(c["lead"]) > 155 else ""),
        h1=c["h1"], trail=trail, faqs=c["faq"], cls="pestpage", article=True,
        hero=ehero(c["h1"], c["lead"], trail, c["photo"], "Roof Problems", "", qs=[(x["h1"], rp_url(x)) for x in items] + [("How does this part of my roof work?", "how"), ("Questions people ask", "faq")]),
        body=body)

_L = sorted({d[1][0].upper() for d in RM.D})
_dict = '<nav class="jump az" aria-label="Letters">' + "".join(f'<a href="#letter-{l}">{l}</a>' for l in _L) + '</nav>'
_body = "".join(f'<div class="dgroup" id="letter-{l}"><h2>{l}</h2><dl class="dict">' + "".join(f'<div id="{k}"><dt>{t}</dt><dd>{d}' + (f' <a href="{dlink(lk)}">Related help {ic("arrow",14)}</a>' if lk else "") + '</dd></div>' for k, t, d, lk in sorted(RM.D, key=lambda z: z[1].lower()) if t[0].upper() == l) + '</dl></div>' for l in _L)
add(url="/roof-dictionary/", title="Roof Dictionary: Plain-English Roofing Terms | RingaRoofer", desc=f"{len(RM.D)} roofing terms explained in plain English, from flashing and underlayment to pipe boots, ice dams and roofing squares.",
    h1="Roof dictionary", trail=[("Roof Dictionary", "/roof-dictionary/")], cls="pestpage", article=True,
    hero=ehero("Roof dictionary", f"{len(RM.D)} roofing words in plain English, so you can follow what a roofer tells you. Each one links to the help page where it matters most.", [("Roof Dictionary", "/roof-dictionary/")], "shingles", "Plain English",
               qs=[("What's flashing?", "/roof-dictionary/#flashing"), ("What's underlayment?", "/roof-dictionary/#underlayment"), ("What's a pipe boot?", "/roof-dictionary/#pipe-boot"), ("What's a roofing square?", "/roof-dictionary/#square"), ("What's an ice dam?", "/roof-dictionary/#ice-dam")]),
    body=sec(_dict, "jumpsec") + sec(_body, "") + sec(catcards(), "soft", "Roof help by problem type", "Keep exploring"))

TJS = f'<script src="/assets/tools.js?v={V}" defer></script>'
TOOLS = [("roof-pitch-calculator", "Roof pitch calculator", "Turn rise and run into a pitch like 6/12, the angle in degrees, and what that steepness means.", "aerial"),
         ("roof-size-calculator", "Roof size calculator", "Rough roof area and roofing squares from your house's length, width, overhang and pitch.", "aerial2"),
         ("storm-roof-notes", "After-storm roof notes", "A printable checklist and notes sheet for after a storm: what you saw, photos taken, and who you spoke to.", "storm")]
def tool_cards(skip=None):
    return '<div class="catgrid">' + "".join(f'<a class="catc" href="/tools/{k}/"><div class="cc-img">{pic(ph, 480, 300)}</div><div class="cc-b"><h3>{n}</h3><p>{d}</p><span class="more">Open the tool {ic("arrow",16)}</span></div></a>' for k, n, d, ph in TOOLS if k != skip) + '</div>'
add(url="/tools/", title="Roof Tools for Homeowners: Pitch, Roof Size & After-Storm Notes | RingaRoofer", desc="Roof tools for homeowners: roof pitch calculator, roof size and squares calculator, and a printable after-storm roof notes sheet.",
    h1="Roof tools", trail=[("Roof Tools", "/tools/")], cls="pestpage",
    hero=ehero("Roof tools for homeowners", "Small tools that answer real roofing questions: how steep is my roof, roughly how big is it, and what should I write down after a storm.", [("Roof Tools", "/tools/")], "aerial", "Tools",
               qs=[(n, f"/tools/{k}/") for k, n, d, ph in TOOLS] + [("What does that roofing word mean?", "/roof-dictionary/")]),
    body=sec(tool_cards(), "") + sec(catcards(), "soft", "Roof help by problem type", "Keep exploring"))

_pfaq = [("What does 6/12 pitch mean?", "The roof rises 6 inches for every 12 inches it runs horizontally."),
         ("How do I find my roof's pitch without going on the roof?", "From the attic, measure 12 inches level along the bottom of a rafter, then measure straight up to the rafter. Or ask your roofer; it's often on old plans."),
         ("What pitch is too flat for shingles?", "Shingles generally need some slope. Very flat roofs use membranes like TPO, EPDM or modified bitumen instead."),
         ("Why does pitch matter?", "It affects which materials work, how water drains, how much material is needed, and the safety setup roofers use."),
         ("Is a steep roof harder to work on?", "Yes. Steep roofs need extra safety gear, which roofers plan for."),
         ("Can I walk on my roof to measure it?", "It's safer not to. Measure from the attic or the ground, and let a roofer go up.")]
_pform = ('<div class="toolbox" id="pitchcalc"><div class="tb-grid"><label>Rise (inches)<input id="pc-rise" type="number" min="0" max="36" step="0.5" value="6" inputmode="decimal"></label><label>Run (inches)<input id="pc-run" type="number" min="1" max="48" step="0.5" value="12" inputmode="decimal"></label></div>'
          '<div class="chips"><span>Common pitches:</span>' + "".join(f'<button type="button" class="chip" data-rise="{r}">{r}/12</button>' for r in (2, 4, 6, 8, 10, 12)) + '</div>'
          '<div class="lc-out" id="pc-out" hidden aria-live="polite"><div><b id="pc-p">6/12</b><span>pitch</span></div><div><b id="pc-d">0</b><span>angle</span></div><div><b id="pc-f">0</b><span>area multiplier</span></div></div><p id="pc-n" class="pc-n"></p>'
          '<p class="small">The area multiplier turns flat footprint into actual sloped roof area. It\'s simple geometry; your roofer measures on site.</p></div>')
add(url="/tools/roof-pitch-calculator/", title="Roof Pitch Calculator: Rise, Run, Angle & What It Means | RingaRoofer", desc="Work out your roof pitch (like 6/12), its angle in degrees and its area multiplier, and what that steepness means for materials and safety.",
    h1="Roof pitch calculator", trail=[("Roof Tools", "/tools/"), ("Roof pitch calculator", "/tools/roof-pitch-calculator/")], cls="pestpage", faqs=_pfaq, article=True,
    hero=ehero("How steep is my roof?", "Enter the rise and run to get the pitch, the angle in degrees, and what that steepness usually means.", [("Roof Tools", "/tools/"), ("Roof pitch calculator", "/tools/roof-pitch-calculator/")], "aerial", "Tool",
               qs=[("Work out my pitch", "tool"), ("How do I measure without going on the roof?", "faq"), ("How big is my roof?", "/tools/roof-size-calculator/")]),
    body=sec(_pform, "", "Roof pitch", "Calculator", id_="tool") + sec(faq_html(_pfaq), "soft", "Questions people ask", "FAQ", id_="faq") + sec(tool_cards("roof-pitch-calculator"), "", "More tools") + TJS)

_sfaq = [("What is a roofing square?", "100 square feet of roof. Roofers talk about roof size in squares."),
         ("Why is my roof bigger than my house's footprint?", "A sloped roof has more surface than the flat area under it, plus the overhang past the walls."),
         ("How accurate is this?", "It's a rough figure for a simple roof. Dormers, valleys, multiple levels and porches change it. A roofer measures on site."),
         ("Does the garage count?", "If it's under the same roof, include it in the length and width. Measure separate roofs separately."),
         ("Why do roofers order extra material?", "Cuts at valleys, hips, edges and waste mean a roof needs more material than its exact area."),
         ("Where do I get my house's length and width?", "Measure outside walls with a tape, or check your property records or plans.")]
_sform = ('<div class="toolbox" id="sizecalc"><div class="tb-grid"><label>House length (feet)<input id="sc-l" type="number" min="0" max="400" value="50" inputmode="decimal"></label><label>House width (feet)<input id="sc-w" type="number" min="0" max="400" value="30" inputmode="decimal"></label>'
          '<label>Overhang past the walls (inches)<input id="sc-oh" type="number" min="0" max="48" value="12" inputmode="decimal"></label><label>Pitch (rise per 12)<select id="sc-p">' + "".join(f'<option value="{r}"{" selected" if r == 6 else ""}>{r}/12</option>' for r in range(0, 13)) + '</select></label></div>'
          '<div class="lc-out" id="sc-out" hidden aria-live="polite"><div><b id="sc-a">0</b><span>sq ft of roof</span></div><div><b id="sc-q">0</b><span>roofing squares</span></div><div><b id="sc-fp">0</b><span>sq ft footprint</span></div></div>'
          '<p class="small">A rough figure for a simple roof shape. Not sure of the pitch? Use the <a href="/tools/roof-pitch-calculator/">pitch calculator</a>.</p></div>')
add(url="/tools/roof-size-calculator/", title="Roof Size Calculator: Square Feet & Roofing Squares | RingaRoofer", desc="Rough roof area and roofing squares from your house's length, width, overhang and pitch. Plain-English help for talking with a roofer.",
    h1="Roof size calculator", trail=[("Roof Tools", "/tools/"), ("Roof size calculator", "/tools/roof-size-calculator/")], cls="pestpage", faqs=_sfaq, article=True,
    hero=ehero("How big is my roof?", "Enter your house's length and width, the overhang and the pitch, and see the rough roof area and how many roofing squares that is.", [("Roof Tools", "/tools/"), ("Roof size calculator", "/tools/roof-size-calculator/")], "aerial2", "Tool",
               qs=[("Work out my roof size", "tool"), ("What's a roofing square?", "faq"), ("How steep is my roof?", "/tools/roof-pitch-calculator/")]),
    body=sec(_sform, "", "Roof size", "Calculator", id_="tool") + sec(faq_html(_sfaq), "soft", "Questions people ask", "FAQ", id_="faq") + sec(tool_cards("roof-size-calculator"), "", "More tools") + TJS)

_nrows = [("Storm date and time", ""), ("What happened", "wind, hail size, tree, heavy rain"), ("What I saw from the ground", "missing shingles, dents on vents, debris"), ("Inside: rooms with drips or stains", ""),
          ("Photos taken (roof, yard, inside, hail)", ""), ("Temporary cover (tarp) by", ""), ("Roofer I called", f"or RingaRoofer {PHONE}"), ("Agreement in writing?", "yes / no, date")]
_card = ('<div class="scard" id="card"><div class="sc-h"><b>After-storm roof notes</b><span>Fill in as soon as it\'s safe. Keep with your home papers.</span></div><div class="sc-rows">'
         + "".join(f'<label><span>{n}</span><input placeholder="{p}"></label>' for n, p in _nrows)
         + '</div><ol class="sc-steps"><li><b>Stay off the roof.</b> Check from the ground and from inside.</li><li><b>Take photos</b> before anything is moved or covered.</li><li><b>Before you hire:</b> get it in writing and don\'t pay in full up front, as the FTC advises.</li></ol>'
         + f'<p class="sc-f">RingaRoofer.com · {PHONE}</p></div>'
         f'<p class="center no-print"><button class="btn btn-call" type="button" data-printcard>{ic("phone",18)}<span>Print my notes</span></button></p><p class="small center no-print">Type in the boxes, then print. Nothing you type is stored or sent anywhere.</p>')
_nfaq = [("What should I photograph after a storm?", "The roof from several sides from the ground, anything on the ground that came off the roof, hailstones next to a coin, and any ceiling stains or drips inside."),
         ("Should I go on the roof after a storm?", "No. Check from the ground and from inside. Wet, steep or broken roofs are dangerous."),
         ("When should I call a roofer?", "If water is coming in, shingles or panels are missing, a tree hit the roof, or you see dents and grit after hail."),
         ("How do I spot a storm scam?", "The FTC warns about door-to-door offers, pressure to sign fast, and demands for full payment up front."),
         ("Why write things down?", "Notes and photos made right away are easier to rely on later, when you talk to roofers and others.")]
add(url="/tools/storm-roof-notes/", title="After-Storm Roof Checklist & Notes (Printable) | RingaRoofer", desc="A printable after-storm roof checklist and notes sheet: what to check from the ground, what to photograph, and what to get in writing before you hire.",
    h1="After-storm roof notes", trail=[("Roof Tools", "/tools/"), ("After-storm roof notes", "/tools/storm-roof-notes/")], cls="pestpage printcard", faqs=_nfaq, article=True,
    hero=ehero("After a storm: what to check and write down", "Check from the ground, take photos, note what you saw, and get everything in writing before you hire. Fill in this sheet and print it.", [("Roof Tools", "/tools/"), ("After-storm roof notes", "/tools/storm-roof-notes/")], "storm", "Printable",
               qs=[("Fill in my notes", "card"), ("What should I photograph?", "faq"), ("Shingles blown off?", "/roof-problems/shingles-blown-off/"), ("Did hail hit my roof?", "/roof-problems/hail-hit-my-roof/")]),
    body=sec(_card, "", "Your after-storm notes", "Fill in and print", id_="cardsec") + sec(f'<div class="srcbox"><h3>Sources</h3>{srclist(["ftc-storm", "fema-wind"])}</div>', "tight") + sec(faq_html(_nfaq), "soft", "Questions people ask", "FAQ", id_="faq") + sec(tool_cards("storm-roof-notes"), "", "More tools") + TJS)

_svc = ["Roof repair", "Leak repair", "Storm and hail repair", "Emergency tarping", "Roof replacement", "Shingle roofs", "Metal roofs", "Tile roofs", "Flat roofs", "Attic ventilation", "Roof checks for home buyers", "Emergency calls"]
_proform = ('<form class="pro-form" id="pro-form" novalidate><div class="fg">'
            '<label>Company name<input name="company" required autocomplete="organization"></label><label>Your name<input name="contact" required autocomplete="name"></label>'
            '<label>Phone<input name="phone" type="tel" inputmode="tel" required autocomplete="tel" placeholder="(555) 555-5555"></label><label>Email<input name="email" type="email" required autocomplete="email"></label>'
            '<label>Website <span class="opt">(optional)</span><input name="site" type="url" placeholder="https://"></label><label>State(s) you work in<input name="states" placeholder="e.g. TX, OK"></label>'
            '<label class="full">Cities, counties or ZIP codes you serve<textarea name="areas" rows="2" maxlength="600"></textarea></label>'
            '<fieldset class="full"><legend>Work you take on</legend><div class="cbx">' + "".join(f'<label><input type="checkbox" name="services" value="{v}"> {v}</label>' for v in _svc) + '</div></fieldset>'
            '<label>Do you take after-hours calls?<select name="emergency"><option>Yes, nights and weekends</option><option>Evenings only</option><option>Business hours only</option></select></label>'
            '<label>Calls you could take per day<select name="capacity"><option>1–3</option><option>4–10</option><option>11–25</option><option>More than 25</option></select></label>'
            '<label>State contractor registration number <span class="opt">(if your state issues one)</span><input name="state_number"></label><label>Years in business<input name="years" inputmode="numeric"></label>'
            '<label class="full">Anything else? <span class="opt">(optional)</span><textarea name="notes" rows="3" maxlength="1000"></textarea></label>'
            '<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<label class="full agree"><input type="checkbox" name="agree" value="yes"> I\'m authorized to share these details for my company, and RingaRoofer may contact me by phone or email about working together.</label>'
            '</div><button class="btn btn-call" type="submit">Send my details</button><p class="pro-msg" id="pro-msg" hidden aria-live="polite"></p></form>')
_profaq = [("What is RingaRoofer?", "A referral service. Homeowners call us, and we connect each call to an independent roofing company that serves their area."),
           ("What kind of calls would I get?", "Homeowners calling about the roofing work you tell us you take on, in the areas you serve. We don't promise a set number of calls; volume depends on your area and the season."),
           ("Do homeowners pay RingaRoofer?", "No. Roofing companies in our network pay for the connections, on terms agreed with each company."),
           ("Who agrees the work with the homeowner?", "You do, directly. We don't set your terms or do the work."),
           ("What do you look for in a roofing company?", "A real local business that answers its phone, serves the areas it lists, does the work it says it does, and holds the credentials and coverage its state and city require."),
           ("What happens after I send my details?", "We review them and reach out by phone or email to talk through areas, services and terms. There's no obligation.")]
add(url="/for-roofing-pros/", title="For Roofing Companies: Get Homeowner Calls in Your Area | RingaRoofer", desc="Roofing companies: tell us where you work and what you take on. RingaRoofer connects homeowner calls to independent local roofing companies.",
    h1="For roofing pros", trail=[("For Roofing Pros", "/for-roofing-pros/")], cls="pestpage", faqs=_profaq, form=True,
    hero=ehero("Roofing company? Get homeowner calls in your area", "Homeowners use RingaRoofer to find a roofer. If you serve their area and take on the work they need, we can connect their calls to you.", [("For Roofing Pros", "/for-roofing-pros/")], "roofer", "For roofing companies",
               qs=[("How does it work?", "how"), ("What do you look for?", "faq"), ("Send my details", "apply")]),
    body=sec('<ol class="steps"><li><span>1</span><h3>Tell us your areas and services</h3><p>Where you work, what you take on, and when you answer the phone.</p></li><li><span>2</span><h3>We talk it through</h3><p>A call or email to agree areas, services and terms. No obligation.</p></li><li><span>3</span><h3>Homeowners call, you answer</h3><p>Calls from homeowners in your areas are connected to your phone. You agree the work with them directly.</p></li></ol>', "", "How it works", "Simple", id_="how")
         + sec(_proform, "soft", "Send your details", "Apply", "Takes about two minutes. We'll reach out by phone or email.", id_="apply")
         + sec(faq_html(_profaq), "", "Questions roofing companies ask", "FAQ", id_="faq") + TJS)

for _p in PAGES:
    if _p["url"] == "/": _p["body"] = _p["body"].replace("__TOOLS__", sec(tool_cards(), "", "Homeowner tools", "Handy tools", "Work out your roof's pitch and size, and print an after-storm checklist. Plus a plain-English roof dictionary.", id_="tools") + sec(f'<div class="dteaser"><div><p class="kick">{ic("book",16)} Roof dictionary</p><h3>Flashing? Underlayment? Pipe boot?</h3><p>{len(RM.D)} roofing words in plain English.</p></div><a class="btn btn-dark" href="/roof-dictionary/">Open the dictionary {ic("arrow",16)}</a></div>', "tight"))

def sitemap_page():
    groups = {"Main": [], "Roof Problems & Tools": [], "Services": [], "Roof Types": [], "Coverage": [], "Roof Library": [], "Legal": []}
    for p in PAGES:
        if p.get("noindex"): continue
        u = p["url"]; k = ("Legal" if p.get("legal") else "Roof Problems & Tools" if u.startswith(("/roof-problems", "/roof-dictionary", "/tools", "/for-roofing-pros")) else "Services" if u.startswith("/services") else "Roof Types" if u.startswith("/roof-types") else "Coverage" if u.startswith("/coverage") else "Roof Library" if u.startswith(("/library", "/questions")) else "Main")
        groups[k].append(f'<li><a href="{u}">{p["h1"]}</a></li>')
    return sec('<div class="smap">' + "".join(f'<div><h2>{k}</h2><ul>{"".join(v)}</ul></div>' for k, v in groups.items()) + '</div>')
add(url="/sitemap/", title="Site Map | RingaRoofer", desc="All pages on RingaRoofer.com.", h1="Site map", trail=[("Site Map", "/sitemap/")], hero=lhero("Site map", [("Site Map", "/sitemap/")]), body="__SMAP__")

# ---------------------------------------------------------------- compliance (build fails on any hit)





# ---------------------------------------------------------------- guide (guidekit)
import guidekit, g_home
_GD = g_home.ROOF
add(url='/roof-problem-guide/', title='Roof Problem Guide: Leaks, Hail, Wind, Missing Shingles & Sagging | RingARoofer', desc='Identify roof problems: leaks, wind-lifted and hail-hit shingles, worn shingles, sagging, flashing failure, attic warning signs and moss. Repair or replace, and when to call a roofer.', h1='Roof problem guide', trail=[('Roof Problem Guide', '/roof-problem-guide/')], article=True, faqs=_GD["faq"], cls="guidepage",
    hero=phero('Roof problem guide', 'Spot roof problems from the ground and the attic, see how urgent each one is and what to do now.', [('Roof Problem Guide', '/roof-problem-guide/')], 'roof-guide', 'storm'),
    body=guidekit.render(_GD, lambda k, w, h: pic(k, w, h), lambda place, cls: call_btn(cls, None, place), {'dark': '#13253F', 'accent': '#1F6FB2', 'soft': '#EAF4FB', 'line': '#DCE5EF', 'ink': '#13202E', 'ink2': '#3E4E60', 'muted': '#66768A', 'cta': '#F26B1D', 'cta2': '#D85A12', 'warm': '#FFF3EC', 'bg': '#F3F7FB', 'hi': '#5DB7E8', 'pop': '#FFB547', 'ctaink': '#fff'},
        dict(brand='RingARoofer', phone=PHONE, url=URL.split("//")[-1].strip("/"), title='Roof problem guide', lead='Spot roof problems from the ground and the attic, see how urgent each one is and what to do now.',
             cover_photo='storm', pdf='/assets/guides/roof-problem-guide.pdf', disclaimer=_GD.get("footnote", "") + " Your call connects you with an independent local company. We are a referral service and do not perform the work.")))
# ---------------------------------------------------------------- end guide

BANNED = ["free", "estimat", "licens", "insur", "bond", "cheap", "low", "afford", "discount", "budget", "bargain", "inexpensive", "gutter", "window",
          "siding", "deal", "save", "saving", "price", "pricing", "cost", "rate", "rates", "quote", "damage", "warrant", "claim", "financ", "professional",
          "skylight", "chimney", "solar", "fascia", "soffit", "best", "certif", "guarant", "septic"]
ALLOW = {"lowell", "freeze", "freezes", "freezing", "below", "allow", "allowed", "follow", "flow", "yellow", "slow", "shallow", "rather", "separate", "moderate", "accurate",
         "corporate", "generate", "operate", "operated", "operates", "operating", "cooperate"}
LEGAL_OK = ("warrant", "rate", "insur", "claim", "cost", "save", "financ", "licens", "damage", "deal", "bond", "window", "guarant", "certif", "quote", "professional", "wildlife", "pric", "pricing", "price")
def check(html, where, legal_page=False):
    html = re.sub(r"<!--qf-->[\s\S]*?<!--/qf-->", " ", html)
    txt = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html)
    txt = re.sub(r"<[^>]+>", " ", txt).replace("&amp;", "&").replace(DISCLAIMER, " ")
    if "24/7" in txt or "24-7" in txt: raise SystemExit(f"24/7 claim on {where}")
    words = re.findall(r"[a-z]+", txt.lower())
    hits = sorted({w for w in words for b in BANNED if w.startswith(b) and w not in ALLOW and not (legal_page and b in LEGAL_OK)})
    if "rated" in words: hits.append("rated")
    if hits: raise SystemExit(f"Banned wording on {where}: {hits}")

def main():
    for n in (os.listdir(OUT) if os.path.isdir(OUT) else []):
        if n != "assets": (shutil.rmtree if os.path.isdir(os.path.join(OUT, n)) else os.remove)(os.path.join(OUT, n))
    smap = sitemap_page()
    for p in PAGES:
        if p["body"] == "__SMAP__": p["body"] = smap
        html = page(p); check(html, p["url"], p.get("legal"))
        d = os.path.join(OUT, p["url"].strip("/")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(html)
    nf = dict(url="/404/", title="Page not found | RingaRoofer", desc="Page not found.", h1="Page not found", noindex=True,
              hero=phero("We couldn't find that page", "It may have moved. The quickest way to get roofing help is to call.", [], "404", "house"), body=sec(svc_cards(SERVICES[:3])))
    open(os.path.join(OUT, "404.html"), "w").write(page(nf).replace(f'<link rel="canonical" href="{URL}/404/">', ""))
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        f'<url><loc>{URL}{p["url"]}</loc><lastmod>{UPDATED}</lastmod></url>' for p in PAGES if not p.get("noindex")) + "\n</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /preview/\nDisallow: /leads-admin/\nDisallow: /publisher-spec/\nDisallow: /publisher-console/\n\nUser-agent: AhrefsBot\nDisallow: /\nUser-agent: SemrushBot\nDisallow: /\nUser-agent: MJ12bot\nDisallow: /\nUser-agent: DotBot\nDisallow: /\n\nSitemap: {URL}/sitemap.xml\n")
    open(os.path.join(OUT, "llms.txt"), "w").write(f"# {BRAND}\n\n> {BRAND} (ringaroofer.com) is a roofing referral service for U.S. homeowners. Calling {PHONE} connects a homeowner with an independent roofing company that serves their area, for roof repair, leak repair, roof inspections, storm and hail repair, emergency roofing and tarping, roof replacement, new roofs and re-roofs on shingle, metal, flat, tile, slate and cedar shake roofs. It does not do roofing work and does not charge homeowners.\n\n## Pages\n" + "\n".join(f"- [{p['h1']}]({URL}{p['url']}): {p['desc']}" for p in PAGES if not p.get("legal") and not p.get("noindex")) + "\n")
    open(os.path.join(OUT, "google6cdd134560bcda8a.html"), "w").write("google-site-verification: google6cdd134560bcda8a.html")
    open(os.path.join(OUT, "BingSiteAuth.xml"), "w").write('<?xml version="1.0"?>\n<users>\n\t<user>143504FD65C9CD8E8439BFD5BD0E4177</user>\n</users>\n')
    open(os.path.join(OUT, "_redirects"), "w").write(legal.REDIRECTS)
    open(os.path.join(OUT, "_headers"), "w").write(legal.HEADERS)
    shutil.copy(os.path.join(ROOT, "favicon.svg"), os.path.join(OUT, "favicon.svg"))
    import quote_funnel, funnel_cfg
    if funnel_cfg.MODE == "leads" and not funnel_cfg.PARTNERS: print("WARNING: funnel_cfg.PARTNERS is empty: add your buyer's company name(s) before running ads to /get-a-quote/")
    quote_funnel.write(OUT, funnel_cfg.cfg(V, DISCLAIMER), check)
    os.makedirs(os.path.join(OUT, "leads-admin"), exist_ok=True)   # private leads dashboard (noindex, password via /api/admin/leads)
    shutil.copy(os.path.join(ROOT, "admin", "leads-admin.html"), os.path.join(OUT, "leads-admin", "index.html"))
    for pg in ("publisher-spec", "publisher-console", "opt-out"):   # publisher docs + no-code test console (noindex)
        os.makedirs(os.path.join(OUT, pg), exist_ok=True); shutil.copy(os.path.join(ROOT, "admin", pg + ".html"), os.path.join(OUT, pg, "index.html"))
    if funnel_cfg.MODE != "leads":   # the lead-mode preview links its consent to /partners/: build that page too
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "assets"))
            quote_funnel.write(td, funnel_cfg._cfg(V, DISCLAIMER), check)
            os.makedirs(os.path.join(OUT, "partners"), exist_ok=True)
            shutil.copy(os.path.join(td, "partners", "index.html"), os.path.join(OUT, "partners", "index.html"))
    print(f"Built {len(PAGES)} pages")

if __name__ == "__main__":
    main()
    import ai_visibility; ai_visibility.apply(OUT)   # AI search visibility: robots.txt + IndexNow key
