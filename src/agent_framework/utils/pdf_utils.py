"""PDF utilities for processing PDF files."""

import logging
import io
from typing import Dict, Any, List
import PyPDF2
import fitz  # PyMuPDF for better PDF handling

logger = logging.getLogger(__name__)


class PdfUtils:
    """Utilities for PDF processing operations."""
    
    def __init__(self):
        """Initialize PDF utilities."""
        pass
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF bytes."""
        if not pdf_bytes:
            return {"error": "PDF bytes are required"}
        
        try:
            text_content = self._extract_text_from_pdf_bytes(pdf_bytes)
            
            return {
                "extracted_text": text_content,
                "text_length": len(text_content),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return {"error": str(e)}
    
    def get_pdf_info(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Get information about a PDF file."""
        if not pdf_bytes:
            return {"error": "PDF bytes are required"}
        
        try:
            # Try PyMuPDF first for better metadata
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            info = {
                "page_count": pdf_document.page_count,
                "metadata": pdf_document.metadata,
                "status": "success"
            }
            
            pdf_document.close()
            return info
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                
                return {
                    "page_count": len(pdf_reader.pages),
                    "metadata": pdf_reader.metadata,
                    "status": "success"
                }
                
            except Exception as e2:
                logger.error(f"Both PDF libraries failed: {e2}")
                return {"error": f"Error getting PDF info: {str(e2)}"}
    
    def search_text_in_pdf(self, pdf_bytes: bytes, search_text: str) -> Dict[str, Any]:
        """Search for text within a PDF."""
        if not pdf_bytes or not search_text:
            return {"error": "PDF bytes and search_text are required"}
        
        try:
            # Extract text first
            text_content = self._extract_text_from_pdf_bytes(pdf_bytes)
            
            # Search for the text
            search_lower = search_text.lower()
            text_lower = text_content.lower()
            
            matches = text_lower.count(search_lower)
            found = search_lower in text_lower
            
            result = {
                "search_text": search_text,
                "found": found,
                "match_count": matches,
                "status": "success"
            }
            
            if found:
                result["preview"] = self._get_text_preview(text_content, search_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching PDF text: {e}")
            return {"error": str(e)}
    
    def extract_pages(self, pdf_bytes: bytes, page_numbers: List[int] = None) -> Dict[str, Any]:
        """Extract specific pages from a PDF."""
        if not pdf_bytes:
            return {"error": "PDF bytes are required"}
        
        try:
            # Try PyMuPDF first
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            if page_numbers is None:
                # Extract all pages
                page_numbers = list(range(pdf_document.page_count))
            
            extracted_pages = []
            for page_num in page_numbers:
                if 0 <= page_num < pdf_document.page_count:
                    page = pdf_document[page_num]
                    page_text = page.get_text()
                    extracted_pages.append({
                        "page_number": page_num,
                        "text": page_text,
                        "text_length": len(page_text)
                    })
            
            pdf_document.close()
            
            return {
                "extracted_pages": extracted_pages,
                "page_count": len(extracted_pages),
                "status": "success"
            }
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                
                if page_numbers is None:
                    page_numbers = list(range(len(pdf_reader.pages)))
                
                extracted_pages = []
                for page_num in page_numbers:
                    if 0 <= page_num < len(pdf_reader.pages):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        extracted_pages.append({
                            "page_number": page_num,
                            "text": page_text,
                            "text_length": len(page_text)
                        })
                
                return {
                    "extracted_pages": extracted_pages,
                    "page_count": len(extracted_pages),
                    "status": "success"
                }
                
            except Exception as e2:
                logger.error(f"Both PDF libraries failed: {e2}")
                return {"error": f"Error extracting pages: {str(e2)}"}
    
    def get_page_count(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Get the number of pages in a PDF."""
        if not pdf_bytes:
            return {"error": "PDF bytes are required"}
        
        try:
            # Try PyMuPDF first
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = pdf_document.page_count
            pdf_document.close()
            
            return {
                "page_count": page_count,
                "status": "success"
            }
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                page_count = len(pdf_reader.pages)
                
                return {
                    "page_count": page_count,
                    "status": "success"
                }
                
            except Exception as e2:
                logger.error(f"Both PDF libraries failed: {e2}")
                return {"error": f"Error getting page count: {str(e2)}"}
    
    def _extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes using PyMuPDF."""
        try:
            # Try PyMuPDF first (better for complex PDFs)
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            text_content = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text_content += page.get_text()
            
            pdf_document.close()
            return text_content.strip()
            
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                text_content = ""
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
                
                return text_content.strip()
                
            except Exception as e2:
                logger.error(f"Both PDF libraries failed: {e2}")
                return f"Error extracting text from PDF: {str(e2)}"
    
    def _get_text_preview(self, text: str, search_text: str, context_length: int = 100) -> str:
        """Get a preview of text around the search term."""
        search_lower = search_text.lower()
        text_lower = text.lower()
        
        index = text_lower.find(search_lower)
        if index == -1:
            return ""
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(search_text) + context_length)
        
        preview = text[start:end]
        if start > 0:
            preview = "..." + preview
        if end < len(text):
            preview = preview + "..."
        
        return preview
