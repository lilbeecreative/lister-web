content = open('main.py').read()

old_parse = '''        response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})
        raw = response.text.strip()
        # Strip markdown fences
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        # Find JSON object boundaries
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        return json.loads(raw)'''

new_parse = '''        response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})
        raw = response.text.strip()
        print(f"   Deep research raw response (lot {lot}): {raw[:300]}")
        # Strip markdown fences
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        # Find JSON object boundaries
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        data = json.loads(raw)
        # Sanitize string fields to prevent SSE encoding issues
        for key in ["image_notes", "rec_reason", "notes", "confidence", "recommendation"]:
            if key in data:
                data[key] = str(data[key]).replace("\\n", " ").replace("\\r", " ")
        if "comps" in data:
            for comp in data["comps"]:
                for k in comp:
                    comp[k] = str(comp[k]).replace("\\n", " ") if isinstance(comp[k], str) else comp[k]
        return data'''

if old_parse in content:
    content = content.replace(old_parse, new_parse)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
