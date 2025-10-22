from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
import pypandoc
import tempfile
import os

pptx_router = APIRouter()

@pptx_router.get("/health")
async def health_check():
    return {"status": "healthy"}

class PptxRequest(BaseModel):
    
    filename: str = "slides.pptx"
    slide_level: int = 2  # Markdown heading level to start new slides
    content: str = ""


def generate_pptx(data: PptxRequest) -> BytesIO:

    buffer = BytesIO()

    # Create temporary input/output files
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp_in:
        tmp_in.write(data.content.encode("utf-8"))
        tmp_in.flush()
        input_path = tmp_in.name

    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_out:
        output_path = tmp_out.name

    try:
        # Run Pandoc conversion via pypandoc
        pypandoc.convert_file(
            input_path,
            "pptx",
            outputfile=output_path,
            extra_args=[f"--slide-level={data.slide_level}"]
        )

        # Read the generated PPTX into memory
        with open(output_path, "rb") as f:
            buffer.write(f.read())

        buffer.seek(0)
        return buffer

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during conversion: {str(e)}")

    finally:
        # Cleanup temp files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)


@pptx_router.post("/generate")
async def create_pptx(request: PptxRequest):
    """
    FastAPI endpoint that receives Markdown and returns a PPTX presentation.
    """
    try:
        buffer = generate_pptx(request)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


