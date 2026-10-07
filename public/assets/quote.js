/* Get-matched funnel: one question per screen, auto-advance, validation, ZIP → state, TrustedForm cert, POST /api/quote, ad conversions. */
(function () {
  "use strict";
  var f = document.getElementById("qf"); if (!f) return;
  var d = document, cfg = {}; try { cfg = JSON.parse(d.getElementById("qf-cfg").textContent); } catch (e) {}
  var steps = [].slice.call(f.querySelectorAll(".qf-step")), cur = 0, t0 = Date.now(), data = {}, Z = null;
  var bar = f.querySelector("[data-bar]"), count = f.querySelector("[data-count]"), back = f.querySelector("[data-back]");
  function q(s, r) { return (r || f).querySelector(s); }
  function track(n, p) { try { if (window.gtag) gtag("event", n, p || {}); } catch (e) {} try { if (window.uetq && uetq.push) uetq.push("event", n, p || {}); } catch (e) {} }
  function show(i) {
    steps.forEach(function (s, k) { s.hidden = k !== i; });
    cur = i; bar.style.width = Math.round((i + 1) / steps.length * 100) + "%";
    count.textContent = "Step " + (i + 1) + " of " + steps.length; back.hidden = i === 0;
    var first = steps[i].querySelector("input:not([type=checkbox]),.qt"); if (first && window.innerWidth > 760) setTimeout(function () { first.focus({ preventScroll: true }); }, 60);
    if (i > 0 && f.getBoundingClientRect().top < 0) f.scrollIntoView({ behavior: "smooth", block: "start" });
    track("quote_step", { step: i + 1, vertical: cfg.vertical });
  }
  function zips() { return Z || (Z = fetch("/assets/zip3.json").then(function (r) { return r.json(); })); }
  function err(s, on) { var e = s.querySelector("[data-err]"); if (e) e.hidden = !on; }
  function phoneOk(v) { var p = v.replace(/\D/g, "").replace(/^1(?=\d{10}$)/, ""); return p.length === 10 && /^[2-9]\d{2}[2-9]\d{6}$/.test(p) && !/^(\d)\1{9}$/.test(p) ? p : ""; }
  function valid(s) {
    var ok = true;
    [].forEach.call(s.querySelectorAll("[data-req]"), function (i) {
      var v = (i.value || "").trim(), good = !!v;
      if (i.name === "zip") good = /^\d{5}$/.test(v);
      if (i.name === "email") good = /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(v);
      if (i.name === "state") good = /^[A-Za-z]{2}$/.test(v);
      if (i.name === "phone") good = !!phoneOk(v);
      i.classList.toggle("bad", !good); if (!good) ok = false;
    });
    var cb = s.querySelector("input[name=consent]"); if (cb && !cb.checked) ok = false;
    err(s, !ok); return ok;
  }
  function next() {
    var s = steps[cur]; if (!valid(s)) return;
    [].forEach.call(s.querySelectorAll("input"), function (i) { if (i.name && i.type !== "checkbox") data[i.name] = i.value.trim(); });
    if (s.getAttribute("data-kind") === "zip") {
      zips().then(function (m) { var st = m[data.zip.slice(0, 3)]; var si = f.querySelector("input[name=state]"); if (st && si && !si.value) si.value = st; data.state_from_zip = st || ""; });
    }
    if (cur < steps.length - 1) show(cur + 1);
  }
  f.addEventListener("click", function (e) {
    var tile = e.target.closest(".qt");
    if (tile) {
      var name = tile.getAttribute("data-name"), val = tile.getAttribute("data-val");
      [].forEach.call(steps[cur].querySelectorAll(".qt"), function (x) { x.classList.toggle("on", x === tile); });
      data[name] = val;
      if (name === cfg.owner_field && val === "no") { steps.forEach(function (s) { s.hidden = true; }); q("[data-dq]").hidden = false; track("quote_disqualified", { reason: "not_owner" }); return; }
      setTimeout(function () { show(cur + 1); }, 180); return;
    }
    if (e.target.closest("[data-next]")) next();
    if (e.target.closest("[data-back]") && cur > 0) show(cur - 1);
    if (e.target.closest("[data-restart]")) { q("[data-dq]").hidden = true; data = {}; show(0); }
  });
  f.addEventListener("keydown", function (e) { if (e.key === "Enter" && e.target.tagName === "INPUT" && steps[cur].querySelector("[data-next]")) { e.preventDefault(); next(); } });
  f.addEventListener("input", function (e) { var s = e.target.closest(".qf-step"); if (s) { e.target.classList && e.target.classList.remove("bad"); err(s, false); } });
  f.addEventListener("change", function (e) { var s = e.target.closest(".qf-step"); if (s) err(s, false); });
  var ph = f.querySelector("input[name=phone]");
  if (ph) ph.addEventListener("input", function () { var p = ph.value.replace(/\D/g, "").slice(0, 11); if (p.length === 11 && p[0] === "1") p = p.slice(1); p = p.slice(0, 10);
    ph.value = p.length > 6 ? "(" + p.slice(0, 3) + ") " + p.slice(3, 6) + "-" + p.slice(6) : p.length > 3 ? "(" + p.slice(0, 3) + ") " + p.slice(3) : p; });
  f.addEventListener("submit", function (e) {
    e.preventDefault(); var s = steps[cur]; if (!valid(s)) return;
    var qs = new URLSearchParams(location.search), body = {};
    Object.keys(data).forEach(function (k) { body[k] = data[k]; });
    body.phone = phoneOk(ph.value); body.consent = "yes"; body.vertical = cfg.vertical;
    body.consent_text = (q("[data-tf-element-role=consent-language]") || {}).textContent || "";
    body.xxTrustedFormCertUrl = (q("input[name=xxTrustedFormCertUrl]") || {}).value || "";
    body.website = q("input[name=website]").value; body.elapsed_ms = Date.now() - t0; body.page = location.href;
    ["gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"].forEach(function (k) {
      var v = qs.get(k); if (!v) { try { v = localStorage.getItem("rr_" + k); } catch (x) {} } if (v) body[k] = v; });
    steps.forEach(function (x) { x.hidden = true; }); q("[data-wait]").hidden = false; q(".qf-top").hidden = true; q(".qf-bar").hidden = true;
    fetch("/api/quote", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        if (!r.ok) throw new Error((r.j && r.j.error) || "error");
        var C = window.RR || {};
        try { if (window.gtag && C.googleAds && C.googleAdsFormLabel) gtag("event", "conversion", { send_to: C.googleAds + "/" + C.googleAdsFormLabel }); } catch (x) {}
        try { if (window.fbq) fbq("track", "Lead"); } catch (x) {}
        track("generate_lead", { vertical: cfg.vertical, method: "get_matched" });
        setTimeout(function () { location.href = "/get-matched/thanks/"; }, 1400);
      })
      .catch(function (x) {
        q("[data-wait]").hidden = true; q(".qf-top").hidden = false; q(".qf-bar").hidden = false; show(steps.length - 1);
        var e2 = steps[cur].querySelector("[data-err]"); e2.hidden = false;
        e2.textContent = x.message === "phone" ? "Please check your phone number." : "Something went wrong sending your request. Please try again, or call us.";
      });
  });
  show(0);
})();
