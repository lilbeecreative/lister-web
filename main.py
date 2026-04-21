"""
Lister AI — FastAPI Web Dashboard
Replaces Streamlit for real-time performance.
"""
import os
import csv
import io
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client
from pydantic import BaseModel
from typing import Optional

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase     = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Lister AI")
import os as _os
if _os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

EBAY_DESCRIPTION = "Shipped primarily with UPS and sometimes USPS. If you have special packing or shipping needs, please send a message. This item is sold in as-is condition. The seller assumes no liability for the use, operation, or installation of this product. Due to the technical nature of this equipment, the buyer is responsible for having the item professionally inspected and installed by a certified technician prior to use."

def photo_url(photo_id: str, thumb: bool = False) -> str:
    if not photo_id or photo_id in ("", "nan", "0"):
        return ""
    if thumb:
        return f"{SUPABASE_URL}/storage/v1/render/image/public/part-photos/{photo_id}?width=500&height=500&resize=cover&quality=80"
    return f"{SUPABASE_URL}/storage/v1/object/public/part-photos/{photo_id}"

# ── PAGES ─────────────────────────────────────────────────────── #

@app.get("/auction/research", response_class=HTMLResponse)
async def auction_research_page(request: Request):
    import os
    with open(os.path.join(os.path.dirname(__file__), "templates", "auction_research.html")) as f:
        html = f.read()
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src * blob: data:; script-src * blob: data: 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * blob: data:;"
    })

@app.get("/auction", response_class=HTMLResponse)
async def auction_page(request: Request):
    import os
    with open(os.path.join(os.path.dirname(__file__), "templates", "auction.html")) as f:
        html = f.read()
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src * blob: data:; script-src * blob: data: 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * blob: data:;"
    })

@app.get("/v2", response_class=HTMLResponse)
async def dashboard_v2(request: Request):
    from fastapi.responses import HTMLResponse
    import os
    with open(os.path.join(os.path.dirname(__file__), "templates", "v2.html")) as f:
        html = f.read()
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src * blob: data:; script-src * blob: data: 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * blob: data:;"
    })

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ── API: LISTINGS ─────────────────────────────────────────────── #

@app.get("/api/listings")
async def get_listings():
    try:
        res = supabase.table("listings")\
            .select("*")\
            .neq("status", "archived")\
            .order("created_at", desc=True)\
            .execute()
        listings = res.data or []

        # Batch fetch all group photos for these listings
        primary_pids = [str(l.get("photo_id") or "") for l in listings if l.get("photo_id")]
        group_photo_map = {}  # photo_id -> [all photo_ids in same group]
        if primary_pids:
            try:
                gp_res = supabase.table("group_photos")                    .select("group_id, photo_id")                    .in_("photo_id", primary_pids[:100])                    .execute()
                # Map primary photo -> group_id
                pid_to_gid = {row["photo_id"]: row["group_id"] for row in (gp_res.data or [])}
                group_ids = list(set(pid_to_gid.values()))
                if group_ids:
                    all_gp = supabase.table("group_photos")                        .select("group_id, photo_id")                        .in_("group_id", group_ids)                        .execute()
                    # Build group_id -> [photo_ids]
                    gid_to_photos = {}
                    for row in (all_gp.data or []):
                        gid_to_photos.setdefault(row["group_id"], []).append(row["photo_id"])
                    # Map primary photo_id -> all photos in its group
                    for pid, gid in pid_to_gid.items():
                        group_photo_map[pid] = gid_to_photos.get(gid, [pid])
            except Exception:
                pass

        for l in listings:
            pid = str(l.get("photo_id") or "")
            all_photos = group_photo_map.get(pid, [pid] if pid else [])
            l["thumb_url"]  = photo_url(pid, thumb=True)
            l["full_url"]   = photo_url(pid)
            l["all_photos"] = [{"thumb": photo_url(p, thumb=True), "full": photo_url(p)} for p in all_photos if p]
            # Coerce types
            l["price"]      = float(l.get("price") or 0)
            l["price_used"] = float(l.get("price_used") or 0)
            l["price_new"]  = float(l.get("price_new") or 0)
            l["quantity"]   = int(l.get("quantity") or 1)
            # Normalize condition — default to "used" if blank/null
            cond = str(l.get("condition") or "").strip().lower()
            l["condition"] = cond if cond in ("new", "used") else "used"
            # Normalize listing_type — items from batch upload are not auctions
            lt = str(l.get("listing_type") or "").strip().lower()
            if lt not in ("auction", "fixed"):
                l["listing_type"] = "fixed"
        return JSONResponse(listings)
    except Exception as e:
        raise HTTPException(500, str(e))

class UpdateField(BaseModel):
    field: str
    value: object


@app.get("/api/stats")
async def get_stats():
    try:
        res = supabase.table("listings").select("price, status").neq("status", "archived").execute()
        items = res.data or []
        total = len(items)
        value = sum(float(i.get("price") or 0) for i in items)
        pending = supabase.table("listing_groups").select("id").in_("status", ["pending", "processing"]).execute()
        processing = len(pending.data or [])
        return {"total": total, "processing": processing, "value": round(value, 2)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.patch("/api/listings/{item_id}")
async def update_listing(item_id: str, body: UpdateField):
    try:
        supabase.table("listings").update({body.field: body.value}).eq("id", item_id).execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/listings/{item_id}/rescan")
async def rescan_listing(item_id: str):
    try:
        res = supabase.table("listings").select("photo_id").eq("id", item_id).limit(1).execute()
        pid = (res.data[0].get("photo_id", "") if res.data else "")
        if pid:
            grp = supabase.table("group_photos").select("group_id").eq("photo_id", pid).limit(1).execute()
            if grp.data:
                gid = grp.data[0]["group_id"]
                supabase.table("listing_groups").update({"status": "pending"}).eq("id", gid).execute()
        supabase.table("listings").update({"status": "pending", "title": "Scanning..."}).eq("id", item_id).execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/listings/archive-batch")
async def archive_batch():
    try:
        res = supabase.table("listings").select("*").neq("status", "archived").execute()
        items = res.data or []
        if items:
            ids = [str(i["id"]) for i in items]
            supabase.table("listings").update({"status": "archived"}).in_("id", ids).execute()
        return {"ok": True, "count": len(items)}
    except Exception as e:
        raise HTTPException(500, str(e))

# ── API: BATCH UPLOAD ─────────────────────────────────────────── #

class CreateGroup(BaseModel):
    session_id: str
    condition:  str

@app.post("/api/groups")
async def create_group(body: CreateGroup):
    try:
        res = supabase.table("listing_groups").insert({
            "session_id": body.session_id,
            "status":     "waiting",
            "quantity":   1,
            "condition":  body.condition,
        }).execute()
        import traceback
        print(f"Group insert result: {res}")
        data = res.data
        gid = data[0]["id"] if isinstance(data, list) and data else (data.get("id") if isinstance(data, dict) else None)
        if not gid:
            raise Exception(f"No ID returned. data={data}")
        return {"id": gid}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, str(e))

class SubmitGroup(BaseModel):
    group_id:  str
    condition: str
    quantity:  int

@app.post("/api/groups/submit")
async def submit_group(body: SubmitGroup):
    try:
        supabase.table("listing_groups").update({
            "condition": body.condition,
            "quantity":  body.quantity,
            "status":    "pending",
        }).eq("id", body.group_id).execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/photos/upload")
async def upload_photo(request: Request):
    try:
        form     = await request.form()
        file     = form["file"]
        gid      = str(form["group_id"])
        idx      = int(form.get("index", 0))
        contents = await file.read()
        dt  = datetime.now()
        fn  = f"{dt.strftime('%d%m%y')}_{dt.strftime('%H%M%S')}_{idx}.jpg"
        print(f"Uploading photo: {fn}, size={len(contents)}, group={gid}")
        supabase.storage.from_("part-photos").upload(
            path=fn,
            file=contents,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )
        supabase.table("group_photos").insert({"group_id": gid, "photo_id": fn}).execute()
        return {"ok": True, "photo_id": fn, "url": photo_url(fn, thumb=True)}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, str(e))



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

    def extract_single_image(pdf_bytes, img_index):
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

    def identify_item_from_image(images, title):
        if not images:
            return title
        try:
            id_prompt = f"Look at this auction item image carefully. The listing title says: {title}. Identify the exact make, model number, and condition. Look for nameplates, labels, screens. Return one line with the most accurate description possible. If unsure, return the original title."
            parts = [id_prompt] + [{"mime_type": "image/jpeg", "data": img} for img in images[:1]]
            r = model.generate_content(parts, generation_config={"max_output_tokens": 150})
            result = r.text.strip().strip('"')
            return result if result else title
        except Exception as e:
            print(f"Image ID error: {e}")
            return title

    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        # Step 1: identify exact model from image
        identified = identify_item_from_image(images, title)
        if identified != title:
            print(f"Lot {lot} image ID: {identified}")

        prompt = f"""You are an expert industrial equipment appraiser. Research this auction item using web search.

Item: Lot #{lot} — {title}
Image-identified model: {identified}
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
            response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})
        raw = response.text.strip()
        print(f"   Deep research raw response (lot {lot}): {raw[:300]}")
        # Strip markdown fences
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        raw = " ".join(raw.splitlines())

        raw = " ".join(raw.splitlines())
        # Find JSON object boundaries
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            from json_repair import repair_json
            data = json.loads(repair_json(raw))
        # Sanitize string fields to prevent SSE encoding issues
        for key in ["image_notes", "rec_reason", "notes", "confidence", "recommendation"]:
            if key in data:
                data[key] = str(data[key]).replace("\n", " ").replace("\r", " ")
        if "comps" in data:
            for comp in data["comps"]:
                for k in comp:
                    comp[k] = str(comp[k]).replace("\n", " ") if isinstance(comp[k], str) else comp[k]
        return data

    async def generate():
        total = len(items)
        for i, item in enumerate(items):
            yield {"data": json.dumps({"type": "start", "lot": item.get("lot"), "index": i, "total": total})}
            try:
                images = []
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
                        print(f"Auto image fetch error: {img_e}")
                result = await loop.run_in_executor(executor, research_item, item, images)
                yield {"data": json.dumps({
                    "type": "result",
                    "lot": item.get("lot"),
                    "index": i,
                    "total": total,
                    "has_image": len(images) > 0,
                    **result
                })}
            except json.JSONDecodeError as e:
                print(f"JSON parse error for lot {item.get('lot')}: {e}")
                yield {"data": json.dumps({
                    "type": "result",
                    "lot": item.get("lot"),
                    "index": i,
                    "total": total,
                    "has_image": len(images) > 0,
                    "revised_value": item.get("your_value", 0),
                    "confidence": "low",
                    "comps": [],
                    "image_notes": "Research completed but response parsing failed",
                    "recommendation": "watch",
                    "rec_reason": "Could not parse research results — try again",
                    "notes": ""
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


@app.post("/api/auction/research-export")
async def research_export(request: Request):
    import io, json
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from fastapi.responses import StreamingResponse

    form = await request.form()
    items = json.loads(form.get("items", "[]"))

    wb = Workbook()
    ws = wb.active
    ws.title = "Deep Research"

    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill("solid", fgColor="1E2535")
    amber_fill = PatternFill("solid", fgColor="412402")
    green_fill = PatternFill("solid", fgColor="052E16")
    alt_fill = PatternFill("solid", fgColor="161B28")
    center = Alignment(horizontal="center", vertical="center")
    wrap = Alignment(wrap_text=True, vertical="center")
    thin = Border(
        bottom=Side(style="thin", color="2D3348"),
        right=Side(style="thin", color="2D3348")
    )

    headers = ["Lot", "Title", "Original Value", "Revised Value", "Confidence", "Recommendation", "Notes", "eBay Search"]
    col_widths = [8, 45, 15, 15, 12, 16, 40, 20]

    for ci, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=ci, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        ws.column_dimensions[get_column_letter(ci)].width = w

    ws.row_dimensions[1].height = 22

    for ri, item in enumerate(items, 2):
        row_data = [
            item.get("lot", ""),
            item.get("title", ""),
            item.get("original_value", 0),
            item.get("revised_value", 0),
            item.get("confidence", "").capitalize(),
            item.get("recommendation", "").capitalize(),
            item.get("rec_reason") or item.get("image_notes", ""),
            "View eBay Sold"
        ]
        rec = item.get("recommendation", "").lower()
        fill = green_fill if rec == "buy" else amber_fill if rec == "watch" else (alt_fill if ri % 2 == 0 else None)

        for ci, val in enumerate(row_data, 1):
            cell = ws.cell(row=ri, column=ci, value=val)
            if fill:
                cell.fill = fill
            cell.border = thin
            cell.alignment = wrap if ci in (2, 7) else center
            if ci in (3, 4) and isinstance(val, (int, float)):
                cell.number_format = '"$"#,##0'
            if ci == 8 and item.get("ebay_search"):
                ws.cell(row=ri, column=ci).hyperlink = item["ebay_search"]
                ws.cell(row=ri, column=ci).font = Font(color="4A9EFF", underline="single")
        ws.row_dimensions[ri].height = 20

    ws.freeze_panes = "A2"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=deep_research.xlsx"}
    )


@app.post("/api/auction/research-export")
async def research_export(request: Request):
    import io, json
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from fastapi.responses import StreamingResponse

    form = await request.form()
    items = json.loads(form.get("items", "[]"))

    wb = Workbook()
    ws = wb.active
    ws.title = "Deep Research"

    # Styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill("solid", fgColor="1E2535")
    amber_fill = PatternFill("solid", fgColor="412402")
    green_fill = PatternFill("solid", fgColor="052E16")
    alt_fill = PatternFill("solid", fgColor="161B28")
    center = Alignment(horizontal="center", vertical="center")
    wrap = Alignment(wrap_text=True, vertical="center")
    thin = Border(
        bottom=Side(style="thin", color="2D3348"),
        right=Side(style="thin", color="2D3348")
    )

    headers = ["Lot", "Title", "Original Value", "Revised Value", "Confidence", "Recommendation", "Notes", "eBay Search"]
    col_widths = [8, 45, 15, 15, 12, 16, 40, 20]

    for ci, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=ci, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        ws.column_dimensions[get_column_letter(ci)].width = w

    ws.row_dimensions[1].height = 22

    for ri, item in enumerate(items, 2):
        row_data = [
            item.get("lot", ""),
            item.get("title", ""),
            item.get("original_value", 0),
            item.get("revised_value", 0),
            item.get("confidence", "").capitalize(),
            item.get("recommendation", "").capitalize(),
            item.get("rec_reason") or item.get("image_notes", ""),
            "View eBay Sold"
        ]
        rec = item.get("recommendation", "").lower()
        fill = green_fill if rec == "buy" else amber_fill if rec == "watch" else (alt_fill if ri % 2 == 0 else None)

        for ci, val in enumerate(row_data, 1):
            cell = ws.cell(row=ri, column=ci, value=val)
            if fill:
                cell.fill = fill
            cell.border = thin
            cell.alignment = wrap if ci in (2, 7) else center
            if ci in (3, 4) and isinstance(val, (int, float)):
                cell.number_format = '"$"#,##0'
            if ci == 8 and item.get("ebay_search"):
                ws.cell(row=ri, column=ci).hyperlink = item["ebay_search"]
                ws.cell(row=ri, column=ci).font = Font(color="4A9EFF", underline="single")
        ws.row_dimensions[ri].height = 20

    ws.freeze_panes = "A2"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=deep_research.xlsx"}
    )

# ── API: AUCTION DEEP RESEARCH ───────────────────────────────── #

class DeepResearch(BaseModel):
    title: str
    current_value: float = 0

@app.post("/api/auction/deep-research")
async def deep_research(body: DeepResearch):
    import os, asyncio, json
    from concurrent.futures import ThreadPoolExecutor
    import google.generativeai as genai
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        raise HTTPException(400, "GEMINI_API_KEY not set")
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are an expert industrial equipment appraiser.
Research this auction item thoroughly: "{body.title}"
Current estimate: ${body.current_value}

Check eBay sold listings, industrial dealers, and recent auction results.
Assume working used condition.

Return ONLY a JSON object (no markdown):
{{"your_value": 5000, "notes": "Sold $4,500-$6,000 on eBay 2024"}}

your_value must be an integer."""

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        response = await loop.run_in_executor(executor, lambda: model.generate_content(prompt, generation_config={"max_output_tokens": 300}))
        raw = response.text.strip().replace("```json","").replace("```","").strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            from json_repair import repair_json
            data = json.loads(repair_json(raw))
        return data
    except Exception as e:
        raise HTTPException(500, str(e))


# ── API: EXCEL EXPORT ─────────────────────────────────────────── #

@app.post("/api/auction/export-excel")
async def export_excel(request: Request):
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    body = await request.json()
    items = body.get("items", [])
    name = body.get("name", "Auction Scan")

    wb = Workbook()
    ws = wb.active
    ws.title = name[:31]

    hdr_font = Font(bold=True, color="FFFFFF", size=11)
    hdr_fill = PatternFill("solid", fgColor="1A1F2E")
    hv_fill = PatternFill("solid", fgColor="5C3A00")
    hv_font = Font(color="FAC775", bold=True)

    headers = ["Lot", "Title", "Est. Value", "Notes", "Deep Scan", "Watchlisted"]
    ws.append(headers)
    for col in range(1, 7):
        cell = ws.cell(row=1, column=col)
        cell.font = hdr_font
        cell.fill = hdr_fill
        cell.alignment = Alignment(horizontal="center")

    for item in items:
        val = int(item.get("your_value", 0) or 0)
        row = [
            str(item.get("lot", "")),
            str(item.get("title", "")),
            f"${val:,}",
            str(item.get("notes", "")),
            "Yes" if item.get("_deep") else "",
            "Yes" if item.get("_watch") else "",
        ]
        ws.append(row)
        if val >= 500:
            r = ws.max_row
            for col in range(1, 7):
                ws.cell(row=r, column=col).fill = hv_fill
                ws.cell(row=r, column=col).font = hv_font

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 45
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 12

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    from datetime import datetime
    fn = f"auction_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={fn}"}
    )


# ── API: AUCTION PAGE IMAGE ───────────────────────────────────── #

@app.get("/api/auction/page-image/{scan_id}/{img_index}")
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
        raise HTTPException(500, str(e))

# ── API: PDF AUCTION SCAN ─────────────────────────────────────── #

from sse_starlette.sse import EventSourceResponse

@app.post("/api/auction/scan-pdf")
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
                chunk_text += doc[page_num].get_text() + "\n"
            if chunk_text.strip():
                page_chunks.append(chunk_text)
        doc.close()
    except Exception as e:
        raise HTTPException(500, f"PDF read error: {e}")

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt_template = """You are a world-class auction appraiser with deep expertise in industrial equipment, lab instruments, and commercial goods.

Extract EVERY auction lot from this catalog section.

For each lot return a JSON object:
- lot: lot number as string
- title: full item title as written
- description: one sentence description
- estimate_low: integer dollar amount
- estimate_high: integer dollar amount
- your_value: integer (your single best estimate - total lot value)
- notes: brief market note with price source

EXPERT AUCTION TITLE INTERPRETATION:
- Quantities: "(2)", "QTY (3)", "SET OF 4", "PAIR", "x3" = price TOTAL for ALL units combined
- Vague lots: "SHELF OF...", "PALLET OF...", "BOX OF..." = estimate total resale of all contents
- Condition notes like "AS-IS", "UNTESTED", "ACTIVATION NOT GUARANTEED" = still price as normal working condition
- Always search for the SPECIFIC brand + model for accurate pricing
- Ignore auction house names, catalog numbers, location references in titles

PRICING RULES:
- All values MUST be plain integers (no $, no text)
- Base on ACTUAL used market values from eBay sold listings
- If no lots found, return: []
- Return ONLY a JSON array, no markdown

Example: [{"lot":"5","title":"Oakton pH Meter","description":"Portable pH/ORP meter with case","estimate_low":80,"estimate_high":150,"your_value":100,"notes":"Sells $80-150 used on eBay"}]"""

    def call_gemini(chunk_text, i, total):
        response = model.generate_content(
            [prompt_template, f"\nCATALOG SECTION {i+1}/{total}:\n{chunk_text[:10000]}"],
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
                raw = await loop.run_in_executor(executor, call_gemini, chunk_text, i, total_chunks)
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


def get_unmatched_photos():
    """Get all photos from storage that haven't been matched yet."""
    try:
        # Get all files in part-photos bucket
        res = supabase.storage.from_("part-photos").list()
        files = [f["name"] for f in (res or []) if f.get("name") and not f["name"].startswith(".")]
        return {"photos": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(500, str(e))

class ScanPartsBody(BaseModel):
    part_numbers: list
    photo_ids:    list
    gemini_key:   Optional[str] = None

@app.post("/api/parts/scan")
async def scan_parts(body: ScanPartsBody):
    """
    Scan a batch of photos through Gemini Vision.
    For each photo, extract any visible part numbers and check against the list.
    Returns matches with confidence.
    """
    import threading
    gemini_key = body.gemini_key or os.getenv("GEMINI_API_KEY", "")
    if not gemini_key:
        raise HTTPException(400, "Gemini API key required")
    if not body.part_numbers:
        raise HTTPException(400, "No part numbers provided")

    results = []
    part_set = [str(p).strip().upper() for p in body.part_numbers if str(p).strip()]

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        try:
            from google import genai as genai2
            from google.genai import types
            client = genai2.Client(api_key=gemini_key)
        except Exception as e:
            raise HTTPException(500, f"Gemini init failed: {e}")

    for photo_id in body.photo_ids[:50]:  # max 50 at a time
        try:
            # Download photo from Supabase
            img_bytes = supabase.storage.from_("part-photos").download(photo_id)
            if not img_bytes:
                continue

            # Build prompt
            parts_list = "\n".join(part_set[:200])
            prompt = f"""Examine this image carefully. 
Read ALL visible text including: part numbers, model numbers, serial numbers, labels, stamps, engravings, stickers, tags.

I am looking for matches to this list of part numbers:
{parts_list}

Return ONLY a JSON object:
{{
  "visible_text": ["list", "of", "all", "text", "you", "can", "read"],
  "part_numbers_found": ["any", "part", "numbers", "you", "see"],
  "matches": ["part numbers that exactly or closely match the search list"],
  "confidence": "high/medium/low",
  "notes": "brief note on what you see"
}}

If no text visible or no matches, still return the JSON with empty arrays."""

            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                import PIL.Image
                import io
                img = PIL.Image.open(io.BytesIO(img_bytes))
                response = model.generate_content([prompt, img])
                raw = response.text or ""
            except Exception:
                try:
                    from google import genai as gc
                    from google.genai import types as gt
                    cl = gc.Client(api_key=gemini_key)
                    models = [m.name for m in cl.models.list()]
                    best = next((m for m in models if "gemini-2.5" in m or "gemini-2.0" in m), models[0] if models else "models/gemini-1.5-pro")
                    resp = cl.models.generate_content(
                        model=best,
                        contents=[gt.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"), prompt]
                    )
                    raw = resp.text or ""
                except Exception as e2:
                    results.append({"photo_id": photo_id, "error": str(e2), "matches": []})
                    continue

            import re, json
            raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\n?```$", "", raw).strip()
            jm = re.search(r'\{.*\}', raw, re.DOTALL)
            if jm:
                data = json.loads(jm.group())
                results.append({
                    "photo_id":        photo_id,
                    "url":             photo_url(photo_id, thumb=True),
                    "full_url":        photo_url(photo_id),
                    "visible_text":    data.get("visible_text", []),
                    "part_numbers_found": data.get("part_numbers_found", []),
                    "matches":         data.get("matches", []),
                    "confidence":      data.get("confidence", ""),
                    "notes":           data.get("notes", ""),
                    "has_match":       len(data.get("matches", [])) > 0,
                })
            else:
                results.append({"photo_id": photo_id, "matches": [], "notes": "Could not parse response"})

        except Exception as e:
            results.append({"photo_id": photo_id, "error": str(e), "matches": []})

    matches    = [r for r in results if r.get("has_match")]
    no_matches = [r for r in results if not r.get("has_match")]
    return {
        "results":     results,
        "matches":     matches,
        "no_matches":  no_matches,
        "match_count": len(matches),
        "scanned":     len(results),
    }

# ── SETTINGS ──────────────────────────────────────────────────── #

@app.get("/api/settings")
async def get_settings():
    try:
        res = supabase.table("app_settings").select("*").execute()
        return {row["key"]: row["value"] for row in (res.data or [])}
    except Exception:
        return {}

class SaveSetting(BaseModel):
    key:   str
    value: str

@app.post("/api/settings")
async def save_setting(body: SaveSetting):
    try:
        supabase.table("app_settings").upsert({"key": body.key, "value": body.value}).execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))
