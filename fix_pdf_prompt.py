content = open('main.py').read()

old_prompt = '''        prompt = """You are an expert auction appraiser. Analyze this auction catalog PDF.

For each auction lot/item found, extract:
1. Lot number (if present)
2. Item title/description
3. Any photos or image references
4. Any listed estimate or starting bid
5. Direct URL to the listing (if present in text)

Then research each item and provide your estimated market value based on recent eBay sold listings.

Return ONLY a JSON array with this exact structure:
[
  {
    "lot": "12",
    "title": "Item name here",
    "description": "Brief description",
    "estimate_low": 50,
    "estimate_high": 100,
    "your_value": 75,
    "listing_url": "https://...",
    "notes": "Brief market notes"
  }
]

Return ONLY the JSON array, no other text."""'''

new_prompt = '''        prompt = """You are an expert industrial auction appraiser with deep knowledge of used equipment markets.

Analyze this auction catalog PDF and extract each lot. For EACH lot you find:

1. Extract: lot number, full title, brief description
2. Use your knowledge of eBay sold listings and industrial equipment markets to estimate realistic USED market values
3. Provide estimate_low and estimate_high as integers (dollar amounts only, no text)
4. your_value should be your single best estimate as an integer
5. listing_url: leave empty string "" unless a real URL is present in the text

CRITICAL PRICING RULES:
- Values must be INTEGERS (numbers only, no $ signs, no text like "TDS" or "conductivity")
- Base prices on actual used market values for that specific item/brand/model
- If you truly cannot estimate, use 0
- Common lab equipment: meters $50-300, analyzers $500-5000, freezers $200-800
- Industrial equipment: mixers $100-2000, tanks $1000-50000, compressors $500-10000

Return ONLY a valid JSON array, no other text, no markdown:
[
  {
    "lot": "12",
    "title": "Item name",
    "description": "One sentence description",
    "estimate_low": 100,
    "estimate_high": 300,
    "your_value": 200,
    "listing_url": "",
    "notes": "Common on eBay for $150-250 used"
  }
]"""'''

if old_prompt in content:
    content = content.replace(old_prompt, new_prompt)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
