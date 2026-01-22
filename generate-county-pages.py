#!/usr/bin/env python3
"""
Generate SEO landing pages for Farmers First service area
Primary counties + outliers for WI and MN
"""

import os
from string import Template

# PRIMARY SERVICE AREA - these get richer content
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
        "Kanabec": ["Mora", "Ogilvie", "Grasston", "Quamba", "Braham"],
        "Anoka": ["Anoka", "Coon Rapids", "Blaine", "Andover", "Ramsey", "Ham Lake", "East Bethel", "Oak Grove"],
        "Washington": ["Stillwater", "Forest Lake", "Cottage Grove", "Woodbury", "Hugo", "Oakdale", "Lake Elmo"],
    }
}

# SECONDARY/OUTLIER COUNTIES - still serve, less detail
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

# Rich template for primary counties
PRIMARY_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crop Insurance $county County $state_abbr | $primary_town | Farmers First</title>
    <meta name="description" content="Local crop insurance agent for $county County $state_full. MPCI, revenue protection, PRF pasture insurance, 590 nutrient management. Serving $towns_text. Call 715-553-0392.">
    <meta name="keywords" content="crop insurance $county County, farm insurance $primary_town $state_abbr, MPCI $county County $state_full, PRF pasture insurance $state_full, 590 nutrient management $county County">
    
    <link rel="canonical" href="https://farmers1st.com/crop-insurance-$slug/">
    
    <meta property="og:title" content="Crop Insurance $county County $state_abbr | Farmers First">
    <meta property="og:description" content="Local crop insurance for $county County farmers. Revenue protection, PRF, 590 plans.">
    <meta property="og:url" content="https://farmers1st.com/crop-insurance-$slug/">
    <meta property="og:type" content="website">
    
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "InsuranceAgency",
      "name": "Farmers First Agri Service - $county County",
      "description": "Crop insurance and agronomy services for $county County $state_full farmers",
      "url": "https://farmers1st.com/crop-insurance-$slug/",
      "telephone": "+1-715-553-0392",
      "areaServed": {
        "@type": "AdministrativeArea",
        "name": "$county County",
        "containedIn": {"@type": "State", "name": "$state_full"}
      },
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Chetek",
        "addressRegion": "WI",
        "postalCode": "54728",
        "addressCountry": "US"
      },
      "geo": {"@type": "GeoCoordinates", "latitude": 45.31, "longitude": -91.65},
      "openingHours": "Mo-Fr 08:00-17:00",
      "priceRange": "$$"
    }
    </script>
    
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root{--bg:#08080c;--panel:#0d0d14;--card:#12121a;--border:#1e1e2a;--accent:#d4a942;--accent-dim:#9a7830;--text:#c8c8d4;--dim:#5a5a70;--bright:#fff}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Space Grotesk',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.7}
        header{background:var(--panel);border-bottom:1px solid var(--border);padding:12px 20px;position:sticky;top:0;z-index:100}
        .header-inner{max-width:1100px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
        .logo{font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:var(--bright);text-decoration:none;letter-spacing:-0.5px}.logo span{color:var(--accent)}
        .header-nav{display:flex;gap:8px;align-items:center}
        .header-nav a{font-size:.8rem;color:var(--dim);text-decoration:none;padding:6px 12px}
        .header-nav a:hover{color:var(--text)}
        .cta-btn{background:var(--accent);color:var(--bg);padding:10px 18px;text-decoration:none;font-weight:600;font-size:.85rem}
        .cta-btn:hover{background:var(--bright)}
        
        main{max-width:900px;margin:0 auto;padding:50px 20px}
        .breadcrumb{font-size:.75rem;color:var(--dim);margin-bottom:24px}
        .breadcrumb a{color:var(--accent);text-decoration:none}
        .breadcrumb a:hover{text-decoration:underline}
        
        h1{font-family:'JetBrains Mono',monospace;font-size:1.9rem;color:var(--bright);margin-bottom:20px;line-height:1.3}
        h1 span{color:var(--accent)}
        h2{font-family:'JetBrains Mono',monospace;font-size:.9rem;color:var(--accent);margin:45px 0 18px;letter-spacing:1.5px;text-transform:uppercase}
        h3{font-size:1.1rem;color:var(--bright);margin-bottom:10px}
        p{margin-bottom:16px;font-size:.95rem}
        
        .intro{font-size:1.05rem;color:var(--text);border-left:3px solid var(--accent);padding-left:20px;margin:25px 0 35px}
        
        .cta-box{background:linear-gradient(135deg,var(--card) 0%,var(--panel) 100%);border:1px solid var(--accent);padding:35px;margin:40px 0;text-align:center}
        .cta-box h3{color:var(--bright);margin-bottom:8px;font-size:1.2rem}
        .cta-box p{color:var(--dim);margin-bottom:16px}
        .cta-box .phone{font-family:'JetBrains Mono',monospace;font-size:1.6rem;color:var(--accent);text-decoration:none;display:inline-block}
        .cta-box .phone:hover{color:var(--bright)}
        
        .towns-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin:20px 0}
        .towns-grid li{list-style:none;background:var(--card);padding:10px 12px;border:1px solid var(--border);font-size:.85rem;text-align:center}
        
        .services-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin:20px 0}
        .service-card{background:var(--card);border:1px solid var(--border);padding:20px}
        .service-card h4{color:var(--bright);font-size:.95rem;margin-bottom:8px}
        .service-card p{color:var(--dim);font-size:.85rem;margin:0}
        
        .info-list{margin:20px 0;list-style:none}
        .info-list li{padding:12px 0;border-bottom:1px solid var(--border);font-size:.9rem}
        .info-list li:last-child{border:none}
        .info-list strong{color:var(--bright)}
        
        .team-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}
        .team-card{background:var(--card);border:1px solid var(--border);padding:20px;text-align:center}
        .team-card h4{color:var(--bright);margin-bottom:4px}
        .team-card .role{color:var(--accent);font-size:.8rem;margin-bottom:12px}
        .team-card .phone{font-family:'JetBrains Mono',monospace;font-size:1.1rem}
        .team-card .phone a{color:var(--bright);text-decoration:none}
        
        .related-counties{background:var(--panel);border:1px solid var(--border);padding:25px;margin-top:50px}
        .related-counties h3{font-family:'JetBrains Mono',monospace;font-size:.8rem;color:var(--accent);margin-bottom:15px;letter-spacing:1px}
        .related-counties a{display:inline-block;margin:4px 8px 4px 0;color:var(--dim);text-decoration:none;font-size:.85rem}
        .related-counties a:hover{color:var(--accent)}
        
        footer{border-top:1px solid var(--border);padding:30px 20px;margin-top:60px;text-align:center}
        .footer-links{font-size:.8rem;color:var(--dim);margin-bottom:12px}
        .footer-links a{color:var(--accent);text-decoration:none;margin:0 10px}
        .footer-copy{font-size:.75rem;color:var(--dim)}
        
        @media(max-width:600px){
            h1{font-size:1.5rem}
            .team-row{grid-template-columns:1fr}
            .header-nav{display:none}
        }
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <a href="/" class="logo">FARMERS<span>FIRST</span></a>
            <nav class="header-nav">
                <a href="/#services">Services</a>
                <a href="/#areas">All Areas</a>
                <a href="https://agsist.com">Free Ag Tools</a>
            </nav>
            <a href="tel:715-553-0392" class="cta-btn">715-553-0392</a>
        </div>
    </header>
    
    <main>
        <nav class="breadcrumb">
            <a href="/">Farmers First</a> / <a href="/#areas">$state_full</a> / $county County
        </nav>
        
        <h1>Crop Insurance for <span>$county County</span>, $state_full</h1>
        
        <p class="intro">Farmers First Agri Service is your local independent crop insurance agency serving $county County. We help farmers in $towns_text and surrounding areas protect their operations with the right coverage.</p>
        
        <p>Whether you're growing corn and soybeans, managing dairy, running beef cattle on pasture, or diversified farming — we have coverage options that fit. As independent agents based in Chetek, Wisconsin, we work for YOU, not the insurance company.</p>
        
        <div class="cta-box">
            <h3>Get Your Free Crop Insurance Quote</h3>
            <p>Talk directly with a local agent who knows $county County farming</p>
            <a href="tel:715-553-0392" class="phone">715-553-0392</a>
        </div>
        
        <h2>Communities We Serve in $county County</h2>
        <ul class="towns-grid">
$towns_html
        </ul>
        
        <h2>Crop Insurance Coverage Options</h2>
        <div class="services-grid">
            <div class="service-card">
                <h4>Revenue Protection (RP)</h4>
                <p>Protects against yield loss AND price decline. Most popular choice for corn and soybeans in $county County.</p>
            </div>
            <div class="service-card">
                <h4>PRF Pasture Insurance</h4>
                <p>Rainfall index coverage for hay and grazing acres. Automatic payouts when rainfall drops — no adjuster needed.</p>
            </div>
            <div class="service-card">
                <h4>Yield Protection (YP)</h4>
                <p>Covers yield losses at your elected price. Lower premium option if you're comfortable with price risk.</p>
            </div>
            <div class="service-card">
                <h4>Whole Farm Revenue</h4>
                <p>Covers your entire operation's revenue. Great for diversified farms with livestock and specialty crops.</p>
            </div>
        </div>
        
        <h2>Crops Commonly Insured in $county County</h2>
        <ul class="info-list">
            <li><strong>Corn</strong> — Grain corn, silage, and high-moisture corn</li>
            <li><strong>Soybeans</strong> — Conventional and specialty varieties</li>
            <li><strong>Small Grains</strong> — Oats, wheat, barley</li>
            <li><strong>Hay & Forage</strong> — Alfalfa, grass hay, haylage</li>
            <li><strong>Pasture</strong> — PRF rainfall index coverage</li>
        </ul>
        
        <h2>590 Nutrient Management Plans</h2>
        <p>Need a 590 nutrient management plan for EQIP cost-share, state permits, or CAFO compliance? Our Certified Crop Advisor Sig Lindquist creates NRCS-compliant plans for $county County farms.</p>
        <ul class="info-list">
            <li><strong>Soil sampling</strong> and lab analysis</li>
            <li><strong>Manure crediting</strong> and spreading recommendations</li>
            <li><strong>Phosphorus Index</strong> calculations</li>
            <li><strong>Annual updates</strong> and record-keeping</li>
        </ul>
        
        <h2>Key Dates for $county County Farmers</h2>
        <ul class="info-list">
            <li><strong>March 15</strong> — Sales closing deadline for corn, soybeans, spring grains</li>
            <li><strong>July 15</strong> — Acreage reporting deadline for spring-planted crops</li>
            <li><strong>September 30</strong> — Sales closing for winter wheat</li>
            <li><strong>December 1</strong> — PRF pasture/forage signup deadline</li>
        </ul>
        
        <h2>Your $county County Team</h2>
        <div class="team-row">
            <div class="team-card">
                <h4>Nate Weness</h4>
                <p class="role">Crop Insurance Agent</p>
                <p class="phone"><a href="tel:715-553-0392">715-553-0392</a></p>
            </div>
            <div class="team-card">
                <h4>Sig Lindquist, CCA</h4>
                <p class="role">Certified Crop Advisor</p>
                <p class="phone"><a href="tel:715-797-2428">715-797-2428</a></p>
            </div>
        </div>
        
        <div class="cta-box">
            <h3>Ready to Review Your Coverage?</h3>
            <p>Free quotes • No pressure • Local expertise</p>
            <a href="tel:715-553-0392" class="phone">Call 715-553-0392</a>
        </div>
        
        <div class="related-counties">
            <h3>ALSO SERVING NEARBY COUNTIES</h3>
$related_links
        </div>
    </main>
    
    <footer>
        <div class="footer-links">
            <a href="/">Home</a>
            <a href="/#services">Services</a>
            <a href="https://agsist.com">Free Ag Dashboard</a>
            <a href="https://lokedrone.com">Drone Services</a>
        </div>
        <p class="footer-copy">© 2025 Farmers First Agri Service • Chetek, Wisconsin • Serving WI & MN Farmers</p>
    </footer>
</body>
</html>'''

# Simpler template for secondary counties
SECONDARY_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crop Insurance $county County $state_abbr | Farmers First Agri Service</title>
    <meta name="description" content="Crop insurance for $county County $state_full farmers. MPCI, revenue protection, PRF pasture insurance. Call 715-553-0392 for a free quote.">
    <link rel="canonical" href="https://farmers1st.com/crop-insurance-$slug/">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"InsuranceAgency","name":"Farmers First - $county County","telephone":"+1-715-553-0392","areaServed":{"@type":"AdministrativeArea","name":"$county County $state_full"}}</script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;500&display=swap" rel="stylesheet">
    <style>:root{--bg:#08080c;--panel:#0d0d14;--card:#12121a;--border:#1e1e2a;--accent:#d4a942;--text:#c8c8d4;--dim:#5a5a70;--bright:#fff}*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Space Grotesk',sans-serif;background:var(--bg);color:var(--text);line-height:1.7}header{background:var(--panel);border-bottom:1px solid var(--border);padding:12px 20px}.header-inner{max-width:900px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}.logo{font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:var(--accent);text-decoration:none}.cta-btn{background:var(--accent);color:var(--bg);padding:10px 18px;text-decoration:none;font-weight:600}main{max-width:700px;margin:0 auto;padding:50px 20px}.breadcrumb{font-size:.75rem;color:var(--dim);margin-bottom:20px}.breadcrumb a{color:var(--accent);text-decoration:none}h1{font-family:'JetBrains Mono',monospace;font-size:1.6rem;color:var(--bright);margin-bottom:20px}h2{font-family:'JetBrains Mono',monospace;font-size:.85rem;color:var(--accent);margin:35px 0 15px}p{margin-bottom:16px}.cta-box{background:var(--card);border:1px solid var(--accent);padding:30px;margin:35px 0;text-align:center}.cta-box h3{color:var(--bright);margin-bottom:10px}.cta-box .phone{font-family:'JetBrains Mono',monospace;font-size:1.4rem;color:var(--accent);text-decoration:none}.info-list{list-style:none;margin:15px 0}.info-list li{padding:10px 0;border-bottom:1px solid var(--border)}.related{background:var(--panel);padding:20px;margin-top:40px}.related h3{font-size:.75rem;color:var(--accent);margin-bottom:12px}.related a{color:var(--dim);text-decoration:none;margin-right:12px;font-size:.85rem}footer{border-top:1px solid var(--border);padding:25px 20px;margin-top:50px;text-align:center;font-size:.75rem;color:var(--dim)}footer a{color:var(--accent);text-decoration:none}</style>
</head>
<body>
    <header><div class="header-inner"><a href="/" class="logo">FARMERS<span>FIRST</span></a><a href="tel:715-553-0392" class="cta-btn">715-553-0392</a></div></header>
    <main>
        <nav class="breadcrumb"><a href="/">Home</a> / <a href="/#areas">$state_full</a> / $county County</nav>
        <h1>Crop Insurance for $county County, $state_full</h1>
        <p>Farmers First Agri Service provides crop insurance coverage for $county County farmers. As an independent agency based in Chetek, Wisconsin, we serve farmers throughout $state_full with multi-peril crop insurance, revenue protection, and PRF pasture coverage.</p>
        <div class="cta-box"><h3>Free Crop Insurance Quote</h3><p>Call your local agent today</p><a href="tel:715-553-0392" class="phone">715-553-0392</a></div>
        <h2>COVERAGE OPTIONS</h2>
        <ul class="info-list">
            <li><strong>Revenue Protection (RP)</strong> — Yield + price protection for corn, soybeans</li>
            <li><strong>PRF Pasture Insurance</strong> — Rainfall index for hay & grazing</li>
            <li><strong>Yield Protection</strong> — Yield coverage at elected price</li>
            <li><strong>590 Nutrient Management</strong> — NRCS-compliant plans</li>
        </ul>
        <h2>CONTACT</h2>
        <p><strong>Nate Weness</strong> — Crop Insurance — <a href="tel:715-553-0392">715-553-0392</a><br>
        <strong>Sig Lindquist, CCA</strong> — 590 Plans — <a href="tel:715-797-2428">715-797-2428</a></p>
        <div class="related"><h3>NEARBY COUNTIES WE SERVE</h3>$related_links</div>
    </main>
    <footer><a href="/">Farmers First Agri Service</a> • Chetek, WI • Serving Wisconsin & Minnesota</footer>
</body>
</html>'''


def make_slug(county):
    return county.lower().replace(' ', '-').replace('.', '')

def generate_related_links(current_county, current_state, all_counties):
    """Generate links to nearby counties"""
    links = []
    # Get other counties from same state first
    for state, counties in all_counties.items():
        for county in counties:
            if county != current_county:
                slug = f"{make_slug(county)}-county-{state.lower()}"
                links.append(f'<a href="/crop-insurance-{slug}/">{county} County {state}</a>')
    return "\n".join(links[:12])  # Limit to 12 links

def generate_pages():
    all_primary = {}
    for state, counties in PRIMARY_COUNTIES.items():
        all_primary[state] = list(counties.keys())
    
    # Generate PRIMARY county pages (rich content)
    for state, counties in PRIMARY_COUNTIES.items():
        state_full = STATE_NAMES[state]
        for county, towns in counties.items():
            slug = f"{make_slug(county)}-county-{state.lower()}"
            folder = f"crop-insurance-{slug}"
            
            towns_html = "\n".join(f"            <li>{t}</li>" for t in towns)
            towns_text = ", ".join(towns[:4])
            if len(towns) > 4:
                towns_text += f", and {len(towns)-4} more communities"
            
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
    
    # Generate SECONDARY county pages (lighter content)
    for county in SECONDARY_WI:
        state = "WI"
        state_full = "Wisconsin"
        slug = f"{make_slug(county)}-county-wi"
        folder = f"crop-insurance-{slug}"
        
        related = generate_related_links(county, state, all_primary)
        
        html = Template(SECONDARY_TEMPLATE).substitute(
            county=county,
            state_abbr=state,
            state_full=state_full,
            slug=slug,
            related_links=related
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
            county=county,
            state_abbr=state,
            state_full=state_full,
            slug=slug,
            related_links=related
        )
        
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/index.html", "w") as f:
            f.write(html)
        print(f"[secondary] {folder}/")

if __name__ == "__main__":
    generate_pages()
    primary_count = sum(len(c) for c in PRIMARY_COUNTIES.values())
    secondary_count = len(SECONDARY_WI) + len(SECONDARY_MN)
    print(f"\n✓ Generated {primary_count} primary + {secondary_count} secondary = {primary_count + secondary_count} total county pages")
