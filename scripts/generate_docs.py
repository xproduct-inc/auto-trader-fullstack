from pathlib import Path
import json
from fastapi.openapi.utils import get_openapi
from src.main import app

def generate_openapi_spec():
    """Generate OpenAPI specification"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Write OpenAPI spec to file
    docs_path = Path("docs")
    docs_path.mkdir(exist_ok=True)
    
    with open(docs_path / "openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)

if __name__ == "__main__":
    generate_openapi_spec() 