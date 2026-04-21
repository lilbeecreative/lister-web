content = open('main.py').read()

# 1. Add endpoint to serve a page image from a stored PDF
new_endpoint = '''
# ── API: AUCTION PAGE IMAGE ───────────────────────────────────── #

@app.get("/api/auction/page-image/{scan_id}/{page_num}")
async def get_page_image(scan_id: str, page_num: int):
    import io, fitz
    try:
        pdf_data = supabase.storage.from_("auction-pdfs").download(f"{scan_id}.pdf")
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        if page_num < 1 or page_num > len(doc):
            raise HTTPException(404, "Page not found")
        page = doc[page_num - 1]
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("jpeg")
        doc.close()
        from fastapi.responses import Response
        return Response(content=img_bytes, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})
    except Exception as e:
        raise HTTPException(500, str(e))

'''

# 2. In scan_pdf endpoint, upload PDF to Supabase storage and include scan_id + page images in response
old_scan_start = '''@app.post("/api/auction/scan-pdf")
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
        chunk_size = 2
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
        raise HTTPException(500, f"PDF read error: {e}")'''

new_scan_start = '''@app.post("/api/auction/scan-pdf")
async def scan_pdf_auction(file: UploadFile = File(...)):
    import os, base64, json, fitz, asyncio, uuid
    import google.generativeai as genai

    contents = await file.read()
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        raise HTTPException(400, "GEMINI_API_KEY not set")

    # Store PDF in Supabase for later image retrieval
    scan_id = str(uuid.uuid4())[:8]
    try:
        supabase.storage.from_("auction-pdfs").upload(
            path=f"{scan_id}.pdf",
            file=contents,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
    except Exception as upload_err:
        print(f"PDF storage warning: {upload_err}")
        scan_id = None

    # Extract text chunks
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        total_pages = len(doc)
        chunk_size = 2
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
        raise HTTPException(500, f"PDF read error: {e}")'''

if old_scan_start in content:
    content = content.replace(old_scan_start, new_scan_start)
    print('✅ scan_pdf updated with storage upload')
else:
    print('❌ scan_pdf start not found')

# 3. Include scan_id in the done message and per-item page image URL
old_done = '        yield {"data": json.dumps({"done": True, "total": len(all_items)})}'
new_done = '        yield {"data": json.dumps({"done": True, "total": len(all_items), "scan_id": scan_id})}'
if old_done in content:
    content = content.replace(old_done, new_done)
    print('✅ scan_id added to done message')
else:
    print('❌ done message not found')

# 4. Add page image URL to each item
old_item_yield = '''                page_start = i * chunk_size + 1
                page_end = min((i + 1) * chunk_size, total_pages)
                for item in items:
                    item["_page_start"] = page_start
                    item["_page_end"] = page_end
                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total_chunks,
                        "items": items,
                        "done": False
                    })
                }'''

new_item_yield = '''                page_start = i * chunk_size + 1
                page_end = min((i + 1) * chunk_size, total_pages)
                for item in items:
                    item["_page_start"] = page_start
                    item["_page_end"] = page_end
                    if scan_id:
                        item["_page_img"] = f"/api/auction/page-image/{scan_id}/{page_start}"
                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total_chunks,
                        "items": items,
                        "scan_id": scan_id,
                        "done": False
                    })
                }'''

if old_item_yield in content:
    content = content.replace(old_item_yield, new_item_yield)
    print('✅ page image URL added to items')
else:
    print('❌ item yield not found')

# Insert new endpoint before the scan_pdf endpoint
anchor = '# ── API: PDF AUCTION SCAN ─────────────────────────────────────── #'
if anchor in content:
    content = content.replace(anchor, new_endpoint + anchor)
    print('✅ page image endpoint added')
else:
    print('❌ anchor not found')

open('main.py', 'w').write(content)
