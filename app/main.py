import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.pdf_parser import extract_tables_from_pdf
from app.services.db_manager import sync_schema_and_insert, fetch_all_records

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Dynamic PDF Parser that evolves its database schema automatically.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/upload", summary="Upload PDF & Extract Data")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Uploads a PDF, extracts tables, adapts the database schema, and stores data.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs allowed.")

    file_path = f"{settings.UPLOAD_DIR}/{file.filename}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="File save failed")

    # Process
    try:
        # Step 1: Extract
        extracted_data = extract_tables_from_pdf(file_path)
        
        # Step 2: Store (with Dynamic Schema)
        db_result = sync_schema_and_insert(extracted_data)
        
        return {
            "filename": file.filename,
            "extraction_summary": db_result,
            "preview_data": extracted_data[:2] if extracted_data else []
        }
    except Exception as e:
        # Log error in production
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup: Remove file after processing to save space (Industrial Best Practice)
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/api/v1/data", summary="Retrieve All Data")
async def get_data():
    """
    Fetches all data stored in the dynamic table.
    """
    return fetch_all_records()

@app.get("/", include_in_schema=False)
def root():
    return {"message": "System Operational. Visit /docs for API."}