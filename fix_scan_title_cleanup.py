content = open('main.py').read()

# Clean up title in scan prompt to strip quantity info for better pricing
old_prompt_template = '        prompt_template = """You are an expert auction appraiser. Extract EVERY auction lot from this catalog section.'
new_prompt_template = '''        def clean_title_for_search(title):
            import re
            return re.sub(r'[,\\s]*\\(\\d+\\)[,\\s]*', ' ', title).strip()

        prompt_template = """You are an expert auction appraiser. Extract EVERY auction lot from this catalog section.

IMPORTANT: When estimating values, note that titles may include quantities like "(2)" or "QTY (3)". 
Price the TOTAL LOT value (all units combined), not per-unit price.'''

# Actually simpler - just update the prompt to note quantity awareness
old_rules = '''CRITICAL PRICING RULES:
- Values must be INTEGERS (numbers only, no $ signs, no text like "TDS" or "conductivity")
- Base prices on actual used market values for that specific item/brand/model
- If you truly cannot estimate, use 0
- Common lab equipment: meters $50-300, analyzers $500-5000, freezers $200-800
- Industrial equipment: mixers $100-2000, tanks $1000-50000, compressors $500-10000'''

new_rules = '''CRITICAL PRICING RULES:
- Values must be INTEGERS (numbers only, no $ signs, no text)
- Base prices on actual used market values for that specific item/brand/model
- If a title says "QTY (2)" or "(3 units)" etc., price the TOTAL for all units combined
- If you truly cannot estimate, use 0
- Common lab equipment: meters $50-300, analyzers $500-5000, freezers $200-800
- Industrial equipment: mixers $100-2000, tanks $1000-50000, compressors $500-10000'''

if old_rules in content:
    content = content.replace(old_rules, new_rules)
    open('main.py','w').write(content)
    print('done')
else:
    print('not found')
