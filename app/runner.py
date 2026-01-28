import subprocess
import tempfile
from app.security import validate_python_code

def run_python_code(code: str):
    validate_python_code(code)

    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        delete=False
    ) as f:
        f.write(code)
        script_path = f.name

    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()
