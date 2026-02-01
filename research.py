from config import model, search_serper

def research_node(state):
    # First get search results
    search_results = search_serper(state.input)
    
    # Format search results
    formatted_results = "Search Results:\n\n"
    
    if "organic" in search_results:
        for idx, result in enumerate(search_results["organic"][:5], 1):
            formatted_results += f"{idx}. {result.get('title', 'No title')}\n"
            formatted_results += f"   {result.get('snippet', 'No snippet')}\n\n"

    prompt = f"""Based on these search results, provide a comprehensive research summary:

    Topic: {state.input}
    
    {formatted_results}
    
    Provide:
    1. Key findings and main concepts
    2. Important facts from reliable sources
    3. Current trends and developments
    4. Expert insights if available
    
    Format as clear, well-organized paragraphs.
    """
    
    try:
        response = model.generate_content(prompt)
        return {"research": response.text}
    except Exception as e:
        return {"research": f"Research Error: {str(e)}"}