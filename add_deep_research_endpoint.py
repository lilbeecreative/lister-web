content = open('main.py').read()

endpoint = '''
# ── API: FULL DEEP RESEARCH ──────────────────────────────────── #

@app.post("/api/auction/deep-research-full")
async def deep_research_full(request: Request):
    import os, json, base64, asyncio, fitz
    from concurrent.futures import ThreadPoolExecutor
    import google.generativeai as genai

    form = await request.form()
    items_json = form.get("items", "[]")
    items = json.loads(items_json)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        raise HTTPException(400, "GEMINI_API_KEY not set")

    pdf_bytes = None
    pdf_file = form.get("pdf")
    if pdf_file and hasattr(pdf_file, "read"):
        pdf_bytes = await pdf_file.read()

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=1)

    def extract_page_image(pdf_bytes, page_start, page_end):
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            for page_num in range(page_start - 1, min(page_end, len(doc))):
                page = doc[page_num]
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                images.append(pix.tobytes("jpeg"))
            doc.close()
            return images
        except Exception as e:
            print(f"Image extract error: {e}")
            return []

    def research_item(item, images):
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
revised_value must be an integer"""

        parts = [prompt]
        for img_bytes in images[:3]:
            parts.append({"mime_type": "image/jpeg", "data": img_bytes})

        response = model.generate_content(parts, generation_config={"max_output_tokens": 1000})
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    async def generate():
        total = len(items)
        for i, item in enumerate(items):
            yield {"data": json.dumps({"type": "start", "lot": item.get("lot"), "index": i, "total": total})}
            try:
                images = []
                if pdf_bytes and item.get("_page_start"):
                    images = await loop.run_in_executor(
                        executor, extract_page_image, pdf_bytes,
                        item["_page_start"], item.get("_page_end", item["_page_start"])
                    )
                result = await loop.run_in_executor(executor, research_item, item, images)
                yield {"data": json.dumps({
                    "type": "result",
                    "lot": item.get("lot"),
                    "index": i,
                    "total": total,
                    "has_image": len(images) > 0,
                    **result
                })}
            except Exception as e:
                print(f"Deep research error for lot {item.get('lot')}: {e}")
                yield {"data": json.dumps({
                    "type": "error",
                    "lot": item.get("lot"),
                    "index": i,
                    "total": total,
                    "error": str(e)
                })}
            await asyncio.sleep(0.1)
        yield {"data": json.dumps({"type": "done", "total": total})}

    return EventSourceResponse(generate())

'''

anchor = '# ── API: AUCTION DEEP RESEARCH ───────────────────────────────── #'
if anchor in content:
    content = content.replace(anchor, endpoint + anchor)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
