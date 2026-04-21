content = open('main.py').read()

# Replace the entire pdf scan endpoint with streaming version
old = '''# ── API: PDF AUCTION SCAN ─────────────────────────────────────── #

@app.post("/api/auction/scan-pdf")
async def scan_pdf_auction(file: UploadFile = File(...)):'''

# Find the end of the endpoint
start_idx = content.find(old)
# Find the next route after this one
next_route = content.find('\n@app.', start_idx + len(old))
old_full = content[start_idx:next_route]

new_endpoint = '''# ── API: PDF AUCTION SCAN ─────────────────────────────────────── #

from sse_starlette.sse import EventSourceResponse

@app.post("/api/auction/scan-pdf")
async def scan_pdf_auction(file: UploadFile = File(...)):
    import os, base64, json, fitz, asyncio
    import google.generativeai as genai

    contents = await file.read()
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        raise HTTPException(400, "GEMINI_API_KEY not set")

    # Extract text chunks (5 pages per chunk ~ 50 items)
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        total_pages = len(doc)
        chunk_size = 5
        page_chunks = []
        for start in range(0, total_pages, chunk_size):
            end = min(start + chunk_size, total_pages)
            chunk_text = ""
            for page_num in range(start, end):
                chunk_text += doc[page_num].get_text() + "\\n"
            if chunk_text.strip():
                page_chunks.append(chunk_text)
        doc.close()
    except Exception as e:
        raise HTTPException(500, f"PDF read error: {e}")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt_template = """You are an expert auction appraiser. Extract EVERY auction lot from this catalog section.

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

Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""

    async def generate():
        total_chunks = len(page_chunks)
        all_items = []
        for i, chunk_text in enumerate(page_chunks):
            try:
                response = model.generate_content(
                    [prompt_template, f"\\nCATALOG SECTION {i+1}/{total_chunks}:\\n{chunk_text[:10000]}"],
                    generation_config={"max_output_tokens": 8192}
                )
                raw = response.text.strip()
                if raw.startswith("```"):
                    raw = raw.split("\\n", 1)[1].rsplit("\\n", 1)[0].strip()
                    if raw.startswith("json"):
                        raw = raw[4:].strip()
                items = json.loads(raw)
                all_items.extend(items)
                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total_chunks,
                        "items": items,
                        "done": False
                    })
                }
            except Exception as e:
                print(f"Chunk {i+1} error: {e}")
                yield {"data": json.dumps({"chunk": i+1, "total_chunks": total_chunks, "items": [], "done": False, "error": str(e)})}
            await asyncio.sleep(0.1)

        yield {"data": json.dumps({"done": True, "total": len(all_items)})}

    return EventSourceResponse(generate())

'''

if start_idx != -1:
    content = content[:start_idx] + new_endpoint + content[next_route:]
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
