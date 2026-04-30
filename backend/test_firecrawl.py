from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key="fc-dbc8c360419e4b34bf8147441aa83a19")
res = app.scrape(url="https://en.wikipedia.org/wiki/Artificial_intelligence", formats=['markdown'])
print(type(res))
if hasattr(res, 'markdown'):
    print("Has markdown attr:", len(res.markdown) if res.markdown else "None")
if hasattr(res, 'metadata'):
    print("Has metadata attr:", bool(res.metadata))
    if res.metadata and hasattr(res.metadata, 'title'):
        print("Title:", res.metadata.title)
    elif isinstance(res.metadata, dict):
        print("Title from dict:", res.metadata.get('title'))
elif isinstance(res, dict):
    print("Dict keys:", res.keys())
