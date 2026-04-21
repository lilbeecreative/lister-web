content = open('main.py').read()

old = '''@app.get("/api/auction/page-image/{scan_id}/{page_num}")
async def get_page_image(scan_id: str, page_num: int):
    import io, fitz
    from fastapi.responses import Response
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
        raise HTTPException(500, str(e))'''

new = '''@app.get("/api/auction/page-image/{scan_id}/{img_index}")
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

if old in content:
    content = content.replace(old, new)
    print('done endpoint')
else:
    print('endpoint not found')

old2 = '                    item["_page_img"] = f"/api/auction/page-image/{scan_id}/{page_start}"'
new2 = '                    img_idx = len(all_items) + items.index(item)\n                    item["_page_img"] = f"/api/auction/page-image/{scan_id}/{img_idx}"'
if old2 in content:
    content = content.replace(old2, new2)
    print('done index')
else:
    print('index not found')

open('main.py', 'w').write(content)
