content = open('main.py').read()

# The generate function needs to be added back after the prompt_template
old = '''Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""


def get_unmatched_photos():'''

new = '''Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""

    def call_gemini(chunk_text, i):
        response = model.generate_content(
            [prompt_template, f"\\nCATALOG SECTION {i+1}/{total_chunks}:\\n{chunk_text[:10000]}"],
            generation_config={"max_output_tokens": 16000}
        )
        return response.text

    async def generate():
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        all_items = []
        total_chunks = len(page_chunks)

        for i, chunk_text in enumerate(page_chunks):
            try:
                raw = await loop.run_in_executor(executor, call_gemini, chunk_text, i)
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
                base_idx = len(all_items)
                all_items.extend(items)
                page_start = i * chunk_size + 1
                page_end = min((i + 1) * chunk_size, total_pages)
                for item in items:
                    item["_page_start"] = page_start
                    item["_page_end"] = page_end
                    if scan_id:
                        item["_page_img"] = f"/api/auction/page-image/{scan_id}/{base_idx + items.index(item)}"
                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total_chunks,
                        "items": items,
                        "scan_id": scan_id,
                        "done": False
                    }, separators=(',', ':'))
                }
            except Exception as e:
                print(f"Chunk {i+1} error: {e}")
            await asyncio.sleep(0.1)

        yield {"data": json.dumps({"done": True, "total": len(all_items), "scan_id": scan_id})}

    return EventSourceResponse(generate())


def get_unmatched_photos():'''

if old in content:
    content = content.replace(old, new)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
    idx = content.find('Example: [{"lot":"5"')
    print('Example at:', idx)
    print(repr(content[idx+180:idx+250]))
