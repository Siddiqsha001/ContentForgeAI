import streamlit as st
from app import graph
from state import WorkflowState
from outline import outline_node
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="Content Agent", layout="centered")
st.title("💬 Content Creation Agent")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "state" not in st.session_state:
    st.session_state.state = WorkflowState(input="", step=0)
if "outline_shown" not in st.session_state:
    st.session_state.outline_shown = False
if "content_shown" not in st.session_state:
    st.session_state.content_shown = False

# Helper to update chat and history
def update_chat(message, role="assistant"):
    st.chat_message(role).markdown(message)
    st.session_state.chat_history.append({"role": role, "content": message})

# Process state transitions
def process_state(state, user_input, result):
    try:
        logger.info(f"Processing state step {state.step} with result keys: {result.keys()}")

        if state.step == 0:
            if result.get("outline"):
                outline_msg = (
                    f"🧠 **Proposed Outline for '{user_input}':**\n\n"
                    f"```\n{result['outline']}\n```\n\n"
                    f"👉 _Type 'yes' or 'continue' to generate content based on this outline._"
                )
                update_chat(outline_msg)
                state.outline = result["outline"]
                state.step = 1
                logger.info("Outline generated")
            else:
                update_chat("❌ Failed to generate outline. Please try again.")

        elif state.step == 1:
            if result.get("content"):
                content_msg = f"📝 **Generated Content:**\n\n{result['content']}\n\n✍️ _Please provide your feedback._"
                update_chat(content_msg)
                state.content = result["content"]
                state.step = 2
                logger.info("Content generated")

        elif state.step == 2:
            if result.get("score"):
                score = float(result["score"]) * 100
                detailed_scores = result.get("detailed_scores", {})
                suggestions = result.get("improvement_suggestions", "")
                score_msg = (
                    f"📊 **Content Score: {score:.1f}%**\n\n"
                    f"**Detailed Scores:**\n"
                    + "\n".join([f"- {k}: {v}" for k, v in detailed_scores.items()])
                    + f"\n\n**Suggestions for Improvement:**\n{suggestions}\n\n"
                    f"_Thank you for your feedback!_"
                )
                update_chat(score_msg)
                state.score = score
                state.evaluated = True
                state.step = 3
                logger.info("Evaluation completed")

        return state

    except Exception as e:
        logger.error(f"Error in process_state: {str(e)}", exc_info=True)
        update_chat(f"❌ Processing Error: {str(e)}")
        return state

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input block
user_input = st.chat_input("Type your topic or message...")

if user_input:
    update_chat(user_input, role="user")
    state = st.session_state.state

    with st.spinner('Processing your request...'):
        try:
            # 💡 Fix: Set input BEFORE invoking the graph
            if state.step == 0:
                state.input = user_input
                logger.info(f"Received topic: {state.input}")

            if state.step == 1:
                if any(x in user_input.strip().lower() for x in ["yes", "proceed", "ok", "sure", "generate", "continue"]):
                    state.approved_outline = state.outline
                    logger.info("Outline approved")
                else:
                    # change request
                    state.change_request = user_input
                    logger.info(f"Change request: {user_input}")
                    # regenerate outline
                    result = outline_node(state)
                    if result.get("outline"):
                        outline_msg = (
                            f"🧠 **Revised Outline for '{state.input}':**\n\n"
                            f"```\n{result['outline']}\n```\n\n"
                            f"👉 _Type 'yes' or 'continue' to generate content, or provide another change request._"
                        )
                        update_chat(outline_msg)
                        state.outline = result["outline"]
                        state.change_request = None  # reset
                        st.session_state.state = state
                        st.rerun()  # to update the display
                    else:
                        update_chat("❌ Failed to revise outline.")
                    st.stop()  # don't proceed to graph invoke

            if state.step == 2:
                state.feedback = user_input
                logger.info(f"Feedback: {user_input[:100]}...")

            # 🧠 Invoke LangGraph agent
            logger.info(f"Calling graph at step {state.step}")
            result = graph.invoke(state)
            logger.info(f"Graph returned: {result.keys()}")

            # Error handling
            if not result:
                update_chat("❌ Received empty response from API")
                st.error("No response from agent.")
            elif "error" in result:
                update_chat(f"❌ Error: {result['error']}")
                st.error(result["error"])
            else:
                state = process_state(state, user_input, result)

        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            update_chat(f"❌ System Error: {str(e)}")
            st.error(f"System error: {str(e)}")

    st.session_state.state = state
