content = open('main.py').read()

old = '''        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash")'''

new = '''        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        for model_name in ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                break
            except Exception:
                continue'''

if old in content:
    content = content.replace(old, new)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
