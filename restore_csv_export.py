"""
restore_csv_export.py
Run from ~/Desktop/lister_web:
    python3 restore_csv_export.py

Restores the original working eBay draft CSV export endpoint.
"""
import sys

MAIN = "main.py"

OLD_ENDPOINT = '''@app.get("/api/export/ebay-csv")
async def export_ebay_csv():
    import csv, io
    from fastapi.responses import StreamingResponse
    try:
        res = supabase.table("listings").select(
            "title,description,price,price_used,price_new,quantity,condition,status"
        ).neq("status", "archived").execute()
        items = res.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

    output = io.StringIO()
    writer = csv.writer(output)

    # eBay flat file compatible headers
    writer.writerow([
        "Title", "Description", "StartPrice", "BuyItNowPrice",
        "Quantity", "Condition", "ListingType", "Status"
    ])

    for item in items:
        cond = str(item.get("condition") or "used").strip().lower()
        ebay_condition = "Used" if cond == "used" else "New"
        ebay_listing = "FixedPriceItem"
        price = item.get("price") or item.get("price_used") or 0
        writer.writerow([
            item.get("title", ""),
            item.get("description", ""),
            round(float(price), 2),
            round(float(item.get("price_new") or price), 2),
            int(item.get("quantity") or 1),
            ebay_condition,
            ebay_listing,
            item.get("status", ""),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ebay-listings.csv"}
    )'''

NEW_ENDPOINT = '''@app.get("/api/export/ebay-csv")
async def export_ebay_csv():
    import csv, io
    from fastapi.responses import StreamingResponse
    from datetime import datetime
    try:
        res = supabase.table("listings").select(
            "title,price,price_used,price_new,quantity,condition,photo_id,ebay_category_id"
        ).neq("status", "archived").execute()
        items = res.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

    output = io.StringIO()

    # eBay draft flat file headers — same format as the working version
    output.write('#INFO,Version=0.0.2,Template= eBay-draft-listings-template_US,,,,,,,,\\n')
    output.write('#INFO Action and Category ID are required fields.,,,,,,,,,,\\n')
    output.write('#INFO,,,,,,,,,,\\n')
    output.write('Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8),Custom label (SKU),Category ID,Title,UPC,Price,Quantity,Item photo URL,Condition ID,Description,Format\\n')

    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    for item in items:
        cond = str(item.get("condition") or "used").strip().lower()
        cond_id = "1000" if cond == "new" else "3000"
        pid = str(item.get("photo_id") or "")
        pic = photo_url(pid) if pid else ""
        category_id = str(int(item.get("ebay_category_id") or 0)).replace(".0","") if item.get("ebay_category_id") else ""
        price = float(item.get("price") or item.get("price_used") or 0)
        writer.writerow([
            "Draft",
            pid.rsplit(".", 1)[0] if pid else "",
            category_id,
            str(item.get("title",""))[:80],
            "",
            f"{price:.2f}",
            str(int(item.get("quantity") or 1)),
            pic,
            cond_id,
            "",
            "FixedPrice",
        ])

    csv_bytes = output.getvalue().encode("utf-8")
    fn = f"listerai_ebay_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fn}"}
    )'''

def main():
    try:
        with open(MAIN, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {MAIN} not found")
        sys.exit(1)

    if OLD_ENDPOINT in src:
        src = src.replace(OLD_ENDPOINT, NEW_ENDPOINT, 1)
        print("✅ Restored original eBay draft CSV format")
    else:
        print("❌ Could not find endpoint — it may have already changed")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py")
    print('   git commit -m "restore original eBay draft CSV export format"')
    print("   git push")

if __name__ == "__main__":
    main()
