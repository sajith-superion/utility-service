from fastapi import FastAPI
from tools import pdf_generator
from tools import ppt
app = FastAPI()


app.include_router(pdf_generator.router, prefix="/api/pdf", tags=["PDF"])
app.include_router(ppt.router, prefix="/api/ppt", tags=["PPT"])


