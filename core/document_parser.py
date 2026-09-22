"""
Document Parser Module for Banking Statements & Customer Verification Files.
Supports parsing plain text, raw logs, JSON, and PDF documents.
"""

from pathlib import Path
from typing import Dict, Any, Union
import json
import re


class DocumentParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Loads and parses a document file, returning structured raw content.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found at: {path}")

        suffix = path.suffix.lower()

        if suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"file_name": path.name, "type": "JSON", "raw_data": data, "text_content": json.dumps(data, indent=2)}

        elif suffix in [".txt", ".log", ".csv"]:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"file_name": path.name, "type": "TEXT", "raw_data": None, "text_content": content}

        elif suffix == ".pdf":
            try:
                import pdfplumber
                extracted_text = []
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text.append(text)
                combined = "\n".join(extracted_text)
                return {"file_name": path.name, "type": "PDF", "raw_data": None, "text_content": combined}
            except Exception as e:
                # Fallback if pdfplumber is not installed or file is binary
                return {"file_name": path.name, "type": "PDF_ERROR", "raw_data": None, "text_content": f"Error parsing PDF: {str(e)}"}

        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {"file_name": path.name, "type": "GENERIC", "raw_data": None, "text_content": content}


document_parser = DocumentParser()
