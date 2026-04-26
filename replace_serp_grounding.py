"""
replace_serp_grounding.py
Run from ~/Desktop/lister_web:
    python3 replace_serp_grounding.py
"""

MAIN = "main.py"

def main():
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()

    changes = 0

    # 1. Add gemini_search_grounding function before serp_ebay_sold
    grounding_func = '''    def gemini_search_grounding(query, gemini_key):
        """
        Use Gemini REST API with Google Search grounding to get real market pricing.
        Uses requests (already installed) — no SDK dependency conflict.
        """
        import requests as _req
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": (
                f"What is the current resale market value for: {query}\\n\\n"
                "Search for:\\n"
                "1. Recent eBay SOLD listings (completed sales) in the last 12 months\\n"
                "2. Current industrial surplus dealer prices\\n"
                "3. Auction results\\n\\n"
                "Give specific dollar ranges. Mention condition factors that affect price."
            )}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"maxOutputTokens": 600}
        }
        try:
            resp = _req.post(url, json=payload, timeout=25)
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return {"summary": "", "sources": []}
            parts = candidates[0].get("content", {}).get("parts", [])
            text = " ".join(p.get("text", "") for p in parts if "text" in p).strip()
            grounding = candidates[0].get("groundingMetadata", {})
            sources = [
                {"url": c["web"]["uri"], "title": c["web"].get("title", "")}
                for c in grounding.get("groundingChunks", [])
                if c.get("web", {}).get("uri")
            ]
            print(f"   Gemini grounding: {len(text)} chars, {len(sources)} sources")
            return {"summary": text, "sources": sources}
        except Exception as e:
            print(f"   Gemini grounding error: {e}")
            return {"summary": "", "sources": []}

'''

    anchor = "    def serp_ebay_sold(query, serp_key, sacat='12576'):"
    if anchor in src:
        src = src.replace(anchor, grounding_func + anchor, 1)
        print("✅ Added gemini_search_grounding function")
        changes += 1
    else:
        print("❌ serp_ebay_sold anchor not found")

    # 2. Replace the entire Step 2 block
    old_step2_start = "        # Step 2: SerpAPI eBay sold lookup (if key available)\n        serp_results = []\n        serp_context = \"\"\n        if serp_key:"
    new_step2 = """        # Step 2: Gemini Search Grounding for real market pricing
        serp_results = []
        serp_context = ""
        if gemini_key:
            _grounding = gemini_search_grounding(clean, gemini_key)
            _gsummary = _grounding.get("summary", "")
            if _gsummary:
                serp_context = f\"\"\"MARKET RESEARCH DATA (from live Google Search — use as PRIMARY pricing source):
{_gsummary}

Extract specific dollar amounts from the above. Base revised_value on actual prices found.
Do NOT ignore this data. Do NOT use your training knowledge if this data contradicts it.
\"\"\"
        # Legacy SerpAPI block (disabled — kept for fallback reference)
        if False and serp_key:"""

    if old_step2_start in src:
        src = src.replace(old_step2_start, new_step2, 1)
        print("✅ Replaced Step 2 with Gemini grounding block")
        changes += 1
    else:
        print("❌ Step 2 block not found")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"\n{changes}/2 changes applied")
    print("\nNow run:")
    print('   python3 -c "import py_compile; py_compile.compile(\'main.py\'); print(\'OK\')"')
    print("   git add main.py")
    print('   git commit -m "replace SerpAPI with Gemini REST search grounding"')
    print("   git push")

if __name__ == "__main__":
    main()
