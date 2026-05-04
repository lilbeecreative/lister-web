"""
add_scan_endpoints.py
Run from ~/Desktop/lister_web:
    python3 add_scan_endpoints.py
"""

MAIN = "main.py"
ANCHOR = '@app.get("/api/auction/load-research/{share_id}")'

NEW_ENDPOINTS = '''@app.get("/api/auction/scans")
async def list_scans():
    try:
        res = supabase.table("auction_research_sessions")\
            .select("share_id, title, items, created_at")\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        scans = []
        for row in (res.data or []):
            import json as _j
            items = row.get("items") or []
            if isinstance(items, str):
                try: items = _j.loads(items)
                except: items = []
            scans.append({
                "id": row["share_id"],
                "name": row.get("title", row["share_id"]),
                "items": items,
                "ts": row.get("created_at", "")
            })
        return {"scans": scans}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/auction/scans/{scan_id}")
async def get_scan(scan_id: str):
    try:
        import json as _j
        res = supabase.table("auction_research_sessions")\
            .select("share_id, title, items")\
            .eq("share_id", scan_id)\
            .limit(1)\
            .execute()
        if not res.data:
            raise HTTPException(404, "Scan not found")
        row = res.data[0]
        items = row.get("items") or []
        if isinstance(items, str):
            try: items = _j.loads(items)
            except: items = []
        return {"id": row["share_id"], "name": row.get("title", row["share_id"]), "items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/auction/scans")
async def save_scan(request: Request):
    try:
        import json as _j
        body = await request.json()
        scan_id = body.get("id")
        name = body.get("name", scan_id)
        items = body.get("items", [])
        supabase.table("auction_research_sessions").upsert({
            "share_id": scan_id,
            "title": name,
            "items": items,
        }, on_conflict="share_id").execute()
        return {"ok": True, "id": scan_id}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.delete("/api/auction/scans/{scan_id}")
async def delete_scan(scan_id: str):
    try:
        supabase.table("auction_research_sessions")\
            .delete()\
            .eq("share_id", scan_id)\
            .execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, str(e))

'''

def main():
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()

    if ANCHOR in src:
        src = src.replace(ANCHOR, NEW_ENDPOINTS + ANCHOR, 1)
        print("✅ Added scan list/get/save/delete endpoints")
    else:
        print("❌ Anchor not found")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

if __name__ == "__main__":
    main()
