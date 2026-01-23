#!/usr/bin/env python3
"""
Generate SEO landing pages for Farmers First service area
Enhanced version with FAQ schema, breadcrumbs, cross-links to partner sites
"""

import os
from string import Template

# PRIMARY SERVICE AREA
PRIMARY_COUNTIES = {
    "WI": {
        "Barron": ["Rice Lake", "Chetek", "Cameron", "Cumberland", "Turtle Lake", "Barron", "Almena", "Dallas", "Haugen", "Prairie Lake"],
        "Dunn": ["Menomonie", "Colfax", "Elk Mound", "Boyceville", "Ridgeland", "Downing", "Wheeler", "Knapp"],
        "St. Croix": ["Hudson", "New Richmond", "River Falls", "Somerset", "Roberts", "Baldwin", "Hammond", "Woodville", "Glenwood City"],
        "Polk": ["St. Croix Falls", "Amery", "Osceola", "Luck", "Milltown", "Balsam Lake", "Centuria", "Frederic", "Clear Lake"],
        "Washburn": ["Spooner", "Shell Lake", "Minong", "Birchwood", "Trego", "Springbrook", "Sarona"],
        "Burnett": ["Siren", "Grantsburg", "Webster", "Danbury", "Alpha", "Hertel", "Yellow Lake"],
        "Eau Claire": ["Eau Claire", "Altoona", "Fall Creek", "Augusta", "Fairchild"],
        "Chippewa": ["Chippewa Falls", "Bloomer", "Stanley", "Cadott", "Cornell", "Boyd", "New Auburn"],
        "Clark": ["Neillsville", "Owen", "Thorp", "Greenwood", "Loyal", "Granton", "Withee", "Curtiss"],
        "Marathon": ["Wausau", "Mosinee", "Rothschild", "Schofield", "Marathon City", "Athens", "Edgar", "Stratford", "Spencer"],
        "Rusk": ["Ladysmith", "Bruce", "Tony", "Weyerhaeuser", "Glen Flora", "Hawkins", "Ingram"],
        "Jackson": ["Black River Falls", "Merrillan", "Hixton", "Alma Center", "Taylor", "Melrose"],
    },
    "MN": {
        "Chisago": ["Lindstrom", "North Branch", "Center City", "Shafer", "Taylors Falls", "Chisago City", "Wyoming", "Stacy"],
        "Isanti": ["Cambridge", "Isanti", "Braham", "Grandy", "Dalbo"],
        "Pine": ["Pine City", "Hinckley", "Sandstone", "Willow River", "Finlayson", "Rock Creek", "Rutledge"],
        "Kanabec": ["Mora", "Ogilvie", "Grasston", "Quamba"],
        "Anoka": ["Anoka", "Coon Rapids", "Blaine", "Andover", "Ramsey", "Ham Lake", "East Bethel", "Oak Grove"],
        "Washington": ["Stillwater", "Forest Lake", "Cottage Grove", "Woodbury", "Hugo", "Oakdale", "Lake Elmo"],
    }
}

SECONDARY_WI = [
    "Price", "Sawyer", "Taylor", "Wood", "Portage", "Waupaca", "Shawano", 
    "Langlade", "Lincoln", "Oneida", "Vilas", "Iron", "Ashland", "Bayfield",
    "Douglas", "Pierce", "Pepin", "Buffalo", "Trempealeau", "La Crosse",
    "Monroe", "Juneau", "Adams", "Waushara", "Marquette"
]

SECONDARY_MN = [
    "Dakota", "Scott", "Carver", "Wright", "Sherburne", "Benton", "Stearns",
    "Mille Lacs", "Aitkin", "Carlton", "St. Louis", "Ramsey", "Hennepin"
]

STATE_NAMES = {"WI": "Wisconsin", "MN": "Minnesota"}

PRIMARY_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crop Insurance $county County $state_abbr | $primary_town | Farmers First</title>
    <meta name="description" content="Local crop insurance for $county County $state_full. MPCI, revenue protection, PRF pasture insurance, 590 nutrient management. Serving $towns_text. Call 715-553-0392.">
    <link rel="canonical" href="https://farmers1st.com/crop-insurance-$slug/">
    <meta property="og:title" content="Crop Insurance $county County $state_abbr | Farmers First">
    <meta property="og:description" content="Local crop insurance for $county County farmers. Revenue protection, PRF, 590 plans.">
    <meta property="og:url" content="https://farmers1st.com/crop-insurance-$slug/">
    <meta property="og:type" content="website">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"InsuranceAgency","name":"Farmers First - $county County","telephone":"+1-715-553-0392","url":"https://farmers1st.com/crop-insurance-$slug/","areaServed":{"@type":"AdministrativeArea","name":"$county County $state_full"},"address":{"@type":"PostalAddress","addressLocality":"Chetek","addressRegion":"WI","postalCode":"54728"}}</script>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://farmers1st.com/"},{"@type":"ListItem","position":2,"name":"$state_full","item":"https://farmers1st.com/#areas"},{"@type":"ListItem","position":3,"name":"$county County"}]}</script>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What is the crop insurance deadline for $county County?","acceptedAnswer":{"@type":"Answer","text":"For $county County $state_full, the sales closing deadline for spring crops is March 15. Acreage reporting is July 15. PRF pasture deadline is December 1."}},{"@type":"Question","name":"Does Farmers First serve $primary_town?","acceptedAnswer":{"@type":"Answer","text":"Yes, we serve all of $county County including $towns_text. Call 715-553-0392 for a free quote."}}]}</script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
    <style>:root{--bg:#08080c;--panel:#0d0d14;--card:#12121a;--border:#1e1e2a;--accent:#d4a942;--accent-dim:#9a7830;--text:#c8c8d4;--dim:#5a5a70;--bright:#fff}*{margin:0;padding:0;box-sizing:border-box}html{scroll-behavior:smooth}body{font-family:'Space Grotesk',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.7}header{background:var(--panel);border-bottom:1px solid var(--border);padding:12px 20px;position:sticky;top:0;z-index:100}.header-inner{max-width:1100px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}.logo{font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:var(--bright);text-decoration:none;display:flex;align-items:center;gap:8px}.logo span{color:var(--accent)}.header-nav{display:flex;gap:8px}.header-nav a{font-size:.8rem;color:var(--dim);text-decoration:none;padding:6px 12px}.header-nav a:hover{color:var(--text)}.cta-btn{background:var(--accent);color:var(--bg);padding:10px 18px;text-decoration:none;font-weight:600;font-size:.85rem}.cta-btn:hover{background:var(--bright)}main{max-width:900px;margin:0 auto;padding:50px 20px}.breadcrumb{font-size:.75rem;color:var(--dim);margin-bottom:24px}.breadcrumb a{color:var(--accent);text-decoration:none}h1{font-family:'JetBrains Mono',monospace;font-size:2rem;color:var(--bright);margin-bottom:20px}h1 span{color:var(--accent)}h2{font-family:'JetBrains Mono',monospace;font-size:.85rem;color:var(--accent);margin:50px 0 20px;letter-spacing:2px;text-transform:uppercase}p{margin-bottom:16px}.intro{font-size:1.05rem;border-left:3px solid var(--accent);padding:20px;margin:25px 0 35px;background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--accent)}.intro p{margin:0}.cta-box{background:linear-gradient(135deg,var(--card) 0%,var(--panel) 100%);border:1px solid var(--accent);padding:40px;margin:45px 0;text-align:center}.cta-box h3{color:var(--bright);margin-bottom:10px;font-size:1.3rem}.cta-box p{color:var(--dim);margin-bottom:18px}.cta-box .phone{font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:var(--accent);text-decoration:none}.cta-box .phone:hover{color:var(--bright)}.towns-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px;margin:20px 0;list-style:none}.towns-grid li{background:var(--card);padding:12px;border:1px solid var(--border);font-size:.85rem;text-align:center}.services-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin:20px 0}.service-card{background:var(--card);border:1px solid var(--border);padding:24px}.service-card:hover{border-color:var(--accent-dim)}.service-card h4{color:var(--bright);font-size:.95rem;margin-bottom:10px}.service-card p{color:var(--dim);font-size:.85rem;margin:0}.info-list{margin:20px 0;list-style:none}.info-list li{padding:14px 0;border-bottom:1px solid var(--border);font-size:.9rem}.info-list li:last-child{border:none}.info-list strong{color:var(--bright)}.deadline-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:20px 0}.deadline-item{background:var(--card);border:1px solid var(--border);padding:18px;text-align:center}.deadline-date{font-family:'JetBrains Mono',monospace;font-size:1.3rem;color:var(--accent);margin-bottom:6px}.deadline-desc{font-size:.8rem;color:var(--dim)}.faq-section{background:var(--panel);border:1px solid var(--border);padding:30px;margin:40px 0}.faq-item{padding:20px 0;border-bottom:1px solid var(--border)}.faq-item:last-child{border:none;padding-bottom:0}.faq-item:first-child{padding-top:0}.faq-q{font-size:1rem;color:var(--bright);margin-bottom:10px}.faq-a{color:var(--dim);font-size:.9rem}.team-row{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:20px 0}.team-card{background:var(--card);border:1px solid var(--border);padding:24px;text-align:center}.team-card h4{color:var(--bright);margin-bottom:4px}.team-card .role{color:var(--accent);font-size:.8rem;margin-bottom:14px}.team-card .phone{font-family:'JetBrains Mono',monospace;font-size:1.15rem}.team-card .phone a{color:var(--bright);text-decoration:none}.partner-section{background:var(--card);border:1px solid var(--border);padding:25px;margin:40px 0}.partner-section h3{font-family:'JetBrains Mono',monospace;font-size:.75rem;color:var(--dim);margin-bottom:15px;letter-spacing:1.5px}.partner-links{display:flex;gap:15px;flex-wrap:wrap}.partner-link{color:var(--dim);text-decoration:none;font-size:.85rem;padding:10px 16px;background:var(--panel);border:1px solid var(--border)}.partner-link:hover{border-color:var(--accent-dim);color:var(--text)}.related-counties{background:var(--panel);border:1px solid var(--border);padding:28px;margin-top:50px}.related-counties h3{font-family:'JetBrains Mono',monospace;font-size:.75rem;color:var(--accent);margin-bottom:18px;letter-spacing:1.5px}.related-counties a{display:inline-block;margin:5px 12px 5px 0;color:var(--dim);text-decoration:none;font-size:.85rem}.related-counties a:hover{color:var(--accent)}footer{border-top:1px solid var(--border);padding:35px 20px;margin-top:60px;text-align:center}.footer-links{font-size:.8rem;color:var(--dim);margin-bottom:14px}.footer-links a{color:var(--accent);text-decoration:none;margin:0 12px}.footer-copy{font-size:.75rem;color:var(--dim)}@media(max-width:600px){h1{font-size:1.6rem}.team-row{grid-template-columns:1fr}.header-nav{display:none}.cta-box .phone{font-size:1.4rem}}</style>
</head>
<body>
    <header><div class="header-inner"><a href="/" class="logo">🌾 FARMERS<span>FIRST</span></a><nav class="header-nav"><a href="/#services">Services</a><a href="/#areas">All Areas</a><a href="https://agsist.com">Ag Tools →</a></nav><a href="tel:715-553-0392" class="cta-btn">📞 715-553-0392</a></div></header>
    <main>
        <nav class="breadcrumb"><a href="/">Farmers First</a> / <a href="/#areas">$state_full</a> / $county County</nav>
        <h1>Crop Insurance for <span>$county County</span>, $state_full</h1>
        <div class="intro"><p><strong>Farmers First Agri Service</strong> is your local crop insurance agency serving $county County. We help farmers in $towns_text protect their operations with the right coverage.</p></div>
        <p>Whether you're growing corn and soybeans, managing dairy, running beef cattle on pasture, or operating a diversified farm — we have coverage options that fit your $county County operation.</p>
        <div class="cta-box"><h3>Get Your Free Crop Insurance Quote</h3><p>Talk directly with a local agent who knows $county County farming</p><a href="tel:715-553-0392" class="phone">715-553-0392</a></div>
        <h2>Communities We Serve in $county County</h2>
        <ul class="towns-grid">$towns_html</ul>
        <h2>Crop Insurance Coverage Options</h2>
        <div class="services-grid">
            <div class="service-card"><h4>Revenue Protection (RP)</h4><p>Protects against yield loss AND price decline. Most popular for corn and soybeans.</p></div>
            <div class="service-card"><h4>PRF Pasture Insurance</h4><p>Rainfall index coverage for hay and grazing. Automatic payouts when rainfall drops.</p></div>
            <div class="service-card"><h4>Yield Protection (YP)</h4><p>Covers yield losses at elected price. Lower premium option.</p></div>
            <div class="service-card"><h4>Whole Farm Revenue</h4><p>Covers entire operation's revenue. Ideal for diversified farms.</p></div>
        </div>
        <h2>Crops Commonly Insured in $county County</h2>
        <ul class="info-list">
            <li><strong>Corn</strong> — Grain, silage, high-moisture</li>
            <li><strong>Soybeans</strong> — Conventional and specialty</li>
            <li><strong>Small Grains</strong> — Oats, wheat, barley</li>
            <li><strong>Hay & Forage</strong> — Alfalfa, grass hay</li>
            <li><strong>Pasture</strong> — PRF rainfall index</li>
        </ul>
        <h2>590 Nutrient Management Plans</h2>
        <p>Need a 590 plan for EQIP, state permits, or CAFO compliance? Our Certified Crop Advisor creates NRCS-compliant plans for $county County farms.</p>
        <h2>Key Deadlines for $county County</h2>
        <div class="deadline-grid">
            <div class="deadline-item"><div class="deadline-date">March 15</div><div class="deadline-desc">Corn, soybeans, spring grains</div></div>
            <div class="deadline-item"><div class="deadline-date">July 15</div><div class="deadline-desc">Acreage reporting</div></div>
            <div class="deadline-item"><div class="deadline-date">Sept 30</div><div class="deadline-desc">Winter wheat</div></div>
            <div class="deadline-item"><div class="deadline-date">Dec 1</div><div class="deadline-desc">PRF pasture/forage</div></div>
        </div>
        <h2>Frequently Asked Questions</h2>
        <div class="faq-section">
            <div class="faq-item"><h3 class="faq-q">What is the crop insurance deadline for $county County?</h3><p class="faq-a">For spring crops like corn and soybeans, the deadline is <strong>March 15</strong>. Acreage reporting is July 15. PRF pasture deadline is December 1.</p></div>
            <div class="faq-item"><h3 class="faq-q">Do you serve $primary_town and other communities?</h3><p class="faq-a">Yes! We serve all of $county County including $towns_text. Call 715-553-0392 for a free quote.</p></div>
        </div>
        <h2>Your $county County Team</h2>
        <div class="team-row">
            <div class="team-card"><h4>Nate Weness</h4><p class="role">Crop Insurance Agent</p><p class="phone"><a href="tel:715-553-0392">715-553-0392</a></p></div>
            <div class="team-card"><h4>Sig Lindquist, CCA</h4><p class="role">Certified Crop Advisor</p><p class="phone"><a href="tel:715-797-2428">715-797-2428</a></p></div>
        </div>
        <div class="cta-box"><h3>Ready to Review Your Coverage?</h3><p>Free quotes • No pressure • Local expertise</p><a href="tel:715-553-0392" class="phone">Call 715-553-0392</a></div>
        <div class="partner-section"><h3>FROM THE FARMERS FIRST NETWORK</h3><div class="partner-links"><a href="https://agsist.com" class="partner-link">📊 AgSist — Free Ag Dashboard</a><a href="https://lokedrone.com" class="partner-link">✈️ Loke Drone — Ag Spraying</a><a href="https://usdronemap.com" class="partner-link">🗺️ US Drone Map</a></div></div>
        <div class="related-counties"><h3>ALSO SERVING NEARBY COUNTIES</h3>$related_links</div>
    </main>
    <footer><div class="footer-links"><a href="/">Home</a><a href="/#services">Services</a><a href="https://agsist.com">Ag Dashboard</a><a href="https://lokedrone.com">Drone Services</a></div><p class="footer-copy">© 2017–2025 Farmers First Agri Service • Chetek, Wisconsin</p></footer>
</body>
</html>'''

SECONDARY_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crop Insurance $county County $state_abbr | Farmers First Agri Service</title>
    <meta name="description" content="Crop insurance for $county County $state_full. MPCI, revenue protection, PRF pasture insurance. Call 715-553-0392.">
    <link rel="canonical" href="https://farmers1st.com/crop-insurance-$slug/">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"InsuranceAgency","name":"Farmers First - $county County","telephone":"+1-715-553-0392","areaServed":{"@type":"AdministrativeArea","name":"$county County $state_full"}}</script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;500&display=swap" rel="stylesheet">
    <style>:root{--bg:#08080c;--panel:#0d0d14;--card:#12121a;--border:#1e1e2a;--accent:#d4a942;--text:#c8c8d4;--dim:#5a5a70;--bright:#fff}*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Space Grotesk',sans-serif;background:var(--bg);color:var(--text);line-height:1.7}header{background:var(--panel);border-bottom:1px solid var(--border);padding:12px 20px}.header-inner{max-width:900px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}.logo{font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:var(--bright);text-decoration:none}.logo span{color:var(--accent)}.cta-btn{background:var(--accent);color:var(--bg);padding:10px 18px;text-decoration:none;font-weight:600}main{max-width:700px;margin:0 auto;padding:50px 20px}.breadcrumb{font-size:.75rem;color:var(--dim);margin-bottom:20px}.breadcrumb a{color:var(--accent);text-decoration:none}h1{font-family:'JetBrains Mono',monospace;font-size:1.7rem;color:var(--bright);margin-bottom:20px}h1 span{color:var(--accent)}h2{font-family:'JetBrains Mono',monospace;font-size:.8rem;color:var(--accent);margin:40px 0 18px}p{margin-bottom:16px}.cta-box{background:var(--card);border:1px solid var(--accent);padding:35px;margin:40px 0;text-align:center}.cta-box h3{color:var(--bright);margin-bottom:12px}.cta-box .phone{font-family:'JetBrains Mono',monospace;font-size:1.5rem;color:var(--accent);text-decoration:none}.info-list{list-style:none;margin:18px 0}.info-list li{padding:12px 0;border-bottom:1px solid var(--border)}.info-list li:last-child{border:none}.partner-section{background:var(--panel);padding:20px;margin:35px 0}.partner-section h3{font-size:.7rem;color:var(--dim);margin-bottom:12px}.partner-links{display:flex;gap:12px;flex-wrap:wrap}.partner-link{color:var(--dim);text-decoration:none;font-size:.8rem;padding:8px 12px;background:var(--card);border:1px solid var(--border)}.partner-link:hover{border-color:var(--accent)}.related{background:var(--panel);padding:22px;margin-top:40px}.related h3{font-size:.7rem;color:var(--accent);margin-bottom:14px}.related a{color:var(--dim);text-decoration:none;margin-right:14px;font-size:.85rem}.related a:hover{color:var(--accent)}footer{border-top:1px solid var(--border);padding:28px 20px;margin-top:50px;text-align:center;font-size:.75rem;color:var(--dim)}footer a{color:var(--accent);text-decoration:none}</style>
</head>
<body>
    <header><div class="header-inner"><a href="/" class="logo">🌾 FARMERS<span>FIRST</span></a><a href="tel:715-553-0392" class="cta-btn">📞 715-553-0392</a></div></header>
    <main>
        <nav class="breadcrumb"><a href="/">Home</a> / <a href="/#areas">$state_full</a> / $county County</nav>
        <h1>Crop Insurance for <span>$county County</span>, $state_full</h1>
        <p>Farmers First Agri Service provides crop insurance coverage for $county County farmers. Based in Chetek, Wisconsin, we serve farmers throughout $state_full with multi-peril crop insurance, revenue protection, and PRF pasture coverage.</p>
        <div class="cta-box"><h3>Free Crop Insurance Quote</h3><p>Talk to a local agent today</p><a href="tel:715-553-0392" class="phone">715-553-0392</a></div>
        <h2>COVERAGE OPTIONS</h2>
        <ul class="info-list">
            <li><strong>Revenue Protection (RP)</strong> — Yield + price protection</li>
            <li><strong>PRF Pasture Insurance</strong> — Rainfall index for hay & grazing</li>
            <li><strong>Yield Protection</strong> — Yield coverage at elected price</li>
            <li><strong>590 Nutrient Management</strong> — NRCS-compliant plans</li>
        </ul>
        <h2>CONTACT</h2>
        <p><strong>Nate Weness</strong> — Crop Insurance — <a href="tel:715-553-0392" style="color:var(--accent)">715-553-0392</a><br>
        <strong>Sig Lindquist, CCA</strong> — 590 Plans — <a href="tel:715-797-2428" style="color:var(--accent)">715-797-2428</a></p>
        <div class="partner-section"><h3>FROM THE FARMERS FIRST NETWORK</h3><div class="partner-links"><a href="https://agsist.com" class="partner-link">📊 AgSist</a><a href="https://lokedrone.com" class="partner-link">✈️ Loke Drone</a><a href="https://usdronemap.com" class="partner-link">🗺️ US Drone Map</a></div></div>
        <div class="related"><h3>NEARBY COUNTIES</h3>$related_links</div>
    </main>
    <footer><a href="/">Farmers First Agri Service</a> • Chetek, WI</footer>
</body>
</html>'''


def make_slug(county):
    return county.lower().replace(' ', '-').replace('.', '')

def generate_related_links(current_county, current_state, all_counties):
    links = []
    for state, counties in all_counties.items():
        for county in counties:
            if county != current_county:
                slug = f"{make_slug(county)}-county-{state.lower()}"
                links.append(f'<a href="/crop-insurance-{slug}/">{county} County {state}</a>')
    return "\n".join(links[:12])

def generate_pages():
    all_primary = {}
    for state, counties in PRIMARY_COUNTIES.items():
        all_primary[state] = list(counties.keys())
    
    # Generate PRIMARY county pages
    for state, counties in PRIMARY_COUNTIES.items():
        state_full = STATE_NAMES[state]
        for county, towns in counties.items():
            slug = f"{make_slug(county)}-county-{state.lower()}"
            folder = f"crop-insurance-{slug}"
            
            towns_html = "".join(f"<li>{t}</li>" for t in towns)
            towns_text = ", ".join(towns[:4])
            if len(towns) > 4:
                towns_text += f", and {len(towns)-4} more"
            
            related = generate_related_links(county, state, all_primary)
            
            html = Template(PRIMARY_TEMPLATE).substitute(
                county=county,
                state_abbr=state,
                state_full=state_full,
                slug=slug,
                primary_town=towns[0],
                towns_html=towns_html,
                towns_text=towns_text,
                related_links=related
            )
            
            os.makedirs(folder, exist_ok=True)
            with open(f"{folder}/index.html", "w") as f:
                f.write(html)
            print(f"[PRIMARY] {folder}/")
    
    # Generate SECONDARY county pages
    for county in SECONDARY_WI:
        state = "WI"
        state_full = "Wisconsin"
        slug = f"{make_slug(county)}-county-wi"
        folder = f"crop-insurance-{slug}"
        related = generate_related_links(county, state, all_primary)
        html = Template(SECONDARY_TEMPLATE).substitute(
            county=county, state_abbr=state, state_full=state_full,
            slug=slug, related_links=related
        )
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/index.html", "w") as f:
            f.write(html)
        print(f"[secondary] {folder}/")
    
    for county in SECONDARY_MN:
        state = "MN"
        state_full = "Minnesota"
        slug = f"{make_slug(county)}-county-mn"
        folder = f"crop-insurance-{slug}"
        related = generate_related_links(county, state, all_primary)
        html = Template(SECONDARY_TEMPLATE).substitute(
            county=county, state_abbr=state, state_full=state_full,
            slug=slug, related_links=related
        )
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/index.html", "w") as f:
            f.write(html)
        print(f"[secondary] {folder}/")

if __name__ == "__main__":
    generate_pages()
    primary_count = sum(len(c) for c in PRIMARY_COUNTIES.values())
    secondary_count = len(SECONDARY_WI) + len(SECONDARY_MN)
    print(f"\n✓ Generated {primary_count} primary + {secondary_count} secondary = {primary_count + secondary_count} total pages")
