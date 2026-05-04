"""
add_ai_overview.py
Run from ~/Desktop/lister_web:
    python3 add_ai_overview.py

Extracts Gemini's grounding metadata (AI overview + sources)
and surfaces it in the research card.
"""
import sys

MAIN  = "main.py"
RHTML = "templates/auction_research.html"

# ── 1. Backend: extract grounding metadata after response ─────────
OLD_RAW = '''        raw = response.text.strip()
        print(f"   Deep research raw response (lot {lot}): {raw[:300]}")'''

NEW_RAW = '''        # Extract AI overview + sources from grounding metadata
        ai_overview_html = ""
        grounding_sources = []
        try:
            candidates = response.candidates
            if candidates:
                gm = getattr(candidates[0], "grounding_metadata", None)
                if gm:
                    sep = getattr(gm, "search_entry_point", None)
                    if sep:
                        ai_overview_html = getattr(sep, "rendered_content", "") or ""
                    chunks = getattr(gm, "grounding_chunks", []) or []
                    for chunk in chunks:
                        web = getattr(chunk, "web", None)
                        if web:
                            grounding_sources.append({
                                "title": getattr(web, "title", ""),
                                "uri":   getattr(web, "uri", ""),
                            })
        except Exception as gm_err:
            print(f"   Grounding metadata error: {gm_err}")

        raw = response.text.strip()
        print(f"   Deep research raw response (lot {lot}): {raw[:300]}")
        print(f"   AI overview chars: {len(ai_overview_html)}, sources: {len(grounding_sources)}")'''

# ── 2. Backend: inject ai_overview into returned data dict ────────
OLD_SANITIZE = '''        for key in ["image_notes", "rec_reason", "notes", "confidence", "recommendation",
                    "pricing_tier", "pricing_flag", "liquidity_note", "weight_note"]:'''

NEW_SANITIZE = '''        data["ai_overview_html"] = ai_overview_html
        data["grounding_sources"] = grounding_sources
        for key in ["image_notes", "rec_reason", "notes", "confidence", "recommendation",
                    "pricing_tier", "pricing_flag", "liquidity_note", "weight_note"]:'''

# ── 3. Frontend: render AI overview in the card ───────────────────
# Insert after the rec_reason/notes rec-box line in bodyHtml
OLD_REC_LINE = "        (res.rec_reason||res.notes ? '<div class=\"rec-box ' + recClass + '\">' + recLabel + ' — ' + esc(res.rec_reason||res.notes||'') + '</div>' : '') +"

NEW_REC_LINE = """        (res.rec_reason||res.notes ? '<div class="rec-box ' + recClass + '">' + recLabel + ' — ' + esc(res.rec_reason||res.notes||'') + '</div>' : '') +
        (res.ai_overview_html ? '<div style="margin-top:4px;"><div class="section-lbl">Google AI Overview</div><div style="background:#161b28;border:1px solid #2d3348;border-radius:8px;padding:12px 14px;font-size:12px;color:#94a3b8;line-height:1.6;max-height:220px;overflow-y:auto;">' + res.ai_overview_html + '</div></div>' : '') +
        (res.grounding_sources && res.grounding_sources.length ? '<div style="margin-top:4px;display:flex;flex-wrap:wrap;gap:6px;">' + res.grounding_sources.slice(0,5).map(function(s){ return '<a href="' + esc(s.uri||'') + '" target="_blank" rel="noopener" style="font-size:10px;background:#1e2535;border:1px solid #2d3348;border-radius:5px;padding:3px 8px;color:#64748b;text-decoration:none;white-space:nowrap;overflow:hidden;max-width:180px;text-overflow:ellipsis;display:inline-block;">↗ ' + esc(s.title||s.uri||'') + '</a>'; }).join('') + '</div>' : '') +"""

def patch(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    for old, new, label in replacements:
        if old in src:
            src = src.replace(old, new, 1)
            print(f"✅ Patched: {label}")
        else:
            print(f"❌ Not found: {label}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)

def main():
    try:
        patch(MAIN, [
            (OLD_RAW,      NEW_RAW,      "grounding metadata extraction"),
            (OLD_SANITIZE, NEW_SANITIZE, "inject ai_overview into data"),
        ])
        patch(RHTML, [
            (OLD_REC_LINE, NEW_REC_LINE, "AI overview card render"),
        ])
    except FileNotFoundError as e:
        print(f"❌ {e} — run from ~/Desktop/lister_web")
        sys.exit(1)

    print("\nNow run:")
    print("   git add main.py templates/auction_research.html")
    print('   git commit -m "show Google AI overview and sources in research cards"')
    print("   git push")

if __name__ == "__main__":
    main()
