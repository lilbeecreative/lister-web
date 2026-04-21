content = open('main.py').read()

# 1. Add PDF auction endpoint before the closing
pdf_endpoint = '''
# ── API: PDF AUCTION SCAN ─────────────────────────────────────── #

@app.post("/api/auction/scan-pdf")
async def scan_pdf_auction(file: UploadFile = File(...)):
    import os, base64, json, io, csv
    try:
        contents = await file.read()
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            raise HTTPException(400, "GEMINI_API_KEY not set")

        # Extract text from PDF using PyMuPDF
        try:
            import fitz
            doc = fitz.open(stream=contents, filetype="pdf")
            pdf_text = ""
            images = []
            for page_num in range(min(len(doc), 20)):
                page = doc[page_num]
                pdf_text += page.get_text() + "\\n"
                for img in page.get_images():
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    images.append({
                        "data": base64.b64encode(base_image["image"]).decode(),
                        "mime": "image/" + base_image["ext"]
                    })
            doc.close()
        except Exception as e:
            pdf_text = f"PDF text extraction failed: {e}"
            images = []

        # Send to Gemini
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-pro")

        prompt = """You are an expert auction appraiser. Analyze this auction catalog PDF.

For each auction lot/item found, extract:
1. Lot number (if present)
2. Item title/description
3. Any photos or image references
4. Any listed estimate or starting bid
5. Direct URL to the listing (if present in text)

Then research each item and provide your estimated market value based on recent eBay sold listings.

Return ONLY a JSON array with this exact structure:
[
  {
    "lot": "12",
    "title": "Item name here",
    "description": "Brief description",
    "estimate_low": 50,
    "estimate_high": 100,
    "your_value": 75,
    "listing_url": "https://...",
    "notes": "Brief market notes"
  }
]

Return ONLY the JSON array, no other text."""

        parts = [prompt, f"\\n\\nPDF TEXT CONTENT:\\n{pdf_text[:8000]}"]
        for img in images[:5]:
            parts.append({"mime_type": img["mime"], "data": base64.b64decode(img["data"])})

        response = model.generate_content(parts)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\\n", 1)[1].rsplit("\\n", 1)[0].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

        items = json.loads(raw)

        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow(["Lot", "Title", "Description", "Est. Low", "Est. High", "Your Value", "Listing URL", "Notes"])
        for item in items:
            writer.writerow([
                item.get("lot", ""),
                item.get("title", ""),
                item.get("description", ""),
                f"${item.get('estimate_low', 0)}",
                f"${item.get('estimate_high', 0)}",
                f"${item.get('your_value', 0)}",
                item.get("listing_url", ""),
                item.get("notes", ""),
            ])

        from datetime import datetime
        fn = f"auction_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={fn}"}
        )
    except json.JSONDecodeError:
        raise HTTPException(500, "Gemini returned invalid JSON — try again")
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, str(e))

'''

# Insert before the last route or at end
anchor = '\n# ── API: AUCTION ──'
if anchor in content:
    content = content.replace(anchor, pdf_endpoint + anchor)
    print('✅ PDF endpoint added')
else:
    # append before end
    content = content.rstrip() + '\n' + pdf_endpoint
    print('✅ PDF endpoint appended')

open('main.py', 'w').write(content)
