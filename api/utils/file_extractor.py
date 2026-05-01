import fitz  # PyMuPDF
import docx
from fastapi import UploadFile
import io

async def extract_text_from_file(file: UploadFile) -> str:
    """Detects file type and extracts text content."""
    filename = file.filename.lower()
    content = await file.read()
    text = ""

    try:
        if filename.endswith(".pdf"):
            # Use PyMuPDF for PDF extraction
            with fitz.open(stream=content, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        
        elif filename.endswith(".docx"):
            # Use python-docx for Word files
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([para.text for para in doc.paragraphs])
        
        elif filename.endswith(".txt"):
            text = content.decode("utf-8")
            
        else:
            return "Unsupported file format. Please upload PDF or DOCX."

    except Exception as e:
        return f"Error extracting text: {str(e)}"
    
    return text.strip()