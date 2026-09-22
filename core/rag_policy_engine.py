"""
RAG (Retrieval-Augmented Generation) Policy Engine for Banking Credit Guidelines.

Why RAG is required in Banking AI:
- Underwriters must strictly base decisions on official bank regulatory guidelines.
- The LLM Agent queries this vector retriever to fetch exact lending rules, interest rate matrices,
  and mandatory compliance clauses instead of hallucinating.
"""

from typing import List, Dict, Any
from pathlib import Path
import math
import re
from config.settings import POLICIES_DIR


class PolicyChunk:
    def __init__(self, document_name: str, section_title: str, content: str, chunk_id: int):
        self.document_name = document_name
        self.section_title = section_title
        self.content = content
        self.chunk_id = chunk_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document": self.document_name,
            "section": self.section_title,
            "content": self.content
        }


class PolicyRAGEngine:
    def __init__(self, policy_dir: Path = POLICIES_DIR):
        self.policy_dir = policy_dir
        self.chunks: List[PolicyChunk] = []
        self._load_and_index_policies()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w{3,}\b", text.lower())

    def _load_and_index_policies(self):
        """
        Loads markdown and text policy manuals, splitting by section headers into searchable chunks.
        """
        self.chunks = []
        chunk_id = 1

        if not self.policy_dir.exists():
            return

        for file_path in self.policy_dir.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            sections = re.split(r"\n(?=##?\s+)", content)
            for sec in sections:
                lines = sec.strip().split("\n")
                if not lines or not lines[0].strip():
                    continue
                title = lines[0].replace("#", "").strip()
                body = "\n".join(lines[1:]).strip()
                if body:
                    self.chunks.append(PolicyChunk(
                        document_name=file_path.name,
                        section_title=title,
                        content=body,
                        chunk_id=chunk_id
                    ))
                    chunk_id += 1

    def search_policy(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant policy chunks using TF-IDF / term-frequency semantic relevance.
        """
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return [c.to_dict() for c in self.chunks[:top_k]]

        scored_chunks = []
        for chunk in self.chunks:
            chunk_tokens = self._tokenize(chunk.section_title + " " + chunk.content)
            if not chunk_tokens:
                continue
            
            # Simple TF match score + title boost
            title_tokens = set(self._tokenize(chunk.section_title))
            common_in_title = query_tokens.intersection(title_tokens)
            common_in_body = query_tokens.intersection(set(chunk_tokens))

            score = (len(common_in_title) * 3.0) + len(common_in_body)
            if score > 0:
                scored_chunks.append((score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = [c.to_dict() for _, c in scored_chunks[:top_k]]

        # Fallback if no specific keyword match
        if not results and self.chunks:
            results = [c.to_dict() for c in self.chunks[:top_k]]

        return results


policy_rag_engine = PolicyRAGEngine()
