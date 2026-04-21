content = open('main.py').read()

# Add /auction/research route
old = '@app.get("/auction", response_class=HTMLResponse)'
new = '''@app.get("/auction/research", response_class=HTMLResponse)
async def auction_research_page(request: Request):
    import os
    with open(os.path.join(os.path.dirname(__file__), "templates", "auction_research.html")) as f:
        html = f.read()
    return HTMLResponse(content=html, headers={
        "Content-Security-Policy": "default-src * blob: data:; script-src * blob: data: 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * blob: data:;"
    })

@app.get("/auction", response_class=HTMLResponse)'''

if old in content:
    content = content.replace(old, new)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
