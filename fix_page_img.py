src = open('main.py').read()

old = '''        doc.close()
        if not all_images or img_index < 0 or img_index >= len(all_images):
            raise HTTPException(404, "Image not found")
        img_data = all_images[img_index]
        ext = img_data.get("ext", "jpeg")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/" + ext
        return Response(content=img_data["image"], media_type=mime, headers={"Cache-Control": "public, max-age=86400"})'''

new = '''        # Fallback: render page and crop item image area for image-only PDFs
        if not all_images or img_index < 0 or img_index >= len(all_images):
            doc2 = fitz.open(stream=pdf_data, filetype="pdf")
            items_per_page = 3
            page_num = img_index // items_per_page
            slot = img_index % items_per_page
            if page_num >= len(doc2):
                page_num = len(doc2) - 1
            page = doc2[page_num]
            pw, ph = page.rect.width, page.rect.height
            slot_h = ph / items_per_page
            clip = fitz.Rect(0, slot * slot_h, pw * 0.28, (slot + 1) * slot_h)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, clip=clip)
            doc2.close()
            return Response(content=pix.tobytes("jpeg"), media_type="image/jpeg",
                          headers={"Cache-Control": "public, max-age=86400"})
        img_data = all_images[img_index]
        ext = img_data.get("ext", "jpeg")
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/" + ext
        return Response(content=img_data["image"], media_type=mime, headers={"Cache-Control": "public, max-age=86400"})'''

if old in src:
    src = src.replace(old, new, 1)
    print("Patched")
else:
    print("Not found")
open('main.py','w').write(src)
