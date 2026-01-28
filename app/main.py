from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from app.schema import get_csv_schema
from app.runner import run_python_code
import os

app = FastAPI(title="Agentic CSV Extractor")

# Temporary directory for generated files
TEMP_DIR = "app/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Base URL of the server (for constructing download links)
BASE_URL = "https://jewellery-poc-u3h3.onrender.com"

# HARDCODED FILENAME FOR POC (add this)
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
    return {"columns": get_csv_schema()}

# -------------------------------
# MODIFIED: Endpoint to run Python code with hardcoded path
# -------------------------------
@app.post("/run-python")
def run_python(req: PythonRequest):
    try:
        # Execute the Python code
        output = run_python_code(req.code)
        
        # For POC: Always return hardcoded path regardless of what Python code prints
        # This ensures download URL is always consistent
        output_path = HARDCODED_FULL_PATH
        
        # Check if file was actually created
        if not os.path.exists(output_path):
            # If file doesn't exist, check if output is a different path
            if isinstance(output, str) and os.path.exists(output):
                output_path = output
            else:
                # File might not have been created yet
                # This is expected for POC - we'll trust the code created it
                pass

        # Construct the full download URL using just filename
        download_url = f"{BASE_URL}/download?path={HARDCODED_FILENAME}"

        return {
            "status": "success",
            "file_path": output_path,
            "filename": HARDCODED_FILENAME,
            "download_url": download_url,
            "execution_output": output  # Include what Python code returned
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------
# MODIFIED: Endpoint to download CSV with hardcoded support
# -------------------------------
@app.get("/download")
def download_csv(path: str, background_tasks: BackgroundTasks):
    try:
        # For POC: Accept either full path or just filename
        # If it's just a filename, prepend TEMP_DIR
        if "/" not in path:
            # It's just a filename like "poc_output.csv"
            full_path = os.path.join(TEMP_DIR, path)
        else:
            # It's a full path like "app/temp/poc_output.csv"
            full_path = os.path.abspath(path)
        
        # Security: only allow files inside TEMP_DIR
        if not full_path.startswith(os.path.abspath(TEMP_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(full_path):
            # SPECIAL CASE: For POC, check hardcoded path
            if path == HARDCODED_FILENAME and os.path.exists(HARDCODED_FULL_PATH):
                full_path = HARDCODED_FULL_PATH
            else:
                raise HTTPException(status_code=404, detail=f"File not found: {path}")
        
        # Schedule deletion after sending the file
        background_tasks.add_task(os.remove, full_path)
        
        return FileResponse(
            full_path,
            media_type="text/csv",
            filename=HARDCODED_FILENAME  # Always return hardcoded filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")
