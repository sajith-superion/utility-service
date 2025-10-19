from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from markdown import markdown
from xhtml2pdf import pisa
from io import BytesIO
import base64

router = APIRouter()

class PDFRequest(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    filename: str = "generated.pdf"
    content: str = ""

@router.post("/")
async def generate_pdf(request: PDFRequest):
    try:
        # 1️⃣ Convert Markdown to HTML
        html_content = markdown(request.content)
        
        # 2️⃣ Create complete HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: {request.page_size} {request.orientation};
                    margin: 2cm;
                }}
                body {{
                    font-family: "DejaVu Sans", "Arial", sans-serif;
                    font-size: 12pt;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #333;
                    margin-top: 1em;
                    margin-bottom: 0.5em;
                }}
                h1 {{ font-size: 18pt; }}
                h2 {{ font-size: 16pt; }}
                h3 {{ font-size: 14pt; }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: "Courier New", monospace;
                    font-size: 10pt;
                }}
                pre {{
                    background-color: #f8f8f8;
                    padding: 12px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border-left: 4px solid #4CAF50;
                    margin: 1em 0;
                }}
                pre code {{
                    background: none;
                    padding: 0;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    padding-left: 1em;
                    margin-left: 0;
                    color: #666;
                    font-style: italic;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #ddd;
                    margin: 2em 0;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # 3️⃣ Create PDF in memory using xhtml2pdf
        pdf_buffer = BytesIO()
        
        # Convert HTML to PDF
        pisa_status = pisa.CreatePDF(
            html_template,
            dest=pdf_buffer,
            encoding='UTF-8'
        )
        
        # Check for errors
        if pisa_status.err:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        pdf_buffer.seek(0)

        # 4️⃣ Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))