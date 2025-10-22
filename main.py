from fastapi import FastAPI
from tools import pdf_endpoint
from tools import presentation_endpoint 
from tools import doc_endpoint
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
#Adding the endpoints to the main app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Specify domains in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(pdf_endpoint.pdf_router, prefix="/api/utility-service/pdf/generate", tags=["PDF"])
app.include_router(presentation_endpoint.pptx_router, prefix="/api/utility-service/pptx/generate", tags=["PPTX"])
app.include_router(doc_endpoint.docx_router, prefix="/api/utility-service/docx/generate", tags=["DOCX"])


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}



