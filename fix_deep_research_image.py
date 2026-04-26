content = open('main.py').read()

old_research = '''    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        prompt = f"""You are a world-class auction appraiser. Research this auction item using web search.

Item: Lot #{lot} — {title}
Current estimate: ${current_val}

TASKS:
1. Search eBay SOLD listings for this exact item or very close matches — use real search results only
2. Search Google for current market pricing from dealers and recent auctions
3. If you have an image, analyze it carefully for make/model/condition details

STRICT RULES:
- Only include comps from ACTUAL search results you can verify — do not fabricate listings
- If you cannot find real comparable sales, say so in notes and use low confidence
- revised_value must be an integer based on real market data
- confidence: high (3+ real comps found), medium (1-2 comps), low (no real comps found)
- recommendation: buy (good value vs market), watch (fair value), pass (overpriced or uncertain)

Return ONLY valid JSON (no markdown, no apostrophes in strings):
{{"revised_value": 1400, "confidence": "high", "comps": [{{"title": "Exact item name from listing", "price": 1200, "date": "Mar 2025", "source": "eBay Sold"}}], "image_notes": "What the image shows", "recommendation": "buy", "rec_reason": "Sells for X on eBay", "notes": "Market summary"}}"""

        # Use Gemini with search grounding if available
        try:
            from google.generativeai import types as gtypes
            search_tool = gtypes.Tool(google_search_retrieval=gtypes.GoogleSearchRetrieval())
            parts = [prompt]
            for img_bytes in images[:2]:
                parts.append({"mime_type": "image/jpeg", "data": img_bytes})
            response = model.generate_content(
                parts,
                tools=[search_tool],
                generation_config={"max_output_tokens": 1500}
            )
        except Exception:
            parts = [prompt]
            for img_bytes in images[:2]:
                parts.append({"mime_type": "image/jpeg", "data": img_bytes})
            response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})'''

new_research = '''    def identify_item_from_image(images, title):
        """First pass: use image to identify exact make/model"""
        if not images:
            return title
        try:
            id_prompt = f"""Look at this auction item image carefully.
The listing title says: "{title}"

Identify:
1. Exact make and manufacturer
2. Exact model number/name (look for labels, nameplates, screens)
3. Any visible serial numbers or specifications
4. Condition assessment (excellent/good/fair/poor)
5. Any accessories or components visible

Return a single line with the most accurate item description possible.
Example: "Oakton PC 300 pH/Conductivity/TDS Meter with case - good condition"
If you cannot improve on the title, return the original title."""
            parts = [id_prompt]
            for img_bytes in images[:2]:
                parts.append({"mime_type": "image/jpeg", "data": img_bytes})
            response = model.generate_content(parts, generation_config={"max_output_tokens": 200})
            identified = response.text.strip().strip('"')
            return identified if identified else title
        except Exception as e:
            print(f"Image ID error: {e}")
            return title

    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        # Step 1: Use image to get more accurate item identification
        identified_title = identify_item_from_image(images, title)
        print(f"Lot {lot} identified as: {identified_title}")

        prompt = f"""You are a world-class auction appraiser. Research this auction item using web search.

Original listing: Lot #{lot} — {title}
Image analysis identified: {identified_title}
Current estimate: ${current_val}

Use the image-identified description for pricing research as it may be more accurate than the listing title.

TASKS:
1. Search eBay SOLD listings for this exact item — use the image-identified model if more specific
2. Search Google for current market pricing from dealers and recent auctions

STRICT RULES:
- Only include data from ACTUAL search results — do not fabricate
- If no real comps found, use low confidence
- revised_value must be an integer
- confidence: high (3+ comps), medium (1-2 comps), low (no comps)
- recommendation: buy/watch/pass

Return ONLY valid JSON:
{{"revised_value": 1400, "confidence": "high", "comps": [{{"title": "Item name", "price": 1200, "date": "Mar 2025", "source": "eBay Sold"}}], "image_notes": "{identified_title}", "recommendation": "buy", "rec_reason": "Reason", "notes": "Market summary"}}"""

        # Use Gemini with search grounding
        try:
            from google.generativeai import types as gtypes
            search_tool = gtypes.Tool(google_search_retrieval=gtypes.GoogleSearchRetrieval())
            response = model.generate_content(
                [prompt],
                tools=[search_tool],
                generation_config={"max_output_tokens": 1500}
            )
        except Exception:
            response = model.generate_content([prompt], generation_config={"max_output_tokens": 1500})'''

if old_research in content:
    content = content.replace(old_research, new_research)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')

# Also need to auto-extract images using scan_id from item._page_img
content2 = open('main.py').read()

old_extract = '''            images = []
                if pdf_bytes and item.get("_page_start"):
                    images = await loop.run_in_executor(
                        executor, extract_page_image, pdf_bytes,
                        item["_page_start"], item.get("_page_end", item["_page_start"])
                    )'''

new_extract = '''            images = []
                # Try to get image from uploaded PDF first
                if pdf_bytes and item.get("_page_start"):
                    images = await loop.run_in_executor(
                        executor, extract_page_image, pdf_bytes,
                        item["_page_start"], item.get("_page_end", item["_page_start"])
                    )
                # Fall back to fetching from stored PDF via scan_id
                if not images and item.get("_page_img"):
                    try:
                        img_url = item["_page_img"]
                        # Extract scan_id and img_index from URL like /api/auction/page-image/{scan_id}/{idx}
                        parts_url = img_url.strip("/").split("/")
                        if len(parts_url) >= 2:
                            sid = parts_url[-2]
                            idx = int(parts_url[-1])
                            stored_pdf = supabase.storage.from_("auction-pdfs").download(f"{sid}.pdf")
                            images = await loop.run_in_executor(
                                executor, lambda: extract_single_image(stored_pdf, idx)
                            )
                    except Exception as img_e:
                        print(f"Auto image fetch error: {img_e}")'''

if old_extract in content2:
    content2 = content2.replace(old_extract, new_extract)
    print('✅ auto image fetch added')
else:
    print('❌ extract not found')

# Add extract_single_image helper
old_extract_fn = '''    def extract_page_image(pdf_bytes, page_start, page_end):'''
new_extract_fn = '''    def extract_single_image(pdf_bytes, img_index):
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            seen = set()
            all_images = []
            for page in doc:
                for img in page.get_images(full=True):
                    xref = img[0]
                    if xref in seen: continue
                    seen.add(xref)
                    bi = doc.extract_image(xref)
                    if bi and len(bi.get("image","")) > 8000:
                        all_images.append(bi["image"])
            doc.close()
            if img_index < len(all_images):
                return [all_images[img_index]]
            return []
        except Exception as e:
            print(f"extract_single_image error: {e}")
            return []

    def extract_page_image(pdf_bytes, page_start, page_end):'''

if old_extract_fn in content2:
    content2 = content2.replace(old_extract_fn, new_extract_fn)
    open('main.py', 'w').write(content2)
    print('✅ extract_single_image added')
else:
    print('❌ extract_page_image not found')
