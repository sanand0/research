# Installation Instructions

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `python-docx` - For Word document manipulation
- `pyinstaller` - For creating standalone executables
- `pytest` - For running tests

### 2. Run the Application

To run the application directly with Python:

```bash
python main_gui.py
```

### 3. Create Standalone Executable (Optional)

To create a standalone executable that can be distributed:

#### On Windows:
```bash
pyinstaller build_exe.spec
```

#### On macOS/Linux:
```bash
pyinstaller build_exe.spec
```

The executable will be created in the `dist` folder:
- Windows: `dist/WordFileSplitterRenamer.exe`
- macOS: `dist/WordFileSplitterRenamer`
- Linux: `dist/WordFileSplitterRenamer`

The executable can be distributed and run without requiring Python to be installed.

## Running Tests

To run the test suite:

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest test_word_splitter.py
python -m pytest test_file_renamer.py
```

## Creating Sample Fixtures

To create sample Word documents for testing:

```bash
python create_fixtures.py
```

This will create a `fixtures` folder with sample documents.

## Troubleshooting

### ImportError: No module named 'tkinter'

On some Linux distributions, tkinter needs to be installed separately:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
tkinter is included with Python from python.org

### ImportError: No module named 'docx'

Make sure you installed `python-docx` (not `docx`):
```bash
pip install python-docx
```

### Executable won't run on other machines

Make sure to:
1. Build the executable on the same OS as the target machine
2. Include all necessary dependencies in the spec file
3. Test the executable on a clean machine without Python installed
