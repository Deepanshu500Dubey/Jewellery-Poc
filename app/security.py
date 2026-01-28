import ast

ALLOWED_IMPORTS = {"pandas", "numpy"}

def validate_python_code(code: str):
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise ValueError(f"Import not allowed: {n.name}")

        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] not in ALLOWED_IMPORTS:
                raise ValueError(f"Import not allowed: {node.module}")

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval", "open"}:
                raise ValueError("Unsafe function usage")

    return True
