from fastapi import FastAPI
from tools import pdf_endpoint
from tools import presentation_endpoint
from tools import doc_endpoint
app = FastAPI()


app.include_router(pdf_endpoint.router, prefix="/api/pdf", tags=["PDF"])
app.include_router(presentation_endpoint.router, prefix="/api/ppt", tags=["PPT"])
app.include_router(doc_endpoint.router,prefix="/api/docs",tags=["DOCX"])


