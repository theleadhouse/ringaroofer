"""guidekit: booklet-style identification guide renderer shared across The Lead House sites.

render(G, pic, call, theme) -> HTML body (self-contained: inline <style> + <script>).
  G      guide data dict (see keys used below)
  pic    site photo helper: pic(key, w, h) -> <img>  (or None for icon-only sites)
  call   call(place, cls) -> call button html
  theme  dict of CSS colors: dark, accent, soft, line, ink, ink2, muted, cta, warm, bg
"""
import json
from html import escape as esc

SV = {
 "alert": '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17.2v.1"/>',
 "drop": '<path d="M12 3s-6 6.6-6 11a6 6 0 0 0 12 0c0-4.4-6-11-6-11z"/>',
 "flame": '<path d="M12 21c3.6 0 6-2.5 6-6 0-2.6-1.6-4.6-2.6-6-.3 1.7-1.2 2.6-2.2 3 .3-2.7-.9-5.3-3-7 .2 3.1-3.2 5.2-3.2 9.6C7 18.3 9.5 21 12 21z"/>',
 "snow": '<path d="M12 2v20M4.9 6.5l14.2 11M19.1 6.5 4.9 17.5"/>',
 "wind": '<path d="M3 8h11a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h8"/>',
 "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21v-6h6v6"/>',
 "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
 "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "camera": '<path d="M4 7h3l2-3h6l2 3h3a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="4"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "check": '<path d="m5 12 4.5 4.5L19 7"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
 "ear": '<path d="M6 9a6 6 0 1 1 12 0c0 3-2 4-3 5.5S14 18 12 20a3 3 0 0 1-4-1"/><path d="M9 9a3 3 0 0 1 6 0"/>',
 "nose": '<path d="M12 3v10l-3 3a2 2 0 0 0 3 3l3-3"/><path d="M5 9c1.5-1 3-1 4 0M15 9c1-1 2.5-1 4 0"/>',
 "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 "gauge": '<path d="M4 18a8 8 0 1 1 16 0"/><path d="m12 18 4-6"/>',
 "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/>',
 "bug": '<rect x="8" y="6" width="8" height="14" rx="4"/><path d="M12 6V4M8 10H4M8 14H3M16 10h4M16 14h5"/>',
 "bath": '<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z"/><path d="M6 12V5a2 2 0 0 1 4 0"/>',
 "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2"/>',
 "arrow": '<path d="M5 12h14M13 5l7 7-7 7"/>',
}
def ic(n, s=22): return f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{SV[n]}</svg>'

DEF_URG = {"high": ("Call today", "u-high"), "med": ("Call this week", "u-med"), "low": ("Not urgent", "u-low")}

def render(G, pic, call, theme, info=None):
    info = info or {}
    U = dict(DEF_URG); U.update(G.get("urgency", {}))
    items, n_items = G["items"], len(G["items"])
    def photo(it, w, h):
        if pic and it.get("photo"):
            return pic(it["photo"], w, h)
        return f'<span class="gk-ph">{ic(it.get("icon", "home"), 56)}</span>'
    # ---------- finder (photo/icon tiles + filter chips) and quiz
    chips = '<button type="button" class="gk-chip on" data-f="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" class="gk-chip" data-f="{k}" aria-pressed="false">{t}</button>' for k, t in G["filter"]["opts"])
    tiles = "".join(f'<a class="gk-tile" href="#{it["k"]}" data-f="{" ".join(it["tags"].get(G["filter"]["key"], []))}"><span class="gk-ti">{photo(it, 360, 270)}<i class="gk-dot {U[it["lvl"]][1]}"></i></span><b>{it["name"]}</b></a>' for it in items)
    def q(n, qq):
        title, key, multi = qq["q"], qq["key"], qq.get("multi", False)
        return (f'<fieldset class="gk-q"><legend><span>{n}</span>{title}</legend><div class="gk-opts">' + "".join(
            f'<label><input type="{"checkbox" if multi else "radio"}" name="gkq{n}" value="{k}"><span>{t}</span></label>' for k, t in qq["opts"]) + '</div></fieldset>')
    data = {it["k"]: {"n": it["name"], "t": [t for v in it["tags"].values() for t in v], "u": U[it["lvl"]][0], "c": U[it["lvl"]][1]} for it in items}
    quiz = (f'<div class="gk-iq" id="identifier"><div class="gk-iq-h"><p class="gk-k">{G["quiz"]["kicker"]}</p><h3>{G["quiz"]["title"]}</h3><p>{G["quiz"]["intro"]}</p></div>'
            '<form class="gk-iq-f" data-gkq>' + "".join(q(i + 1, qq) for i, qq in enumerate(G["quiz"]["qs"])) +
            f'<button class="gk-btn gk-btn-cta" type="submit">Show my match</button></form><div class="gk-iq-r" data-gkq-out aria-live="polite"></div></div>'
            f'<script type="application/json" id="gk-data">{json.dumps(data)}</script>')
    finder = (f'<section class="gk-fd"><div class="gk-wrap"><p class="gk-k">{G["finder_kicker"]}</p><h2>{G["finder_title"]}</h2>'
              f'<div class="gk-chips" role="group" aria-label="Filter">{chips}</div><div class="gk-grid">{tiles}</div>{quiz}</div></section>')
    # ---------- chapters
    num = lambda i: f"{i:02d}"
    sig = ('<section class="gk-ch" id="quick-check"><header class="gk-ch-h"><span class="gk-num">01</span><div><p class="gk-k">Start here</p>'
           f'<h2>{G["signs_title"]}</h2></div></header><p class="gk-intro">{G["signs_intro"]}</p><div class="gk-signs">' +
           "".join(f'<a class="gk-sign" href="#{k}"><span>{a}</span><b>{b} {ic("arrow", 14)}</b></a>' for a, b, k in G["signs"]) + '</div></section>')
    chs = []
    for i, it in enumerate(items):
        lab, cls = U[it["lvl"]]
        prv = items[i - 1] if i else None
        nxt = items[i + 1] if i + 1 < n_items else None
        pn = ('<nav class="gk-pn" aria-label="Previous and next">' +
              (f'<a class="pv" href="#{prv["k"]}">{ic("arrow", 15)}<span><small>Previous</small>{prv["name"]}</span></a>' if prv else '<span></span>') +
              (f'<a class="nx" href="#{nxt["k"]}"><span><small>Next</small>{nxt["name"]}</span>{ic("arrow", 15)}</a>' if nxt else
               f'<a class="nx" href="#{"compare" if G.get("compare") else "tips"}"><span><small>Next</small>{"Side by side" if G.get("compare") else "Tips"}</span>{ic("arrow", 15)}</a>') + '</nav>')
        cap = f'<figcaption>{esc(it.get("cap", ""))}</figcaption>' if it.get("cap") else ""
        chs.append(
            f'<article class="gk-ch" id="{it["k"]}"><header class="gk-ch-h"><span class="gk-num">{num(i + 2)}</span><div><p class="gk-k">{G["item_word"]} {i + 1} of {n_items}</p><h2>{it["name"]}</h2></div><span class="gk-urg {cls}">{lab}</span></header>'
            f'<div class="gk-spread"><figure class="gk-fig">{photo(it, 760, 570)}{cap}</figure><div class="gk-info"><div class="gk-stats">' +
            "".join(f'<div><span>{a}</span><b>{b}</b></div>' for a, b in it["stats"]) + '</div>' +
            "".join(f'<h3>{h}</h3><p>{t}</p>' for h, t in it["info"]) + '</div></div>'
            f'<div class="gk-cols"><div class="gk-box"><h3>{G.get("signs_box", "Signs to look for")}</h3><ul class="gk-ticks">' + "".join(f"<li>{x}</li>" for x in it["signs"]) + '</ul></div>'
            f'<div class="gk-box now"><h3>{G.get("now_box", "Do this now")}</h3><ol>' + "".join(f"<li>{x}</li>" for x in it["now"]) + '</ol></div></div>'
            f'<div class="gk-cta {cls}"><p>{it["note"]}</p><div class="gk-btns">{call("gk-" + it["k"], "gk-btn gk-btn-cta")}' +
            (f'<a class="gk-btn gk-btn-ghost" href="{it["link"][0]}">{it["link"][1]}</a>' if it.get("link") else "") + f'</div></div>{pn}</article>')
    n = n_items + 2
    cmp = ""
    if G.get("compare"):
        cards = "".join(f'<div class="gk-lk"><h3>{t}</h3><table><thead><tr><th></th><th>{a}</th><th>{b}</th></tr></thead><tbody>' +
                        "".join(f'<tr><th scope="row">{r}</th><td>{x}</td><td>{y}</td></tr>' for r, x, y in rows) + '</tbody></table></div>' for t, a, b, rows in G["compare"])
        cmp = (f'<section class="gk-ch" id="compare"><header class="gk-ch-h"><span class="gk-num">{num(n)}</span><div><p class="gk-k">Side by side</p><h2>{G["compare_title"]}</h2></div></header>'
               f'<p class="gk-intro">{G["compare_intro"]}</p><div class="gk-lks">{cards}</div></section>')
        n += 1
    tips = (f'<section class="gk-ch" id="tips"><header class="gk-ch-h"><span class="gk-num">{num(n)}</span><div><p class="gk-k">How to</p><h2>{G["tips_title"]}</h2></div></header><div class="gk-tips">' +
            "".join(f'<div><span class="gk-tic">{ic(i_, 22)}</span><h3>{t}</h3><p>{d}</p></div>' for i_, t, d in G["tips"]) + '</div>'
            f'<div class="gk-unsure"><div><p class="gk-k">{G["unsure"][0]}</p><h2>{G["unsure"][1]}</h2><p>{G["unsure"][2]}</p></div><div class="gk-btns">{call("gk-unsure", "gk-btn gk-btn-cta gk-xl")}</div></div>'
            + (f'<p class="gk-foot">{G["footnote"]}</p>' if G.get("footnote") else "") + '</section>')
    n += 1
    faq = (f'<section class="gk-ch" id="faq"><header class="gk-ch-h"><span class="gk-num">{num(n)}</span><div><p class="gk-k">FAQ</p><h2>{G["faq_title"]}</h2></div></header><div class="gk-faq">' +
           "".join(f'<details><summary>{qq}<i aria-hidden="true">+</i></summary><p>{a}</p></details>' for qq, a in G["faq"]) + '</div></section>')
    # ---------- contents
    toc_items = [("quick-check", "Identify by sign", None)] + [(it["k"], it["name"], U[it["lvl"]][1]) for it in items]
    if G.get("compare"): toc_items.append(("compare", "Side by side", None))
    toc_items += [("tips", G["tips_title"], None), ("faq", "Questions", None)]
    dl = (f'<a class="gk-btn gk-btn-ghost gk-block gk-dl" href="{info["pdf"]}" download data-gk-dl>Download the booklet (PDF)</a>' if info.get("pdf") else "")
    toc = ('<aside class="gk-toc"><div class="gk-toc-in"><p class="gk-toc-t">Contents</p><ol>' +
           "".join(f'<li><a href="#{k}"><span class="n">{num(i + 1)}</span>{t}' + (f'<i class="gk-dot {c}"></i>' if c else "") + '</a></li>' for i, (k, t, c) in enumerate(toc_items)) +
           f'</ol><div class="gk-toc-cta">{call("gk-toc", "gk-btn gk-btn-cta gk-block")}{dl}<button type="button" class="gk-btn gk-btn-ghost gk-block" data-gk-print>Print this page</button></div>'
           f'<p class="gk-legend"><i class="gk-dot u-high"></i>{U["high"][0]} <i class="gk-dot u-med"></i>{U["med"][0]} <i class="gk-dot u-low"></i>{U["low"][0]}</p></div></aside>')
    mj = '<div class="gk-mj"><nav class="gk-mjn" aria-label="Jump to">' + (f'<a href="{info["pdf"]}" download>Booklet PDF</a>' if info.get("pdf") else "") + '<a href="#identifier">Identifier</a>' + "".join(f'<a href="#{k}">{t}</a>' for k, t, _ in toc_items) + '</nav></div>'
    I_ = info
    inside = "".join(f'<li><span>{num(i + 2)}</span>{it["name"]}</li>' for i, it in enumerate(items))
    cover_img = pic(I_["cover_photo"], 1400, 900) if (pic and I_.get("cover_photo")) else f'<span class="gk-ph">{ic("home", 90)}</span>'
    phone_html = f'<p class="gk-pc-call"><small>Call a local pro</small>{I_["phone"]}</p>' if I_.get("phone") else ""
    pcover = (f'<div class="gk-pcover"><div class="gk-pc-top"><b>{I_.get("brand", "")}</b><span>{I_.get("url", "")}</span></div>'
              f'<div class="gk-pc-img">{cover_img}</div><p class="gk-k">The homeowner\'s field guide</p><h1>{I_.get("title", "")}</h1><p class="gk-pc-lead">{I_.get("lead", "")}</p>'
              f'<div class="gk-pc-grid"><div><p class="gk-pc-h">Inside this guide</p><ol class="gk-pc-in">{inside}</ol></div><div class="gk-pc-box">{phone_html}<p>Keep this guide where you can find it fast: by the water heater, in a kitchen drawer or on the fridge.</p></div></div></div>')
    pback = (f'<div class="gk-pback"><p class="gk-k">When you need help</p><h2>One call to a local pro</h2>{phone_html}<p class="gk-pb-url">{I_.get("url", "")}</p>'
             f'<p class="gk-pb-note">{I_.get("disclaimer", "")}</p></div>')
    t = theme
    style = (f'--gk-dark:{t["dark"]};--gk-accent:{t["accent"]};--gk-soft:{t["soft"]};--gk-line:{t["line"]};--gk-ink:{t["ink"]};--gk-ink2:{t["ink2"]};'
             f'--gk-muted:{t["muted"]};--gk-cta:{t["cta"]};--gk-cta2:{t.get("cta2", t["cta"])};--gk-ctaink:{t.get("ctaink", "#fff")};--gk-warm:{t["warm"]};--gk-bg:{t["bg"]};--gk-hi:{t.get("hi", t["accent"])};--gk-pop:{t.get("pop", t["accent"])}')
    pstyle = f'@media print{{@page{{@bottom-left{{content:"{I_.get("brand", "")} \\00b7  {I_.get("phone", "") or I_.get("url", "")}";font:600 8.5pt system-ui,sans-serif;color:#667}}@bottom-right{{content:counter(page);font:700 8.5pt system-ui,sans-serif;color:#667}}}}@page:first{{@bottom-left{{content:none}}@bottom-right{{content:none}}}}}}'
    return (f'<style>{CSS}{pstyle}</style><div class="gk" style="{style}">{pcover}{finder}{mj}<section class="gk-bk"><div class="gk-wrap gk-layout">{toc}<div class="gk-main">'
            f'{sig}{"".join(chs)}{cmp}{tips}{faq}{pback}</div></div></section></div><script>{JS}</script>')

def faq_schema(G): return G["faq"]

JS = r'''(function(){var g=document.querySelector(".gk");if(!g)return;
var l=g.querySelectorAll(".gk-toc a[href^='#']"),m={};l.forEach(function(a){m[a.getAttribute("href").slice(1)]=a});
if("IntersectionObserver" in window){var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){l.forEach(function(a){a.classList.remove("on")});var a=m[e.target.id];if(a)a.classList.add("on")}})},{rootMargin:"-30% 0px -60% 0px"});g.querySelectorAll(".gk-ch[id]").forEach(function(s){o.observe(s)})}
var c=g.querySelectorAll(".gk-chip"),t=g.querySelectorAll(".gk-tile");c.forEach(function(b){b.addEventListener("click",function(){c.forEach(function(x){x.classList.remove("on");x.setAttribute("aria-pressed","false")});b.classList.add("on");b.setAttribute("aria-pressed","true");var r=b.getAttribute("data-f");t.forEach(function(e){e.hidden=!(r==="all"||(" "+e.getAttribute("data-f")+" ").indexOf(" "+r+" ")>-1)})})});
function prep(){g.querySelectorAll("details").forEach(function(d){d.open=true});var im=[].slice.call(document.querySelectorAll("main img"));im.forEach(function(i){i.loading="eager";if(i.dataset.src)i.src=i.dataset.src});return Promise.all(im.map(function(i){return i.complete&&i.naturalWidth?1:new Promise(function(r){i.addEventListener("load",r,{once:true});i.addEventListener("error",r,{once:true});setTimeout(r,6000)})}))}
window.addEventListener("beforeprint",function(){g.querySelectorAll("details").forEach(function(d){d.open=true})});
g.querySelectorAll("[data-gk-print]").forEach(function(p){p.addEventListener("click",function(){var t=p.textContent;p.textContent="Preparing pages…";prep().then(function(){p.textContent=t;window.print()})})});
var f=g.querySelector("[data-gkq]"),out=g.querySelector("[data-gkq-out]"),d=JSON.parse((document.getElementById("gk-data")||{}).textContent||"{}");if(!f)return;
f.addEventListener("submit",function(e){e.preventDefault();var pk=[].map.call(f.querySelectorAll("input:checked"),function(i){return i.value});if(!pk.length){out.innerHTML="<p class=gk-empty>Pick at least one answer.</p>";return}
var s=Object.keys(d).map(function(k){var n=0;pk.forEach(function(v){if(d[k].t.indexOf(v)>-1)n++});return[k,n]}).filter(function(x){return x[1]>0}).sort(function(a,b){return b[1]-a[1]});
if(!s.length){out.innerHTML="<p class=gk-empty>No clear match. Call and describe it, and a local pro can help.</p>";return}
var h="<p class=gk-rk>Likeliest match"+(s.length>1?"es":"")+"</p>";s.slice(0,2).forEach(function(x,i){var r=d[x[0]];h+="<a class=\"gk-m"+(i?"":" top")+"\" href=\"#"+x[0]+"\"><span><b>"+r.n+"</b><small>"+(i?"Also possible":"Closest fit")+"</small></span><em class=\"gk-urg "+r.c+"\">"+r.u+"</em></a>"});
out.innerHTML=h+"<p class=gk-empty>Not sure? A local pro can confirm it on the phone.</p>";if(window.gtag)gtag("event","guide_identifier",{match:s[0][0]});out.scrollIntoView({block:"nearest",behavior:"smooth"})})})();'''

CSS = r'''
.gk{--gk-r:16px;color:var(--gk-ink);font-size:17px}
.gk *{box-sizing:border-box}
.gk h2,.gk h3{color:var(--gk-dark);letter-spacing:-.02em;line-height:1.12}
.gk-wrap{max-width:1200px;margin:0 auto;padding-inline:16px}@media(min-width:640px){.gk-wrap{padding-inline:28px}}
.gk-k{font-weight:800;font-size:12.5px;line-height:1.2;letter-spacing:.14em;text-transform:uppercase;color:var(--gk-accent);margin:0 0 10px}
.gk-btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:48px;padding:0 20px;border-radius:12px;border:2px solid transparent;font-weight:800;font-size:16px;text-decoration:none;cursor:pointer;font-family:inherit;line-height:1.1;text-align:center}
.gk-btn svg{flex:none}
.gk-btn-cta{background:var(--gk-cta);color:var(--gk-ctaink)}.gk-btn-cta:hover{background:var(--gk-cta2);color:var(--gk-ctaink)}
.gk-btn-ghost{background:#fff;color:var(--gk-dark);border-color:var(--gk-line)}.gk-btn-ghost:hover{border-color:var(--gk-dark);color:var(--gk-dark)}
.gk-xl{min-height:56px;padding:0 26px;font-size:17px}.gk-block{width:100%}
.gk-dot{display:inline-block;width:9px;height:9px;border-radius:50%;flex:none}
.u-high.gk-dot,.gk-urg.u-high{background:#D9442B}.u-med.gk-dot,.gk-urg.u-med{background:#B7791F}.u-low.gk-dot,.gk-urg.u-low{background:var(--gk-accent)}
.gk-urg{display:inline-block;font-weight:800;font-size:11.5px;line-height:1;letter-spacing:.06em;text-transform:uppercase;padding:8px 12px;border-radius:999px;color:#fff;white-space:nowrap;font-style:normal}
.gk-ph{display:flex;align-items:center;justify-content:center;width:100%;aspect-ratio:4/3;border-radius:12px;background:var(--gk-soft);color:var(--gk-accent)}
/* finder */
.gk-fd{padding:44px 0 8px;background:var(--gk-bg)}.gk-fd h2{margin:0 0 16px;font-size:clamp(1.6rem,3vw,2.3rem)}
.gk-chips{display:flex;gap:8px;overflow-x:auto;padding:2px 0 14px;scrollbar-width:none}.gk-chips::-webkit-scrollbar{display:none}
.gk-chip{flex:none;font-weight:700;font-size:14.5px;line-height:1;font-family:inherit;padding:10px 15px;border-radius:999px;border:1px solid var(--gk-line);background:#fff;color:var(--gk-dark);cursor:pointer}
.gk-chip.on{background:var(--gk-dark);border-color:var(--gk-dark);color:#fff}
.gk-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.gk-tile{display:flex;flex-direction:column;gap:8px;text-decoration:none;color:var(--gk-dark);background:#fff;border:1px solid var(--gk-line);border-radius:14px;padding:8px 8px 12px;transition:border-color .15s,transform .15s}
.gk-tile[hidden]{display:none}.gk-tile:hover{border-color:var(--gk-accent);transform:translateY(-2px)}
.gk-ti{position:relative;display:block}.gk-ti img,.gk-ti .gk-ph{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;background:var(--gk-soft);display:flex}
.gk-ti .gk-ph svg{width:40px;height:40px}
.gk-ti .gk-dot{position:absolute;top:8px;right:8px;width:12px;height:12px;border:2px solid #fff}
.gk-tile b{font-size:14.5px;line-height:1.25;padding:0 4px}
.gk-iq{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.6fr) minmax(0,1fr);gap:24px;align-items:start;margin-top:26px;background:var(--gk-dark);color:#fff;border-radius:20px;padding:28px}
.gk-iq-h h3{color:#fff;font-size:1.6rem;margin:0 0 8px}.gk-iq-h p{color:rgba(255,255,255,.8);margin:0;font-size:15.5px}.gk-iq .gk-k{color:var(--gk-pop)}
.gk-iq-f{display:grid;gap:14px}.gk-q{border:0;margin:0;padding:0;min-width:0}
.gk-q legend{display:flex;align-items:center;gap:8px;font-weight:800;margin-bottom:8px;font-size:15px;color:#fff}
.gk-q legend span{display:inline-flex;width:22px;height:22px;border-radius:50%;background:var(--gk-pop);color:var(--gk-dark);font-size:12px;align-items:center;justify-content:center}
.gk-opts{display:flex;flex-wrap:wrap;gap:6px}.gk-opts label{cursor:pointer;position:relative}.gk-opts input{position:absolute;left:0;top:0;width:1px;height:1px;margin:0;opacity:0;pointer-events:none}
.gk-opts span{display:inline-block;padding:8px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.3);font-size:14px;font-weight:600;color:#fff}
.gk-opts input:checked+span{background:var(--gk-pop);border-color:var(--gk-pop);color:var(--gk-dark)}
.gk-opts input:focus-visible+span{outline:2px solid #fff;outline-offset:2px}
.gk-iq-f .gk-btn{justify-self:start}
.gk-iq-r{background:rgba(255,255,255,.07);border:1px dashed rgba(255,255,255,.28);border-radius:14px;padding:16px;min-height:160px}
.gk-iq-r:empty::before{content:"Your match shows here.";color:rgba(255,255,255,.6);font-size:15px}
.gk-rk{font-weight:800;font-size:12px;line-height:1;letter-spacing:.12em;text-transform:uppercase;color:var(--gk-pop);margin:0 0 10px}
.gk-m{display:flex;align-items:center;justify-content:space-between;gap:10px;background:#fff;color:var(--gk-dark);border-radius:12px;padding:12px 14px;margin-bottom:8px;text-decoration:none}
.gk-m b{display:block;font-size:17px}.gk-m small{color:var(--gk-muted);font-size:13px}.gk-m.top{box-shadow:0 0 0 3px var(--gk-pop)}.gk-m .gk-urg{font-size:10.5px;padding:6px 9px}
.gk-empty{color:rgba(255,255,255,.85);font-size:14px;margin:6px 0 0}
/* booklet */
.gk-mj{display:none;position:sticky;top:var(--hh,64px);z-index:30;background:rgba(255,255,255,.96);backdrop-filter:blur(8px);border-block:1px solid var(--gk-line)}
.gk-mjn{display:flex;gap:8px;overflow-x:auto;padding:10px 16px;scrollbar-width:none}.gk-mjn::-webkit-scrollbar{display:none}
.gk-mjn a{flex:none;padding:8px 14px;border-radius:999px;background:#fff;border:1px solid var(--gk-line);font-weight:700;font-size:14px;color:var(--gk-dark);text-decoration:none;white-space:nowrap}
.gk-bk{padding:40px 0 72px;background:var(--gk-bg)}
.gk-layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:44px;align-items:start}
.gk-toc{position:sticky;top:96px}
.gk-toc-in{background:#fff;border:1px solid var(--gk-line);border-radius:var(--gk-r);padding:18px 14px 16px;max-height:calc(100vh - 120px);overflow:auto}
.gk-toc-t{font-weight:800;font-size:12px;line-height:1;letter-spacing:.14em;text-transform:uppercase;color:var(--gk-muted);margin:0 6px 10px}
.gk-toc ol{list-style:none;margin:0 0 14px;padding:0}
.gk-toc a{display:flex;align-items:center;gap:10px;padding:7px 8px;border-radius:9px;color:var(--gk-ink2);text-decoration:none;font-size:15px;font-weight:600;line-height:1.25}
.gk-toc a:hover{background:var(--gk-soft);color:var(--gk-dark)}.gk-toc a.on{background:var(--gk-dark);color:#fff}.gk-toc a.on .n{color:var(--gk-pop)}
.gk-toc .n{font-weight:800;font-size:12px;line-height:1;color:var(--gk-muted);min-width:20px}.gk-toc a .gk-dot{margin-left:auto}
.gk-toc-cta{display:grid;gap:8px}.gk-toc a.gk-dl{color:var(--gk-dark);background:#fff;border:2px solid var(--gk-dark)}.gk-toc a.gk-btn{display:inline-flex;justify-content:center;padding:0 16px;font-size:15px;font-weight:800;border-radius:12px}.gk-toc a.gk-btn-cta,.gk-toc a.gk-btn-cta:hover{color:var(--gk-ctaink);background:var(--gk-cta)}.gk-toc a.gk-btn-cta:hover{background:var(--gk-cta2)}
.gk-legend{display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;color:var(--gk-muted);margin:12px 4px 0}.gk-legend .gk-dot{margin-left:6px}.gk-legend .gk-dot:first-child{margin-left:0}
.gk-main{display:grid;gap:28px;min-width:0}
.gk-ch{background:#fff;border:1px solid var(--gk-line);border-radius:20px;padding:30px 32px;scroll-margin-top:96px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.gk-ch-h{display:flex;align-items:center;gap:18px;padding-bottom:18px;margin-bottom:22px;border-bottom:1px solid var(--gk-line)}
.gk-ch-h h2{margin:0;font-size:clamp(1.6rem,2.6vw,2.1rem)}.gk-ch-h .gk-k{margin:0 0 6px}.gk-ch-h .gk-urg{margin-left:auto}
.gk-num{font-weight:800;font-size:44px;line-height:1;color:var(--gk-hi);letter-spacing:-.03em;min-width:62px}
.gk-intro{color:var(--gk-ink2);font-size:1.05rem;margin:-6px 0 18px}
.gk-signs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.gk-sign{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:14px 16px;border:1px solid var(--gk-line);border-radius:12px;color:var(--gk-ink);text-decoration:none;background:var(--gk-soft);font-size:15.5px}
.gk-sign b{display:inline-flex;align-items:center;gap:6px;color:var(--gk-accent);white-space:nowrap;font-size:14.5px}.gk-sign:hover{border-color:var(--gk-accent);background:#fff}
.gk-spread{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:28px;align-items:start}
.gk-fig{margin:0}.gk-fig img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:14px;background:var(--gk-soft);display:block;height:auto}
.gk-fig figcaption{font-size:13px;color:var(--gk-muted);margin-top:8px}
.gk-stats{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:18px}
.gk-stats div{background:var(--gk-soft);border-radius:12px;padding:12px 14px}
.gk-stats span{display:block;font-weight:800;font-size:11.5px;line-height:1;letter-spacing:.1em;text-transform:uppercase;color:var(--gk-accent);margin-bottom:6px}
.gk-stats b{font-size:15px;line-height:1.4;color:var(--gk-dark);font-weight:700}
.gk-info h3{font-size:1.05rem;margin:0 0 6px}.gk-info p{color:var(--gk-ink2);font-size:16px;margin:0 0 16px;line-height:1.6}
.gk-cols{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}
.gk-box{border:1px solid var(--gk-line);border-radius:14px;padding:18px 20px}.gk-box h3{font-size:1.05rem;margin:0 0 12px}
.gk-ticks{list-style:none;margin:0;padding:0;font-size:15.5px}.gk-ticks li{position:relative;padding-left:26px;margin-bottom:9px;line-height:1.5}
.gk-ticks li::before{content:"";position:absolute;left:2px;top:.45em;width:11px;height:11px;border-radius:50%;background:var(--gk-accent);box-shadow:0 0 0 3px var(--gk-soft)}
.gk-box.now{background:var(--gk-warm);border-color:rgba(0,0,0,.06)}.gk-box.now ol{margin:0;padding-left:20px;font-size:15.5px}.gk-box.now li{margin-bottom:8px;line-height:1.5}
.gk-cta{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px;margin-top:20px;padding:16px 18px;border-radius:14px;background:var(--gk-soft);border-left:5px solid var(--gk-accent)}
.gk-cta.u-high{border-left-color:#D9442B}.gk-cta.u-med{border-left-color:#B7791F}
.gk-cta p{margin:0;font-weight:600;color:var(--gk-dark);flex:1 1 280px}.gk-btns{display:flex;gap:10px;flex-wrap:wrap}
.gk-pn{display:flex;justify-content:space-between;gap:12px;margin-top:20px;padding-top:16px;border-top:1px dashed var(--gk-line)}
.gk-pn a{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--gk-dark);font-weight:700}
.gk-pn a.pv svg{transform:rotate(180deg)}.gk-pn a.nx{text-align:right;margin-left:auto}
.gk-pn small{display:block;font-size:12px;font-weight:700;color:var(--gk-muted);text-transform:uppercase;letter-spacing:.08em}
.gk-lks{display:grid;gap:16px}.gk-lk{border:1px solid var(--gk-line);border-radius:14px;overflow:hidden;min-width:0}
.gk-lk h3{font-size:1.05rem;margin:0;padding:14px 16px;background:var(--gk-soft);border-bottom:1px solid var(--gk-line)}
.gk-lk table{width:100%;min-width:0;border-collapse:collapse;font-size:14.5px;table-layout:fixed}
.gk-lk th,.gk-lk td{padding:10px 12px;border-bottom:1px solid var(--gk-line);text-align:left;vertical-align:top;background:#fff;color:var(--gk-ink)}
.gk-lk tr:last-child th,.gk-lk tr:last-child td{border-bottom:0}
.gk-lk thead th{font-size:13.5px;color:var(--gk-accent);border-bottom:2px solid var(--gk-line)}
.gk-lk thead th:first-child,.gk-lk tbody th{width:22%}.gk-lk tbody th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--gk-muted);background:var(--gk-bg)}
.gk-tips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:22px}
.gk-tips>div{border:1px solid var(--gk-line);border-radius:14px;padding:18px}
.gk-tic{display:inline-flex;width:42px;height:42px;align-items:center;justify-content:center;border-radius:11px;background:var(--gk-soft);color:var(--gk-accent);margin-bottom:10px}
.gk-tips h3{font-size:1.05rem;margin:0 0 4px}.gk-tips p{margin:0;font-size:15px;color:var(--gk-ink2);line-height:1.55}
.gk-unsure{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px;background:var(--gk-dark);color:#fff;border-radius:16px;padding:26px 28px}
.gk-unsure h2{color:#fff;margin:0 0 6px;font-size:1.6rem}.gk-unsure p{color:rgba(255,255,255,.82);max-width:52ch;margin:0}.gk-unsure .gk-k{color:var(--gk-pop)}
.gk-foot{font-size:14.5px;color:var(--gk-ink2);margin:16px 0 0}
.gk-faq details{border-bottom:1px solid var(--gk-line)}.gk-faq summary{display:flex;justify-content:space-between;gap:16px;align-items:center;padding:16px 2px;font-weight:700;color:var(--gk-dark);cursor:pointer;list-style:none}
.gk-faq summary::-webkit-details-marker{display:none}.gk-faq summary i{font-style:normal;font-size:22px;color:var(--gk-accent);transition:transform .2s}.gk-faq details[open] summary i{transform:rotate(45deg)}
.gk-faq details p{margin:0 0 16px;color:var(--gk-ink2);line-height:1.6}
@media(max-width:1100px){.gk-iq{grid-template-columns:1fr 1fr}.gk-iq-h{grid-column:1/-1}}
@media(max-width:1060px){.gk-layout{grid-template-columns:1fr}.gk-toc{display:none}.gk-mj{display:block}.gk-bk{padding-top:24px}}
@media(max-width:820px){.gk-spread,.gk-cols{grid-template-columns:1fr}.gk-tips{grid-template-columns:1fr 1fr}.gk-signs{grid-template-columns:1fr}.gk-iq{grid-template-columns:1fr;padding:22px 18px}}
@media(max-width:560px){.gk-ch{padding:20px 16px;border-radius:16px}.gk-num{font-size:32px;min-width:42px}.gk-ch-h{flex-wrap:wrap;gap:10px 14px}.gk-ch-h .gk-urg{margin-left:0}
 .gk-tips,.gk-stats{grid-template-columns:1fr}.gk-cta .gk-btns,.gk-cta .gk-btn{width:100%}.gk-unsure{padding:22px 18px}.gk-sign{flex-direction:column;align-items:flex-start;gap:4px}
 .gk-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.gk-lk th,.gk-lk td{padding:9px 8px;font-size:13.5px}.gk-lk tbody th{font-size:10.5px}}
.gk-pcover,.gk-pback{display:none}
@media print{
 @page{size:letter;margin:.55in .6in .7in}
 html,body{background:#fff!important;padding:0!important;margin:0!important}
 body.guidepage>*:not(main),body.guidepage main>*:not(.gk):not(style):not(script){display:none!important}
 .gk{font-size:11pt;color:#111}
 .gk *{-webkit-print-color-adjust:exact;print-color-adjust:exact;box-shadow:none!important;animation:none!important;transition:none!important}
 .gk-fd,.gk-mj,.gk-toc,.gk-pn,.gk-btns,.gk-faq summary i{display:none!important}
 .gk-cta{display:block;margin-top:14px;padding:12px 16px;break-inside:avoid}.gk-cta p{font-size:11pt}
 .gk-bk{padding:0;background:#fff}.gk-wrap{padding:0;max-width:none}.gk-layout{display:block}.gk-main{display:block}
 .gk-pcover{display:flex;flex-direction:column;min-height:9.6in;break-after:page}
 .gk-pc-top{display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid var(--gk-dark);padding-bottom:10px;margin-bottom:18px}
 .gk-pc-top b{font-size:17pt;color:var(--gk-dark);letter-spacing:-.02em}.gk-pc-top span{font-size:10pt;color:var(--gk-muted)}
 .gk-pc-img img,.gk-pc-img .gk-ph{width:100%;height:3.9in;object-fit:cover;border-radius:10px;display:block}
 .gk-pcover .gk-k{margin:22px 0 6px}.gk-pcover h1{font-size:34pt;line-height:1.02;margin:0 0 10px;color:var(--gk-dark);letter-spacing:-.03em}
 .gk-pc-lead{font-size:13pt;color:var(--gk-ink2);margin:0 0 18px;max-width:6in}
 .gk-pc-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:22px;margin-top:auto}
 .gk-pc-h{font-weight:800;font-size:9pt;letter-spacing:.14em;text-transform:uppercase;color:var(--gk-muted);margin:0 0 8px}
 .gk-pc-in{list-style:none;margin:0;padding:0;columns:2;column-gap:18px;font-size:10pt}
 .gk-pc-in li{break-inside:avoid;padding:3px 0;border-bottom:1px solid var(--gk-line);display:flex;gap:8px}.gk-pc-in span{font-weight:800;color:var(--gk-accent)}
 .gk-pc-box{background:var(--gk-dark);color:#fff;border-radius:12px;padding:16px 18px;font-size:10pt}.gk-pc-box p{margin:8px 0 0;color:rgba(255,255,255,.85)}
 .gk-pc-call{font-size:22pt;font-weight:800;margin:0!important;color:#fff!important;line-height:1.1}.gk-pc-call small{display:block;font-size:8.5pt;letter-spacing:.12em;text-transform:uppercase;color:var(--gk-pop);margin-bottom:4px}
 .gk-ch{break-before:page;break-inside:auto;border:0;border-radius:0;padding:0;margin:0}
 .gk-ch#quick-check{break-before:auto}
 .gk-ch-h{padding-bottom:10px;margin-bottom:14px;border-bottom:2px solid var(--gk-dark)}
 .gk-num{font-size:30pt;min-width:48px}.gk-ch-h h2{font-size:21pt}
 .gk-spread{grid-template-columns:1fr 1fr!important;gap:18px}
 .gk-fig img,.gk-fig .gk-ph{height:3.7in;aspect-ratio:auto}.gk-fig figcaption{font-size:8pt}
 .gk-stats{grid-template-columns:1fr!important;gap:8px;margin-bottom:12px}.gk-stats div{padding:10px 12px}.gk-stats b{font-size:11pt}
 .gk-info h3,.gk-box h3{font-size:12pt;margin-bottom:5px}.gk-info p{font-size:11pt;margin-bottom:12px;line-height:1.5}
 .gk-cols{grid-template-columns:1fr 1fr!important;gap:14px;margin-top:18px}.gk-box{break-inside:avoid}
 .gk-ticks,.gk-box.now ol{font-size:11pt}.gk-ticks li,.gk-box.now li{margin-bottom:7px}.gk-box{padding:16px 18px}
 .gk-ch .gk-urg{font-size:8pt;padding:6px 10px}
 .gk-signs{grid-template-columns:1fr 1fr!important;gap:8px}.gk-sign{padding:11px 12px;font-size:10.5pt;break-inside:avoid}.gk-sign svg{display:none}
 .gk-intro{font-size:10.5pt;margin:0 0 12px}
 .gk-tips{grid-template-columns:repeat(3,1fr)!important;gap:8px}.gk-tips>div{padding:10px;break-inside:avoid}.gk-tips p{font-size:9.5pt}.gk-tic{width:30px;height:30px;margin-bottom:6px}
 .gk-unsure{padding:14px 18px;margin-top:6px}.gk-unsure h2{font-size:15pt}
 .gk-lk{break-inside:avoid;margin-bottom:10px}.gk-lk th,.gk-lk td{padding:6px 8px;font-size:9.5pt}
 .gk-faq{columns:2;column-gap:22px}.gk-faq details{break-inside:avoid;border:0;margin-bottom:8px}.gk-faq summary{padding:0 0 3px;font-size:10.5pt}.gk-faq details p{font-size:9.5pt;margin:0}
 .gk-faq details:not([open])>p{display:block}
 .gk-pback{display:block;break-before:page;text-align:center;padding-top:2.4in}
 .gk-pback h2{font-size:28pt;margin:0 0 18px}.gk-pback .gk-pc-call{display:inline-block;background:var(--gk-dark);border-radius:14px;padding:18px 30px;font-size:30pt}
 .gk-pb-url{font-size:14pt;font-weight:700;color:var(--gk-dark);margin:16px 0 30px}.gk-pb-note{font-size:8.5pt;color:var(--gk-muted);max-width:5.6in;margin:0 auto;line-height:1.5}
 .gk-foot{font-size:8.5pt}
}
'''
