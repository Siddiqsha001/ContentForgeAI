from concurrent.futures import ThreadPoolExecutor
import logging
from config import model

logger = logging.getLogger(__name__)

def evaluate_component(prompt, component_name):
    """Evaluate a single component with error handling and logging"""
    try:
        response = model.generate_content(prompt)
        score = float(response.text.strip())
        if 0 <= score <= 10:
            logger.info(f"{component_name} score: {score}")
            return score
        else:
            logger.warning(f"Invalid {component_name} score: {score}, defaulting to 5")
            return 5.0
    except Exception as e:
        logger.error(f"Error evaluating {component_name}: {str(e)}")
        return 5.0

def generate_suggestions(scores):
    """Generate specific improvement suggestions based on scores"""
    suggestions = []
    
    if scores['research'] < 7:
        suggestions.append("• Add more depth to research with credible sources")
    if scores['outline'] < 7:
        suggestions.append("• Improve outline structure and organization")
    if scores['content'] < 7:
        suggestions.append("• Enhance writing quality and reader engagement")
        
    return "\n".join(suggestions) if suggestions else "Content meets quality standards!"

def judge_node(state):
    """Evaluate content with detailed scoring and suggestions"""
    prompts = {
        'research': f"""Rate the research quality (0-10):
        Content: {state.content}
        Criteria:
        - Depth of research (3 points)
        - Source credibility (4 points)
        - Information relevance (3 points)
        Return only the numerical score.""",
        
        'outline': f"""Rate the outline structure (0-10):
        Outline: {state.outline}
        Criteria:
        - Logical flow (4 points)
        - Section completeness (3 points)
        - Clarity (3 points)
        Return only the numerical score.""",
        
        'content': f"""Rate the content quality (0-10):
        Content: {state.content}
        Feedback: {state.feedback}
        Criteria:
        - Writing quality (4 points)
        - Coherence (3 points)
        - Engagement (3 points)
        Return only the numerical score."""
    }

    try:
        # Concurrent evaluation with logging
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                key: executor.submit(evaluate_component, prompt, key)
                for key, prompt in prompts.items()
            }
            scores = {key: future.result() for key, future in futures.items()}

        # Calculate weighted final score
        weights = {'research': 0.3, 'outline': 0.3, 'content': 0.4}
        final_score = sum(scores[k] * weights[k] for k in weights) / 10

        # Format detailed scores with letter grades
        def get_grade(score):
            if score >= 9: return "A"
            elif score >= 8: return "B"
            elif score >= 7: return "C"
            elif score >= 6: return "D"
            else: return "F"

        detailed_scores = {
            k: f"{v:.1f}/10 ({get_grade(v)})" 
            for k, v in scores.items()
        }

        return {
            "score": f"{final_score:.2f}",
            "detailed_scores": detailed_scores,
            "improvement_suggestions": generate_suggestions(scores)
        }

    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        return {
            "score": "0.5",
            "detailed_scores": {
                "research": "5.0/10 (C)",
                "outline": "5.0/10 (C)",
                "content": "5.0/10 (C)"
            },
            "improvement_suggestions": "Error during evaluation. Please try again."
        }