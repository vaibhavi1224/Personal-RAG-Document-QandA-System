from datetime import datetime
from .document_processor import DocumentProcessor
from .text_chunker import TextChunker
from .vector_store import VectorStore
from .llm_interface import LLMInterface

class RAGSystem:
    """Main RAG system orchestrator"""

    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.chunker = TextChunker()
        self.vector_store = VectorStore()
        self.conversation_history = []

    def add_document(self, file_path: str, file_name: str = None) -> bool:
        try:
            text = self.doc_processor.load_document(file_path)
            source = file_name or file_path
            chunks = self.chunker.chunk_text(text, source)
            self.vector_store.add_documents(chunks)
            return True
        except Exception as e:
            return False

    def query(self, question: str, use_llm: bool = True, llm_config: dict = None) -> dict:
        relevant = self.vector_store.search(question, top_k=5)
        if not relevant:
            return {'answer': "No relevant info.", 'sources': [], 'context': ""}

        context = "\n\n".join([f"From {c['source']}:\n{c['text']}" for c in relevant])
        if use_llm and llm_config:
            prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer comprehensively."
            if llm_config['provider'] == 'openai':
                answer = LLMInterface.call_openai(prompt, llm_config['api_key'], llm_config.get('model'))
            elif llm_config['provider'] == 'ollama':
                answer = LLMInterface.call_ollama(prompt, llm_config.get('model'), llm_config.get('base_url'))
            else:
                answer = LLMInterface.generate_simple_response(question, context)
        else:
            answer = LLMInterface.generate_simple_response(question, context)

        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'sources': [c['source'] for c in relevant],
            'num_chunks': len(relevant)
        })

        return {
            'answer': answer,
            'sources': list(set(c['source'] for c in relevant)),
            'context': context,
            'chunks': relevant
        }

    def get_stats(self):
        stats = self.vector_store.get_stats()
        stats['conversations'] = len(self.conversation_history)
        return stats
