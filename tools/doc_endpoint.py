from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from docx import Document
from docx.shared import Inches, Mm, Cm
from docx.enum.section import WD_ORIENT
import pypandoc
from io import BytesIO
import os

docx_router = APIRouter()

@docx_router.get("/health")
async def health_check():
    return {"status": "healthy"}


class DocxRequest(BaseModel):
    page_size: str = "A4"
    orientation: str = "PORTRAIT"
    filename: str = "generated.docx"
    content: str = ""

def generate_docx(data: DocxRequest) -> BytesIO:
    buffer = BytesIO()

    # Create a temporary Markdown file
    temp_md_path = "temp.md"
    with open(temp_md_path, "w", encoding="utf-8") as f:
        f.write(data.content)

    # Convert Markdown to DOCX
    temp_docx_path = "temp.docx"
    try:
        pypandoc.convert_file(
            temp_md_path,
            to="docx",
            outputfile=temp_docx_path,
            extra_args=["--wrap=none"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert Markdown to DOCX: {str(e)}"
        )

    # Load the generated DOCX into memory
    with open(temp_docx_path, "rb") as f:
        buffer.write(f.read())

    # Clean up temporary files
    os.remove(temp_md_path)
    os.remove(temp_docx_path)

    buffer.seek(0)
    return buffer

@docx_router.post("/generate")
async def create_docx(request: DocxRequest):
    try:
        buffer = generate_docx(request)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
