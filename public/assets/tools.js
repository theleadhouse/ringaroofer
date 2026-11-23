/* RingaRoofer tools: roof pitch calculator, roof size (squares) calculator, storm notes card print, roofing pros form. Nothing stored. */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var fmt = function (n) { return Math.round(n).toLocaleString("en-US"); };
  // ---------- pitch: rise per 12 of run (or measured rise + run) -> angle, factor, steepness note
  var pc = $("#pitchcalc");
  if (pc) {
    var runP = function () {
      var rise = Math.max(0, +$("#pc-rise").value || 0), run = Math.max(0.1, +$("#pc-run").value || 12);
      var r12 = rise / run * 12, deg = Math.atan(rise / run) * 180 / Math.PI, f = Math.sqrt(1 + Math.pow(rise / run, 2));
      $("#pc-out").hidden = false;
      $("#pc-p").textContent = (Math.round(r12 * 10) / 10) + "/12"; $("#pc-d").textContent = (Math.round(deg * 10) / 10) + "°"; $("#pc-f").textContent = f.toFixed(3);
      var n = r12 < 2 ? "Flat or nearly flat. Usually covered with a membrane (TPO, EPDM, modified bitumen), not shingles." :
              r12 < 4 ? "Gentle slope. Shingles on slopes like this usually need extra underlayment; many roofers use other materials." :
              r12 < 7 ? "Moderate slope, the most common range for houses with shingles." :
              r12 < 10 ? "Steep. Roofers use extra safety gear and roof jacks." : "Very steep. Specialized safety setup needed.";
      $("#pc-n").textContent = n + " Whatever the pitch, stay off the roof yourself.";
    };
    pc.addEventListener("input", runP);
    pc.querySelectorAll("[data-rise]").forEach(function (b) { b.addEventListener("click", function () { $("#pc-rise").value = b.getAttribute("data-rise"); $("#pc-run").value = 12; runP(); }); });
    runP();
  }
  // ---------- size: footprint (+ overhang) x pitch factor -> roof area and squares
  var sc = $("#sizecalc");
  if (sc) {
    var runS = function () {
      var L = +$("#sc-l").value || 0, W = +$("#sc-w").value || 0, oh = (+$("#sc-oh").value || 0) / 12, p = +$("#sc-p").value || 0;
      var foot = (L + 2 * oh) * (W + 2 * oh), f = Math.sqrt(1 + Math.pow(p / 12, 2)), area = foot * f;
      $("#sc-out").hidden = !(L && W);
      $("#sc-a").textContent = fmt(area); $("#sc-q").textContent = (Math.round(area / 10) / 10).toFixed(1); $("#sc-fp").textContent = fmt(foot);
    };
    sc.addEventListener("input", runS); runS();
  }
  // ---------- print card
  var pb = $("[data-printcard]"); if (pb) pb.addEventListener("click", function () { window.print(); });
  // ---------- pros form
  var pf = $("#pro-form");
  if (pf) {
    var t0 = Date.now();
    pf.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = $("#pro-msg"), btn = pf.querySelector("button[type=submit]"), d = {};
      new FormData(pf).forEach(function (v, k) { d[k] = d[k] ? d[k] + ", " + v : v; });
      d.agree = pf.querySelector("[name=agree]").checked ? "yes" : ""; d.elapsed_ms = Date.now() - t0;
      if (!d.company || !d.contact || !d.phone || !d.email || d.agree !== "yes") { msg.hidden = false; msg.className = "pro-msg warn"; msg.textContent = "Please fill in company, contact name, phone and email, and tick the box."; return; }
      btn.disabled = true; btn.textContent = "Sending…";
      fetch("/api/pro", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(d) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (x) {
          msg.hidden = false;
          if (x.ok) { pf.reset(); msg.className = "pro-msg ok"; msg.textContent = "Thanks. We've received your details and will reach out by phone or email."; if (window.gtag) gtag("event", "pro_application"); }
          else { msg.className = "pro-msg warn"; msg.textContent = x.j && x.j.error === "phone" ? "Please check the phone number." : x.j && x.j.error === "email" ? "Please check the email address." : "Something went wrong. Please email us instead."; }
        })
        .catch(function () { msg.hidden = false; msg.className = "pro-msg warn"; msg.textContent = "Something went wrong. Please email us instead."; })
        .then(function () { btn.disabled = false; btn.textContent = "Send my details"; });
    });
  }
})();
