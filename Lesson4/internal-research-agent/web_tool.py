from langchain_core.tools import tool

try:
    from langchain_tavily import TavilySearch
except ImportError:  # Backward compatibility with older installs
    from langchain_community.tools.tavily_search import TavilySearchResults

    def _build_search_tool():
        return TavilySearchResults(max_results=3)
else:
    def _build_search_tool():
        return TavilySearch(max_results=3)

@tool
def web_search(query: str):
    """
    Search the web for current information.
    """

    search = _build_search_tool()
    results = search.invoke(query)

    return results
if __name__ == "__main__":
    question = input("Search: ")

    results = web_search.invoke({"query": question})

    print(results)