"""
fix_pdf_image_scan.py
Run from ~/Desktop/lister_web:
    python3 fix_pdf_image_scan.py

When PDF pages have no extractable text (image-only PDFs like screenshots),
falls back to rendering each page as an image and sending to Gemini Vision.
"""
import sys

MAIN = "main.py"

OLD_CHUNKS = '''    # Extract text chunks
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

NEW_CHUNKS = '''    # Extract text chunks — fall back to image rendering for image-only PDFs
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        total_pages = len(doc)
        chunk_size = 2
        page_chunks = []
        page_images = []  # list of (page_num, jpeg_bytes) for image fallback
        for start in range(0, total_pages, chunk_size):
            end = min(start + chunk_size, total_pages)
            chunk_text = ""
            for page_num in range(start, end):
                chunk_text += doc[page_num].get_text() + "\\n"
            if chunk_text.strip():
                page_chunks.append(chunk_text)

        # If no text found, render pages as images
        if not page_chunks:
            print(f"PDF has no text — switching to image scan ({total_pages} pages)")
            for page_num in range(total_pages):
                page = doc[page_num]
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                page_images.append((page_num, pix.tobytes("jpeg")))
        doc.close()
    except Exception as e:
        raise HTTPException(500, f"PDF read error: {e}")'''

OLD_CALL_GEMINI = '''    def call_gemini(chunk_text, i, total):
        response = model.generate_content(
            [prompt_template, f"\\nCATALOG SECTION {i+1}/{total}:\\n{chunk_text[:10000]}"],
            generation_config={"max_output_tokens": 16000}
        )
        return response.text'''

NEW_CALL_GEMINI = '''    def call_gemini(chunk_text, i, total):
        response = model.generate_content(
            [prompt_template, f"\\nCATALOG SECTION {i+1}/{total}:\\n{chunk_text[:10000]}"],
            generation_config={"max_output_tokens": 16000}
        )
        return response.text

    def call_gemini_image(page_num, img_bytes, total):
        """Send a rendered page image to Gemini Vision for lot extraction."""
        print(f"   Image scan page {page_num+1}/{total}")
        img_prompt = prompt_template + f"\\n\\nThis is page {page_num+1} of {total} of an auction catalog. Extract all lots visible in this image."
        response = model.generate_content(
            [img_prompt, {"mime_type": "image/jpeg", "data": img_bytes}],
            generation_config={"max_output_tokens": 16000}
        )
        return response.text'''

OLD_GENERATE = '''    async def generate():
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        all_items = []
        total_chunks = len(page_chunks)

        for i, chunk_text in enumerate(page_chunks):'''

NEW_GENERATE = '''    async def generate():
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        all_items = []

        # Image-only PDF path
        if page_images and not page_chunks:
            total_chunks = len(page_images)
            for i, (page_num, img_bytes) in enumerate(page_images):
                try:
                    raw = await loop.run_in_executor(executor, call_gemini_image, page_num, img_bytes, total_chunks)
                    raw = " ".join(raw.splitlines())
                    if "```" in raw:
                        raw = raw.split("```")[1]
                        if raw.startswith("json"): raw = raw[4:]
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
                    for item in items:
                        item["_page_start"] = page_num + 1
                        item["_page_end"] = page_num + 1
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
                    print(f"Image page {page_num+1} error: {e}")
                await asyncio.sleep(0.1)
            yield {"data": json.dumps({"done": True, "total": len(all_items), "scan_id": scan_id})}
            return

        total_chunks = len(page_chunks)

        for i, chunk_text in enumerate(page_chunks):'''

def main():
    try:
        with open(MAIN, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {MAIN} not found")
        sys.exit(1)

    patches = [
        (OLD_CHUNKS,       NEW_CHUNKS,       "image fallback chunk extraction"),
        (OLD_CALL_GEMINI,  NEW_CALL_GEMINI,  "call_gemini_image function"),
        (OLD_GENERATE,     NEW_GENERATE,     "generate() image path"),
    ]

    for old, new, label in patches:
        if old in src:
            src = src.replace(old, new, 1)
            print(f"✅ Patched: {label}")
        else:
            print(f"❌ Not found: {label}")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py")
    print('   git commit -m "image-only PDF scan fallback for screenshot PDFs"')
    print("   git push")

if __name__ == "__main__":
    main()
