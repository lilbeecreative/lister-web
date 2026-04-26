"""
add_sacat_iqr.py
Run from ~/Desktop/lister_web:
    python3 add_sacat_iqr.py

Adds:
1. _sacat eBay category pre-classification via Gemini Flash
2. Negative keywords for industrial items
3. IQR variance-based sanity check replacing fixed 15% threshold
"""
import sys

MAIN = "main.py"

OLD_SERP_BLOCK = '''        # Step 2: SerpAPI eBay sold lookup (if key available)
        serp_results = []
        serp_context = ""
        if serp_key:
            # Preserve brand names with quotes for precision
            import re as _re
            _words = clean.split()
            _w = clean.split()
            search_query = '"' + clean + '"' if len(_w) >= 3 else clean
            print(f"   SerpAPI eBay sold search: '{search_query}'")
            serp_results = serp_ebay_sold(search_query, serp_key)
            # Discard if avg is less than 15% of current estimate
            if serp_results:
                prices = [r["price"] for r in serp_results]
                _avg = sum(prices) / len(prices)
                if current_val > 0 and _avg < current_val * 0.15:
                    print(f"   SerpAPI results discarded — avg ${_avg:.0f} too low vs estimate ${current_val}")
                    serp_results = []
            if serp_results:
                prices = [r["price"] for r in serp_results]
                avg = sum(prices) / len(prices)
                low = min(prices)
                high = max(prices)
                lines = [f"  - ${r['price']:.0f} — {r['title']} ({r['condition']}) {r['date']}" for r in serp_results]
                serp_context = f"""
REAL EBAY SOLD DATA (from live eBay completed listings — use this as primary pricing source):
Found {len(serp_results)} sold comps: low ${low:.0f}, high ${high:.0f}, avg ${avg:.0f}
{chr(10).join(lines)}

Base your revised_value on these actual sold prices. Do not override this with guesses.
"""
                print(f"   SerpAPI: {len(serp_results)} comps, avg ${avg:.0f}, range ${low:.0f}-${high:.0f}")
            else:
                serp_context = "No eBay sold comps found via SerpAPI - use web search grounding for pricing."
                print(f"   SerpAPI: no results for '{search_query}'")'''

NEW_SERP_BLOCK = '''        # Step 2: SerpAPI eBay sold lookup (if key available)
        serp_results = []
        serp_context = ""
        if serp_key:
            # --- Pre-classification: get eBay _sacat and negative keywords ---
            _sacat_map = {
                "12576": "Business & Industrial - Other",
                "11804": "CNC, Metalworking & Manufacturing",
                "11808": "Electrical Equipment & Supplies",
                "11803": "Semiconductor & PCB Equipment",
                "78989": "Test, Measurement & Inspection",
                "4666":  "Pumps & Plumbing",
                "11816": "Hydraulics, Pneumatics & Plumbing",
                "11815": "Healthcare, Lab & Dental",
                "3673":  "Computers & Networking",
                "58058": "Lasers & Laser Accessories",
                "11700": "Consumer Electronics",
                "26230": "Hand Tools",
                "92074": "Power Tools",
            }
            _cat_prompt = f"""You are an eBay category classifier for industrial equipment.

Item: {clean}

Choose the single best eBay category ID from this list:
{chr(10).join(f'  {k}: {v}' for k,v in _sacat_map.items())}

Also decide if negative keywords are needed to filter out medical/consumer results.
Negative keywords to consider: -medical -dental -cosmetic -hair -aesthetic -salon

Respond ONLY with valid JSON, no markdown:
{{"sacat": "12576", "negative_keywords": "-medical -dental", "is_industrial": true}}

If unsure about negative keywords, use empty string for negative_keywords."""

            _sacat = "12576"
            _negative_kw = ""
            _is_industrial = True
            try:
                _cat_response = model.generate_content(
                    _cat_prompt,
                    generation_config={"max_output_tokens": 100, "temperature": 0}
                )
                _cat_text = _cat_response.text.strip()
                if "```" in _cat_text:
                    _cat_text = _cat_text.split("```")[1]
                    if _cat_text.startswith("json"):
                        _cat_text = _cat_text[4:]
                import json as _json2
                _cat_data = _json2.loads(_cat_text.strip())
                _sacat = str(_cat_data.get("sacat", "12576"))
                _negative_kw = str(_cat_data.get("negative_keywords", ""))
                _is_industrial = bool(_cat_data.get("is_industrial", True))
                print(f"   Category: {_sacat_map.get(_sacat, _sacat)}, industrial={_is_industrial}, negatives='{_negative_kw}'")
            except Exception as _ce:
                print(f"   Category pre-classification failed: {_ce}, using default sacat=12576")

            # Build search query with phrase matching + negative keywords
            _w = clean.split()
            _base_query = '"' + clean + '"' if len(_w) >= 3 else clean
            search_query = (_base_query + " " + _negative_kw).strip()
            print(f"   SerpAPI eBay sold search: '{search_query}' (sacat={_sacat})")
            serp_results = serp_ebay_sold(search_query, serp_key, sacat=_sacat)

            # --- IQR variance-based sanity check ---
            if serp_results:
                prices = sorted([r["price"] for r in serp_results])
                n = len(prices)
                if n >= 4:
                    q1 = prices[n // 4]
                    q3 = prices[(3 * n) // 4]
                    iqr = q3 - q1
                    median = prices[n // 2]
                    cv = (iqr / median) if median > 0 else 1
                    if cv > 1.5:
                        print(f"   SerpAPI results discarded — high variance (CV={cv:.2f}), mixed categories likely")
                        serp_results = []
                    else:
                        print(f"   SerpAPI variance OK: IQR=${iqr:.0f}, CV={cv:.2f}, median=${median:.0f}")
                elif n >= 2:
                    # Small sample: check if range is >5x spread
                    _spread = prices[-1] / prices[0] if prices[0] > 0 else 10
                    if _spread > 5:
                        print(f"   SerpAPI results discarded — spread too wide ({prices[0]:.0f}-{prices[-1]:.0f})")
                        serp_results = []

            if serp_results:
                prices = [r["price"] for r in serp_results]
                avg = sum(prices) / len(prices)
                low = min(prices)
                high = max(prices)
                lines = [f"  - ${r['price']:.0f} — {r['title']} ({r['condition']}) {r['date']}" for r in serp_results]
                serp_context = f"""
REAL EBAY SOLD DATA (from live eBay completed listings — use this as primary pricing source):
Found {len(serp_results)} sold comps: low ${low:.0f}, high ${high:.0f}, avg ${avg:.0f}
{chr(10).join(lines)}

Base your revised_value on these actual sold prices. Do not override this with guesses.
"""
                print(f"   SerpAPI: {len(serp_results)} comps, avg ${avg:.0f}, range ${low:.0f}-${high:.0f}")
            else:
                serp_context = "No eBay sold comps found via SerpAPI - use web search grounding for pricing."
                print(f"   SerpAPI: no results for '{search_query}'")'''

# Also need to update serp_ebay_sold to accept sacat parameter
OLD_SERP_FUNC_PARAMS = '''        params = urllib.parse.urlencode({
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": query,
            "LH_Sold": "1",
            "LH_Complete": "1",
            "api_key": serp_key,
        })'''

NEW_SERP_FUNC_PARAMS = '''        _params = {
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": query,
            "LH_Sold": "1",
            "LH_Complete": "1",
            "api_key": serp_key,
        }
        if sacat and sacat != "12576":
            _params["_sacat"] = sacat
        params = urllib.parse.urlencode(_params)'''

OLD_SERP_FUNC_DEF = "    def serp_ebay_sold(query, serp_key):"
NEW_SERP_FUNC_DEF = "    def serp_ebay_sold(query, serp_key, sacat='12576'):"

def main():
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()

    changes = 0

    # Update function signature
    if OLD_SERP_FUNC_DEF in src:
        src = src.replace(OLD_SERP_FUNC_DEF, NEW_SERP_FUNC_DEF, 1)
        print("✅ Updated serp_ebay_sold signature")
        changes += 1
    else:
        print("❌ serp_ebay_sold signature not found")

    # Update params to include _sacat
    if OLD_SERP_FUNC_PARAMS in src:
        src = src.replace(OLD_SERP_FUNC_PARAMS, NEW_SERP_FUNC_PARAMS, 1)
        print("✅ Updated SerpAPI params to include _sacat")
        changes += 1
    else:
        print("❌ SerpAPI params block not found")

    # Replace the whole serp block
    if OLD_SERP_BLOCK in src:
        src = src.replace(OLD_SERP_BLOCK, NEW_SERP_BLOCK, 1)
        print("✅ Replaced SerpAPI block with _sacat + IQR logic")
        changes += 1
    else:
        print("❌ SerpAPI block not found — may need manual patch")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"\n{changes}/3 changes applied")
    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py")
    print('   git commit -m "add _sacat category pre-classification and IQR variance sanity check"')
    print("   git push")

if __name__ == "__main__":
    main()
