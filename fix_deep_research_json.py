content = open('main.py').read()

old = '''        result = await loop.run_in_executor(executor, research_item, item, images)
                yield {"data": json.dumps({
                    "type": "result",
                    "lot": item.get("lot"),
                    "index": i,
                    "total": total,
                    "has_image": len(images) > 0,
                    **result
                })}
            except Exception as e:
                print(f"Deep research error for lot {item.get('lot')}: {e}")
                yield {"data": json.dumps({
                    "type": "error",
                    "lot": item.get("lot"),
                    "index": i,
                    "total": total,
                    "error": str(e)
                })}'''

new = '''        result = await loop.run_in_executor(executor, research_item, item, images)
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
                })}'''

if old in content:
    content = content.replace(old, new)
    print('✅ error handling updated')
else:
    print('❌ not found')

# Also make the research_item function more robust
old_parse = '''        response = model.generate_content(parts, generation_config={"max_output_tokens": 1000})
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)'''

new_parse = '''        response = model.generate_content(parts, generation_config={"max_output_tokens": 1500})
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

if old_parse in content:
    content = content.replace(old_parse, new_parse)
    print('✅ JSON parsing made more robust')
else:
    print('❌ parse not found')

open('main.py', 'w').write(content)
