"""
upgrade_auction_ui.py
Run from ~/Desktop/lister_web:
    python3 upgrade_auction_ui.py
"""
import sys

TARGET = "templates/auction_research.html"

OLD_BLOCK = """    var conf = res.confidence || 'medium';
    var confClass = conf === 'high' ? 'conf-high' : conf === 'low' ? 'conf-low' : 'conf-medium';
    var recClass = res.recommendation === 'buy' ? 'rec-buy' : res.recommendation === 'pass' ? 'rec-pass' : 'rec-watch';
    var recLabel = res.recommendation === 'buy' ? 'Strong buy' : res.recommendation === 'pass' ? 'Pass' : 'Watch';

    var pageImg = item._page_img || '';
    var imgHtml = pageImg
      ? '<img src="' + esc(pageImg) + '" alt="" style="width:100%;height:100%;object-fit:cover;display:block;" onerror="this.style.display=&quot;none&quot;">'
      : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
    var imgLabel = res.has_image ? 'Lot image analyzed' : (pageImg ? 'Catalog page' : 'No image available');
    bodyHtml = '<div class="rc-body">' +
      '<div class="rc-img-col"><div class="rc-img-box">' + imgHtml + '</div><div class="rc-img-label">' + imgLabel + '</div></div>' +
      '<div class="rc-detail">' +
        '<div><div class="section-lbl">Revised estimate</div><div class="value-row"><span class="old-val">$' + (item.your_value||0).toLocaleString() + '</span><span class="new-val">$' + (res.revised_value||0).toLocaleString() + '</span><span class="conf-badge ' + confClass + '">' + conf.charAt(0).toUpperCase() + conf.slice(1) + ' confidence</span></div></div>' +
        '<div><a href="https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent((item.title||'').replace(/\\s*,?\\s*QTY\\s*\\(?\\d*\\)?/gi,'').replace(/\\s*,?\\s*\\(\\d+\\)/g,'').replace(/,\\s*$/,'').trim()) + '&LH_Sold=1&LH_Complete=1' + '" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px;background:#1e2535;border:1px solid #2d3348;border-radius:8px;padding:9px 14px;color:#94a3b8;font-size:12px;font-weight:600;text-decoration:none;">Search eBay Sold Listings ↗</a></div>' +
        (res.image_notes ? '<div><div class="section-lbl">Image analysis</div><div class="image-notes">' + esc(res.image_notes) + '</div></div>' : '') +
        (res.rec_reason||res.notes ? '<div class="rec-box ' + recClass + '">' + recLabel + ' — ' + esc(res.rec_reason||res.notes||'') + '</div>' : '') +
      '</div></div>';"""

NEW_BLOCK = """    var conf = res.confidence || 'medium';
    var confClass = conf === 'high' ? 'conf-high' : conf === 'low' ? 'conf-low' : 'conf-medium';
    var recClass = res.recommendation === 'buy' ? 'rec-buy' : res.recommendation === 'pass' ? 'rec-pass' : 'rec-watch';
    var recLabel = res.recommendation === 'buy' ? 'Strong buy' : res.recommendation === 'pass' ? 'Pass' : 'Watch';

    // ── Pricing tier badge ──
    var tier = res.pricing_tier || '';
    var tierHtml = '';
    if (tier === 'SOLD_COMPS') {
      tierHtml = '<span style="background:#052e16;color:#4ade80;border:1px solid #166534;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;letter-spacing:.4px;">✓ SOLD COMPS</span>';
    } else if (tier === 'ASKING_PRICES') {
      tierHtml = '<span style="background:#422006;color:#fb923c;border:1px solid #9a3412;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;letter-spacing:.4px;">⚠ ASKING PRICES</span>';
    } else if (tier === 'MSRP_ONLY') {
      tierHtml = '<span style="background:#450a0a;color:#f87171;border:1px solid #991b1b;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;letter-spacing:.4px;">⚠ MSRP ONLY</span>';
    } else if (tier === 'COMPARABLE_ITEMS') {
      tierHtml = '<span style="background:#1e1b4b;color:#a5b4fc;border:1px solid #3730a3;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;letter-spacing:.4px;">~ COMPARABLE</span>';
    } else if (tier === 'NO_DATA') {
      tierHtml = '<span style="background:#1e2535;color:#64748b;border:1px solid #2d3348;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;letter-spacing:.4px;">— NO DATA</span>';
    }

    // ── Pricing flag warning ──
    var flagHtml = res.pricing_flag ? '<div style="background:#1c1007;border:1px solid #78350f;border-radius:6px;padding:7px 11px;color:#fb923c;font-size:11px;margin-top:6px;">⚠️ ' + esc(res.pricing_flag) + '</div>' : '';
    var compNoteHtml = res.comp_note ? '<div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:6px;padding:7px 11px;color:#93c5fd;font-size:11px;margin-top:4px;">ℹ️ ' + esc(res.comp_note) + '</div>' : '';

    // ── Liquidity score ──
    var liq = parseInt(res.liquidity_score) || 0;
    var liqColor = liq >= 4 ? '#4ade80' : liq === 3 ? '#facc15' : '#f87171';
    var liqDots = '';
    for (var d = 1; d <= 5; d++) {
      liqDots += '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:3px;background:' + (d <= liq ? liqColor : '#2d3348') + ';"></span>';
    }
    var liqHtml = liq > 0 ? '<div style="display:flex;align-items:center;gap:8px;margin-top:8px;"><span style="font-size:10px;font-weight:700;color:#64748b;letter-spacing:.5px;text-transform:uppercase;">Liquidity</span><span>' + liqDots + '</span><span style="font-size:11px;color:#94a3b8;">' + liq + '/5' + (res.liquidity_note ? ' — ' + esc(res.liquidity_note) : '') + '</span></div>' : '';

    // ── Shipping weight ──
    var weightHtml = '';
    if (res.weight_item_lbs || res.weight_packaged_lbs) {
      var wStr = '';
      if (res.weight_item_lbs) wStr += res.weight_item_lbs + ' lbs item';
      if (res.weight_packaged_lbs) wStr += (wStr ? ' / ' : '') + res.weight_packaged_lbs + ' lbs packaged';
      if (res.weight_note) wStr += ' <span style="color:#64748b;">(' + esc(res.weight_note) + ')</span>';
      weightHtml = '<div style="display:flex;align-items:center;gap:8px;margin-top:6px;"><span style="font-size:10px;font-weight:700;color:#64748b;letter-spacing:.5px;text-transform:uppercase;">Shipping</span><span style="font-size:11px;color:#94a3b8;">📦 ' + wStr + '</span></div>';
    }

    var pageImg = item._page_img || '';
    var imgHtml = pageImg
      ? '<img src="' + esc(pageImg) + '" alt="" style="width:100%;height:100%;object-fit:cover;display:block;" onerror="this.style.display=&quot;none&quot;">'
      : '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';
    var imgLabel = res.has_image ? 'Lot image analyzed' : (pageImg ? 'Catalog page' : 'No image available');
    bodyHtml = '<div class="rc-body">' +
      '<div class="rc-img-col"><div class="rc-img-box">' + imgHtml + '</div><div class="rc-img-label">' + imgLabel + '</div></div>' +
      '<div class="rc-detail">' +
        '<div><div class="section-lbl">Revised estimate</div><div class="value-row" style="align-items:center;gap:10px;flex-wrap:wrap;"><span class="old-val">$' + (item.your_value||0).toLocaleString() + '</span><span class="new-val">$' + (res.revised_value||0).toLocaleString() + '</span><span class="conf-badge ' + confClass + '">' + conf.charAt(0).toUpperCase() + conf.slice(1) + ' confidence</span>' + tierHtml + '</div>' + flagHtml + compNoteHtml + '</div>' +
        (liqHtml || weightHtml ? '<div>' + liqHtml + weightHtml + '</div>' : '') +
        '<div><a href="https://www.ebay.com/sch/i.html?_nkw=' + encodeURIComponent((item.title||'').replace(/\\s*,?\\s*QTY\\s*\\(?\\d*\\)?/gi,'').replace(/\\s*,?\\s*\\(\\d+\\)/g,'').replace(/,\\s*$/,'').trim()) + '&LH_Sold=1&LH_Complete=1' + '" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px;background:#1e2535;border:1px solid #2d3348;border-radius:8px;padding:9px 14px;color:#94a3b8;font-size:12px;font-weight:600;text-decoration:none;">Search eBay Sold Listings ↗</a></div>' +
        (res.image_notes ? '<div><div class="section-lbl">Image analysis</div><div class="image-notes">' + esc(res.image_notes) + '</div></div>' : '') +
        (res.rec_reason||res.notes ? '<div class="rec-box ' + recClass + '">' + recLabel + ' — ' + esc(res.rec_reason||res.notes||'') + '</div>' : '') +
      '</div></div>';"""

def main():
    try:
        with open(TARGET, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {TARGET} not found — run from ~/Desktop/lister_web")
        sys.exit(1)

    if OLD_BLOCK not in src:
        print("❌ Could not find card render block — it may have changed")
        print("   Run: sed -n '170,200p' templates/auction_research.html")
        sys.exit(1)

    src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)

    print("✅ Patched auction_research.html — pricing tier, liquidity, weight added to cards")
    print("\nNow run:")
    print("   git add templates/auction_research.html")
    print('   git commit -m "auction ui: show pricing tier, liquidity score, shipping weight"')
    print("   git push")

if __name__ == "__main__":
    main()
