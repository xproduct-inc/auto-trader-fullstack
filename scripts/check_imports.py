import importlib
import os
import sys
from pathlib import Path

def check_imports(directory: str = "src"):
    """Check all Python files for import errors"""
    errors = []
    root = Path(directory)
    
    for path in root.rglob("*.py"):
        module_path = str(path.relative_to(root.parent)).replace("/", ".")[:-3]
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            errors.append(f"{module_path}: {str(e)}")
            
    return errors

if __name__ == "__main__":
    errors = check_imports()
    if errors:
        print("Found import errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("No import errors found") 