from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from docx import Document
from docx.shared import Inches, Mm, Cm
from docx.enum.section import WD_ORIENT
import pypandoc
from io import BytesIO

router = APIRouter()


class DocxRequest(BaseModel):
    page_size: str = "A4"
    orientation: str = "PORTRAIT"
    content: str = ""
    filename: str = "generated.docx"


def generate_docx(data: DocxRequest) -> BytesIO:
    buffer = BytesIO()
    doc = Document()

    section = doc.sections[0]

    # Page size
    if data.page_size.upper() == "LETTER":
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
    elif data.page_size.upper() == "LEGAL":
        section.page_width = Inches(8.5)
        section.page_height = Inches(14)
    else:  # default A4
        section.page_width = Mm(210)
        section.page_height = Mm(297)

    # Orientation
    if data.orientation.upper() == "PORTRAIT":
        section.orientation = WD_ORIENT.PORTRAIT
    else:
        section.orientation = WD_ORIENT.LANDSCAPE

    # Margins
    section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Cm(3)

    # Save base doc
    doc.save("temp.docx")

    # Convert RTF content -> DOCX using pypandoc
    if data.content:
        pypandoc.convert_text(data.content, to="docx", format="rtf", outputfile="temp.docx")

    # Load final DOCX into memory
    with open("temp.docx", "rb") as f:
        buffer.write(f.read())

    buffer.seek(0)
    return buffer


@router.post("/generate")
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
