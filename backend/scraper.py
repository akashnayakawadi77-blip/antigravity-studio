from duckduckgo_search import DDGS

def get_travel_info(destination: str) -> str:
    """
    Fetches real-time travel logistics using DuckDuckGo search.
    It scrapes info about flights, hotel tiers, and seasons.
    """
    ddgs = DDGS()
    
    # We will do a few targeted searches
    queries = [
        f"{destination} best time to visit weather season",
        f"how to get to {destination} flights trains transport",
        f"best areas to stay in {destination} budget hostels mid-range luxury hotels"
    ]
    
    results = []
    
    for query in queries:
        try:
            # Using text search (generator)
            search_results = ddgs.text(query, max_results=3)
            results.append(f"--- Results for: {query} ---")
            for r in search_results:
                results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}")
        except Exception as e:
            results.append(f"Error fetching {query}: {e}")
            
    return "\n\n".join(results)

if __name__ == "__main__":
    print(get_travel_info("Goa"))
