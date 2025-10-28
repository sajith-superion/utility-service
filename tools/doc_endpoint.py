from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from docx import Document
from docx.shared import Mm
from docx.enum.section import WD_ORIENT
import pypandoc
from io import BytesIO
import os

docx_router = APIRouter()

@docx_router.get("/health")
async def health_check():
    return {"status": "healthy"}


class DocxRequest(BaseModel):
    page_size: str = "A4"          # Options: A4, Letter, Legal
    orientation: str = "PORTRAIT"  # Options: PORTRAIT, LANDSCAPE
    filename: str = "generated.docx"
    content: str = ""


def get_page_dimensions(size_name: str):
    """Return (width_mm, height_mm) for given page size."""
    size_name = size_name.upper()
    if size_name == "LETTER":
        return (215.9, 279.4)   # 8.5 x 11 inches
    elif size_name == "LEGAL":
        return (215.9, 355.6)   # 8.5 x 14 inches
    else:
        return (210, 297)       # Default A4


def generate_docx(data: DocxRequest) -> BytesIO:
    buffer = BytesIO()
    temp_md_path = "temp.md"
    temp_docx_path = "temp.docx"

    # 1️⃣ Write Markdown to file
    with open(temp_md_path, "w", encoding="utf-8") as f:
        f.write(data.content)

    # 2️⃣ Convert Markdown → DOCX
    try:
        pypandoc.convert_file(
            temp_md_path,
            to="docx",
            outputfile=temp_docx_path,
            extra_args=["--wrap=none"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pandoc conversion failed: {str(e)}")

    # 3️⃣ Open the DOCX and adjust layout
    document = Document(temp_docx_path)
    width_mm, height_mm = get_page_dimensions(data.page_size)

    for section in document.sections:
        if data.orientation.upper() == "LANDSCAPE":
            section.orientation = WD_ORIENT.LANDSCAPE
            section.page_width = Mm(height_mm)
            section.page_height = Mm(width_mm)
        else:
            section.orientation = WD_ORIENT.PORTRAIT
            section.page_width = Mm(width_mm)
            section.page_height = Mm(height_mm)

        # Optional: set consistent margins
        section.top_margin = Mm(25)
        section.bottom_margin = Mm(25)
        section.left_margin = Mm(25)
        section.right_margin = Mm(25)

    # 4️⃣ Save modified DOCX to memory
    document.save(buffer)
    buffer.seek(0)

    # Cleanup
    os.remove(temp_md_path)
    os.remove(temp_docx_path)

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
