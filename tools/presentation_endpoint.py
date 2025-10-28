from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
import pypandoc
import tempfile
import os
import re

pptx_router = APIRouter()

@pptx_router.get("/health")
async def health_check():
    return {"status": "healthy"}

class PptxRequest(BaseModel):
    filename: str = "slides.pptx"
    slide_level: int = 2
    content: str = ""

def preprocess_markdown(md_text: str) -> str:
    """
    Prepares Markdown for Pandoc conversion.
    Converts Marpit or generic Markdown slide separators into Pandoc-friendly structure.
    """
    text = md_text.strip()

    # Detect Marpit-like style using '---' slide separators
    if re.search(r"(?m)^---\s*$", text):
        slides = re.split(r"(?m)^---\s*$", text)
        processed_slides = []
        for idx, slide in enumerate(slides, start=1):
            slide = slide.strip()
            if not slide:
                continue
            # Add a header if missing
            if not re.match(r"^#{1,6}\s", slide):
                slide = f"## Slide {idx}\n\n" + slide
            processed_slides.append(slide)
        return "\n\n".join(processed_slides)

    # If it's already Pandoc-style, just return as is
    return text

def generate_pptx(data: PptxRequest) -> BytesIO:
    buffer = BytesIO()

    # Preprocess Markdown to normalize structure
    clean_content = preprocess_markdown(data.content)

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp_in:
        tmp_in.write(clean_content.encode("utf-8"))
        tmp_in.flush()
        input_path = tmp_in.name

    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_out:
        output_path = tmp_out.name

    try:
        pypandoc.convert_file(
            input_path,
            "pptx",
            outputfile=output_path,
            extra_args=[f"--slide-level={data.slide_level}"]
        )

        with open(output_path, "rb") as f:
            buffer.write(f.read())

        buffer.seek(0)
        return buffer

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during conversion: {str(e)}")

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

@pptx_router.post("/generate")
async def create_pptx(request: PptxRequest):
    try:
        buffer = generate_pptx(request)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
