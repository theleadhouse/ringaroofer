/* RingaRoofer site.js — menu, tracking (US opt-out model, GPC honored), call-click conversions, live weather alerts, callback form */
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
    var u = inject("https://bat.bing.com/bat.js");
    u.onload = function () { var o = { ti: C.microsoftUet, enableAutoSpaTracking: true }; o.q = window.uetq; window.uetq = new UET(o); window.uetq.push("pageLoad"); };
  }
  if (C.clarity) (function (c, l, a, r, i) { c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); }; inject("https://www.clarity.ms/tag/" + i); })(window, d, "clarity", "script", C.clarity);

  function conv(kind) {
    try {
      if (kind === "call") {
        gtag("event", "phone_call_click", { page_location: location.href });
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
  d.addEventListener("click", function (e) { if (e.target.closest("[data-call], a[href^='tel:']")) conv("call"); });

  // ---------- opt-out ----------
  $$("[data-optout-btn]").forEach(function (b) {
    var st = $(".optout-status");
    if (optedOut && st) st.textContent = "You're opted out on this browser.";
    b.addEventListener("click", function () { store("rr_optout", "1"); if (st) st.textContent = "Done. You're opted out on this browser."; });
  });

  // ---------- live weather alerts (National Weather Service) ----------
  var ROOF = /hail|tornado|severe thunderstorm|high wind|extreme wind|wind advisory|hurricane|tropical storm|winter storm|ice storm|blizzard|heavy snow|flash flood/i;
  $$("[data-alerts]").forEach(function (box) {
    var area = box.getAttribute("data-alerts"), url = "https://api.weather.gov/alerts/active?status=actual&message_type=alert" + (area !== "US" ? "&area=" + area : "");
    fetch(url, { headers: { Accept: "application/geo+json" } }).then(function (r) { return r.json(); }).then(function (j) {
      var seen = {}, list = [];
      (j.features || []).forEach(function (f) {
        var p = f.properties || {}; if (!ROOF.test(p.event || "")) return;
        var key = p.event + (area === "US" ? "" : "|" + (p.areaDesc || "").split(";")[0]); if (seen[key]) { seen[key].n++; return; }
        seen[key] = { e: p.event, a: (p.areaDesc || "").split(";").slice(0, 2).join(", "), n: 1 }; list.push(seen[key]);
      });
      if (!list.length) return;
      box.hidden = false;
      box.innerHTML = '<p class="al-h"><span class="dot"></span>Live weather alerts ' + (area === "US" ? "nationwide" : "here") + ' that can affect roofs</p><ul>' +
        list.slice(0, 4).map(function (x) { return "<li><b>" + x.e.replace(/[<>&]/g, "") + "</b>" + (area !== "US" && x.a ? " · " + x.a.replace(/[<>&]/g, "") : x.n > 1 ? " · " + x.n + " active" : "") + "</li>"; }).join("") +
        '</ul><p class="al-s">Source: National Weather Service. Roofers get busy fast after storms, so call early.</p>';
    }).catch(function () {});
  });

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
