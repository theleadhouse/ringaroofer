"""Buyer-approved legal text (Privacy Policy, Terms of Service, California Privacy Rights Notice) shared by all
The Lead House / Ziplead Digital homeowner sites. Source: the pestguardco.com pages our buyers reviewed and approved.
Each site fills in its own domain, email and trade wording. The California notice keeps the approved text and adds
the items CCPA/CPRA regulations also ask for (sources, purposes, third parties, retention, GPC, authorized agents)."""

def _s(id_, h, body): return f"<h2 id='{id_}'>{h}</h2>{body}"

def _contact(domain, email):
    return (f"<p><b>Website:</b> {domain}<br><b>Operating Entity:</b> Ziplead Digital / The Lead House<br>"
            f"<b>Email:</b> <a href='mailto:{email}'>{email}</a></p>")

def privacy(domain, email, trade, notdo, request, dnc_url, tt=False, eff="October 7, 2026"):
    toc = [("visitors", "Website Visitors"), ("pii", "Personally-Identifying Information"), ("tcpa", "FCC &amp; TCPA 1-to-1 Consent Disclosure"),
           ("security", "Data Security"), ("advertising", "Advertising &amp; Remarketing Usage"), ("stats", "Aggregated Statistics"),
           ("cookies", "Cookies"), ("referral", "Referral Service Disclaimer"), ("changes", "Privacy Policy Changes"), ("contact", "Contact Information")]
    tt_p = ("<p>Some links on this site go to Thumbtack, an independent online marketplace and our partner. When you use Thumbtack, Thumbtack's own "
            "<a href='https://www.thumbtack.com/privacy/' rel='noopener'>Privacy Policy</a> and <a href='https://www.thumbtack.com/terms/' rel='noopener'>Terms</a> apply. "
            "Those links include tracking parameters so Thumbtack can credit the referral to us, and we may be paid a referral fee.</p>") if tt else ""
    return "".join([
        f"<p class='eff'><b>{domain}</b><br>Effective Date: {eff}</p>",
        f"<p>Your privacy is important to us. It is the policy of The Lead House, operated by Ziplead Digital (hereinafter, “us”, “we”, or “{domain}”), to respect your privacy regarding any information we may collect while operating our website.</p>",
        "<h2>Contents</h2><p>Click below to jump to any section:</p><ol class='toc'>" + "".join(f"<li><a href='#{i}'>{t}</a></li>" for i, t in toc) + "</ol>",
        _s("visitors", "1. Website Visitors", f"<p>Like most website operators, the Company collects non-personally-identifying information of the sort that web browsers and servers typically make available, such as the browser type, language preference, referring site, and the date and time of each visitor request. Our purpose in collecting this data is to better understand how visitors use {domain}.</p>"),
        _s("pii", "2. Personally-Identifying Information", f"<p>Certain visitors to our Website choose to interact with us in ways that require us to gather personally-identifying information. The amount and type of information depends on the nature of the interaction. For example, when calling us or requesting {request}, we collect your name, phone number, and zip code to facilitate a 1-to-1 match with a local professional. Calls may be recorded for quality assurance.</p>"),
        _s("tcpa", "3. FCC &amp; TCPA 1-to-1 Consent Disclosure", f"<p>In strict accordance with the latest FCC regulations for the home services industry, by interacting with the call buttons or submitting information on {domain}, you provide express written consent to be contacted by The Lead House, Ziplead Digital, and our specific network of pre-vetted local service partners regarding your specific request. You understand that this consent is for a 1-to-1 professional match. You may be contacted via telephone, including cellular numbers, even if your number is on a federal or state Do-Not-Call registry. You can ask us to stop contacting you at any time; see our <a href='{dnc_url}'>Do Not Call</a> page.</p>"),
        _s("security", "4. Data Security", "<p>The security of your Personal Information is a priority. We utilize industry-standard, commercially acceptable means to protect your data. However, please be aware that no method of transmission over the Internet or electronic storage is 100% secure, and we cannot guarantee absolute security.</p>"),
        _s("advertising", "5. Advertising &amp; Remarketing Usage", f"<p>We use remarketing services (including Google Ads, Microsoft Advertising and Meta) to advertise on third-party websites to previous visitors to our Site. This could be in the form of an advertisement on the Google search results page or a social media feed. Third-party vendors use cookies to serve ads based on past visits to {domain}. All data usage is in accordance with our policy and the respective advertising platform's privacy standards.</p>"),
        _s("stats", "6. Aggregated Statistics", "<p>The Company may collect statistics about the behavior of visitors to its website. We may display this information publicly or provide it to others. However, we do not disclose your personally-identifying information to unrelated third-party marketing lists.</p>"),
        _s("cookies", "7. Cookies", "<p>To enrich and perfect your online experience, we use “Cookies” and similar technologies to display personalized content, appropriate advertising, and store your preferences on your computer. A cookie is a string of information that a website stores on a visitor's computer, and that the browser provides to the website each time the visitor returns. By continuing to navigate our website without changing your settings, you hereby acknowledge and agree to our use of cookies. You can opt out of the sale or sharing of your information with the “Do Not Sell or Share My Personal Information” link in our footer, and we honor Global Privacy Control signals.</p>"),
        _s("referral", "8. Referral Service Disclaimer", f"<p>{domain} is a professional referral resource. We do not provide {notdo} directly. All service providers are independent local contractors. It is the homeowner’s responsibility to verify that the contractor they hire furnishes the necessary license and insurance required for the specific work being performed.</p>{tt_p}"),
        _s("changes", "9. Privacy Policy Changes", "<p>Although most changes are likely to be minor, we may change our Privacy Policy from time to time at our sole discretion. We encourage visitors to frequently check this page for any changes. Your continued use of this site after any change in this Privacy Policy will constitute your acceptance of such change.</p>"),
        _s("contact", "10. Contact Information", "<p>If you have any questions about this Privacy Policy or wish to exercise your data rights, please contact our compliance department via email:</p>" + _contact(domain, email)),
        f"<p class='small'>© 2026 {domain} | All Rights Reserved.</p>"])

def terms(domain, email, trade, contractor, notdo, tt=False, eff="October 7, 2026"):
    tt_p = (" This includes Thumbtack, an independent online marketplace and our partner; your use of Thumbtack is governed by Thumbtack's own terms and privacy policy.") if tt else ""
    return "".join([
        f"<p class='eff'><b>{domain}</b><br>Effective Date: {eff}</p>",
        f"<p>Welcome to {domain} (the “Site”). These Terms of Service (“Terms”) govern your access to and use of our website and services. This Site is a brand managed by The Lead House and operated by Ziplead Digital (“we,” “us,” or “the Company”).</p>",
        "<p>By accessing this Site, you agree to be bound by these Terms in full. If you do not agree with any part of these Terms, you must immediately discontinue use of the Site.</p>",
        _s("t1", "1. The Nature of Our Service (Referral Only)", f"<p><b>IMPORTANT:</b> {domain} is a professional referral resource. We are not a {contractor}. We do not perform {notdo} directly. Our role is solely to connect homeowners with independent local service providers. We do not endorse, warrant, or guarantee the work, pricing, or conduct of any contractor found through this Site.</p>"),
        _s("t2", "2. User Responsibilities &amp; Verification", f"<p>It is the sole responsibility of the user (homeowner) to verify that any service provider they hire possesses the necessary state/local licenses, insurance, and bonding required for the {trade} work being performed. We recommend that you request proof of these credentials directly from the contractor before work begins.</p>"),
        _s("t3", "3. Consent to Communication (TCPA Compliance)", f"<p>In accordance with FCC regulations, by submitting your information or interacting with call buttons on {domain}, you provide express written consent to be contacted by The Lead House, Ziplead Digital, and our network of pre-vetted local service partners via telephone (including cellular networks) or email regarding your request. This consent applies even if your number is currently listed on any federal or state Do-Not-Call registry.</p>"),
        _s("t4", "4. Limitation of Liability", "<p>To the maximum extent permitted by law, the Company, its owners, and affiliates shall not be liable for any direct, indirect, incidental, or consequential damages resulting from (a) your use of the Site, (b) the conduct or performance of any third-party service provider, or (c) any disputes arising between you and a contractor.</p>"),
        _s("t5", "5. Intellectual Property Rights", f"<p>Unless otherwise stated, we own the intellectual property rights for all material on {domain}. You may access this for your own personal use, but you must not republish, sell, or duplicate Site content without our express written permission.</p>"),
        _s("t6", "6. Cookies &amp; Technical Data", "<p>We utilize cookies and tracking technologies to enhance user experience and optimize our advertising. By using the Site, you consent to our use of cookies in accordance with our <a href='/privacy/'>Privacy Policy</a>. Our affiliate and advertising partners may also utilize cookies to track conversions and performance.</p>"),
        _s("t7", "7. Prohibited Uses", "<p>You agree not to use the Site for any fraudulent or illegal purposes, including the submission of false information or the harassment of our service partners. We reserve the right to terminate access to any user who violates these standards.</p>"),
        _s("t8", "8. External Links", f"<p>Our Site may contain links to third-party websites or services that are not owned or controlled by us.{tt_p} We have no control over, and assume no responsibility for, the content, privacy policies, or practices of any third-party websites.</p>"),
        _s("t9", "9. Governing Law", "<p>These Terms shall be governed by and construed in accordance with the laws of the United States and the specific jurisdictions in which our operating entities are registered, without regard to conflict of law provisions.</p>"),
        _s("t10", "10. Modifications to Service", f"<p>We reserve the right to change or discontinue any aspect of {domain} or these Terms at any time without prior notice. Your continued use of the Site following any changes constitutes your acceptance of the new Terms.</p>"),
        _s("contact", "Contact Information", "<p>If you have any questions regarding these Terms or our service model, please contact our compliance team:</p>" + _contact(domain, email))])

def ca_privacy(domain, email, trade, eff="October 7, 2026"):
    rows = [("A. Identifiers", "Name, IP address, email address, unique personal identifier.", "YES"),
            ("B. Personal Records", "Telephone number, name, zip code.", "YES"),
            ("C. Commercial Info", f"Records of {trade} services considered or requested.", "YES"),
            ("D. Internet Activity", "Search history, interaction with our website or ads.", "YES"),
            ("E. Geolocation Data", "General location based on IP or Zip Code.", "YES"),
            ("F. Sensory Data", "Call recordings for quality assurance.", "YES"),
            ("G. Inferences", "Consumer profiles reflecting service preferences.", "YES"),
            ("H. Sensitive Info", "Social security numbers, precise biometric data, etc.", "NO")]
    table = ("<div class='tbl'><table><thead><tr><th>Category</th><th>Data Examples</th><th>Collected</th></tr></thead><tbody>"
             + "".join(f"<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td></tr>" for a, b, c in rows) + "</tbody></table></div>")
    return "".join([
        f"<p class='eff'><b>California Privacy Rights Notice</b><br>Effective Date: {eff}</p>",
        f"<p>This privacy notice for California residents supplements the information contained in the main <a href='/privacy/'>Privacy Policy</a> of {domain}, an online brand managed by The Lead House and operated by Ziplead Digital (“the Company”). We adopt this notice to comply with the California Consumer Privacy Act of 2018 (CCPA) and the California Privacy Rights Act of 2020 (CPRA).</p>",
        _s("collect", "1. Categories of Information We Collect", f"<p>In the preceding twelve (12) months, the Company has collected the following categories of personal information to facilitate {trade} service requests:</p>{table}"
           f"<p><b>NOTICE:</b> In the preceding 12 months, the Company has shared or “sold” (as broadly defined by California law) personal information to our network of matched service providers and marketing partners for the express business purpose of fulfilling your {trade} service request.</p>"),
        _s("sources", "2. Sources, Purposes &amp; Who Receives It", "<ul><li><b>Sources:</b> directly from you (calls, forms and emails), from your browser or device (cookies and similar tools), and from our call-routing and analytics providers.</li>"
           f"<li><b>Purposes:</b> to connect you with a local service provider for your request, to operate and secure the Site, to measure and improve our advertising, to prevent fraud, and to comply with law.</li>"
           "<li><b>Categories of third parties:</b> matched local service providers and the companies that work with them, call-routing, hosting and analytics providers, and advertising partners such as Google, Microsoft and Meta.</li>"
           "<li><b>Retention:</b> we keep personal information only as long as reasonably necessary for these purposes, generally no longer than 24 months after your last interaction with us, unless a longer period is required by law or to resolve disputes.</li>"
           "<li><b>Sensitive information:</b> we do not collect sensitive personal information, so the right to limit its use does not apply.</li></ul>"),
        _s("rights", "3. Your Rights Under CCPA/CPRA", "<p>As a California resident, you have the following specific rights regarding your data:</p><ul>"
           "<li><b>Right to Know &amp; Access:</b> You may request that we disclose the categories and specific pieces of personal information we have collected about you over the past 12 months.</li>"
           "<li><b>Right to Correct:</b> You have the right to request that we correct any inaccurate personal information that we maintain about you.</li>"
           "<li><b>Right to Delete:</b> You may request that we delete personal information we have collected from you, subject to certain legal exceptions.</li>"
           "<li><b>Right to Opt-Out:</b> You have the right to direct us not to “sell” or “share” your personal information for cross-context behavioral advertising.</li></ul>"),
        _s("exercise", "4. Exercising Your Data Rights", f"<p>To exercise your rights to know, correct, or delete your information, please submit a verifiable consumer request to our compliance team via email:</p><p><b>Email:</b> <a href='mailto:{email}?subject=California%20privacy%20request'>{email}</a></p>"
           "<p>We will verify your request by matching information you provide (such as the phone number you called from) with information we hold. You may use an authorized agent to submit a request on your behalf with your signed written permission; we may ask you to confirm your identity directly.</p>"
           "<p>To exercise your Right to Opt-Out of the sale or sharing of information, please use the “Do Not Sell or Share My Personal Information” link located in our website footer, or the button below.</p>"),
        "<h2 id='opt-out'>Do Not Sell or Share My Personal Information</h2><p>Advertising cookies and pixels may be considered “selling” or “sharing” under California law. Click below to opt out on this browser. We also honor Global Privacy Control (GPC) signals as a valid opt-out request.</p>"
        "<p><button class='btn btn-ghost' type='button' data-optout-btn>Opt out on this browser</button> <span class='optout-status' role='status'></span></p>",
        _s("timing", "5. Response Timing", "<p>We aim to respond to a verifiable consumer request within forty-five (45) days of receipt. If we require more time (up to 90 days total), we will inform you of the reason and extension period in writing.</p>"),
        _s("nondiscrimination", "6. Non-Discrimination", "<p>We will not discriminate against you for exercising any of your CCPA/CPRA rights. Unless permitted by law, we will not deny you services or provide a different level of quality because you exercised your privacy rights.</p>"),
        "<p><b>Website:</b> " + domain + "<br><b>Operating Entity:</b> Ziplead Digital / The Lead House<br><b>Compliance Contact:</b> <a href='mailto:" + email + "'>" + email + "</a></p>",
        f"<p class='small'>© 2026 {domain} | All Rights Reserved.</p>"])

def apply(pages, domain, email, trade, contractor, notdo, request, tt=False, eff_main="October 7, 2026", eff_ca="October 7, 2026"):
    """Swap the Privacy, Terms and California pages in a site's legal PAGES list for the approved text."""
    by = {p["url"]: p for p in pages}
    ca = by.get("/ca-privacy/") or by.get("/california-privacy/")
    dnc = "/dnc/" if "/dnc/" in by else "/do-not-call/"
    p = by["/privacy/"]
    p.update(h1="Privacy Policy", title="Privacy Policy", desc=f"How {domain} collects, uses and protects your information.", body=privacy(domain, email, trade, notdo, request, dnc, tt, eff_main))
    t = by["/terms/"]
    t.update(h1="Terms of Service", title="Terms of Service", desc=f"Terms of Service for {domain}, a referral service managed by The Lead House and operated by Ziplead Digital.", body=terms(domain, email, trade, contractor, notdo, tt, eff_main))
    ca.update(h1="California Privacy Rights Notice", title="California Privacy Rights Notice", desc=f"California (CCPA/CPRA) privacy rights for {domain} visitors, and how to opt out of sale or sharing.", body=ca_privacy(domain, email, trade, eff_ca))
    return pages
