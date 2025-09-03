from fastapi import FastAPI
from tools import pdf_generator

app = FastAPI()


app.include_router(pdf_generator.router, prefix="/api/pdf", tags=["PDF"])

