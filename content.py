from config import model
def content_generation_node(state):
    prompt = f"""Generate professional content following this outline:

    {state.approved_outline}

    Requirements:
    1. Follow outline structure exactly
    2. Professional and engaging tone
    3. Include relevant examples
    4. Clear transitions between sections
    5. Proper formatting with headers
    6. 800-1200 words total"""
    
    try:
        response = model.generate_content(prompt)
        return {"content": response.text}
    except Exception as e:
        return {"content": f"Content Generation Error: {str(e)}"}