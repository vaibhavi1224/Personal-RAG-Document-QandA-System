from typing import List, Dict, Any

class TextChunker:
    """Handles text chunking with overlap"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source: str = "") -> List[Dict[str, Any]]:
        chunks = []
        sentences = text.replace('\n', ' ').split('. ')
        current_chunk = ""
        chunk_idx = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'source': source,
                    'chunk_id': f"{source}_{chunk_idx}",
                    'chunk_index': chunk_idx
                })
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                chunk_idx += 1
            else:
                current_chunk += " " + sentence

        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'source': source,
                'chunk_id': f"{source}_{chunk_idx}",
                'chunk_index': chunk_idx
            })

        return chunks
