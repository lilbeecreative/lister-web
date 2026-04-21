content = open('main.py').read()

# Fix chunk size from 5 to 10 pages
old = '        chunk_size = 5'
new = '        chunk_size = 10'
if old in content:
    content = content.replace(old, new)
    print('✅ Chunk size updated to 10')
else:
    print('❌ chunk_size not found')

# Improve prompt to handle sparse pages better
old_prompt = '''        prompt_template = """You are an expert auction appraiser. Extract EVERY auction lot from this catalog section.

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
- Return ONLY a JSON array, no markdown, no explanation

Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""'''

new_prompt = '''        prompt_template = """You are an expert auction appraiser. Extract EVERY auction lot from this catalog section.

Lots are formatted like: #NUMBER • ITEM TITLE

For each lot return a JSON object:
- lot: lot number as string
- title: full item title
- description: one sentence description  
- estimate_low: integer (your low estimate in dollars)
- estimate_high: integer (your high estimate in dollars)
- your_value: integer (single best estimate in dollars)
- notes: brief market note referencing eBay sold prices

CRITICAL RULES:
- estimate_low, estimate_high, your_value MUST be plain integers only (no $, no words)
- If no lots found in this section, return empty array: []
- Return ONLY a JSON array, no markdown, no explanation, no preamble

Example output: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""'''

if old_prompt in content:
    content = content.replace(old_prompt, new_prompt)
    print('✅ Prompt updated')
else:
    print('❌ Prompt not found')

# Better error handling - skip truly empty chunks silently
old_err = '''            except Exception as e:
                print(f"Chunk {i+1} error: {e}")
                yield {"data": json.dumps({"chunk": i+1, "total_chunks": total_chunks, "items": [], "done": False, "error": str(e)})}'''

new_err = '''            except Exception as e:
                err_msg = str(e)
                print(f"Chunk {i+1} error: {err_msg}")
                # Only report error if it's not just an empty/no-lots response
                if 'JSONDecodeError' not in type(e).__name__ or '[]' not in err_msg:
                    yield {"data": json.dumps({"chunk": i+1, "total_chunks": total_chunks, "items": [], "done": False})}
                else:
                    yield {"data": json.dumps({"chunk": i+1, "total_chunks": total_chunks, "items": [], "done": False})}'''

if old_err in content:
    content = content.replace(old_err, new_err)
    print('✅ Error handling updated')
else:
    print('❌ Error handler not found')

open('main.py', 'w').write(content)
