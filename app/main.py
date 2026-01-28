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
# Endpoint to run Python code
# Returns download URL along with file path
# -------------------------------
@app.post("/run-python")
def run_python(req: PythonRequest):
    try:
        # Execute the Python code
        output_path = run_python_code(req.code)

        # Construct the full download URL
        download_url = f"{BASE_URL}/download?path={output_path}"

        return {
            "status": "success",
            "file_path": output_path,
            "download_url": download_url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------
# Endpoint to download CSV
# Streams the file and schedules deletion
# -------------------------------
@app.get("/download")
def download_csv(path: str, background_tasks: BackgroundTasks):
    full_path = os.path.abspath(path)

    # Security: only allow files inside TEMP_DIR
    if not full_path.startswith(os.path.abspath(TEMP_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Schedule deletion after sending the file
    background_tasks.add_task(os.remove, full_path)

    return FileResponse(
        full_path,
        media_type="text/csv",
        filename=os.path.basename(full_path)
    )
