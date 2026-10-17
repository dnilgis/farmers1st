/**
 * FFAI v3 Embeddable Badge (retired)
 *
 * FFAI v3 was retired in October 2026 and is no longer updated. Its last
 * reading (Q2 2026) used a different method from FFAI v4 and disagrees with
 * the current index for the same quarter (v3 70 FAVORABLE, v4 11 STRESSED),
 * so this badge no longer shows a score. It shows a short notice and a link.
 *
 * The frozen v3 data stays at https://farmers1st.com/api/v3/current.json.
 * For the current index use https://farmers1st.com/api/v4/badge.js
 * (see https://farmers1st.com/api/#badge).
 */
(function(){
  var el = document.getElementById('ffai-badge');
  if (!el) return;
  var dark = el.getAttribute('data-theme') === 'dark';
  var bg = dark ? '#1a1a1a' : '#f5f5f0', border = dark ? '#333' : '#d4d4cc',
      sub = dark ? '#b0b0a6' : '#5f5f5f', link = dark ? '#5cb85c' : '#2d6a2e';
  var mono = "'Courier New',monospace";
  el.innerHTML = '<div style="display:inline-block;padding:8px 12px;background:' + bg + ';border:1px solid ' + border
    + ';font-family:system-ui,-apple-system,sans-serif;font-size:.75rem;color:' + sub + '">'
    + '<span style="font-family:' + mono + ';font-size:.6rem;letter-spacing:1px">FFAI v3 // RETIRED OCT 2026</span><br>'
    + 'This version is no longer updated. '
    + '<a href="https://farmers1st.com/#index" target="_blank" rel="noopener" style="color:' + link + '">See the current index at farmers1st.com</a>'
    + '</div>';
})();
