"""
add_landing_page.py
Run from ~/Desktop/lister_web:
    python3 add_landing_page.py
"""
import sys

MAIN = "main.py"
ANCHOR = '@app.get("/", response_class=HTMLResponse)'

NEW_ROUTE = '''@app.get("/portal", response_class=HTMLResponse)
async def portal(request: Request):
    import os
    with open(os.path.join(os.path.dirname(__file__), "templates", "portal.html")) as f:
        html = f.read()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src * blob: data:; script-src * blob: data: 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * blob: data:;"
    })


'''

PORTAL_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Precision Industrial — Staff Portal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
html,body{height:100%;background:#0b0c0e;}
body{font-family:"DM Mono",monospace;display:flex;flex-direction:column;min-height:100vh;}
.bar{display:flex;align-items:center;justify-content:space-between;padding:14px 32px;border-bottom:1px solid #141618;}
.bar-logo{font-family:"Syne",sans-serif;font-size:14px;font-weight:800;color:#eee;letter-spacing:.04em;text-transform:uppercase;}
.bar-right{display:flex;align-items:center;gap:20px;}
.bar-clock{font-size:11px;color:#2a2a2a;}
.bar-status{display:flex;align-items:center;gap:6px;font-size:10px;color:#1a4a2a;}
.dot{width:5px;height:5px;border-radius:50%;background:#22c55e;box-shadow:0 0 5px #22c55e80;}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;padding:48px 32px;}
.label{font-size:10px;color:#2a2a2a;letter-spacing:.1em;text-transform:uppercase;margin-bottom:28px;}
.tools{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:800px;}
.tool{display:block;text-decoration:none;border-radius:12px;padding:32px 28px;cursor:pointer;transition:border-color .15s,background .15s;position:relative;}
.tool-a{background:#0f1013;border:1px solid #1a1c20;}
.tool-b{background:#100e08;border:1px solid #1e1900;}
.tool-a:hover{border-color:#2a3040;background:#111316;}
.tool-b:hover{border-color:#EF9F2760;background:#131008;}
.tool-tag{font-size:9px;color:#252525;letter-spacing:.1em;text-transform:uppercase;margin-bottom:16px;}
.tool-name{font-family:"Syne",sans-serif;font-size:28px;font-weight:800;letter-spacing:-.02em;line-height:1.1;}
.tool-a .tool-name{color:#c0c8d8;}
.tool-b .tool-name{color:#EF9F27;}
.tool-arrow{position:absolute;top:28px;right:28px;font-size:16px;color:#1e2228;}
.tool-b .tool-arrow{color:#2a2000;}
.tool-a:hover .tool-arrow{color:#3a4858;}
.tool-b:hover .tool-arrow{color:#EF9F27;}
.foot{padding:14px 32px;border-top:1px solid #111214;display:flex;align-items:center;justify-content:space-between;}
.foot-note{font-size:9px;color:#1a1a1a;letter-spacing:.06em;}
.foot-badge{font-size:9px;color:#1a1a1a;border:1px solid #141618;border-radius:20px;padding:3px 10px;}
</style>
</head>
<body>
<div class="bar">
  <div class="bar-logo">Precision Industrial</div>
  <div class="bar-right">
    <div class="bar-status"><span class="dot"></span>Systems online</div>
    <div class="bar-clock" id="clk"></div>
  </div>
</div>
<div class="main">
  <div class="label">// select a tool to get started</div>
  <div class="tools">
    <a class="tool tool-a" href="/auction">
      <div class="tool-tag">01 — research</div>
      <div class="tool-name">Auction<br>Scanner</div>
      <div class="tool-arrow">↗</div>
    </a>
    <a class="tool tool-b" href="/">
      <div class="tool-tag">02 — listing</div>
      <div class="tool-name">Lister<br>Dashboard</div>
      <div class="tool-arrow">↗</div>
    </a>
  </div>
</div>
<div class="foot">
  <div class="foot-note">internal use only</div>
  <div class="foot-badge">app.reselljunkie.com</div>
</div>
<script>
function tick(){
  document.getElementById('clk').textContent = new Date().toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
}
tick(); setInterval(tick, 1000);
</script>
</body>
</html>'''

def main():
    # Write portal.html
    with open("templates/portal.html", "w") as f:
        f.write(PORTAL_HTML)
    print("✅ Created templates/portal.html")

    # Add route to main.py
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()

    if ANCHOR in src:
        src = src.replace(ANCHOR, NEW_ROUTE + ANCHOR, 1)
        print("✅ Added /portal route to main.py")
    else:
        print("❌ Anchor not found in main.py")

    with open(MAIN, "w", encoding="utf-8") as f:
        f.write(src)

    print("\nNow run:")
    print("   python3 -c \"import py_compile; py_compile.compile('main.py'); print('OK')\"")
    print("   git add main.py templates/portal.html")
    print('   git commit -m "add /portal landing page"')
    print("   git push")

if __name__ == "__main__":
    main()
