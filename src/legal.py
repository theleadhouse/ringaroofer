"""Legal pages, the callback form, TrustedForm, redirects and headers for RingaRoofer."""
from content import PHONE, TEL, EMAIL, URL

CONTACT = f"<p>RingaRoofer<br>Email: <a href='mailto:{EMAIL}'>{EMAIL}</a><br>Phone: <a href='tel:{TEL}'>{PHONE}</a></p>"

CONSENT = ("By clicking “Request my callback”, I agree that RingaRoofer and the roofing company it connects me with may contact me about my roofing request at the phone number and email "
           "I provided, including by calls and texts using automated technology or a prerecorded or artificial voice. Consent is not a condition of any purchase. Message and data charges may apply. "
           "Reply STOP to opt out. I also agree to the <a href='/terms/'>Terms of Use</a> and <a href='/privacy/'>Privacy Policy</a>.")

FORM = f'''<div class="form-wrap"><form class="lead-form" id="lead-form" novalidate>
<h2>Tell us about your roof</h2>
<div class="fg">
 <label>First name<input name="first_name" autocomplete="given-name" required></label>
 <label>Last name<input name="last_name" autocomplete="family-name" required></label>
 <label>Mobile phone<input name="phone" type="tel" inputmode="tel" autocomplete="tel" required placeholder="(555) 555-5555"></label>
 <label>Email<input name="email" type="email" autocomplete="email" required></label>
 <label>ZIP code<input name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" required></label>
 <label>What do you need?<select name="service" required><option value="">Choose one…</option><option>Roof repair</option><option>Roof leak</option><option>Emergency roof repair / tarp</option><option>Storm or hail roof repair</option><option>Roof replacement / re-roof</option><option>New roof</option></select></label>
 <label>Roof type<select name="roof_type"><option value="">Not sure</option><option>Asphalt shingle</option><option>Metal</option><option>Flat (TPO / EPDM / rubber)</option><option>Tile</option><option>Slate</option><option>Cedar shake</option></select></label>
 <label>How soon?<select name="timing"><option>As soon as possible</option><option>Within a week</option><option>Within a month</option><option>Just planning</option></select></label>
 <label class="full">Anything else? <span class="opt">(optional)</span><textarea name="details" maxlength="1000" rows="3"></textarea></label>
</div>
<input type="hidden" name="xxTrustedFormCertUrl" id="xxTrustedFormCertUrl">
<div class="hp" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
<p class="consent" data-tf-element-role="consent-language">{CONSENT}</p>
<button class="btn btn-call block" type="submit" data-tf-element-role="submit">Request my callback</button>
<p class="form-status" role="status" aria-live="polite"></p>
</form>
<aside class="panel"><h3>Faster by phone</h3><p>Calls connect straight to a roofing company serving your area.</p><a class="btn btn-call block" href="tel:{TEL}" data-call>Call {PHONE}</a>
<ul class="ticks sm"><li>Roof repairs and leaks</li><li>New roofs and re-roofs</li><li>Fast emergency service</li></ul></aside></div>'''

TF_SCRIPT = '''<script>
(function () {
  var field = "xxTrustedFormCertUrl", provideReferrer = false, invertFieldSensitivity = false;
  var tf = document.createElement("script"); tf.type = "text/javascript"; tf.async = true;
  tf.src = "https://api.trustedform.com/trustedform.js?provide_referrer=" + escape(provideReferrer) + "&field=" + escape(field) +
    "&l=" + new Date().getTime() + Math.random() + "&invert_field_sensitivity=" + invertFieldSensitivity + "&use_tagged_consent=true";
  var s = document.getElementsByTagName("script")[0]; s.parentNode.insertBefore(tf, s);
})();
</script>
<noscript><img src="https://api.trustedform.com/ns.gif" alt=""></noscript>'''

def S(h, b): return f"<h2>{h}</h2>{b}"
PAGES = [
 dict(url="/privacy/", h1="Privacy Policy", title="Privacy Policy", desc="How RingaRoofer collects, uses and shares personal information.",
  body="".join([
   S("Who we are", "<p>RingaRoofer (“RingaRoofer,” “we,” “us”) operates ringaroofer.com, a referral service that connects homeowners with independent roofing contractors. This policy explains what personal information we collect, how we use and share it, and your choices.</p>"),
   S("Information we collect", "<ul><li><b>Information you give us:</b> name, phone number, email, ZIP code, the roofing help you need and any details you add when you use our callback form.</li><li><b>Call information:</b> when you call a number on our site, we and our call-routing provider process your phone number, the number dialed, date, time, duration, approximate location based on your number or what you tell us, and, where disclosed, a recording of the call.</li><li><b>Form interaction records:</b> our form uses TrustedForm, a service of ActiveProspect, which records how the form was completed, including the consent language shown and your acceptance, time, IP address and browser details, to document consent.</li><li><b>Device and usage information:</b> IP address, browser, device, pages viewed, referring page and ad click identifiers, collected with cookies and similar tools.</li></ul>"),
   S("How we use information", "<ul><li>To connect you with a roofing contractor who serves your area and route your call or request.</li><li>To document consent and maintain records required by law.</li><li>To measure and improve our site and advertising.</li><li>To prevent fraud, abuse and unwanted calls, and to honor Do Not Call requests.</li><li>To comply with law and enforce our terms.</li></ul>"),
   S("How we share information", "<ul><li><b>Roofing contractors:</b> when you call or submit a request, your call is connected to, and your request is shared with, an independent roofing contractor who serves your area so they can contact you about your request.</li><li><b>Service providers:</b> call routing, hosting, form and consent verification, analytics and email providers who work on our behalf.</li><li><b>Advertising and analytics partners:</b> such as Google, Microsoft and Meta, through cookies and pixels, to measure ads. See “Your choices.”</li><li><b>Legal and safety:</b> where required by law or to protect rights and safety.</li><li><b>Business transfers:</b> as part of a merger, acquisition or sale of assets.</li></ul><p>We do not sell lists of homeowner contact information.</p>"),
   S("Cookies and tracking", "<p>We use cookies, pixels and similar technologies for site functions, analytics (Google Analytics) and advertising measurement (Google Ads, Microsoft Advertising, Meta). You can block cookies in your browser. We honor Global Privacy Control signals as an opt-out of sale and sharing, and you can opt out using the “Do Not Sell or Share My Personal Information” link in the footer.</p>"),
   S("Your choices", "<ul><li><b>Calls and texts:</b> tell the caller to stop, reply STOP to texts, or use our <a href='/do-not-call/'>Do Not Call</a> page.</li><li><b>Advertising cookies:</b> use the footer opt-out link or enable Global Privacy Control.</li><li><b>Access and deletion:</b> residents of some states have rights to access, correct and delete personal information. See our <a href='/california-privacy/'>California Privacy</a> page or contact us.</li></ul>"),
   S("Retention and security", "<p>We keep personal information only as long as needed for the purposes above, including consent records required by law, and protect it with reasonable administrative, technical and physical safeguards. No system is perfectly secure.</p>"),
   S("Children", "<p>Our site is for adults and is not directed to children under 16. We do not knowingly collect information from children.</p>"),
   S("Changes and contact", "<p>We may update this policy and will post the new date above.</p>" + CONTACT)])),
 dict(url="/terms/", h1="Terms of Use", title="Terms of Use", desc="Terms for using ringaroofer.com and RingaRoofer's referral service.",
  body="".join([
   S("Agreement", "<p>By using ringaroofer.com or calling a number on it, you agree to these Terms. If you do not agree, do not use the site.</p>"),
   S("Our service", "<p>RingaRoofer is a referral service. We connect homeowners with independent roofing contractors by phone or through our callback form. <b>We do not perform roofing work, we are not a contractor, and we do not employ, supervise or guarantee any contractor.</b> Any agreement for work is solely between you and the contractor, who is responsible for its credentials, permits, scheduling, workmanship and terms. We do not charge homeowners for referrals; contractors pay us for marketing.</p>"),
   S("Your responsibilities", "<p>Confirm any contractor's credentials and coverage before hiring, get the scope of work in writing, and use your own judgment. Provide accurate information and use the site only for lawful, personal purposes.</p>"),
   S("Consent to contact", "<p>If you submit our callback form, you agree to be contacted as described in the consent shown on the form, and you may revoke consent at any time by replying STOP, telling the caller, or using our <a href='/do-not-call/'>Do Not Call</a> page. Calls may be recorded for quality and compliance.</p>"),
   S("Site content", "<p>Information on this site is general and not a substitute for an in-person inspection by a qualified roofer. Availability of contractors varies by location and time.</p>"),
   S("Disclaimers and limitation of liability", "<p>The site and service are provided “as is.” To the fullest extent allowed by law, RingaRoofer disclaims all warranties and is not liable for any indirect, incidental or consequential losses, or for the acts or omissions of any contractor.</p>"),
   S("Disputes", "<p>These Terms are governed by U.S. federal law and the laws of the state where RingaRoofer is organized, without regard to conflict-of-law rules.</p>"),
   S("Changes and contact", "<p>We may update these Terms by posting a new version.</p>" + CONTACT)])),
 dict(url="/referral-disclosure/", h1="Referral Disclosure", title="Referral Disclosure", desc="How RingaRoofer works as a referral service and how it is paid.",
  body=S("How we're paid", "<p>RingaRoofer is a free-to-call referral service for homeowners. Independent roofing contractors, or companies that work with them, pay us for connecting them with homeowners who call or submit a request.</p>".replace("free-to-call", "no-charge")) + S("What that means for you", "<ul><li>We don't perform roofing work and don't endorse any contractor.</li><li>The contractor you're connected with may be one of several in our network serving your area.</li><li>You're never obliged to hire anyone.</li><li>Please confirm the credentials and coverage of any contractor before hiring.</li></ul>") + S("Questions", CONTACT)),
 dict(url="/california-privacy/", h1="California Privacy Rights", title="California Privacy Rights", desc="Notice of California privacy rights and how to opt out of sale or sharing.",
  body="".join([
   S("Notice at collection", "<p>We collect identifiers (name, phone, email, IP address), commercial information (the roofing help you request), internet activity, approximate location and, where disclosed, call recordings, for the purposes described in our <a href='/privacy/'>Privacy Policy</a>. We keep it only as long as needed for those purposes and legal recordkeeping.</p>"),
   S("Your rights", "<p>California residents may request to know, access, correct or delete personal information, and to opt out of the sale or sharing of personal information and of cross-context behavioral advertising. We will not discriminate against you for exercising these rights.</p>"),
   "<h2 id='opt-out'>Do Not Sell or Share My Personal Information</h2><p>Use of advertising cookies and pixels may be considered “sharing.” Click below to opt out on this browser. We also honor Global Privacy Control.</p><p><button class='btn btn-ghost' type='button' data-optout-btn>Opt out on this browser</button> <span class='optout-status' role='status'></span></p>",
   S("How to make a request", f"<p>Email <a href='mailto:{EMAIL}?subject=California%20privacy%20request'>{EMAIL}</a> or call <a href='tel:{TEL}'>{PHONE}</a>. We'll verify your request by matching the information you provide to our records and respond within the time required by law. An authorized agent may submit a request with your written permission.</p>"),
   S("Contact", CONTACT)])),
 dict(url="/do-not-call/", h1="Do Not Call Policy", title="Do Not Call Policy", desc="How to stop calls and texts from RingaRoofer.",
  body="".join([
   S("Our policy", "<p>RingaRoofer maintains a written Do Not Call policy and an internal Do Not Call list. We route calls that homeowners place to us; we do not cold call consumers.</p>"),
   S("How to stop calls and texts", f"<ul><li>Tell the caller you don't want further calls.</li><li>Reply STOP to any text.</li><li>Email <a href='mailto:{EMAIL}?subject=Do%20Not%20Call'>{EMAIL}</a> or call <a href='tel:{TEL}'>{PHONE}</a> with the number to add.</li></ul><p>We process requests promptly and within the time required by law, and ask contractors we work with to honor them.</p>"),
   S("Contact", CONTACT)])),
 dict(url="/accessibility/", h1="Accessibility", title="Accessibility Statement", desc="RingaRoofer's commitment to an accessible website.",
  body=S("Our commitment", "<p>We want ringaroofer.com to work for everyone and aim to meet WCAG 2.1 AA: keyboard access, readable contrast, text alternatives and clear structure.</p>") + S("Need help?", f"<p>If something doesn't work for you, call <a href='tel:{TEL}'>{PHONE}</a> or email <a href='mailto:{EMAIL}'>{EMAIL}</a> and tell us the page and the problem.</p>")),
]

REDIRECTS = """/reviews/write/                                /questions/                                301
/reviews/                                     /questions/                                301
/review-admin/                                /                                          301
/index.html                                   /                                          301
/how-it-works.html                            /how-it-works/                             301
/faq.html                                     /#faq                                      301
/about.html                                   /how-it-works/                             301
/contact.html                                 /contact/                                  301
/reviews.html                                 /                                          301
/referral-disclosure.html                     /referral-disclosure/                      301
/privacy.html                                 /privacy/                                  301
/terms.html                                   /terms/                                    301
/california-privacy.html                      /california-privacy/                       301
/do-not-call.html                             /do-not-call/                              301
/services/roof-replacement.html               /services/roof-replacement/                301
/services/roof-leak.html                      /services/roof-leak-repair/                301
/services/storm-damage.html                   /services/storm-roof-repair/               301
/services/hail-damage.html                    /services/hail-roof-repair/                301
/services/roof-inspection.html                /services/roof-inspection/                 301
/services/emergency-roofing.html              /services/emergency-roof-repair/           301
/services/roof-maintenance.html               /services/roof-repair/                     301
/roofing-types                                /roof-types/                               301
/roofing-types/                               /roof-types/                               301
/roofing-types/shingle-roofing.html           /roof-types/asphalt-shingle/               301
/roofing-types/metal-roofing.html             /roof-types/metal/                         301
/roofing-types/flat-roofing.html              /roof-types/flat/                          301
/roofing-types/tile-roofing.html              /roof-types/tile/                          301
/cities                                       /coverage/                                 301
/cities/*                                     /coverage/                                 301
/resources                                    /library/                                  301
/resources/                                   /library/                                  301
/resources/roof-leak-what-to-do.html          /library/roof-leaking-what-to-do-now/      301
/resources/signs-you-need-a-new-roof.html     /library/signs-you-need-a-new-roof/        301
/resources/roofing-estimate-checklist.html    /library/choosing-a-roofing-material/      301
/call                                         tel:+18556359281                           302
"""
REDIRECTS = REDIRECTS.replace("/call                                         tel:+18556359281                           302\n", "")

HEADERS = """/*
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://challenges.cloudflare.com https://www.googletagmanager.com https://www.google-analytics.com https://www.googleadservices.com https://googleads.g.doubleclick.net https://connect.facebook.net https://bat.bing.com https://www.clarity.ms https://*.clarity.ms https://api.trustedform.com https://cert.trustedform.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https:; frame-src https://challenges.cloudflare.com https://www.googletagmanager.com https://td.doubleclick.net https://www.facebook.com https://*.trustedform.com; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests

/assets/*
  Cache-Control: public, max-age=31536000, immutable
"""
