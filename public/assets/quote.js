/* Smart 3-step quote form: tiles → ZIP/homeowner/chips → contact + consent. Prefill: ?zip=75201&project=Metal (any tile/chip value).
   TrustedForm cert, POST /api/quote, ad conversions. */
(function () {
  "use strict";
  var f = document.getElementById("qf"); if (!f) return;
  var d = document, cfg = {}; try { cfg = JSON.parse(d.getElementById("qf-cfg").textContent); } catch (e) {}
  var steps = [].slice.call(f.querySelectorAll(".qf-step")), cur = 0, t0 = Date.now(), data = {}, Z = null, zipState = "";
  function q(s, r) { return (r || f).querySelector(s); } function qa(s, r) { return [].slice.call((r || f).querySelectorAll(s)); }
  function track(n, p) { try { if (window.gtag) gtag("event", n, p || {}); } catch (e) {} try { if (window.uetq && uetq.push) uetq.push("event", n, p || {}); } catch (e) {} }
  function esc(x) { return String(x).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function show(i) {
    steps.forEach(function (s, k) { s.hidden = k !== i; }); q("[data-dq]").hidden = true; cur = i;
    qa("[data-dot]").forEach(function (x) { var k = +x.getAttribute("data-dot"); x.className = k < i ? "done" : k === i ? "on" : ""; });
    if (i === 1) setTimeout(function () { var z = q("input[name=zip]"); if (!z.value && window.innerWidth > 760) z.focus({ preventScroll: true }); }, 80);
    if (i === 2) summary();
    var top = f.getBoundingClientRect().top; if (i > 0 && (top < 0 || top > window.innerHeight * .6)) f.scrollIntoView({ behavior: "smooth", block: "start" });
    track("quote_step", { step: i + 1, vertical: cfg.vertical });
  }
  function zips() { return Z || (Z = fetch("/assets/zip3.json").then(function (r) { return r.json(); })); }
  function phoneOk(v) { var p = String(v).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, ""); return /^[2-9]\d{2}[2-9]\d{6}$/.test(p) && !/^(\d)\1{9}$/.test(p) ? p : ""; }
  // ---- step 2 readiness
  function ready() {
    var ok = /^\d{5}$/.test(data.zip || "") && zipState && data.homeowner === "yes";
    qa(".qc-group[data-required]", steps[1]).forEach(function (g) { if (!data[g.getAttribute("data-group")]) ok = false; });
    q("[data-next]").disabled = !ok; return ok;
  }
  var zi = q("input[name=zip]"), zok = q("[data-zok]");
  function checkZip() {
    var v = zi.value.replace(/\D/g, "").slice(0, 5); zi.value = v; data.zip = v; zipState = "";
    if (v.length < 5) { zok.hidden = true; zi.classList.remove("bad", "good"); ready(); return; }
    zips().then(function (m) { var st = m[v.slice(0, 3)];
      if (st) { zipState = st; zok.hidden = false; zok.innerHTML = "✓ " + st; zi.classList.add("good"); zi.classList.remove("bad"); track("quote_zip", { state: st }); }
      else { zok.hidden = false; zok.textContent = "Check ZIP"; zi.classList.add("bad"); }
      ready(); });
  }
  zi.addEventListener("input", checkZip);
  // ---- summary with change links
  function summary() {
    var L = cfg.labels || {}, parts = [];
    Object.keys(L).forEach(function (k) { if (data[k] && k !== "homeowner") parts.push('<span>' + esc(data[k]) + '</span>'); });
    parts.push('<span>' + esc(data.zip) + (zipState ? " " + zipState : "") + "</span>"); parts.push("<span>Homeowner</span>");
    q("[data-sum]").innerHTML = '<div class="qs-items">' + parts.join("") + '</div><button type="button" class="qf-link" data-change>Change</button>';
  }
  // ---- clicks
  f.addEventListener("click", function (e) {
    var t = e.target.closest(".qt");
    if (t) { data[t.getAttribute("data-name")] = t.getAttribute("data-val"); qa(".qt").forEach(function (x) { x.classList.toggle("on", x === t); }); setTimeout(function () { show(1); }, 160); return; }
    var c = e.target.closest(".qc");
    if (c) {
      var n = c.getAttribute("data-name"), v = c.getAttribute("data-val"); data[n] = v;
      qa('.qc[data-name="' + n + '"]').forEach(function (x) { var on = x === c; x.classList.toggle("on", on); x.setAttribute("aria-pressed", String(on)); });
      if (n === "homeowner" && v === "no") { steps.forEach(function (s) { s.hidden = true; }); q("[data-dq]").hidden = false; track("quote_disqualified", { reason: "not_owner" }); return; }
      if (ready()) setTimeout(function () { if (cur === 1 && ready()) show(2); }, 220);
      return;
    }
    if (e.target.closest("[data-next]")) { if (ready()) show(2); else q("[data-err]", steps[1]).hidden = false; }
    if (e.target.closest("[data-change]")) show(0);
    if (e.target.closest("[data-restart]")) { data.homeowner = ""; qa('.qc[data-name="homeowner"]').forEach(function (x) { x.classList.remove("on"); }); show(0); }
  });
  f.addEventListener("keydown", function (e) { if (e.key === "Enter" && cur === 1) { e.preventDefault(); if (ready()) show(2); } });
  // ---- phone format + clear errors
  var ph = q("input[name=phone]");
  ph.addEventListener("input", function () { var p = ph.value.replace(/\D/g, ""); if (p.length === 11 && p[0] === "1") p = p.slice(1); p = p.slice(0, 10);
    ph.value = p.length > 6 ? "(" + p.slice(0, 3) + ") " + p.slice(3, 6) + "-" + p.slice(6) : p.length > 3 ? "(" + p.slice(0, 3) + ") " + p.slice(3) : p; });
  f.addEventListener("input", function (e) { if (e.target.classList) e.target.classList.remove("bad"); var s = e.target.closest(".qf-step"); if (s) { var er = q("[data-err]", s); if (er) er.hidden = true; } });
  // ---- submit
  f.addEventListener("submit", function (e) {
    e.preventDefault(); if (cur !== 2) return;
    var nm = q("input[name=full_name]"), em = q("input[name=email]"), ad = q("input[name=address]"), ok = true;
    var parts = nm.value.trim().replace(/\s+/g, " ").split(" ");
    if (parts.length < 2 || parts[0].length < 1 || parts[parts.length - 1].length < 2) { nm.classList.add("bad"); ok = false; }
    if (!phoneOk(ph.value)) { ph.classList.add("bad"); ok = false; }
    if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(em.value.trim())) { em.classList.add("bad"); ok = false; }
    if (!ok) { q("[data-err]", steps[2]).hidden = false; return; }
    var qs = new URLSearchParams(location.search), body = {};
    Object.keys(data).forEach(function (k) { body[k] = data[k]; });
    body.first_name = parts[0]; body.last_name = parts.slice(1).join(" "); body.phone = phoneOk(ph.value); body.email = em.value.trim(); body.address = ad.value.trim();
    body.state = zipState; body.consent = "yes"; body.vertical = cfg.vertical;
    body.consent_text = (q(".qf-consent") || {}).textContent || "";
    body.xxTrustedFormCertUrl = (q("input[name=xxTrustedFormCertUrl]") || {}).value || "";
    body.website = q("input[name=website]").value; body.elapsed_ms = Date.now() - t0; body.page = location.href;
    ["gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"].forEach(function (k) {
      var v = qs.get(k); if (!v) { try { v = localStorage.getItem("rr_" + k); } catch (x) {} } if (v) body[k] = v; });
    steps.forEach(function (x) { x.hidden = true; }); q(".qf-steps").hidden = true; q("[data-wait]").hidden = false;
    fetch("/api/quote", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        if (!r.ok) throw new Error((r.j && r.j.error) || "error");
        var C = window.RR || {};
        try { if (window.gtag && C.googleAds && C.googleAdsFormLabel) gtag("event", "conversion", { send_to: C.googleAds + "/" + C.googleAdsFormLabel }); } catch (x) {}
        try { if (window.fbq) fbq("track", "Lead"); } catch (x) {}
        track("generate_lead", { vertical: cfg.vertical, method: "get_a_quote" });
        setTimeout(function () { location.href = "/get-a-quote/thanks/"; }, 1300);
      })
      .catch(function (x) {
        q("[data-wait]").hidden = true; q(".qf-steps").hidden = false; show(2);
        var er = q("[data-err]", steps[2]); er.hidden = false;
        er.textContent = x.message === "phone" ? "Please check your mobile number." : "Something went wrong sending your request. Please try again, or call us.";
      });
  });
  // ---- prefill from ad links (?zip=&project=…)
  var qs0 = new URLSearchParams(location.search), pre = 0;
  qs0.forEach(function (v, k) {
    if (k === "zip" && /^\d{5}$/.test(v)) { zi.value = v; checkZip(); return; }
    var el = qa('.qt[data-name="' + k + '"], .qc[data-name="' + k + '"]').filter(function (x) { return x.getAttribute("data-val").toLowerCase() === v.toLowerCase(); })[0];
    if (el && k !== "homeowner") { el.classList.add("on"); data[k] = el.getAttribute("data-val"); if (el.classList.contains("qt")) pre = 1; if (el.classList.contains("qc")) el.setAttribute("aria-pressed", "true"); }
  });
  show(pre);
})();
