from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from app.schema import get_csv_schema
from app.runner import run_python_code
import os
import urllib.parse

app = FastAPI(title="Agentic CSV Extractor")

# Temporary directory for generated files
TEMP_DIR = "app/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# ✅ HARDCODED FILENAME FOR POC (This is correct!)
HARDCODED_FILENAME = "poc_output.csv"
HARDCODED_FULL_PATH = os.path.join(TEMP_DIR, HARDCODED_FILENAME)

# Pydantic model for incoming Python code requests
class PythonRequest(BaseModel):
    code: str

# -------------------------------
# Endpoint to fetch CSV schema
# -------------------------------
@app.get("/schema")
def fetch_schema():
    """Get the CSV schema/column definitions"""
    try:
        schema = get_csv_schema()
        return {
            "status": "success",
            "schema": schema,
            "message": f"CSV schema retrieved. The output file will be: {HARDCODED_FILENAME}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema: {str(e)}")

# -------------------------------
# Endpoint to run Python code
# -------------------------------
@app.post("/run-python")
async def run_python(req: PythonRequest, request: Request):
    """Execute Python code and generate CSV file"""
    try:
        # Execute the Python code
        output = run_python_code(req.code)
        
        # ✅ ALWAYS use hardcoded path for POC
        output_path = HARDCODED_FULL_PATH
        
        # ✅ Check if file was created (optional but good for debugging)
        if not os.path.exists(output_path):
            print(f"Warning: File not found at {output_path}. Python code output: {output}")
            # For POC, we can continue even if file isn't created yet
            # Or we can raise an error based on requirements
        
        # ✅ Get base URL from request (most reliable method)
        base_url = str(request.base_url).rstrip('/')
        
        # ✅ Construct download URL using hardcoded filename
        download_url = f"{base_url}/download/{HARDCODED_FILENAME}"
        
        return {
            "status": "success",
            "message": "Python code executed successfully",
            "filename": HARDCODED_FILENAME,
            "download_url": download_url,
            "execution_output": str(output),
            "note": f"Download your file at: {download_url}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------
# Endpoint to download CSV
# -------------------------------
@app.get("/download/{filename}")
def download_csv(filename: str, background_tasks: BackgroundTasks):
    """Download the generated CSV file"""
    try:
        # ✅ SECURITY: Only allow hardcoded filename for POC
        if filename != HARDCODED_FILENAME:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Only '{HARDCODED_FILENAME}' is allowed for POC."
            )
        
        # ✅ Always use hardcoded path
        full_path = HARDCODED_FULL_PATH
        
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404, 
                detail=f"File '{HARDCODED_FILENAME}' not found. Please run /run-python first to generate the CSV file."
            )
        
        # Schedule deletion after sending (optional for POC)
        background_tasks.add_task(os.remove, full_path)
        
        return FileResponse(
            full_path,
            media_type="text/csv",
            filename=HARDCODED_FILENAME,  # Download with same name
            headers={"Content-Disposition": f"attachment; filename={HARDCODED_FILENAME}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

# -------------------------------
# Health check endpoint
# -------------------------------
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Agentic CSV Extractor API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This information",
            "GET /schema": "Get CSV schema/column definitions",
            "POST /run-python": "Execute Python code to generate CSV",
            "GET /download/{filename}": f"Download generated CSV (use: {HARDCODED_FILENAME})",
            "GET /test": "Test endpoint"
        },
        "note": f"This is a POC. All outputs use hardcoded filename: {HARDCODED_FILENAME}"
    }

# -------------------------------
# Test endpoint
# -------------------------------
@app.get("/test")
def test_endpoint(request: Request):
    """Test endpoint to verify URLs are working"""
    base_url = str(request.base_url).rstrip('/')
    return {
        "status": "success",
        "message": "API is working correctly",
        "hardcoded_filename": HARDCODED_FILENAME,
        "example_endpoints": {
            "get_schema": f"{base_url}/schema",
            "run_python": f"{base_url}/run-python (POST)",
            "download_file": f"{base_url}/download/{HARDCODED_FILENAME}"
        },
        "notes": [
            "This is a POC with hardcoded filename for simplicity",
            "All generated files will be named: poc_output.csv",
            "Run /run-python first to generate the file, then download it"
        ]
    }
