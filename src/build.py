"""RingaRoofer static site generator → ../public  (python3 build.py)"""
import os, re, json, shutil, datetime
from html import escape as esc
from content import *
import legal

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.normpath(os.path.join(ROOT, "..", "public"))
V = "20261001"; UPDATED = "2026-10-01"
GSC_META = "xz9ncKiRn5z77EkCuE-lelMPzNC5h_5giCsF33PhNyk"

I = {  # 24px stroke icons
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
 "shingle": '<path d="M2 12 12 4l10 8"/><path d="M5 11h14M4 14h16M3 17h18"/>',
 "metal": '<path d="M2 12 12 4l10 8"/><path d="M7 8v12M12 4v16M17 8v12"/>',
 "flat": '<rect x="3" y="8" width="18" height="12" rx="1"/><path d="M3 8h18l-1-3H4z"/>',
 "tile": '<path d="M2 12 12 4l10 8"/><path d="M4 15a2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0"/>',
 "slate": '<path d="M2 12 12 4l10 8"/><path d="M5 12h4v4H5zM10 12h4v4h-4zM15 12h4v4h-4z"/>',
 "shake": '<path d="M2 12 12 4l10 8"/><path d="M6 11v7M10 10v9M14 10v9M18 11v7"/>',
 "map": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>', "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>', "x": '<path d="M18 6 6 18M6 6l12 12"/>', "chev": '<path d="m6 9 6 6 6-6"/>',
 "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
 "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
}
def ic(n, s=22): return f'<svg class="ic" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[n]}</svg>'
def call_btn(cls="btn btn-call", label=None): return f'<a class="{cls}" href="tel:{TEL}" data-call>{ic("phone",20)}<span>{label or "Call " + PHONE}</span></a>'

LOGO = ('<svg class="logo-mark" width="38" height="38" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#13233A"/>'
        '<path d="M8 22 20 12l12 10" fill="none" stroke="#F26B1D" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M12 21v9h16v-9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
        '<path d="M26.5 7.5a6 6 0 0 1 3.5 3.5M28 4.5a9.5 9.5 0 0 1 5.5 5.5" fill="none" stroke="#F26B1D" stroke-width="2" stroke-linecap="round"/></svg>')
BRAND = f'{LOGO}<span class="wm"><span>Ringa<b>Roofer</b></span><small>Roofing referral service</small></span>'

NAV = [("Services", "/services/", [(s["name"], f"/services/{s['slug']}/") for s in SERVICES]),
       ("Roof Types", "/roof-types/", [(t["name"], f"/roof-types/{t['slug']}/") for t in TYPES]),
       ("Coverage", "/coverage/", None), ("How It Works", "/how-it-works/", None), ("Roof Library", "/library/", None)]

def header(active):
    li = []
    for i, (t, h, sub) in enumerate(NAV):
        cur = ' aria-current="page"' if active.startswith(h) else ""
        if sub:
            dd = "".join(f'<a href="{u}">{n}</a>' for n, u in sub)
            li.append(f'<li class="has-dd"><a href="{h}"{cur}>{t}</a><button class="dd-btn" aria-label="{t} menu" aria-expanded="false">{ic("chev",16)}</button><div class="dd">{dd}</div></li>')
        else:
            li.append(f'<li><a href="{h}"{cur}>{t}</a></li>')
    mob = "".join(f'<a href="{h}">{t}</a>' + ("".join(f'<a class="sub" href="{u}">{n}</a>' for n, u in sub) if sub else "") for t, h, sub in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><span>{ic("clock",15)} Fast emergency service · Repairs, new roofs &amp; re-roofs · Nationwide</span><a href="tel:{TEL}" data-call>Call {PHONE}</a></div></div>
<header class="hdr"><div class="wrap hdr-in">
 <a class="brand" href="/" aria-label="RingaRoofer home">{BRAND}</a>
 <nav class="nav" aria-label="Main"><ul>{"".join(li)}</ul></nav>
 <div class="hdr-cta">{call_btn("btn btn-call hdr-call", PHONE)}<button class="menu" aria-label="Open menu" aria-expanded="false" aria-controls="mnav">{ic("menu",26)}</button></div>
</div>
<div class="mnav" id="mnav" hidden><nav aria-label="Mobile">{mob}<a href="/contact/">Request a Callback</a></nav>{call_btn("btn btn-call block")}</div>
</header>'''

DISCLAIMER = ("RingaRoofer.com is a referral service that connects homeowners with independent local roofing contractors. RingaRoofer does not charge homeowners and does not perform roofing work. "
              "All contractors are independent, and RingaRoofer does not warrant or guarantee any work performed. Homeowners should confirm that any contractor they hire holds the credentials and coverage required for the work in their area. "
              "Calls may be recorded for quality purposes.")
# note: "warrant" appears in this legal disclaimer only; the validator exempts DISCLAIMER and legal pages from that stem
def footer():
    svc = "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    typ = "".join(f'<li><a href="/roof-types/{t["slug"]}/">{t["name"]}</a></li>' for t in TYPES)
    return f'''<section class="cta-final"><div class="wrap cta-in"><div><h2>Roof problem? Talk to a roofer today.</h2><p>One call connects you with a roofing company that serves your area. Repairs, new roofs, re-roofs and fast emergency service.</p></div>
<div class="cta-btns">{call_btn("btn btn-call xl")}<a class="btn btn-ghost" href="/contact/">Request a callback</a></div></div></section>
<footer class="ftr"><div class="wrap">
 <div class="f-grid">
  <div class="f-brand"><a class="brand" href="/">{BRAND}</a><p>Connecting homeowners with independent roofing companies across the United States.</p>
   <p><a class="f-phone" href="tel:{TEL}" data-call>{ic("phone",18)} {PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
  <div><h2>Services</h2><ul>{svc}</ul></div>
  <div><h2>Roof Types</h2><ul>{typ}</ul></div>
  <div><h2>RingaRoofer</h2><ul><li><a href="/how-it-works/">How It Works</a></li><li><a href="/coverage/">Coverage by State</a></li><li><a href="/library/">Roof Library</a></li><li><a href="/contact/">Request a Callback</a></li><li><a href="/sitemap/">Site Map</a></li></ul></div>
 </div>
 <p class="disc">{DISCLAIMER}</p>
 <div class="f-legal"><nav aria-label="Legal"><a href="/privacy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/referral-disclosure/">Referral Disclosure</a><a href="/california-privacy/">California Privacy</a><a href="/california-privacy/#opt-out" data-optout>Do Not Sell or Share My Personal Information</a><a href="/do-not-call/">Do Not Call</a><a href="/accessibility/">Accessibility</a></nav>
 <p>&copy; 2026 RingaRoofer.com</p></div>
</div></footer>
<div class="callbar">{call_btn("callbar-btn", "Call a Roofer · " + PHONE)}</div>'''

def crumbs(trail):
    if not trail: return ""
    items = [("Home", "/")] + trail
    html = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
        f'<li><a href="{u}">{n}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{n}</li>' for i, (n, u) in enumerate(items)) + '</ol></nav>'
    return html

def schema(p):
    g = [{"@type": "Organization", "@id": URL + "/#org", "name": "RingaRoofer", "url": URL + "/", "logo": URL + "/assets/img/logo-512.png",
          "email": EMAIL, "telephone": TEL, "areaServed": {"@type": "Country", "name": "United States"},
          "description": "RingaRoofer is a roofing referral service that connects homeowners with independent local roofing companies.",
          "contactPoint": {"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service", "areaServed": "US", "availableLanguage": "en"}},
         {"@type": "WebSite", "@id": URL + "/#site", "url": URL + "/", "name": "RingaRoofer", "publisher": {"@id": URL + "/#org"}},
         {"@type": p.get("stype", "WebPage"), "@id": URL + p["url"] + "#page", "url": URL + p["url"], "name": p["title"], "description": p["desc"],
          "isPartOf": {"@id": URL + "/#site"}, "dateModified": UPDATED, "inLanguage": "en-US"}]
    if p.get("trail"):
        items = [("Home", "/")] + p["trail"]
        g.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": URL + u} for i, (n, u) in enumerate(items)]})
    if p.get("faqs"):
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in p["faqs"]]})
    if p.get("service"):
        g.append({"@type": "Service", "name": p["service"], "serviceType": p["service"], "provider": {"@id": URL + "/#org"},
                  "areaServed": {"@type": "Country", "name": "United States"} if not p.get("state") else {"@type": "State", "name": p["state"]},
                  "description": p["desc"]})
    if p.get("article"):
        g.append({"@type": "Article", "headline": p["h1"], "description": p["desc"], "datePublished": UPDATED, "dateModified": UPDATED,
                  "author": {"@type": "Organization", "name": "RingaRoofer"}, "publisher": {"@id": URL + "/#org"}, "mainEntityOfPage": URL + p["url"]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, separators=(",", ":"))

def page(p):
    tf = p.get("form")
    return f'''<!doctype html>
<html lang="en-US"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["desc"])}">
<link rel="canonical" href="{URL}{p["url"]}">
<meta name="robots" content="{"noindex, follow" if p.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"}">
<meta name="google-site-verification" content="{GSC_META}">
<meta property="og:type" content="{"article" if p.get("article") else "website"}"><meta property="og:site_name" content="RingaRoofer">
<meta property="og:title" content="{esc(p["title"])}"><meta property="og:description" content="{esc(p["desc"])}"><meta property="og:url" content="{URL}{p["url"]}">
<meta property="og:image" content="{URL}/assets/img/og.png"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13233A"><meta name="format-detection" content="telephone=yes">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/img/logo-192.png">
<link rel="stylesheet" href="/assets/site.css?v={V}">
<script type="application/ld+json">{schema(p)}</script>
<script src="/assets/config.js?v={V}"></script>
<script src="/assets/site.js?v={V}" defer></script>
</head>
<body class="{p.get("cls","")}">
{header(p["url"])}
<main id="main">
{p["hero"]}
{p["body"]}
</main>
{footer()}
{legal.TF_SCRIPT if tf else ""}
</body></html>
'''

# ---------------------------------------------------------------- shared blocks
HERO_ART = '''<svg class="hero-art" viewBox="0 0 520 420" role="img" aria-label="Illustration of a house with a new roof and a phone call connecting to a roofer">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#23406A"/><stop offset="1" stop-color="#13233A"/></linearGradient></defs>
<rect x="0" y="0" width="520" height="420" rx="28" fill="url(#sky)"/>
<circle cx="420" cy="92" r="46" fill="#F26B1D" opacity=".18"/><circle cx="420" cy="92" r="28" fill="#F26B1D" opacity=".35"/>
<path d="M70 250 250 120l180 130" fill="none" stroke="#F26B1D" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>
<path d="M100 236 250 128l150 108v134H100z" fill="#F4F1EA"/>
<g stroke="#D9D2C3" stroke-width="3"><path d="M130 214h240M112 228h276"/></g>
<path d="M92 244 250 130l158 114" fill="none" stroke="#1B2F4E" stroke-width="10" stroke-linejoin="round"/>
<g fill="#35507A"><path d="M126 200 250 112l124 88v12L250 124 126 212z" opacity=".55"/></g>
<rect x="222" y="292" width="56" height="78" rx="4" fill="#1B2F4E"/><circle cx="266" cy="333" r="3" fill="#F26B1D"/>
<rect x="136" y="280" width="52" height="44" rx="4" fill="#9FB5D1"/><rect x="312" y="280" width="52" height="44" rx="4" fill="#9FB5D1"/>
<g transform="translate(372 300)"><rect x="0" y="0" width="92" height="92" rx="24" fill="#F26B1D"/>
<path d="M62 60v7a4.6 4.6 0 0 1-5 4.6 45 45 0 0 1-19.6-7 44 44 0 0 1-13.6-13.6A45 45 0 0 1 16.8 31.5 4.6 4.6 0 0 1 21.4 26.5h7a4.6 4.6 0 0 1 4.6 4c.3 2 .9 4 1.6 6a4.6 4.6 0 0 1-1 4.8l-3 3a37 37 0 0 0 13.6 13.6l3-3a4.6 4.6 0 0 1 4.8-1c2 .7 4 1.3 6 1.6a4.6 4.6 0 0 1 4 4.7z" fill="#fff"/></g>
<g fill="none" stroke="#F26B1D" stroke-width="5" stroke-linecap="round" opacity=".9"><path d="M470 286a26 26 0 0 0-26-26"/><path d="M490 286a46 46 0 0 0-46-46"/></g>
</svg>'''

TRUST = ('<div class="trust"><div>' + ic("users") + '<span><b>One call, one roofer</b>Connected to a company that serves your area</span></div>'
         '<div>' + ic("siren") + '<span><b>Fast emergency service</b>Leaks, open roofs and storm-hit roofs</span></div>'
         '<div>' + ic("house") + '<span><b>Full service roofing</b>Repairs, new roofs and re-roofs</span></div>'
         '<div>' + ic("map") + '<span><b>Nationwide network</b>Roofers in all 50 states</span></div></div>')

def steps():
    return ('<ol class="steps">'
            f'<li><span>1</span><h3>Call {PHONE}</h3><p>Tell us what\'s going on with your roof and your ZIP code.</p></li>'
            '<li><span>2</span><h3>We connect you</h3><p>Your call goes straight to an independent roofing company that serves your area.</p></li>'
            '<li><span>3</span><h3>You decide</h3><p>Talk it through with the roofer and choose whether to go ahead. No obligation.</p></li></ol>')

def svc_cards(items=SERVICES):
    return '<div class="cards">' + "".join(f'<a class="card" href="/services/{s["slug"]}/"><span class="cic">{ic(s["icon"],26)}</span><h3>{s["name"]}</h3><p>{s["short"]}</p><span class="more">Learn more {ic("arrow",16)}</span></a>' for s in items) + '</div>'
def type_cards():
    return '<div class="cards c3">' + "".join(f'<a class="card" href="/roof-types/{t["slug"]}/"><span class="cic">{ic(t["icon"],26)}</span><h3>{t["name"]}</h3><p>{t["lead"]}</p></a>' for t in TYPES) + '</div>'
def faq_html(faqs):
    return '<div class="faq">' + "".join(f'<details><summary>{q}{ic("chev",18)}</summary><p>{a}</p></details>' for q, a in faqs) + '</div>'
def sec(inner, cls="", title=None, kicker=None, intro=None, id_=None):
    head = ""
    if title: head = f'<div class="sec-h">{f"<p class=kick>{kicker}</p>" if kicker else ""}<h2>{title}</h2>{f"<p>{intro}</p>" if intro else ""}</div>'
    return f'<section class="sec {cls}"{f" id={id_}" if id_ else ""}><div class="wrap">{head}{inner}</div></section>'
def phero(h1, lead, trail, extra="", alerts=None):
    al = f'<div class="alerts" data-alerts="{alerts}" hidden></div>' if alerts else ""
    return (f'<section class="phero"><div class="wrap phero-in"><div>{crumbs(trail)}<h1>{h1}</h1><p class="lead">{lead}</p>'
            f'<div class="hero-btns">{call_btn("btn btn-call xl")}<a class="btn btn-ghost" href="/contact/">Request a callback</a></div>{extra}{al}</div>'
            f'<aside class="callcard"><p class="cc-k">Talk to a roofer today</p><a class="cc-num" href="tel:{TEL}" data-call>{PHONE}</a>'
            '<ul class="ticks sm"><li>Roof repairs and leaks</li><li>New roofs and re-roofs</li><li>Fast emergency service</li></ul><p class="cc-note">Your call connects you with an independent roofing company serving your area.</p></aside></div></section>')

# ---------------------------------------------------------------- pages
PAGES = []
def add(**p): PAGES.append(p)

home_hero = f'''<section class="hero"><div class="wrap hero-in"><div class="hero-txt">
<p class="kick">Roofing referral service · Nationwide</p>
<h1>Need a roofer near you? <span>One call connects you.</span></h1>
<p class="lead">Roof leak, storm-hit shingles or time for a new roof. Call RingaRoofer and we'll connect you with an independent roofing company that serves your area.</p>
<div class="hero-btns">{call_btn("btn btn-call xl")}<a class="btn btn-ghost-dark" href="/contact/">Request a callback</a></div>
<ul class="hero-ticks"><li>{ic("check",18)}Roof repairs &amp; leaks</li><li>{ic("check",18)}New roofs &amp; re-roofs</li><li>{ic("check",18)}Fast emergency service</li></ul>
</div><div class="hero-vis">{HERO_ART}</div></div></section>'''
home_body = (sec(TRUST, "tight")
 + sec(svc_cards(), "", "Full service roofing", "Services", "From a single missing shingle to a complete re-roof, one call puts you in touch with a roofer who handles it.")
 + sec(steps(), "soft", "How it works", "Simple", "No forms to wade through. Just call.")
 + sec('<div class="split"><div><h2>Roof leaking right now?</h2><p>Water coming through the ceiling or a roof opened up by wind needs attention today. Call and tell us it\'s an emergency; we\'ll connect you with a roofer taking emergency calls in your area.</p>'
       '<ol class="nums"><li>Catch the water and move belongings away.</li><li>Keep out of rooms with a sagging ceiling.</li><li>Photograph the ceiling and the roof from the ground.</li><li>Call a roofer. A tarp can stop more water getting in.</li></ol>'
       f'<div class="hero-btns">{call_btn("btn btn-call")}<a class="btn btn-ghost" href="/services/emergency-roof-repair/">Emergency roof repair</a></div></div>'
       '<div class="panel"><h3>Common roof problems</h3><ul class="ticks"><li><a href="/services/roof-leak-repair/">Leaks and ceiling stains</a></li><li><a href="/services/storm-roof-repair/">Wind-lifted or missing shingles</a></li><li><a href="/services/hail-roof-repair/">Hail marks and granule loss</a></li><li><a href="/services/roof-repair/">Flashing and vent boot failures</a></li><li><a href="/services/roof-replacement/">Curling, aging shingles</a></li><li><a href="/services/roof-repair/">Sagging or soft spots</a></li></ul></div></div>', "dark")
 + sec(type_cards(), "", "Every type of roof", "Roof types", "Asphalt shingle, metal, flat, tile, slate and cedar shake.")
 + sec('<div class="states">' + "".join(f'<a href="/coverage/{s[1].lower().replace(" ", "-").replace(",", "").replace(".", "")}/">{s[1]}</a>' for s in STATES) + '</div>', "soft", "Roofers in all 50 states", "Coverage", "Our network connects homeowners with independent roofing companies nationwide. Availability can vary by ZIP code.")
 + sec(faq_html(HOME_FAQS := [
     ("What is RingaRoofer?", "RingaRoofer is a roofing referral service. When you call, we connect you with an independent roofing company that serves your area. We don't do roofing work ourselves."),
     ("Is there a charge to call?", "No. RingaRoofer doesn't charge homeowners. You agree any work and terms directly with the roofing company."),
     ("What roofing work is covered?", "Full service roofing: roof repairs, leak repairs, new roofs, re-roofs and fast emergency service, across asphalt shingle, metal, flat, tile, slate and cedar shake roofs."),
     ("Do you cover my area?", "Our network covers all 50 states. Availability can vary by ZIP code and by the type of work, so call and we'll check for you."),
     ("Who will I talk to?", "Your call connects you with an independent local roofing company. You decide whether to go ahead.")]), "", "Common questions", "FAQ"))
add(url="/", title="RingaRoofer | Find a Roofer Near You · Call (855) 635-9281", desc="Need a roofer near you? One call connects you with a local roofing company for roof repair, leaks, new roofs, re-roofs and fast emergency service. Nationwide.",
    h1="Need a roofer near you?", hero=home_hero, body=home_body, faqs=HOME_FAQS, cls="home")

# services
add(url="/services/", title="Roofing Services: Repair, Leaks, Replacement & Emergency | RingaRoofer", desc="Full service roofing: roof repair, leak repair, emergency roofing, storm and hail repair, roof replacement, new roofs and re-roofs. Call (855) 635-9281.",
    h1="Roofing services", trail=[("Services", "/services/")], hero=phero("Full service roofing, one call away", "Repairs, new roofs, re-roofs and fast emergency service. Choose your problem below, or just call.", [("Services", "/services/")]),
    body=sec(svc_cards()) + sec(steps(), "soft", "How it works"))
for s in SERVICES:
    rel = [x for x in SERVICES if x is not s][:3]
    body = (sec('<div class="doc">' + "".join(f'<h2>{h}</h2>{b}' for h, b in s["sections"]) + '</div>'
               + f'<aside class="doc-side"><div class="panel sticky"><h3>Talk to a roofer</h3><p>{s["name"]}: one call connects you with a roofing company serving your area.</p>{call_btn("btn btn-call block")}<a class="btn btn-ghost block" href="/contact/">Request a callback</a></div></aside>', "doc-wrap")
            + sec(steps(), "soft", "How it works")
            + sec(faq_html(s["faqs"]), "", f'{s["name"]}: common questions', "FAQ")
            + sec(svc_cards(rel), "soft", "Related roofing services"))
    storm = s["slug"] in ("storm-roof-repair", "hail-roof-repair", "emergency-roof-repair", "roof-tarping")
    add(url=f'/services/{s["slug"]}/', title=s["title"], desc=s["desc"], h1=s["h1"], trail=[("Services", "/services/"), (s["name"], f'/services/{s["slug"]}/')],
        hero=phero(s["h1"], s["lead"], [("Services", "/services/"), (s["name"], f'/services/{s["slug"]}/')], alerts="US" if storm else None),
        body=body, faqs=s["faqs"], service=s["name"])

# roof types
add(url="/roof-types/", title="Roof Types: Shingle, Metal, Flat, Tile, Slate & Cedar | RingaRoofer", desc="Asphalt shingle, metal, flat (TPO, EPDM), tile, slate and cedar shake roofs: repairs and replacements from roofers near you. Call (855) 635-9281.",
    h1="Roof types", trail=[("Roof Types", "/roof-types/")], hero=phero("Every type of roof", "Whatever your roof is made of, one call connects you with a roofer who works with it.", [("Roof Types", "/roof-types/")]),
    body=sec(type_cards()) + sec('<p class="center"><a class="btn btn-ghost" href="/library/choosing-a-roofing-material/">Compare roofing materials</a></p>', "tight"))
for t in TYPES:
    add(url=f'/roof-types/{t["slug"]}/', title=t["title"], desc=t["desc"], h1=t["h1"], trail=[("Roof Types", "/roof-types/"), (t["name"], f'/roof-types/{t["slug"]}/')],
        hero=phero(t["h1"], t["lead"], [("Roof Types", "/roof-types/"), (t["name"], f'/roof-types/{t["slug"]}/')]),
        body=sec(f'<div class="doc">{t["body"]}</div><aside class="doc-side"><div class="panel sticky"><h3>{t["name"]} roofers</h3><p>Repairs, replacements and new installs.</p>{call_btn("btn btn-call block")}</div></aside>', "doc-wrap")
             + sec(svc_cards(SERVICES[:3]), "soft", "Popular services"), service=f'{t["name"]} repair and replacement')

# coverage
def st_slug(n): return n.lower().replace(" ", "-").replace(",", "").replace(".", "")
by_region = {}
for code, name, reg, cities, extra in STATES: by_region.setdefault(reg, []).append((code, name))
cov = "".join(f'<div class="region"><h3>{r}</h3><p>{REGIONS[r]}</p><div class="states">' + "".join(f'<a href="/coverage/{st_slug(n)}/">{n}</a>' for c, n in v) + '</div></div>' for r, v in by_region.items())
add(url="/coverage/", title="Roofers Near You in All 50 States | RingaRoofer Coverage", desc="RingaRoofer connects homeowners with independent roofing companies in all 50 states and D.C. Find roofing help in your state. Call (855) 635-9281.",
    h1="Coverage", trail=[("Coverage", "/coverage/")], hero=phero("Roofers near you, nationwide", "Our network connects homeowners with independent roofing companies across the country. Availability can vary by ZIP code.", [("Coverage", "/coverage/")]),
    body=sec(cov, "", None))
for code, name, reg, cities, extra in STATES:
    slug = st_slug(name); u = f"/coverage/{slug}/"
    body = (sec(f'<div class="doc"><h2>Roofing in {name}</h2><p>{extra} {REGIONS[reg]}</p>'
                f'<h2>Roofing help we connect {name} homeowners with</h2><ul class="ticks">' + "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES) + '</ul>'
                f'<h2>Areas served in {name}</h2><p>Homeowners across {name} call us, including in and around ' + ", ".join(cities[:-1]) + f' and {cities[-1]}. Availability can vary by ZIP code; call and we\'ll check for you.</p>'
                f'<h2>Before you hire a roofer in {name}</h2><ul class="ticks"><li>Ask how long they\'ve worked in {name} and for local references.</li><li>Confirm they hold the credentials and coverage {name} requires for roofing work.</li><li>Get the scope of work in writing before work starts.</li><li>After big storms, be cautious with door-to-door crews.</li></ul></div>'
                f'<aside class="doc-side"><div class="panel sticky"><h3>Roofers in {name}</h3><p>One call connects you with an independent roofing company serving your area.</p>{call_btn("btn btn-call block")}</div></aside>', "doc-wrap")
            + sec(svc_cards(SERVICES[:4]), "soft", f"Popular roofing services in {name}"))
    fq = [(f"Do you have roofers in {name}?", f"Yes. Our network connects homeowners across {name} with independent roofing companies. Availability can vary by ZIP code and type of work."),
          (f"How fast can a roofer come out in {name}?", "It depends on your location, the season and recent weather. After major storms roofers book up quickly, so call early.")]
    add(url=u, title=f"Roofers in {name} | Roof Repair & Replacement | RingaRoofer", desc=f"Need a roofer in {name}? Call (855) 635-9281 to connect with a local roofing company for roof repair, leaks, new roofs, re-roofs and emergency service.",
        h1=f"Roofers in {name}", trail=[("Coverage", "/coverage/"), (name, u)],
        hero=phero(f"Need a roofer in {name}?", f"Roof leak, storm-hit roof or a new roof in {name}? One call connects you with an independent roofing company that serves your area.", [("Coverage", "/coverage/"), (name, u)], alerts=code),
        body=body + sec(faq_html(fq), "", "Questions"), faqs=fq, service="Roofing referral", state=name)

# how it works, library, contact
add(url="/how-it-works/", title="How RingaRoofer Works | One Call, One Local Roofer", desc="How RingaRoofer works: call, describe your roof problem and ZIP code, and we connect you with an independent roofing company serving your area.",
    h1="How it works", trail=[("How It Works", "/how-it-works/")], hero=phero("One call, one local roofer", "Here's exactly what happens when you call RingaRoofer.", [("How It Works", "/how-it-works/")]),
    body=sec(steps()) + sec('<div class="doc"><h2>What RingaRoofer is</h2><p>RingaRoofer is a referral service. We don\'t do roofing work, and we don\'t charge homeowners. Roofing companies in our network pay us for connecting them with homeowners who need roofing help.</p>'
        '<h2>Who you\'ll speak with</h2><p>An independent roofing company that serves your area. They discuss the job, schedule a visit, and agree any work and terms directly with you.</p>'
        '<h2>Your choice, always</h2><p>You\'re never obliged to hire anyone. If a call isn\'t helpful, you can end it. To stop calls, see our <a href="/do-not-call/">Do Not Call</a> page.</p></div>', "soft"),
    stype="AboutPage")
add(url="/library/", title="Roof Library: Leaks, New Roofs, Materials & Hail | RingaRoofer", desc="Plain-English roofing help for homeowners: what to do when the roof leaks, signs you need a new roof, choosing a roofing material and hail checklists.",
    h1="Roof Library", trail=[("Roof Library", "/library/")], hero=phero("Roof Library", "Plain-English roofing help for homeowners.", [("Roof Library", "/library/")]),
    body=sec('<div class="cards c2">' + "".join(f'<a class="card" href="/library/{a["slug"]}/"><span class="cic">{ic("book",26)}</span><h3>{a["h1"]}</h3><p>{a["lead"]}</p><span class="more">Read {ic("arrow",16)}</span></a>' for a in ARTICLES) + '</div>'))
for a in ARTICLES:
    u = f'/library/{a["slug"]}/'
    add(url=u, title=a["title"], desc=a["desc"], h1=a["h1"], trail=[("Roof Library", "/library/"), (a["h1"], u)], article=True,
        hero=phero(a["h1"], a["lead"], [("Roof Library", "/library/"), (a["h1"], u)]),
        body=sec(f'<div class="doc">{a["body"]}</div><aside class="doc-side"><div class="panel sticky"><h3>Need a roofer?</h3><p>One call connects you with a local roofing company.</p>{call_btn("btn btn-call block")}</div></aside>', "doc-wrap"))
add(url="/contact/", title="Request a Callback From a Roofer | RingaRoofer", desc="Call (855) 635-9281 or request a callback. RingaRoofer connects you with an independent roofing company serving your area.",
    h1="Request a callback", trail=[("Request a Callback", "/contact/")], form=True,
    hero=phero("Request a callback", "The fastest way is to call. Prefer a callback? Fill in the form and a roofing company serving your area will reach out.", [("Request a Callback", "/contact/")]),
    body=sec(legal.FORM, "soft"))

# legal
for lp in legal.PAGES:
    add(url=lp["url"], title=lp["title"] + " | RingaRoofer", desc=lp["desc"], h1=lp["h1"], trail=[(lp["h1"], lp["url"])], legal=True,
        hero=f'<section class="phero lg"><div class="wrap">{crumbs([(lp["h1"], lp["url"])])}<h1>{lp["h1"]}</h1><p class="lead">Last updated October 1, 2026</p></div></section>',
        body=sec(f'<div class="doc legal">{lp["body"]}</div>'))

def sitemap_page():
    groups = {"Main": [], "Services": [], "Roof Types": [], "Coverage": [], "Roof Library": [], "Legal": []}
    for p in PAGES:
        u = p["url"]; k = ("Legal" if p.get("legal") else "Services" if u.startswith("/services") else "Roof Types" if u.startswith("/roof-types")
             else "Coverage" if u.startswith("/coverage") else "Roof Library" if u.startswith("/library") else "Main")
        groups[k].append(f'<li><a href="{u}">{p["h1"]}</a></li>')
    return sec('<div class="smap">' + "".join(f'<div><h2>{k}</h2><ul>{"".join(v)}</ul></div>' for k, v in groups.items()) + '</div>')
add(url="/sitemap/", title="Site Map | RingaRoofer", desc="All pages on RingaRoofer.com.", h1="Site map", trail=[("Site Map", "/sitemap/")], hero=phero("Site map", "Every page on RingaRoofer.", [("Site Map", "/sitemap/")]), body="__SMAP__")

# ---------------------------------------------------------------- compliance check (build fails on any hit)
BANNED = ["free", "estimat", "licens", "insur", "bond", "cheap", "low", "afford", "discount", "budget", "bargain", "inexpensive", "gutter", "window",
          "siding", "deal", "save", "saving", "price", "pricing", "cost", "rate", "rates", "quote", "damage", "warrant", "claim", "financ", "professional",
          "skylight", "chimney", "solar", "fascia", "soffit"]
def check(html, where, legal_page=False):
    txt = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html)
    txt = re.sub(r'<[^>]+>', " ", txt).replace("&amp;", "&")
    txt = txt.replace(DISCLAIMER, " ")
    words = re.findall(r"[a-z]+", txt.lower())
    allow = {"lowell", "freeze", "freezes", "freezing", "below", "allow", "allowed", "follow", "flow", "yellow", "slow", "shallow", "rather", "separate", "moderate", "accurate", "corporate", "generate", "operate", "operated", "operates", "operating", "cooperate", "rated"}
    hits = sorted({w for w in words for b in BANNED if w.startswith(b) and w not in allow and not (legal_page and b in ("warrant", "rate", "insur", "claim", "cost", "save", "financ", "licens", "damage", "deal", "bond", "window"))})
    if "rated" in words: hits.append("rated")
    if hits: raise SystemExit(f"Banned wording on {where}: {hits}")

def main():
    for n in os.listdir(OUT) if os.path.isdir(OUT) else []:
        if n != "assets": (shutil.rmtree if os.path.isdir(os.path.join(OUT, n)) else os.remove)(os.path.join(OUT, n))
    os.makedirs(OUT, exist_ok=True)
    smap = sitemap_page()
    for p in PAGES:
        if p["body"] == "__SMAP__": p["body"] = smap
        html = page(p); check(html, p["url"], p.get("legal"))
        d = os.path.join(OUT, p["url"].strip("/")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(html)
    nf = dict(url="/404/", title="Page not found | RingaRoofer", desc="Page not found.", h1="Page not found", noindex=True,
              hero=phero("We couldn't find that page", "It may have moved. The quickest way to get roofing help is to call.", []), body=sec(svc_cards(SERVICES[:4])))
    open(os.path.join(OUT, "404.html"), "w").write(page(nf).replace(f'<link rel="canonical" href="{URL}/404/">', ""))
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        f'<url><loc>{URL}{p["url"]}</loc><lastmod>{UPDATED}</lastmod></url>' for p in PAGES if not p.get("noindex")) + "\n</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nUser-agent: AhrefsBot\nDisallow: /\nUser-agent: SemrushBot\nDisallow: /\nUser-agent: MJ12bot\nDisallow: /\nUser-agent: DotBot\nDisallow: /\n\nSitemap: {URL}/sitemap.xml\n")
    open(os.path.join(OUT, "llms.txt"), "w").write("# RingaRoofer\n\n> RingaRoofer (ringaroofer.com) is a roofing referral service for U.S. homeowners. Calling (855) 635-9281 connects a homeowner with an independent roofing company that serves their area, for roof repair, leak repair, new roofs, re-roofs and emergency roofing. RingaRoofer does not do roofing work and does not charge homeowners.\n\n## Pages\n" + "\n".join(f"- [{p['h1']}]({URL}{p['url']}): {p['desc']}" for p in PAGES if not p.get("legal")) + "\n")
    open(os.path.join(OUT, "google6cdd134560bcda8a.html"), "w").write("google-site-verification: google6cdd134560bcda8a.html")
    open(os.path.join(OUT, "_redirects"), "w").write(legal.REDIRECTS)
    open(os.path.join(OUT, "_headers"), "w").write(legal.HEADERS)
    shutil.copy(os.path.join(ROOT, "favicon.svg"), os.path.join(OUT, "favicon.svg"))
    print(f"Built {len(PAGES)} pages")

if __name__ == "__main__": main()
