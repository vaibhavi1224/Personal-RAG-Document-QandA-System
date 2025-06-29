import streamlit as st
import os
from rag import RAGSystem

def main():
    st.set_page_config(
        page_title="Personal RAG Q&A",
        page_icon="🧠",
        layout="wide"
    )

    st.markdown(
        """
        <style>
        .big-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #4A90E2;
        }
        .small-note {
            font-size: 0.9rem;
            color: #666;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="big-title">🧠 Personal RAG Document Q&A System</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-note">Upload documents, ask questions, and get intelligent answers.</div>', unsafe_allow_html=True)

    # Initialize
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGSystem()
    rag = st.session_state.rag_system

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        provider = st.radio(
            "LLM Provider",
            ["None (Simple Response)", "OpenAI", "Ollama"],
            index=0,
            help="Choose an LLM provider to generate richer answers."
        )
        llm_config = {}
        if provider.startswith("OpenAI"):
            api_key = st.text_input("🔑 OpenAI API Key", type="password")
            model = st.selectbox("🤖 Model", ["gpt-3.5-turbo", "gpt-4"])
            if api_key:
                llm_config = {"provider": "openai", "api_key": api_key, "model": model}
        elif provider.startswith("Ollama"):
            url = st.text_input("🔗 Ollama Base URL", value="http://localhost:11434")
            model = st.text_input("🦙 Model", value="llama2")
            llm_config = {"provider": "ollama", "base_url": url, "model": model}

        st.divider()
        st.subheader("📊 System Statistics")
        stats = rag.get_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Documents", stats['unique_sources'])
        col2.metric("Chunks", stats['total_chunks'])
        col3.metric("Conversations", stats['conversations'])

    # Tabs for workflow
    tab1, tab2, tab3 = st.tabs(["📄 Document Upload", "❓ Ask Questions", "💬 Conversation History"])

    with tab1:
        st.subheader("📄 Upload Your Documents")
        files = st.file_uploader(
            "Drag & drop or browse files (TXT, PDF, DOCX)",
            type=['txt', 'pdf', 'docx'],
            accept_multiple_files=True
        )

        if files:
            for f in files:
                if st.button(f"Process '{f.name}'", key=f"btn_{f.name}"):
                    temp = f"temp_{f.name}"
                    with open(temp, "wb") as out:
                        out.write(f.getbuffer())
                    with st.spinner(f"Processing '{f.name}'..."):
                        success = rag.add_document(temp, f.name)
                        os.remove(temp)
                    if success:
                        st.success(f"✅ '{f.name}' processed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to process '{f.name}'.")

    with tab2:
        st.subheader("❓ Ask a Question About Your Documents")
        q = st.text_area(
            "Enter your question here",
            placeholder="E.g., What are the main findings? Summarize key points...",
            height=100
        )
        if st.button("🔍 Generate Answer"):
            if not q.strip():
                st.warning("⚠️ Please enter a question.")
            elif stats['total_chunks'] == 0:
                st.warning("⚠️ Please upload documents first.")
            else:
                with st.spinner("Retrieving relevant information and generating answer..."):
                    res = rag.query(
                        q,
                        use_llm=not provider.startswith("None"),
                        llm_config=llm_config if llm_config else None
                    )
                st.success("✅ Answer generated!")
                st.markdown("### 💡 Answer")
                st.write(res['answer'])

                if res['sources']:
                    st.markdown("### 📚 Sources")
                    st.write(", ".join(res['sources']))

                with st.expander("🔍 View Retrieved Context"):
                    for i, c in enumerate(res['chunks']):
                        st.write(f"**Chunk {i+1}** (Score: {c['similarity_score']:.3f}) — {c['source']}")
                        st.write(c['text'])
                        st.divider()

    with tab3:
        st.subheader("💬 Recent Conversation History")
        if rag.conversation_history:
            for conv in reversed(rag.conversation_history[-5:]):
                with st.expander(f"Q: {conv['question']}"):
                    st.write(f"**Answer:** {conv['answer']}")
                    st.write(f"**Sources:** {', '.join(conv['sources'])}")
                    st.caption(f"🕒 {conv['timestamp']}")
        else:
            st.info("No conversations yet. Ask a question to see history here.")

if __name__ == "__main__":
    main()
