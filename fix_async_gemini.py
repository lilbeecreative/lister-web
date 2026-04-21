content = open('main.py').read()

old = '''    async def generate():
        total_chunks = len(page_chunks)
        all_items = []
        for i, chunk_text in enumerate(page_chunks):
            try:
                response = model.generate_content(
                    [prompt_template, f"\\nCATALOG SECTION {i+1}/{total_chunks}:\\n{chunk_text[:10000]}"],
                    generation_config={"max_output_tokens": 8192}
                )'''

new = '''    async def generate():
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)

        def call_gemini(chunk_text, i):
            return model.generate_content(
                [prompt_template, f"\\nCATALOG SECTION {i+1}/{total_chunks}:\\n{chunk_text[:10000]}"],
                generation_config={"max_output_tokens": 8192}
            )

        total_chunks = len(page_chunks)
        all_items = []
        for i, chunk_text in enumerate(page_chunks):
            try:
                response = await loop.run_in_executor(executor, call_gemini, chunk_text, i)'''

if old in content:
    content = content.replace(old, new)
    open('main.py', 'w').write(content)
    print('done')
else:
    print('not found')
