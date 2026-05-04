"""
replace_prompt.py
Run from ~/Desktop/lister_web:
    python3 replace_prompt.py
"""

MAIN = "main.py"

OLD_PROMPT_START = '        prompt = f"""You are an expert resale market researcher and appraiser. Research this auction item thoroughly.'
OLD_PROMPT_END = 'pricing_tier values: SOLD_COMPS | ASKING_PRICES | MSRP_ONLY | COMPARABLE_ITEMS | NO_DATA\npricing_flag: blank if sold comps found, otherwise plain English warning such as:\n  Based on active asking prices only - no sold comps found\n  Based on original MSRP - resale value may differ significantly\n  No exact match found - priced against comparable [item]'

NEW_PROMPT = '''        prompt = f"""You are an expert industrial machinery appraiser and secondary market researcher.
Your job is to determine the actual cash value of an industrial asset at auction.

--- ITEM DETAILS ---
Lot: #{lot}
Clean Title: {clean}
Image-Identified Model: {identified}
Initial Estimate: ${current_val}

--- MARKET RESEARCH DATA ---
{serp_context}

--- PRICING HIERARCHY RULES (CRITICAL) ---
You must evaluate the MARKET RESEARCH DATA using this strict waterfall hierarchy. Do NOT skip tiers.

TIER 1: SOLD/COMPLETED LISTINGS (Highest Priority)
If the data contains actual verified sold prices, base your estimate entirely on these. Ignore all asking prices.
-> pricing_tier = "SOLD_COMPS"

TIER 2: ACTIVE MARKETPLACE LISTINGS (The Ceiling)
If no sold data exists, look for active listings on open marketplaces (eBay, etc).
Rule: The LOWEST reasonable active listing establishes the absolute CEILING of value. A buyer will not pay $8,000 if they can buy it right now on eBay for $3,995.
Calculation: Find the lowest active price. Apply a 15-25% discount to estimate actual sell price. Ignore high-priced outliers.
-> pricing_tier = "ASKING_PRICES"

TIER 3: INDUSTRIAL DEALER ASKING PRICES (Last Resort Anchor)
If NO marketplace data exists, use retail/surplus dealer asking prices (Radwell, PLC Center, etc).
Rule: Dealers charge massive premiums. Apply a 40-60% discount to find auction/resale cash value.
-> pricing_tier = "ASKING_PRICES"

TIER 4: NO DATA
If the MARKET RESEARCH DATA contains no dollar values relevant to this item, admit it.
-> pricing_tier = "NO_DATA"

--- HALLUCINATION GUARDRAILS ---
- You are FORBIDDEN from using pricing_tier "SOLD_COMPS" unless the word "sold" or "completed" is explicitly in the data.
- Do NOT average a $3,995 eBay listing with a $15,000 dealer listing. The $3,995 becomes the absolute ceiling.
- Do NOT fabricate comps. Only list prices explicitly found in the MARKET RESEARCH DATA above.
- confidence must be "high" only with 3+ verified sold comps, otherwise "medium" or "low".

SHIPPING WEIGHT: Estimate from item type and visible size.

Return ONLY valid JSON, no markdown:
{{"revised_value": 3200, "confidence": "medium", "pricing_tier": "ASKING_PRICES", "pricing_flag": "Based on lowest active eBay listing $3,995 minus 20% discount", "comps": [{{"title": "Item name", "price": 3995, "date": "Apr 2025", "source": "eBay Active"}}], "image_notes": "What the image shows", "recommendation": "watch", "rec_reason": "One active eBay listing at $3,995 sets ceiling, estimated sell price $3,200", "notes": "Market summary with sources", "weight_item_lbs": 50.0, "weight_packaged_lbs": 55.0, "weight_note": "Estimated", "liquidity_score": 2, "liquidity_note": "Limited market data", "sold_30d": 0, "sold_90d": 0, "active_listings": 1}}

pricing_tier values: SOLD_COMPS | ASKING_PRICES | MSRP_ONLY | COMPARABLE_ITEMS | NO_DATA'''

def main():
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()

    # Find the prompt block
    start_idx = src.find(OLD_PROMPT_START)
    if start_idx == -1:
        print("❌ Prompt start not found")
        return

    end_idx = src.find(OLD_PROMPT_END, start_idx)
    if end_idx == -1:
        print("❌ Prompt end not found")
        return

    end_idx += len(OLD_PROMPT_END)
    
    src = src[:start_idx] + NEW_PROMPT + src[end_idx:]
    
    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)
    
    print("✅ Prompt replaced")
    print("\nNow run:")
    print('   python3 -c "import py_compile; py_compile.compile(\'main.py\'); print(\'OK\')"')
    print("   git add main.py")
    print('   git commit -m "replace pricing prompt with deterministic hierarchy"')
    print("   git push")

if __name__ == "__main__":
    main()
