"""
upgrade_deep_research.py
Run from ~/Desktop/lister_web:
    python3 upgrade_deep_research.py
"""
import sys

TARGET = "main.py"

OLD_PROMPT = '''        prompt = f"""You are an expert industrial equipment appraiser. Research this auction item using web search.

Item: Lot #{lot} — {title}
Image-identified model: {identified}
Current estimate: ${current_val}

TASKS:
1. Search eBay SOLD listings for this exact item or very close matches — use real search results only
2. Search Google for current market pricing from dealers and recent auctions
3. If you have an image, analyze it carefully for make/model/condition details

STRICT RULES:
- Only include comps from ACTUAL search results you can verify — do not fabricate listings
- If you cannot find real comparable sales, say so in notes and use low confidence
- revised_value must be an integer based on real market data
- confidence: high (3+ real comps found), medium (1-2 comps), low (no real comps found)
- recommendation: buy (good value vs market), watch (fair value), pass (overpriced or uncertain)

Return ONLY valid JSON (no markdown, no apostrophes in strings):
{{"revised_value": 1400, "confidence": "high", "comps": [{{"title": "Exact item name from listing", "price": 1200, "date": "Mar 2025", "source": "eBay Sold"}}], "image_notes": "What the image shows", "recommendation": "buy", "rec_reason": "Sells for X on eBay", "notes": "Market summary"}}"""'''

NEW_PROMPT = '''        prompt = f"""You are an expert resale market researcher and appraiser. Research this auction item thoroughly.

Item: Lot #{lot} — {title}
Image-identified model: {identified}
Current estimate: ${current_val}

PRICING RESEARCH — follow this exact hierarchy:

TIER 1 — SOLD / REALIZED PRICES (search first, highest priority):
- eBay COMPLETED/SOLD listings (most important — real transaction prices)
- LiveAuctioneers realized hammer prices
- Heritage Auctions, Invaluable.com sold results
- Worthpoint if accessible
If you find 3+ sold comps from the last 90 days, stop here for pricing.

TIER 2 — ACTIVE ASKING PRICES (only if fewer than 3 sold comps found):
- eBay active Buy It Now listings
- Amazon new and used
- Dealer/retailer sites, Google Shopping
Label these clearly as ASKING prices, not confirmed sales.

TIER 3 — ORIGINAL MSRP (only if tiers 1 and 2 both fail):
- Manufacturer original retail price, catalog pricing
Label clearly as MSRP — resale is typically 20-60% of original retail.

TIER 4 — COMPARABLE ITEMS (if exact item not found at any tier):
- Same category, similar specs, different brand or model
Label clearly and note what item was used as proxy.

SHIPPING WEIGHT:
Search manufacturer spec sheets, Amazon listings, or retailer pages for listed weight.
If exact weight not found, estimate based on item type and visible size.
Report item weight and estimated packaged weight (add 1-2 lbs for materials).

LIQUIDITY SIGNALS:
- How many sold comps in last 30 days?
- How many sold comps in last 90 days?
- How many active listings currently exist?
- Price variance: tight (within 20%) / moderate / wide (50%+ spread)
Liquidity score 1-5:
  5 = 10+ sold in 30 days, tight range
  4 = 5-9 sold in 30 days or 10+ in 90 days
  3 = 3-4 sold in 90 days, moderate variance
  2 = 1-2 sold comps or asking prices only
  1 = no sold comps, wide variance, or niche item

STRICT RULES:
- Only include comps from actual search results — do not fabricate listings
- revised_value must be an integer
- confidence: high (3+ real sold comps), medium (1-2 comps or asking prices), low (MSRP only or no data)
- recommendation: buy / watch / pass

Return ONLY valid JSON (no markdown, no apostrophes in strings):
{{"revised_value": 1400, "confidence": "high", "pricing_tier": "SOLD_COMPS", "pricing_flag": "", "comps": [{{"title": "Item name", "price": 1200, "date": "Mar 2025", "source": "eBay Sold"}}], "image_notes": "What the image shows", "recommendation": "buy", "rec_reason": "Sells for X on eBay", "notes": "Market summary", "weight_item_lbs": 12.5, "weight_packaged_lbs": 14.0, "weight_note": "Manufacturer spec", "liquidity_score": 4, "liquidity_note": "8 sold comps in 90 days tight range", "sold_30d": 3, "sold_90d": 8, "active_listings": 12}}

pricing_tier values: SOLD_COMPS | ASKING_PRICES | MSRP_ONLY | COMPARABLE_ITEMS | NO_DATA
pricing_flag: blank if sold comps found, otherwise plain English warning such as:
  Based on active asking prices only - no sold comps found
  Based on original MSRP - resale value may differ significantly
  No exact match found - priced against comparable [item]
weight fields: use null if truly unknown"""'''

def main():
    try:
        with open(TARGET, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {TARGET} not found — run from ~/Desktop/lister_web")
        sys.exit(1)

    if OLD_PROMPT not in src:
        print("❌ Could not find the prompt block — it may have changed")
        print("   Run: sed -n '310,370p' main.py")
        print("   and share the output so we can re-anchor")
        sys.exit(1)

    src = src.replace(OLD_PROMPT, NEW_PROMPT, 1)
    print("✅ Patched research prompt — tiered pricing, weight, liquidity added")

    # Upgrade sanitization to cover new string fields
    OLD_SANITIZE = '        for key in ["image_notes", "rec_reason", "notes", "confidence", "recommendation"]:'
    NEW_SANITIZE = '        for key in ["image_notes", "rec_reason", "notes", "confidence", "recommendation", "pricing_tier", "pricing_flag", "liquidity_note", "weight_note"]:'

    if OLD_SANITIZE in src:
        src = src.replace(OLD_SANITIZE, NEW_SANITIZE, 1)
        print("✅ Patched sanitize keys")
    else:
        print("⚠️  Sanitize block not found — skipping (non-critical)")

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   git add main.py")
    print('   git commit -m "upgrade deep research: tiered pricing, weight, liquidity"')
    print("   git push")

if __name__ == "__main__":
    main()
