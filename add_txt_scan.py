"""
add_txt_scan.py
Run from ~/Desktop/lister_web:
    python3 add_txt_scan.py
"""
import sys

MAIN = "main.py"
ANCHOR = '@app.post("/api/auction/scan-pdf")'

NEW_ENDPOINT = '''@app.post("/api/auction/scan-txt")
async def scan_txt_auction(file: UploadFile = File(...)):
    import os, json, asyncio
    import google.generativeai as genai

    contents = await file.read()
    text = contents.decode("utf-8", errors="ignore")

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        raise HTTPException(400, "GEMINI_API_KEY not set")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt_template = """You are a world-class auction appraiser with deep expertise in industrial equipment, lab instruments, and commercial goods.

Extract EVERY auction lot from this catalog text.

For each lot return a JSON object:
- lot: lot number as string
- title: full item title as written
- description: one sentence description
- estimate_low: integer dollar amount
- estimate_high: integer dollar amount
- your_value: integer (your single best estimate - total lot value)
- notes: brief market note with price source

PRICING RULES:
- All values MUST be plain integers (no $, no text)
- Base on ACTUAL used market values from eBay sold listings
- If no lots found, return: []
- Return ONLY a JSON array, no markdown"""

    # Split text into chunks of ~8000 chars
    chunk_size = 8000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    if not chunks:
        chunks = [text]

    from sse_starlette.sse import EventSourceResponse

    async def generate():
        loop = asyncio.get_event_loop()
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)
        all_items = []
        total = len(chunks)

        for i, chunk in enumerate(chunks):
            try:
                def call_gemini(c=chunk, idx=i):
                    response = model.generate_content(
                        [prompt_template, f"\\nCATALOG SECTION {idx+1}/{total}:\\n{c}"],
                        generation_config={"max_output_tokens": 16000}
                    )
                    return response.text

                raw = await loop.run_in_executor(executor, call_gemini)
                raw = " ".join(raw.splitlines())
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                    raw = raw.strip()
                start = raw.find("[")
                end = raw.rfind("]") + 1
                if start >= 0 and end > start:
                    raw = raw[start:end]
                try:
                    items = json.loads(raw)
                except Exception:
                    from json_repair import repair_json
                    items = json.loads(repair_json(raw))
                all_items.extend(items)
                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total,
                        "items": items,
                        "scan_id": None,
                        "done": False
                    }, separators=(',', ':'))
                }
            except Exception as e:
                print(f"TXT chunk {i+1} error: {e}")
            await asyncio.sleep(0.1)

        yield {"data": json.dumps({"done": True, "total": len(all_items), "scan_id": None})}

    return EventSourceResponse(generate())


'''

def main():
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()

    if ANCHOR in src:
        src = src.replace(ANCHOR, NEW_ENDPOINT + ANCHOR, 1)
        print("✅ Added /api/auction/scan-txt endpoint")
    else:
        print("❌ Anchor not found")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py templates/auction.html")
    print('   git commit -m "add TXT file upload support to auction scanner"')
    print("   git push")

if __name__ == "__main__":
    main()
