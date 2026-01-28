from fastapi import FastAPI, HTTPException , BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.schema import get_csv_schema
from app.runner import run_python_code
import os
app = FastAPI(title="Agentic CSV Extractor")

TEMP_DIR = "app/temp"

class PythonRequest(BaseModel):
    code: str


@app.get("/schema")
def fetch_schema():
    return {"columns": get_csv_schema()}


@app.post("/run-python")
def run_python(req: PythonRequest):
    try:
        output_path = run_python_code(req.code)
        return {
            "status": "success",
            "file_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/download")
def download_csv(path: str, background_tasks: BackgroundTasks):
    full_path = os.path.abspath(path)

    # 🔒 Security: allow only temp dir
    if not full_path.startswith(os.path.abspath(TEMP_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 🧹 Schedule deletion AFTER response is sent
    background_tasks.add_task(os.remove, full_path)

    return FileResponse(
        full_path,
        media_type="text/csv",
        filename=os.path.basename(full_path)
    )
