/**
 * FFAI v4 Embeddable Badge (USDA prices received / prices paid)
 *
 * Shows the ratio of prices U.S. farms receive to prices they pay (2011 = 100),
 * its change from the same quarter a year earlier, and the score and label
 * (LOW / BELOW MIDDLE / ABOVE MIDDLE / HIGH, vs 1995-2019). The label is read
 * from current.json; the badge does not compute it.
 *
 * Usage: add this anywhere on your page (several badges per page are fine;
 * use id="ffai-badge" for one, or the attribute data-ffai-badge on each):
 *   <div id="ffai-badge"></div>
 *   <script src="https://farmers1st.com/api/v4/badge.js"></script>
 *
 * Options (data attributes on the div):
 *   data-theme="light" (default) | "dark"
 *   data-size="standard" (default) | "compact" | "full"
 *   data-sector="all" (default) | "crops" | "livestock" | "dairy"
 *
 * Examples:
 *   <div id="ffai-badge" data-theme="dark"></div>
 *   <div id="ffai-badge" data-size="compact"></div>
 *   <div id="ffai-badge" data-size="full" data-theme="dark"></div>
 */
(function(){
  var API = 'https://farmers1st.com/api/v4/current.json';
  var els = document.querySelectorAll('#ffai-badge,[data-ffai-badge]');
  Array.prototype.forEach.call(els, function(el) {

  var theme = el.getAttribute('data-theme') || 'light';
  var size = el.getAttribute('data-size') || 'standard';
  var sector = el.getAttribute('data-sector') || 'all';

  var colors = {
    light: { bg:'#f5f5f0', border:'#d4d4cc', text:'#2a2a2a', sub:'#5f5f5f', link:'#2d6a2e' },
    dark:  { bg:'#1a1a1a', border:'#333',     text:'#e8e8e2', sub:'#b0b0a6', link:'#5cb85c' }
  };
  var c = colors[theme] || colors.light;

  // The label comes from current.json (written by the publish step); the badge never computes it.
  function labelColor(l) {
    var good = l === 'HIGH' || l === 'ABOVE MIDDLE', mid = l === 'BELOW MIDDLE', low = l === 'LOW';
    if (theme === 'dark') return good ? '#6fbf73' : mid ? '#e0b040' : low ? '#e57373' : c.sub;
    return good ? '#2d6a2e' : mid ? '#8b6508' : low ? '#a63030' : c.sub;
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function(ch) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]; }); }
  function chg(p) {
    if (p == null) return '';
    return Math.abs(p) < 0.05 ? 'no change' : (p > 0 ? '&#9650; +' : '&#9660; -') + Math.abs(p).toFixed(1) + '%';
  }

  function render(d) {
    var vs = d.label_vs || '1995-2019';
    var ya = d.year_ago && d.year_ago.quarter;
    // Every size leads with the ratio and its change from the same quarter a year earlier,
    // then shows the score and label with the comparison period, so an old or cached badge
    // still says what it measures and when.
    var asOf = esc(d.quarter || '');
    var mono = "'Courier New',monospace";
    var sans = "system-ui,-apple-system,sans-serif";
    var html = '';
    function pick(k) {
      if (k === 'all' || !d.sectors || !d.sectors[k]) return { name: 'ALL FARMS', ratio: d.ratio, yoy: d.ratio_change_vs_year_ago_pct, score: d.score, label: d.label };
      var s = d.sectors[k];
      return { name: k.toUpperCase(), ratio: s.ratio, yoy: s.ratio_change_vs_year_ago_pct, score: s.score, label: s.label };
    }
    function yoyHtml(p, size) {
      if (p == null || !ya) return '';
      return '<span style="font-family:'+mono+';font-size:'+size+';font-weight:700;color:'+(p >= 0 ? labelColor('HIGH') : labelColor('LOW'))+';white-space:nowrap">'+chg(p)+' vs '+esc(ya)+'</span>';
    }
    function labelHtml(x, size) {
      if (!x.label) return '';
      var lc = labelColor(x.label);
      return '<span style="font-family:'+mono+';font-size:'+size+';letter-spacing:.5px;color:'+lc+';padding:2px 6px;border:1px solid '+lc+';white-space:nowrap">'
        + 'SCORE '+Math.round(x.score)+' &middot; '+esc(x.label)+' vs '+esc(vs)+'</span>';
    }
    var f = pick(sector);

    // COMPACT: ratio, change from a year earlier, label
    if (size === 'compact') {
      html = '<div style="display:inline-flex;flex-wrap:wrap;align-items:center;gap:6px 8px;padding:6px 12px;background:'+c.bg+';border:1px solid '+c.border+';font-family:'+sans+'">'
        + '<span style="font-family:'+mono+';font-size:.6rem;letter-spacing:1px;color:'+c.sub+'">FFAI '+asOf+(f.name !== 'ALL FARMS' ? ' '+f.name : '')+'</span>'
        + '<span style="font-family:'+mono+';font-size:1.1rem;font-weight:800;color:'+c.text+'">'+f.ratio.toFixed(1)+'</span>'
        + yoyHtml(f.yoy, '.6rem')
        + labelHtml(f, '.5rem')
        + '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="font-size:.6rem;color:'+c.link+';text-decoration:none;white-space:nowrap;font-family:'+mono+'">farmers1st.com</a>'
        + '</div>';
    }
    // FULL: all farms plus each sector
    else if (size === 'full') {
      var subHtml = ['crops', 'livestock', 'dairy'].map(function(k) {
        var x = pick(k), lc = labelColor(x.label);
        return '<div style="flex:1;min-width:70px;text-align:center">'
          + '<div style="font-family:'+mono+';font-size:.6rem;letter-spacing:1px;color:'+c.sub+'">'+x.name+'</div>'
          + '<div style="font-family:'+mono+';font-size:1rem;font-weight:800;color:'+c.text+'">'+x.ratio.toFixed(1)+'</div>'
          + '<div style="font-family:'+mono+';font-size:.55rem;color:'+c.sub+'">'+(x.yoy == null ? '' : chg(x.yoy)+' y/y')+'</div>'
          + '<div style="font-family:'+mono+';font-size:.5rem;font-weight:700;color:'+lc+';margin-top:2px">'+esc(x.label || '')+' ('+Math.round(x.score)+')</div>'
          + '</div>';
      }).join('');
      var a = pick('all');
      html = '<div style="max-width:100%;width:380px;box-sizing:border-box;background:'+c.bg+';border:1px solid '+c.border+';padding:16px;font-family:'+sans+'">'
        + '<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:8px;gap:8px">'
        + '<span style="font-family:'+mono+';font-size:.6rem;letter-spacing:2px;color:'+c.sub+'">FFAI v4 // ALL U.S. FARMS // '+asOf+'</span>'
        + '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="font-size:.6rem;color:'+c.link+';text-decoration:none;white-space:nowrap;font-family:'+mono+'">farmers1st.com</a>'
        + '</div>'
        + '<div style="font-family:'+mono+';font-size:.55rem;letter-spacing:1px;color:'+c.sub+'">PRICES RECEIVED &divide; PRICES PAID, 2011 = 100</div>'
        + '<div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;margin:2px 0 6px">'
        + '<span style="font-family:'+mono+';font-size:2.4rem;font-weight:800;color:'+c.text+'">'+a.ratio.toFixed(1)+'</span>'
        + yoyHtml(a.yoy, '.75rem')
        + '</div>'
        + labelHtml(a, '.6rem')
        + '<div style="display:flex;gap:6px;margin-top:10px;padding-top:10px;border-top:1px solid '+c.border+'">'+subHtml+'</div>'
        + '<div style="font-family:'+mono+';font-size:.55rem;color:'+c.sub+';margin-top:8px;text-align:center">A PRICE POSITION, NOT A FARM INCOME READING // USDA NASS // CC BY 4.0</div>'
        + '</div>';
    }
    // STANDARD: one sector (default all farms)
    else {
      html = '<div style="display:inline-flex;align-items:center;gap:12px;padding:10px 16px;background:'+c.bg+';border:1px solid '+c.border+';font-family:'+sans+'">'
        + '<div>'
        + '<div style="font-family:'+mono+';font-size:.6rem;letter-spacing:1.5px;color:'+c.sub+'">FFAI // '+f.name+' // '+asOf+' // RECEIVED &divide; PAID</div>'
        + '<div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 8px">'
        + '<span style="font-family:'+mono+';font-size:1.6rem;font-weight:800;color:'+c.text+'">'+f.ratio.toFixed(1)+'</span>'
        + yoyHtml(f.yoy, '.65rem')
        + '</div>'
        + '<div style="margin-top:4px">'+labelHtml(f, '.5rem')+'</div>'
        + '</div>'
        + '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="font-size:.6rem;color:'+c.link+';text-decoration:none;white-space:nowrap;font-family:'+mono+';border-left:1px solid '+c.border+';padding-left:10px">farmers1st<br>.com</a>'
        + '</div>';
    }

    el.innerHTML = html;
  }

  // Fetch and render
  var xhr = new XMLHttpRequest();
  xhr.open('GET', API, true);
  var fallback = '<a href="https://farmers1st.com/#index" style="font-size:.8rem;color:#2d6a2e">FFAI @ farmers1st.com</a>';
  xhr.onload = function() {
    if (xhr.status !== 200) { el.innerHTML = fallback; return; }
    try { render(JSON.parse(xhr.responseText)); }
    catch(e) { el.innerHTML = fallback; }
  };
  xhr.onerror = function() {
    el.innerHTML = '<a href="https://farmers1st.com" style="font-size:.8rem;color:#2d6a2e">FFAI @ farmers1st.com</a>';
  };
  xhr.send();
  });
})();
