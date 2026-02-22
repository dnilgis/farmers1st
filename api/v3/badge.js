/**
 * FFAI v3.0 Embeddable Badge
 * 
 * Usage: Add this anywhere on your page:
 *   <div id="ffai-badge"></div>
 *   <script src="https://farmers1st.com/api/v3/badge.js"></script>
 *
 * Options (data attributes on the div):
 *   data-theme="light" (default) | "dark"
 *   data-size="standard" (default) | "compact" | "full"
 *   data-sector="all" (default) | "grain" | "dairy" | "livestock"
 *
 * Examples:
 *   <div id="ffai-badge" data-theme="dark"></div>
 *   <div id="ffai-badge" data-size="compact"></div>
 *   <div id="ffai-badge" data-size="full" data-theme="dark"></div>
 */
(function(){
  var API = 'https://farmers1st.com/api/v3/current.json';
  var el = document.getElementById('ffai-badge');
  if (!el) return;

  var theme = el.getAttribute('data-theme') || 'light';
  var size = el.getAttribute('data-size') || 'standard';
  var sector = el.getAttribute('data-sector') || 'all';

  var colors = {
    light: { bg:'#f5f5f0', border:'#d4d4cc', text:'#2a2a2a', sub:'#777', link:'#2d6a2e' },
    dark:  { bg:'#1a1a1a', border:'#333',     text:'#e8e8e2', sub:'#999', link:'#5cb85c' }
  };
  var c = colors[theme] || colors.light;

  function regimeColor(v) {
    if (v >= 70) return '#2d6a2e';
    if (v >= 55) return '#b8860b';
    if (v >= 40) return '#b8860b';
    return '#a63030';
  }
  function regime(v) {
    if (v >= 70) return 'STRONG';
    if (v >= 55) return 'FAVORABLE';
    if (v >= 40) return 'GUARDED';
    return 'STRESSED';
  }

  function render(d) {
    var comp = d.composite;
    var rc = regimeColor(comp);
    var mono = "'Courier New',monospace";
    var sans = "system-ui,-apple-system,sans-serif";
    var html = '';

    // ── COMPACT: just the score ──
    if (size === 'compact') {
      html = '<div style="display:inline-flex;align-items:center;gap:8px;padding:6px 12px;background:'+c.bg+';border:1px solid '+c.border+';font-family:'+sans+'">'
        + '<span style="font-family:'+mono+';font-size:.6rem;letter-spacing:1px;color:'+c.sub+'">FFAI</span>'
        + '<span style="font-family:'+mono+';font-size:1.1rem;font-weight:800;color:'+rc+'">'+comp+'</span>'
        + '<span style="font-family:'+mono+';font-size:.5rem;letter-spacing:.5px;color:'+rc+';padding:2px 6px;border:1px solid '+rc+'">'+regime(comp)+'</span>'
        + '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="font-size:.55rem;color:'+c.link+';text-decoration:none;font-family:'+mono+'">farmers1st.com</a>'
        + '</div>';
    }
    // ── FULL: composite + all sub-indexes ──
    else if (size === 'full') {
      var subs = [
        ['GRAIN', d.sub_indexes.grain],
        ['DAIRY', d.sub_indexes.dairy],
        ['LIVESTOCK', d.sub_indexes.livestock],
        ['OUTLOOK', d.outlook]
      ];
      var subHtml = subs.map(function(s) {
        var sv = s[1], sc = regimeColor(sv);
        return '<div style="flex:1;min-width:70px;text-align:center">'
          + '<div style="font-family:'+mono+';font-size:.48rem;letter-spacing:1px;color:'+c.sub+'">'+s[0]+'</div>'
          + '<div style="font-family:'+mono+';font-size:1rem;font-weight:800;color:'+sc+'">'+sv+'</div>'
          + '<div style="height:3px;background:'+c.border+';margin-top:3px"><div style="height:100%;width:'+sv+'%;background:'+sc+'"></div></div>'
          + '</div>';
      }).join('');

      html = '<div style="max-width:380px;background:'+c.bg+';border:1px solid '+c.border+';padding:16px;font-family:'+sans+'">'
        + '<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:8px">'
        + '<span style="font-family:'+mono+';font-size:.52rem;letter-spacing:2px;color:'+c.sub+'">FFAI v3.0 // '+d.quarter+'</span>'
        + '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="font-size:.52rem;color:'+c.link+';text-decoration:none;font-family:'+mono+'">farmers1st.com</a>'
        + '</div>'
        + '<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:4px">'
        + '<span style="font-family:'+mono+';font-size:2.4rem;font-weight:800;color:'+rc+'">'+comp+'</span>'
        + '<span style="font-family:'+mono+';font-size:.7rem;letter-spacing:2px;color:'+rc+';font-weight:700">'+regime(comp)+'</span>'
        + '</div>'
        + '<div style="display:flex;gap:6px;margin-top:10px;padding-top:10px;border-top:1px solid '+c.border+'">'+subHtml+'</div>'
        + '<div style="font-family:'+mono+';font-size:.45rem;color:'+c.sub+';margin-top:8px;text-align:center">VALIDATED r=0.51 // 16 FRED SERIES // CC BY 4.0</div>'
        + '</div>';
    }
    // ── STANDARD: composite + sector focus ──
    else {
      var focusLabel = '', focusVal = comp;
      if (sector === 'grain')     { focusLabel = 'GRAIN'; focusVal = d.sub_indexes.grain; }
      else if (sector === 'dairy'){ focusLabel = 'DAIRY'; focusVal = d.sub_indexes.dairy; }
      else if (sector === 'livestock') { focusLabel = 'LIVESTOCK'; focusVal = d.sub_indexes.livestock; }

      html = '<div style="display:inline-flex;align-items:center;gap:12px;padding:10px 16px;background:'+c.bg+';border:1px solid '+c.border+';font-family:'+sans+'">'
        + '<div>'
        + '<div style="font-family:'+mono+';font-size:.48rem;letter-spacing:1.5px;color:'+c.sub+'">FFAI'+(focusLabel?' // '+focusLabel:'')+'</div>'
        + '<div style="display:flex;align-items:baseline;gap:6px">'
        + '<span style="font-family:'+mono+';font-size:1.6rem;font-weight:800;color:'+regimeColor(focusVal)+'">'+focusVal+'</span>'
        + '<span style="font-family:'+mono+';font-size:.5rem;letter-spacing:.5px;color:'+regimeColor(focusVal)+';padding:2px 6px;border:1px solid '+regimeColor(focusVal)+';font-weight:700">'+regime(focusVal)+'</span>'
        + '</div></div>';
      if (sector !== 'all' && sector) {
        html += '<div style="border-left:1px solid '+c.border+';padding-left:10px">'
          + '<div style="font-family:'+mono+';font-size:.42rem;letter-spacing:1px;color:'+c.sub+'">COMPOSITE</div>'
          + '<div style="font-family:'+mono+';font-size:1rem;font-weight:700;color:'+rc+'">'+comp+'</div></div>';
      }
      html += '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="font-size:.52rem;color:'+c.link+';text-decoration:none;font-family:'+mono+';border-left:1px solid '+c.border+';padding-left:10px">farmers1st<br>.com</a>'
        + '</div>';
    }

    el.innerHTML = html;
  }

  // Fetch and render
  var xhr = new XMLHttpRequest();
  xhr.open('GET', API, true);
  xhr.onload = function() {
    if (xhr.status === 200) {
      try { render(JSON.parse(xhr.responseText)); }
      catch(e) { el.innerHTML = '<a href="https://farmers1st.com" style="font-size:.8rem;color:#2d6a2e">FFAI @ farmers1st.com</a>'; }
    }
  };
  xhr.onerror = function() {
    el.innerHTML = '<a href="https://farmers1st.com" style="font-size:.8rem;color:#2d6a2e">FFAI @ farmers1st.com</a>';
  };
  xhr.send();
})();
