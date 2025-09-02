from io import BytesIO
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

router = APIRouter()

class PDFRequest(BaseModel):
    font: str
    font_size: int
    margin: int
    page_number: bool = True
    orientation: str
    page_size: str = "A4"
    filename: str = "test.pdf"  # default filename



def generate_pdf(data: PDFRequest) -> bytes:
    # Pick page size
    if data.page_size.upper() == "LETTER":
        base_size = LETTER
    else:
        base_size = A4  # default is A4

    # Apply orientation
    if data.orientation.lower() == "landscape":
        pagesize = landscape(base_size)
    else:
        pagesize = base_size

    # Use BytesIO instead of saving to disk
    buffer = BytesIO()

    # Create document with margins
    margin = data.margin
    doc = SimpleDocTemplate(
        buffer,
        pagesize= pagesize,
        leftMargin= margin * cm,
        rightMargin= margin * cm,
        topMargin= margin * cm,
        bottomMargin= margin * cm,
    )

    # Base styles
    styles = getSampleStyleSheet()

    # Custom styles
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading1"],
        fontName=data.font,
        fontSize=20,
        textColor=colors.darkblue,
        spaceAfter=12,
    )

    subheading_style = ParagraphStyle(
        "Subheading",
        parent=styles["Heading2"],
        fontName=data.font,
        fontSize=16,
        textColor=colors.darkgreen,
        spaceAfter=10,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=data.font_size,
        leading=16,  # line spacing
    )

    # Build story
    story = [
        Paragraph("Main Heading Example", heading_style),
        Paragraph("This is a subheading example", subheading_style),
        Paragraph(
            """Lorem ipsum dolor sit amet. Sed Quis dolore non consectetur ipsam aut optio quibusdam.
            Ea suscipit impedit rem eveniet explicabo sit facere repudiandae cum distinctio alias
            ut reiciendis nobis qui consequuntur nostrum et cupiditate beatae.""",
            body_style,
        ),
        Spacer(1, 12),
        Paragraph("new content 123.", body_style),
    ]

    # Function to add page numbers
    def add_page_number(canvas, doc):
        if data.page_number:
            page_num = canvas.getPageNumber()
            text = f"Page {page_num}"
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(pagesize[0] - 2 * cm, 1.5 * cm, text)

    # Build PDF into buffer
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


@router.post("/generate-pdf")
async def create_pdf(request: PDFRequest):
    try:
        pdf_bytes = generate_pdf(request)
        buffer = BytesIO(pdf_bytes)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

