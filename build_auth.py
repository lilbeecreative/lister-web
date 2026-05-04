"""
build_auth.py
Run from ~/Desktop/lister_web:
    python3 build_auth.py

Adds session-based auth with business_id to lister-web.
"""
import os

# ── 1. Create login.html template ──────────────────────────────
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login — Lister AI</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0a0c10; color:#f1f5f9; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; min-height:100vh; display:flex; align-items:center; justify-content:center; }
  .card { background:#111318; border:1px solid #1e2330; border-radius:16px; padding:40px; width:100%; max-width:400px; }
  .logo { text-align:center; margin-bottom:32px; }
  .logo img { width:56px; height:56px; border-radius:50%; }
  .logo h1 { font-size:22px; font-weight:800; margin-top:12px; }
  .logo p { color:#64748b; font-size:13px; margin-top:4px; }
  .field { margin-bottom:16px; }
  .field label { display:block; font-size:12px; color:#64748b; font-weight:600; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.05em; }
  .field input { width:100%; background:#0f1117; border:1px solid #1e2330; border-radius:8px; padding:12px 14px; color:#f1f5f9; font-size:14px; outline:none; transition:border-color 0.2s; }
  .field input:focus { border-color:#22c55e; }
  .btn { width:100%; background:#22c55e; border:none; border-radius:8px; padding:13px; color:#000; font-size:15px; font-weight:700; cursor:pointer; margin-top:8px; transition:background 0.2s; }
  .btn:hover { background:#16a34a; }
  .error { background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:8px; padding:12px; color:#ef4444; font-size:13px; margin-bottom:16px; }
  .link { text-align:center; margin-top:20px; font-size:13px; color:#64748b; }
  .link a { color:#22c55e; text-decoration:none; }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <img src="/static/favicon.png" alt="Logo">
    <h1>Lister AI</h1>
    <p>Sign in to your account</p>
  </div>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <div class="field"><label>Email</label><input type="email" name="email" required autofocus></div>
    <div class="field"><label>Password</label><input type="password" name="password" required></div>
    <button class="btn" type="submit">Sign In</button>
  </form>
  <div class="link">Don\'t have an account? <a href="/register">Register</a></div>
</div>
</body>
</html>'''

# ── 2. Create register.html template ───────────────────────────
REGISTER_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Register — Lister AI</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0a0c10; color:#f1f5f9; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; min-height:100vh; display:flex; align-items:center; justify-content:center; }
  .card { background:#111318; border:1px solid #1e2330; border-radius:16px; padding:40px; width:100%; max-width:400px; }
  .logo { text-align:center; margin-bottom:32px; }
  .logo img { width:56px; height:56px; border-radius:50%; }
  .logo h1 { font-size:22px; font-weight:800; margin-top:12px; }
  .logo p { color:#64748b; font-size:13px; margin-top:4px; }
  .field { margin-bottom:16px; }
  .field label { display:block; font-size:12px; color:#64748b; font-weight:600; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.05em; }
  .field input { width:100%; background:#0f1117; border:1px solid #1e2330; border-radius:8px; padding:12px 14px; color:#f1f5f9; font-size:14px; outline:none; transition:border-color 0.2s; }
  .field input:focus { border-color:#22c55e; }
  .btn { width:100%; background:#22c55e; border:none; border-radius:8px; padding:13px; color:#000; font-size:15px; font-weight:700; cursor:pointer; margin-top:8px; transition:background 0.2s; }
  .btn:hover { background:#16a34a; }
  .error { background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:8px; padding:12px; color:#ef4444; font-size:13px; margin-bottom:16px; }
  .link { text-align:center; margin-top:20px; font-size:13px; color:#64748b; }
  .link a { color:#22c55e; text-decoration:none; }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <img src="/static/favicon.png" alt="Logo">
    <h1>Create Account</h1>
    <p>Start using Lister AI for your business</p>
  </div>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST" action="/register">
    <div class="field"><label>Business Name</label><input type="text" name="business_name" required autofocus></div>
    <div class="field"><label>Email</label><input type="email" name="email" required></div>
    <div class="field"><label>Password</label><input type="password" name="password" required minlength="8"></div>
    <button class="btn" type="submit">Create Account</button>
  </form>
  <div class="link">Already have an account? <a href="/login">Sign in</a></div>
</div>
</body>
</html>'''

# ── 3. Auth routes to add to main.py ───────────────────────────
AUTH_ROUTES = '''
import hashlib, secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(":")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False

def get_business_id(request: Request):
    """Get business_id from session cookie."""
    session = request.cookies.get("session_id")
    if not session:
        return None
    try:
        res = supabase.table("sessions").select("business_id").eq("token", session).execute()
        if res.data:
            return res.data[0]["business_id"]
    except Exception:
        pass
    return None

@app.get("/login")
async def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login_submit(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))
    try:
        res = supabase.table("businesses").select("id,password_hash").eq("email", email).execute()
        if not res.data:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})
        biz = res.data[0]
        if not verify_password(password, biz["password_hash"]):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})
        token = secrets.token_hex(32)
        supabase.table("sessions").insert({"token": token, "business_id": biz["id"]}).execute()
        from fastapi.responses import RedirectResponse
        resp = RedirectResponse("/", status_code=302)
        resp.set_cookie("session_id", token, httponly=True, max_age=60*60*24*30)
        return resp
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": f"Login failed: {e}"})

@app.get("/register")
async def register_page(request: Request, error: str = ""):
    return templates.TemplateResponse("register.html", {"request": request, "error": error})

@app.post("/register")
async def register_submit(request: Request):
    form = await request.form()
    business_name = str(form.get("business_name", "")).strip()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))
    if not business_name or not email or not password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "All fields required"})
    if len(password) < 8:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Password must be at least 8 characters"})
    try:
        existing = supabase.table("businesses").select("id").eq("email", email).execute()
        if existing.data:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered"})
        password_hash = hash_password(password)
        res = supabase.table("businesses").insert({
            "name": business_name,
            "email": email,
            "password_hash": password_hash
        }).execute()
        business_id = res.data[0]["id"]
        token = secrets.token_hex(32)
        supabase.table("sessions").insert({"token": token, "business_id": business_id}).execute()
        from fastapi.responses import RedirectResponse
        resp = RedirectResponse("/", status_code=302)
        resp.set_cookie("session_id", token, httponly=True, max_age=60*60*24*30)
        return resp
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": f"Registration failed: {e}"})

@app.get("/logout")
async def logout(request: Request):
    from fastapi.responses import RedirectResponse
    token = request.cookies.get("session_id")
    if token:
        try:
            supabase.table("sessions").delete().eq("token", token).execute()
        except Exception:
            pass
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("session_id")
    return resp

'''

def main():
    # Write templates
    with open("templates/login.html", "w") as f:
        f.write(LOGIN_HTML)
    print("✅ Created templates/login.html")

    with open("templates/register.html", "w") as f:
        f.write(REGISTER_HTML)
    print("✅ Created templates/register.html")

    # Add auth routes to main.py
    src = open("main.py").read()
    anchor = '@app.get("/login")'
    if anchor in src:
        print("⚠️  Auth routes already exist in main.py")
    else:
        # Insert before the first @app.get("/")
        insert_at = src.find('@app.get("/")')
        if insert_at == -1:
            insert_at = src.find('@app.get("/portal")')
        src = src[:insert_at] + AUTH_ROUTES + src[insert_at:]
        with open("main.py", "w") as f:
            f.write(src)
        print("✅ Added auth routes to main.py")

    print("\nNow run the SQL to add sessions table and password_hash column, then commit.")

if __name__ == "__main__":
    main()
