"""
add_serp_research.py
Run from ~/Desktop/lister_web:
    python3 add_serp_research.py

Adds SerpAPI eBay sold listing lookup as the first step in deep research.
If SERP_API_KEY is set, real sold prices are fetched and injected into the
Gemini prompt as ground truth. Falls back to Gemini grounding if not set.
"""
import sys

MAIN = "main.py"

OLD_RESEARCH_ITEM = '''    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        # Clean title before research — remove address/company junk
        clean = clean_title(title)
        if clean != title:
            print(f"Lot {lot} title cleaned: '{title}' → '{clean}'")

        # Step 1: identify exact model from image
        identified = identify_item_from_image(images, clean)
        if identified != clean:
            print(f"Lot {lot} image ID: {identified}")'''

NEW_RESEARCH_ITEM = '''    def serp_ebay_sold(query, serp_key):
        """
        Call SerpAPI to get eBay completed/sold listings for a query.
        Returns a list of dicts with title, price, date, condition, url.
        """
        import urllib.request, urllib.parse, json as _json
        params = urllib.parse.urlencode({
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": query,
            "LH_Sold": "1",
            "LH_Complete": "1",
            "LH_ItemCondition": "3000",  # used
            "_sop": "13",  # sort by recently sold
            "api_key": serp_key,
        })
        url = f"https://serpapi.com/search?{params}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                data = _json.loads(r.read())
            results = []
            for item in (data.get("organic_results") or [])[:8]:
                price_raw = item.get("price", {})
                price = price_raw.get("extracted") or price_raw.get("raw") or 0
                try:
                    price = float(str(price).replace("$","").replace(",",""))
                except Exception:
                    price = 0
                if price > 0:
                    results.append({
                        "title": item.get("title","")[:80],
                        "price": price,
                        "condition": item.get("condition","Used"),
                        "date": item.get("selling_states",{}).get("sold_date","") or "",
                        "url": item.get("link",""),
                    })
            return results
        except Exception as e:
            print(f"   SerpAPI error: {e}")
            return []

    def research_item(item, images):
        import os as _os
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0
        serp_key = _os.getenv("SERP_API_KEY", "")

        # Clean title before research — remove address/company junk
        clean = clean_title(title)
        if clean != title:
            print(f"Lot {lot} title cleaned: '{title}' → '{clean}'")

        # Step 1: identify exact model from image
        identified = identify_item_from_image(images, clean)
        if identified != clean:
            print(f"Lot {lot} image ID: {identified}")

        # Step 2: SerpAPI eBay sold lookup (if key available)
        serp_results = []
        serp_context = ""
        if serp_key:
            search_query = identified if identified != clean else clean
            print(f"   SerpAPI eBay sold search: '{search_query}'")
            serp_results = serp_ebay_sold(search_query, serp_key)
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
                serp_context = "\nNo eBay sold comps found via SerpAPI — use web search grounding for pricing.\n"
                print(f"   SerpAPI: no results for '{search_query}'")'''

OLD_PROMPT_START = '''        prompt = f"""You are an expert resale market researcher and appraiser. Research this auction item thoroughly.

Item: Lot #{lot} — {clean}
Image-identified model: {identified}
Current estimate: ${current_val}

IMPORTANT — SEARCH TERM CONSTRUCTION:
Before searching, extract just the brand name and model number from the item title.
Strip out: company addresses, "GmbH", "Inc", street names, loading fees, lot numbers, and any other non-product text.
Example: "IPG Laser #YLR-400-SM-EOS IPG Laser GmbH Siemensstrasse 7" → search "IPG YLR-400-SM-EOS fiber laser"
Use the cleanest possible search term to find accurate comps.'''

NEW_PROMPT_START = '''        prompt = f"""You are an expert resale market researcher and appraiser. Research this auction item thoroughly.

Item: Lot #{lot} — {clean}
Image-identified model: {identified}
Current estimate: ${current_val}
{serp_context}
IMPORTANT — SEARCH TERM CONSTRUCTION:
Before searching, extract just the brand name and model number from the item title.
Strip out: company addresses, "GmbH", "Inc", street names, loading fees, lot numbers, and any other non-product text.
Example: "IPG Laser #YLR-400-SM-EOS IPG Laser GmbH Siemensstrasse 7" → search "IPG YLR-400-SM-EOS fiber laser"
Use the cleanest possible search term to find accurate comps.'''

def main():
    try:
        with open(MAIN, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {MAIN} not found")
        sys.exit(1)

    patches = [
        (OLD_RESEARCH_ITEM, NEW_RESEARCH_ITEM, "serp_ebay_sold + research_item"),
        (OLD_PROMPT_START,  NEW_PROMPT_START,  "inject serp_context into prompt"),
    ]

    for old, new, label in patches:
        if old in src:
            src = src.replace(old, new, 1)
            print(f"✅ Patched: {label}")
        else:
            print(f"❌ Not found: {label}")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py")
    print('   git commit -m "add SerpAPI eBay sold lookup to deep research"')
    print("   git push")
    print("\nAlso add SERP_API_KEY to Railway lister-web Variables.")

if __name__ == "__main__":
    main()
