import streamlit as st

from agent import answer_query


# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(
    page_title="Internal Research Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Internal Research Agent")

st.markdown(
    """
Ask questions related to:

- 📄 HR Policies
- 🏥 Insurance Documents
- 🌐 Industry Trends & Regulations
"""
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask your question...")

if prompt:

    # Display user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_query(prompt)

            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )