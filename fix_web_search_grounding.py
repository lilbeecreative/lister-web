content = open('main.py').read()

old_research = '''    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        prompt = f"""You are an expert industrial equipment appraiser doing deep market research.

Item: Lot #{lot} — {title}
Current estimate: ${current_val}

RESEARCH TASKS:
1. Analyze the item image carefully — identify exact make/model, condition, completeness
2. Search eBay sold listings for this exact item or closest matches
3. Consider Google shopping, industrial dealers, auction records
4. Provide 3-5 real comparable sold listings with prices and dates

Return ONLY a JSON object (no markdown):
{{
  "revised_value": 18000,
  "confidence": "high",
  "comps": [
    {{"title": "Similar item description", "price": 19500, "date": "Mar 2025", "source": "eBay"}},
    {{"title": "Similar item description", "price": 16200, "date": "Jan 2025", "source": "eBay"}}
  ],
  "image_notes": "What you observed from the catalog image",
  "recommendation": "buy/watch/pass",
  "rec_reason": "Brief reason for recommendation",
  "notes": "Market summary"
}}

confidence must be: high, medium, or low
recommendation must be: buy, watch, or pass
revised_value must be an integer
CRITICAL: All string values must use only standard ASCII characters. No apostrophes, smart quotes, or special characters in any field."""

        parts = [prompt]
        for img_bytes in images[:3]:
            parts.append({"mime_type": "image/jpeg", "data": img_bytes})

        response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})'''

new_research = '''    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        prompt = f"""You are an expert industrial equipment appraiser. Research this auction item using web search.

Item: Lot #{lot} — {title}
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
{{"revised_value": 1400, "confidence": "high", "comps": [{{"title": "Exact item name from listing", "price": 1200, "date": "Mar 2025", "source": "eBay Sold"}}], "image_notes": "What the image shows", "recommendation": "buy", "rec_reason": "Sells for X on eBay", "notes": "Market summary"}}"""

        # Use Gemini with search grounding if available
        try:
            from google.generativeai import types as gtypes
            search_tool = gtypes.Tool(google_search_retrieval=gtypes.GoogleSearchRetrieval())
            parts = [prompt]
            for img_bytes in images[:2]:
                parts.append({"mime_type": "image/jpeg", "data": img_bytes})
            response = model.generate_content(
                parts,
                tools=[search_tool],
                generation_config={"max_output_tokens": 1500}
            )
        except Exception:
            parts = [prompt]
            for img_bytes in images[:2]:
                parts.append({"mime_type": "image/jpeg", "data": img_bytes})
            response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})'''

if old_research in content:
    content = content.replace(old_research, new_research)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
    idx = content.find('def research_item')
    print(repr(content[idx:idx+100]))
