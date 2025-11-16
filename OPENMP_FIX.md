# OpenMP Library Conflict Fix

## Problem
The error "OMP: Error #15: Initializing libomp140.x86_64.dll, but found libiomp5md.dll already initialized" occurs when multiple libraries load different OpenMP runtimes.

## Root Cause
Multiple Python packages (NumPy, SciPy, PyTorch, sentence-transformers, etc.) include their own OpenMP runtime libraries, causing conflicts.

## Solutions Implemented

### Quick Fix (Applied)
Set the environment variable `KMP_DUPLICATE_LIB_OK=TRUE` at the beginning of the application:

```python
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

This has been added to:
- `src/backend/main.py`
- `src/backend/api/chat.py`
- `src/rag/__init__.py`

### Alternative Solutions (Long-term)

#### 1. Use Intel MKL NumPy (Recommended)
Install NumPy built with Intel MKL which handles OpenMP better:

```powershell
pip uninstall numpy
pip install numpy --only-binary :all: -c constraints.txt
```

Or use conda:
```powershell
conda install numpy
```

#### 2. Reinstall PyTorch with specific build
```powershell
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

#### 3. Set Environment Variable System-wide (Windows)
Add to system environment variables:
- Variable: `KMP_DUPLICATE_LIB_OK`
- Value: `TRUE`

Or in PowerShell before running:
```powershell
$env:KMP_DUPLICATE_LIB_OK="TRUE"
uvicorn src.backend.main:app --reload
```

#### 4. Use Poetry with Specific Package Versions
Update `pyproject.toml` to use compatible versions:

```toml
[project]
dependencies = [
    "numpy>=2.2.4,<3.0.0",
    "torch>=2.6.0,<3.0.0",
    "mkl>=2024.0",  # Add this
    "mkl-service",   # Add this
]
```

## Testing the Fix

Run your application and check if the warning disappears:

```powershell
cd D:\KMA_ChatBot_Frontend_System\chatbot_agent
uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Performance Considerations

The `KMP_DUPLICATE_LIB_OK=TRUE` workaround may cause:
- Slightly degraded performance
- Potentially incorrect results in rare edge cases
- Thread scheduling conflicts

For production, consider implementing one of the long-term solutions.

## References
- [OpenMP Documentation](http://openmp.llvm.org/)
- [Intel MKL NumPy](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html)
- [PyTorch Installation](https://pytorch.org/get-started/locally/)
