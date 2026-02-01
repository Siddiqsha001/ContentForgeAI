from langgraph.graph import StateGraph
from state import WorkflowState
from research import research_node
from outline import outline_node
from content import content_generation_node
from judge import judge_node
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize concurrent executor
executor = ThreadPoolExecutor(max_workers=3)

# Initialize workflow
workflow = StateGraph(WorkflowState)

# Add nodes with concurrent wrapper
def make_concurrent(func):
    def wrapper(state):
        future = executor.submit(func, state)
        return future.result()
    return wrapper

# Add nodes with concurrent execution
workflow.add_node("research_node", make_concurrent(research_node))
workflow.add_node("outline_node", make_concurrent(outline_node))
workflow.add_node("content_node", make_concurrent(content_generation_node))
workflow.add_node("judge", make_concurrent(judge_node))

# Set workflow
workflow.set_entry_point("research_node")
workflow.add_edge("research_node", "outline_node")
workflow.add_edge("outline_node", "content_node")
workflow.add_edge("content_node", "judge")

# Compile graph with optimized settings
graph = workflow.compile()

# Cleanup executor on exit
import atexit
atexit.register(lambda: executor.shutdown(wait=True))