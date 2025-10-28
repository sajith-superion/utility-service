from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from markdown import markdown
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.lib.pagesizes import A4, LETTER, legal, landscape, portrait

pdf_router = APIRouter()

class PDFRequest(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    filename: str = "generated.pdf"
    content: str = ""

@pdf_router.get("/health")
async def health_check():
    return {"status": "healthy"}

def get_page_size(size_name: str, orientation: str):
    PAGE_SIZES = {"A4": A4, "LETTER": LETTER, "LEGAL": legal}
    size = PAGE_SIZES.get(size_name.upper(), A4)
    return landscape(size) if orientation.lower() == "landscape" else portrait(size)

@pdf_router.post("/generate")
async def generate_pdf(request: PDFRequest):
    try:
        # 1️⃣ Convert Markdown to HTML
        html_content = markdown(request.content)

        # 2️⃣ Compute page size manually
        page_size = get_page_size(request.page_size, request.orientation)

        # 3️⃣ Proper XHTML Template
        html_template = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta charset="UTF-8" />
<style>
    @page {{
        size: {page_size[0]}pt {page_size[1]}pt;
        margin: 2cm;
    }}
    body {{
        font-family: "DejaVu Sans", Arial, sans-serif;
        color: #000;
        font-size: 12pt;
        line-height: 1.5;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: #333;
    }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""

        # 4️⃣ Create PDF in memory
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_template,
            dest=pdf_buffer,
            encoding="UTF-8"
        )

        if pisa_status.err:
            raise HTTPException(status_code=500, detail="PDF generation failed")

        pdf_buffer.seek(0)

        # 5️⃣ Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
