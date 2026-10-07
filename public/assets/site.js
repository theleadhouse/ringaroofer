/* RingaRoofer site.js — menu, tracking (US opt-out model, GPC honored), call-click conversions with placement, project matcher */
(function () {
  "use strict";
  var C = window.RR || {}, d = document;
  function $(s, r) { return (r || d).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || d).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  // ---------- menu ----------
  var mb = $(".menu"), mn = $("#mnav");
  if (mb && mn) mb.addEventListener("click", function () { var o = mn.hidden; mn.hidden = !o; mb.setAttribute("aria-expanded", String(o)); });
  $$(".dd-btn").forEach(function (b) { b.addEventListener("click", function () { var li = b.parentNode, o = !li.classList.contains("open"); $$(".has-dd").forEach(function (x) { x.classList.remove("open"); }); li.classList.toggle("open", o); b.setAttribute("aria-expanded", String(o)); }); });
  d.addEventListener("click", function (e) { if (!e.target.closest(".has-dd")) $$(".has-dd").forEach(function (x) { x.classList.remove("open"); }); });

  // ---------- click IDs (kept for the form) ----------
  var qs = new URLSearchParams(location.search);
  ["gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"].forEach(function (k) { if (qs.get(k)) store("rr_" + k, qs.get(k)); });

  // ---------- tags (load unless opted out or GPC) ----------
  var optedOut = store("rr_optout") === "1" || navigator.globalPrivacyControl === true;
  function inject(src) { var s = d.createElement("script"); s.async = true; s.src = src; d.head.appendChild(s); return s; }
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  gtag("js", new Date());
  if (C.ga4 || C.googleAds) {
    inject("https://www.googletagmanager.com/gtag/js?id=" + (C.ga4 || C.googleAds));
    if (optedOut) gtag("set", { allow_ad_personalization_signals: false, restricted_data_processing: true });
    if (C.ga4) gtag("config", C.ga4);
    if (C.googleAds) gtag("config", C.googleAds, optedOut ? { allow_ad_personalization_signals: false } : {});
  }
  if (!optedOut && C.metaPixel) {
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, d, "script", "https://connect.facebook.net/en_US/fbevents.js");
    fbq("init", C.metaPixel); fbq("track", "PageView");
  }
  if (!optedOut && C.microsoftUet) {
    window.uetq = window.uetq || [];
    var u = inject("https://bat.bing.net/bat.js");
    u.onload = function () { var o = { ti: C.microsoftUet, enableAutoSpaTracking: true }; o.q = window.uetq; window.uetq = new UET(o); window.uetq.push("pageLoad"); };
  }
  if (C.clarity) (function (c, l, a, r, i) { c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); }; inject("https://www.clarity.ms/tag/" + i); })(window, d, "clarity", "script", C.clarity);

  function conv(kind, place) {
    try {
      if (kind === "call") {
        gtag("event", "phone_call_click", { page_location: location.href, placement: place || "" });
        if (C.googleAds && C.googleAdsCallLabel) gtag("event", "conversion", { send_to: C.googleAds + "/" + C.googleAdsCallLabel });
        if (window.fbq) fbq("track", "Contact");
        if (window.uetq && window.uetq.push) window.uetq.push("event", "phone_call_click", {});
      } else {
        gtag("event", "generate_lead", { method: "callback_form" });
        if (C.googleAds && C.googleAdsFormLabel) gtag("event", "conversion", { send_to: C.googleAds + "/" + C.googleAdsFormLabel });
        if (window.fbq) fbq("track", "Lead");
        if (window.uetq && window.uetq.push) window.uetq.push("event", "submit_lead_form", {});
      }
    } catch (e) {}
  }
  d.addEventListener("click", function (e) {
    var c = e.target.closest("[data-call], a[href^='tel:']");
    if (c) conv("call", c.getAttribute("data-call"));
    var t = e.target.closest("[data-tt]");
    if (t) try {
      gtag("event", "thumbtack_click", { placement: t.getAttribute("data-tt"), transport_type: "beacon" });
      if (C.googleAds && C.googleAdsThumbtackLabel) gtag("event", "conversion", { send_to: C.googleAds + "/" + C.googleAdsThumbtackLabel, transport_type: "beacon" });
      if (window.uetq && window.uetq.push) window.uetq.push("event", "thumbtack_click", {});
    } catch (x) {}
  });

  // ---------- opt-out ----------
  $$("[data-optout-btn]").forEach(function (b) {
    var st = $(".optout-status");
    if (optedOut && st) st.textContent = "You're opted out on this browser.";
    b.addEventListener("click", function () { store("rr_optout", "1"); if (st) st.textContent = "Done. You're opted out on this browser."; });
  });

  // ---------- live weather alerts (National Weather Service) ----------
  var WET = /severe thunderstorm|tornado|hurricane|tropical storm|high wind|extreme wind|wind advisory|winter storm|ice storm|blizzard|heavy snow|hail/i;
  $$("[data-alerts]").forEach(function (box) {
    var area = box.getAttribute("data-alerts"), url = "https://api.weather.gov/alerts/active?status=actual&message_type=alert" + (area !== "US" ? "&area=" + area : "");
    fetch(url, { headers: { Accept: "application/geo+json" } }).then(function (r) { return r.json(); }).then(function (j) {
      var seen = {}, list = [];
      (j.features || []).forEach(function (f) {
        var p = f.properties || {}; if (!WET.test(p.event || "")) return;
        var key = p.event + (area === "US" ? "" : "|" + (p.areaDesc || "").split(";")[0]); if (seen[key]) { seen[key].n++; return; }
        seen[key] = { e: p.event, a: (p.areaDesc || "").split(";").slice(0, 2).join(", "), n: 1 }; list.push(seen[key]);
      });
      if (!list.length) return;
      box.hidden = false;
      box.innerHTML = '<p class="al-h"><span class="dot"></span>Live weather alerts ' + (area === "US" ? "nationwide" : "here") + ' that can hit roofs</p><ul>' +
        list.slice(0, 4).map(function (x) { return "<li><b>" + x.e.replace(/[<>&]/g, "") + "</b>" + (area !== "US" && x.a ? " · " + x.a.replace(/[<>&]/g, "") : x.n > 1 ? " · " + x.n + " active" : "") + "</li>"; }).join("") +
        '</ul><p class="al-s">Source: National Weather Service. Roofers book up fast after storms, so call early.</p>';
    }).catch(function () {});
  });

  // ---------- project matcher ----------
  var mt = $("#match");
  if (mt) {
    var mi = $("[data-mimg]", mt), ti = $("[data-mtitle]", mt), tx = $("[data-mtext]", mt), ln = $("[data-mlink]", mt), mc = $(".m-call", mt), mtt = $(".m-tt", mt);
    $$(".mchip", mt).forEach(function (b) {
      b.addEventListener("click", function () {
        $$(".mchip", mt).forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        ti.textContent = b.getAttribute("data-name"); tx.textContent = b.getAttribute("data-msg");
        ln.setAttribute("href", b.getAttribute("data-url"));
        var tt = b.getAttribute("data-route") === "thumbtack"; mc.hidden = tt; mtt.hidden = !tt;
        mi.style.opacity = ".3"; var im = new Image(); im.onload = function () { mi.src = im.src; mi.style.opacity = "1"; }; im.onerror = function () { mi.style.opacity = "1"; }; im.src = b.getAttribute("data-photo");
        try { gtag("event", "project_pick", { project: b.getAttribute("data-k") }); } catch (e) {}
      });
    });
  }

  // ---------- broken image fallback ----------
  d.addEventListener("error", function (e) { var t = e.target; if (t && t.tagName === "IMG") { t.classList.add("img-x"); t.removeAttribute("srcset"); } }, true);

  // header height for sticky sub-nav
  var hd = $(".hdr"); function hh() { if (hd) d.documentElement.style.setProperty("--hh", hd.offsetHeight + "px"); } hh(); window.addEventListener("resize", hh);

  // ---------- tab bar menu button ----------
  $$(".tb-menu").forEach(function (b) { b.addEventListener("click", function () { var m = $("#mnav"); if (!m) return; m.hidden = !m.hidden; window.scrollTo({ top: 0, behavior: "smooth" }); }); });

  // ---------- reviews (published, moderated, real callers) ----------
  function esc2(x) { return String(x || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function stars(n) { n = Math.round(n); return "★★★★★".slice(0, n) + "☆☆☆☆☆".slice(0, 5 - n); }
  function mon(m) { if (!m) return ""; var p = m.split("-"); return ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][+p[1] - 1] + " " + p[0]; }
  $$("[data-reviews]").forEach(function (w) {
    var pest = w.getAttribute("data-pest") || "", lim = w.getAttribute("data-limit") || "3";
    fetch("/api/reviews?limit=" + lim + (pest ? "&pest=" + encodeURIComponent(pest) : "")).then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
      if (!j || !j.count) return;
      $("[data-rv-empty]", w).hidden = true;
      var s = $("[data-rv-sum]", w); s.hidden = false;
      s.innerHTML = '<span class="rv-avg">' + j.avg.toFixed(1) + '</span><span><span class="rv-stars" aria-label="' + j.avg + ' out of 5">' + stars(j.avg) + '</span><br><span class="rv-meta">' + j.count + ' review' + (j.count > 1 ? "s" : "") + (pest ? " about " + esc2(pest.toLowerCase()) : "") + ' from callers</span></span>';
      $("[data-rv-list]", w).innerHTML = j.reviews.map(function (r) {
        return '<article class="rv"><div class="rv-stars" aria-label="' + r.rating + ' out of 5">' + stars(r.rating) + '</div><h3>' + esc2(r.title || r.pest) + '</h3><p>' + esc2(r.text) + '</p>' +
          (r.reply ? '<p class="rv-reply"><b>Our reply:</b> ' + esc2(r.reply) + '</p>' : "") +
          '<p class="rv-meta">' + esc2(r.name) + ' · ' + esc2([r.city, r.state].filter(Boolean).join(", ")) + ' · ' + esc2(r.pest) + (r.month ? " · " + mon(r.month) : "") + (r.verified ? '<span class="rv-ver">✓ Verified caller</span>' : "") + '</p></article>';
      }).join("");
    }).catch(function () {});
  });
  var rf = $("[data-review-form]");
  if (rf) {
    var msg = $("[data-f-msg]", rf), tsBox = $("[data-turnstile]", rf);
    if (C.turnstileSiteKey && tsBox) { var ts = d.createElement("div"); ts.className = "cf-turnstile"; ts.setAttribute("data-sitekey", C.turnstileSiteKey); tsBox.appendChild(ts); inject("https://challenges.cloudflare.com/turnstile/v0/api.js"); }
    rf.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = new FormData(rf), b = {};
      f.forEach(function (v, k) { b[k] = v; });
      b.consent = !!rf.consent.checked; b.turnstile = f.get("cf-turnstile-response") || "";
      if (!b.rating) { msg.className = "f-msg err"; msg.textContent = "Please choose a star rating."; return; }
      msg.className = "f-msg"; msg.textContent = "Sending…";
      fetch("/api/reviews", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(b) }).then(function (r) { return r.json(); }).then(function (j) {
        if (j.ok) { rf.reset(); msg.className = "f-msg ok"; msg.textContent = "Thank you! Your review was received. We check every review against our call records before it appears, usually within a few days."; try { gtag("event", "review_submit", { rating: b.rating }); } catch (x) {} }
        else { msg.className = "f-msg err"; msg.textContent = j.error || "Something went wrong. Please try again."; }
      }).catch(function () { msg.className = "f-msg err"; msg.textContent = "Couldn't send. Please check your connection and try again."; });
    });
  }
  var adm = $("[data-review-admin]");
  if (adm) {
    var tk = $("[data-adm-token]", adm), out = $("[data-adm-out]", adm);
    try { tk.value = sessionStorage.getItem("ee_adm") || ""; } catch (x) {}
    function api(m, body) { return fetch("/api/reviews-admin", { method: m, headers: { authorization: "Bearer " + tk.value, "content-type": "application/json" }, body: body ? JSON.stringify(body) : undefined }).then(function (r) { return r.json(); }); }
    function load() {
      try { sessionStorage.setItem("ee_adm", tk.value); } catch (x) {}
      api("GET").then(function (j) {
        if (j.error) { out.textContent = j.error; return; }
        out.innerHTML = "<h2>Waiting for review (" + j.pending.length + ")</h2>" + (j.pending.map(function (r) {
          return '<div class="adm" data-id="' + r.id + '"><b>' + stars(r.rating) + " " + esc2(r.title) + '</b><p>' + esc2(r.text) + '</p><p class="rv-meta">' + esc2(r.name) + " · " + esc2(r.city) + " " + r.state + " · " + esc2(r.pest) + " · call date " + (r.callDate || "?") + " · phone last 4: " + (r.last4 || "?") + " · " + esc2(r.email || "") + '</p>' +
            '<textarea placeholder="Optional public reply" rows="2"></textarea><div class="row"><label><input type="checkbox" class="ver"> Matched to a call (Verified caller)</label><button class="btn btn-call sm" data-a="approve">Publish</button><button class="btn btn-ghost sm" data-a="reject">Reject (spam/abuse/not a caller)</button></div></div>';
        }).join("") || "<p>Nothing waiting.</p>") + "<h2>Published</h2>" + j.published.map(function (r) { return '<div class="adm" data-id="' + r.id + '"><b>' + stars(r.rating) + " " + esc2(r.title) + '</b> <span class="rv-meta">' + esc2(r.name) + '</span><div class="row"><button class="btn btn-ghost sm" data-a="unpublish">Unpublish</button></div></div>'; }).join("");
        $$("[data-a]", out).forEach(function (b) { b.addEventListener("click", function () {
          var box = b.closest(".adm"), ta = $("textarea", box), ver = $(".ver", box);
          api("POST", { id: box.getAttribute("data-id"), action: b.getAttribute("data-a"), verified: ver ? ver.checked : false, reply: ta ? ta.value : "" }).then(load);
        }); });
      });
    }
    $("[data-adm-load]", adm).addEventListener("click", load);
  }
  // ---------- callback form ----------
  var f = $("#lead-form");
  if (f) {
    var started = Date.now(), status = $(".form-status", f);
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = $$("[required]", f).filter(function (x) { return !x.value.trim(); });
      if (bad.length) { status.textContent = "Please fill in the highlighted fields."; bad.forEach(function (x) { x.setAttribute("aria-invalid", "true"); }); bad[0].focus(); return; }
      var ph = f.phone.value.replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
      if (ph.length !== 10) { status.textContent = "Please enter a 10-digit U.S. phone number."; f.phone.focus(); return; }
      if (!/^\d{5}$/.test(f.zip.value.trim())) { status.textContent = "Please enter a 5-digit ZIP code."; f.zip.focus(); return; }
      var data = {}; new FormData(f).forEach(function (v, k) { data[k] = v; });
      data.phone = ph; data.elapsed_ms = Date.now() - started; data.page = location.href; data.consent_text = $(".consent", f).textContent.trim();
      ["gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"].forEach(function (k) { var v = store("rr_" + k); if (v) data[k] = v; });
      var btn = $("button[type=submit]", f); btn.disabled = true; status.textContent = "Sending…";
      fetch(C.formEndpoint || "/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (x) {
          if (!x.ok) throw new Error(x.j && x.j.error || "error");
          conv("form");
          f.innerHTML = '<h2>Thanks, ' + String(data.first_name).replace(/[<>&]/g, "") + '.</h2><p>A roofing company serving your area will call you shortly. Need help now? Call <a href="tel:' + C.phone + '" data-call>' + C.phoneDisplay + "</a>.</p>";
        })
        .catch(function () { btn.disabled = false; status.innerHTML = 'Sorry, that didn\'t go through. Please call <a href="tel:' + C.phone + '">' + C.phoneDisplay + "</a>."; });
    });
  }
})();
