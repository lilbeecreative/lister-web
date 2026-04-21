content = open('main.py').read()

# The image index approach is unreliable - use page-based image extraction instead
# Each lot is on a specific page, extract the FIRST large image from that page
old_endpoint = '''@app.get("/api/auction/page-image/{scan_id}/{img_index}")
async def get_page_image(scan_id: str, img_index: int):
    import fitz
    from fastapi.responses import Response
    try:
        pdf_data = supabase.storage.from_("auction-pdfs").download(f"{scan_id}.pdf")
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        all_images = []
        for page in doc:
            for img in page.get_images():
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    if base_image and base_image.get("image") and len(base_image["image"]) > 2000:
                        all_images.append(base_image)
                except Exception:
                    pass
        doc.close()
        if not all_images or img_index < 0 or img_index >= len(all_images):
            raise HTTPException(404, "Image not found")
        img_data = all_images[img_index]
        ext = img_data.get("ext", "jpeg")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/" + ext
        return Response(content=img_data["image"], media_type=mime, headers={"Cache-Control": "public, max-age=86400"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))'''

new_endpoint = '''@app.get("/api/auction/page-image/{scan_id}/{img_index}")
async def get_page_image(scan_id: str, img_index: int):
    import fitz
    from fastapi.responses import Response
    try:
        pdf_data = supabase.storage.from_("auction-pdfs").download(f"{scan_id}.pdf")
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        # Collect all large embedded images (skip logos/watermarks < 5KB)
        all_images = []
        seen_xrefs = set()
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                try:
                    base_image = doc.extract_image(xref)
                    if base_image and base_image.get("image") and len(base_image["image"]) > 8000:
                        all_images.append(base_image)
                except Exception:
                    pass
        doc.close()
        if not all_images or img_index < 0 or img_index >= len(all_images):
            raise HTTPException(404, "Image not found")
        img_data = all_images[img_index]
        ext = img_data.get("ext", "jpeg")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/" + ext
        return Response(content=img_data["image"], media_type=mime, headers={"Cache-Control": "public, max-age=86400"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))'''

if old_endpoint in content:
    content = content.replace(old_endpoint, new_endpoint)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
