from fastapi import FastAPI
from tools import pdf_generator
from tools import ppt
from tools import doc_gen
app = FastAPI()


app.include_router(pdf_generator.router, prefix="/api/pdf", tags=["PDF"])
app.include_router(ppt.router, prefix="/api/ppt", tags=["PPT"])
app.include_router(doc_gen.router,prefix="/api/docs",tags=["DOCX"])


