from fastapi import FastAPI
from tools import pdf_endpoint
from tools import presentation_endpoint
from tools import doc_endpoint
app = FastAPI()


app.include_router(pdf_endpoint.router, prefix="/api/utility-service/pdf", tags=["PDF"])
app.include_router(presentation_endpoint.router, prefix="/api/utility-service/ppt", tags=["PPT"])
app.include_router(doc_endpoint.router,prefix="/api/utility-service/docs",tags=["DOCX"])
