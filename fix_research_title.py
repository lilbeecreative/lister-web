"""
fix_research_title.py
Run from ~/Desktop/lister_web:
    python3 fix_research_title.py
"""
import sys

MAIN = "main.py"

OLD = '''    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        # Step 1: identify exact model from image
        identified = identify_item_from_image(images, title)
        if identified != title:
            print(f"Lot {lot} image ID: {identified}")

        prompt = f"""You are an expert resale market researcher and appraiser. Research this auction item thoroughly.

Item: Lot #{lot} — {title}
Image-identified model: {identified}
Current estimate: ${current_val}'''

NEW = '''    def clean_title(raw_title):
        """Strip address fragments, company boilerplate, and catalog noise from auction titles."""
        import re
        t = raw_title
        # Remove street addresses like "Siemensstrasse 7", "123 Main St"
        t = re.sub(r'\b\d+\s+[A-Z][a-z]+(?:strasse|street|ave|blvd|rd|st|dr|ln|way)\b', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\b[A-Z][a-z]+(?:strasse|gasse|platz|weg)\s+\d+\b', '', t, flags=re.IGNORECASE)
        # Remove "GmbH", "Inc", "LLC", "Ltd", "Corp", "Co." standalone
        t = re.sub(r'\b(?:GmbH|Inc\.?|LLC|Ltd\.?|Corp\.?|Co\.)\b', '', t)
        # Remove loading fee notes
        t = re.sub(r'Loading Fee[:\s]*\$?\d+', '', t, flags=re.IGNORECASE)
        # Remove QTY annotations for search purposes
        t = re.sub(r'\s*,?\s*QTY\s*\(?\d*\)?', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\s*\(\d+\)\s*$', '', t)
        # Collapse extra whitespace
        t = ' '.join(t.split()).strip().strip(',').strip()
        return t

    def research_item(item, images):
        title = item.get("title", "")
        lot = item.get("lot", "")
        current_val = item.get("your_value", 0) or 0

        # Clean title before research — remove address/company junk
        clean = clean_title(title)
        if clean != title:
            print(f"Lot {lot} title cleaned: '{title}' → '{clean}'")

        # Step 1: identify exact model from image
        identified = identify_item_from_image(images, clean)
        if identified != clean:
            print(f"Lot {lot} image ID: {identified}")

        prompt = f"""You are an expert resale market researcher and appraiser. Research this auction item thoroughly.

Item: Lot #{lot} — {clean}
Image-identified model: {identified}
Current estimate: ${current_val}

IMPORTANT — SEARCH TERM CONSTRUCTION:
Before searching, extract just the brand name and model number from the item title.
Strip out: company addresses, "GmbH", "Inc", street names, loading fees, lot numbers, and any other non-product text.
Example: "IPG Laser #YLR-400-SM-EOS IPG Laser GmbH Siemensstrasse 7" → search "IPG YLR-400-SM-EOS fiber laser"
Use the cleanest possible search term to find accurate comps.'''

def main():
    try:
        with open(MAIN, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"❌ {MAIN} not found")
        sys.exit(1)

    if OLD in src:
        src = src.replace(OLD, NEW, 1)
        print("✅ Patched title cleaning + search term construction")
    else:
        print("❌ Block not found")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py")
    print('   git commit -m "clean auction titles before deep research, strip address junk"')
    print("   git push")

if __name__ == "__main__":
    main()
