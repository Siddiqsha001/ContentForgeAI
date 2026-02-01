from config import model

def outline_node(state):
    base_prompt = f"""Create a detailed outline based on this research topic:
    
    Topic: {state.input}
    
    Requirements:
    1. Introduction section
    2. 3-5 main sections with subsections
    3. Conclusion section
    
    Format: Use proper outline formatting with numbers and letters
    (1., A., i., etc.)"""
    
    if hasattr(state, 'change_request') and state.change_request:
        prompt = f"{base_prompt}\n\nChange Request: {state.change_request}\n\nPlease revise the outline accordingly."
    else:
        prompt = base_prompt
    
    try:
        response = model.generate_content(prompt)
        return {"outline": response.text}
    except Exception as e:
        return {"outline": f"Outline Error: {str(e)}"}