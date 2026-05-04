"""
add_ebay_csv.py
Run from ~/Desktop/lister_web:
    python3 add_ebay_csv.py
"""
import sys

MAIN  = "main.py"
HTML  = "templates/index.html"

ANCHOR = '@app.get("/api/stats")'

NEW_ENDPOINT = '''
@app.get("/api/export/ebay-csv")
async def export_ebay_csv():
    import csv, io
    from fastapi.responses import StreamingResponse
    try:
        res = supabase.table("listings").select(
            "title,description,price,price_used,price_new,quantity,condition,listing_type,status"
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
        listing_type = str(item.get("listing_type") or "fixed").strip().lower()
        ebay_listing = "FixedPriceItem" if listing_type == "fixed" else "Chinese"
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
    )


'''

# Fix the nav link to trigger a proper download
OLD_NAV = '<a class="nav-download" href="/api/export/ebay-csv" download>⬇️ eBay CSV</a>'
NEW_NAV = '<a class="nav-download" href="/api/export/ebay-csv" download="ebay-listings.csv">⬇️ eBay CSV</a>'

def main():
    try:
        with open(MAIN, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {MAIN} not found")
        sys.exit(1)

    if ANCHOR in src:
        src = src.replace(ANCHOR, NEW_ENDPOINT + ANCHOR, 1)
        print("✅ Added /api/export/ebay-csv endpoint")
    else:
        print("❌ Anchor not found in main.py")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    try:
        with open(HTML, "r", encoding="utf-8") as f:
            hsrc = f.read()
        if OLD_NAV in hsrc:
            hsrc = hsrc.replace(OLD_NAV, NEW_NAV, 1)
            print("✅ Fixed nav download link")
        else:
            print("⚠️  Nav link not found — may already be correct")
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(hsrc)
    except FileNotFoundError:
        print("⚠️  index.html not found")

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py templates/index.html")
    print('   git commit -m "add eBay CSV export endpoint"')
    print("   git push")

if __name__ == "__main__":
    main()
