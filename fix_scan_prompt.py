content = open('main.py').read()

old = '''    prompt_template = """You are an expert auction appraiser. Extract EVERY auction lot from this catalog section.

For each lot return a JSON object with these exact fields:
- lot: lot number as string
- title: full item title
- description: one sentence description
- estimate_low: integer dollar amount (your low estimate)
- estimate_high: integer dollar amount (your high estimate)
- your_value: integer dollar amount (single best estimate)
- notes: brief market note

RULES:
- estimate_low, estimate_high, your_value MUST be integers (no $, no text)
- Research real used market values - do not copy text from descriptions
- Lots are formatted as: #NUMBER \u00e2\u00a2 ITEM TITLE
- If no lots found in this section, return empty array: []
- Return ONLY a JSON array, no markdown, no explanation, no preamble

Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""'''

new = '''    prompt_template = """You are a world-class auction appraiser with deep expertise in industrial equipment, lab instruments, and commercial goods.

Extract EVERY auction lot from this catalog section.

For each lot return a JSON object:
- lot: lot number as string
- title: full item title as written
- description: one sentence description
- estimate_low: integer dollar amount
- estimate_high: integer dollar amount
- your_value: integer (your single best estimate — total lot value)
- notes: brief market note with price source

EXPERT AUCTION TITLE INTERPRETATION:
- Quantities: "(2)", "QTY (3)", "SET OF 4", "PAIR", "x3" = price TOTAL for ALL units combined
- Vague lots: "SHELF OF...", "PALLET OF...", "BOX OF...", "ASSORTED..." = estimate total resale of all contents
- Condition notes like "AS-IS", "UNTESTED", "ACTIVATION NOT GUARANTEED" = still price as normal working condition — auction items are typically functional
- Always search for the SPECIFIC brand + model for accurate pricing
- Ignore auction house names, catalog numbers, location references in titles

PRICING RULES:
- All values MUST be plain integers (no $, no text)
- Base on ACTUAL used market values from eBay sold listings
- Lots are formatted as: #NUMBER • ITEM TITLE
- If no lots found, return: []
- Return ONLY a JSON array, no markdown

Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""'''

if old in content:
    content = content.replace(old, new)
    open('main.py', 'w').write(content)
    print('done')
else:
    # try finding with different encoding
    idx = content.find('prompt_template = """You are an expert auction appraiser')
    if idx > 0:
        end = content.find('"""', idx + 50)
        end2 = content.find('"""', end + 3)
        print('found at:', idx, 'ends at:', end2)
        print(repr(content[end-50:end+10]))
    else:
        print('not found at all')
