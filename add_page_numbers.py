content = open('main.py').read()

# Add page range to items returned from each chunk
old_yield = '''                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total_chunks,
                        "items": items,
                        "done": False
                    })
                }'''

new_yield = '''                page_start = i * chunk_size + 1
                page_end = min((i + 1) * chunk_size, total_pages)
                for item in items:
                    item["_page_start"] = page_start
                    item["_page_end"] = page_end
                yield {
                    "data": json.dumps({
                        "chunk": i + 1,
                        "total_chunks": total_chunks,
                        "items": items,
                        "done": False
                    })
                }'''

if old_yield in content:
    content = content.replace(old_yield, new_yield)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
