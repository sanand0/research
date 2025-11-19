# Word File Splitter & Renamer GUI

A cross-platform Python GUI application for splitting Word documents and batch renaming files with customizable naming schemes.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-44%20passed-brightgreen)

## Features

### Word Document Splitter
- **Split Word files** based on customizable delimiters (default: ***)
- **Batch processing** - split multiple Word files at once
- **Preserve formatting** - maintains document styles, fonts, and formatting
- **Progress tracking** - real-time progress bar and status updates
- **Control options** - Start, Pause/Resume, and Stop operations
- **Flexible paths** - Browse for files/folders or paste paths directly
- **Note preservation** - creates temporary copy to preserve document notes

### File Renamer
- **Batch rename files** with customizable prefixes and suffixes
- **Multiple suffix types**:
  - Numeric: 1, 2, 3, ...
  - Alphabetic (lowercase): a, b, c, ..., z, aa, ab, ...
  - Alphabetic (uppercase): A, B, C, ..., Z, AA, AB, ...
  - Roman (lowercase): i, ii, iii, iv, v, ...
  - Roman (uppercase): I, II, III, IV, V, ...
- **Predefined prefixes**: Chapter, Section, Part, Figure, Table, Equation
- **Custom prefixes** - use any prefix you want
- **File reordering** - drag and rearrange files in the list
- **Move controls** - Up, Down, To Top, To Bottom
- **Custom start number** - begin numbering from any value
- **Progress tracking** - real-time progress updates

## Screenshots

### Word Splitter Tab
The Word Splitter tab allows you to split Word documents based on delimiters:
- Input path (file or folder for batch processing)
- Output path for split files
- Configurable delimiter
- Batch processing option
- Progress bar and status

### File Renamer Tab
The File Renamer tab provides comprehensive file renaming capabilities:
- File list with add/remove/reorder controls
- Predefined or custom prefix options
- Multiple suffix type options (numeric, alphabetic, roman)
- Custom start number
- Drag and drop support

## Installation

### Requirements
- Python 3.7 or higher
- tkinter (included with Python)
- python-docx

### Quick Install

```bash
# Clone or download this repository
cd word-file-splitter-gui

# Install dependencies
pip install -r requirements.txt

# Run the application
python main_gui.py
```

### Creating a Standalone Executable

To create a distributable executable:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Build the executable
pyinstaller build_exe.spec

# Find the executable in the 'dist' folder
# Windows: dist/WordFileSplitterRenamer.exe
# macOS/Linux: dist/WordFileSplitterRenamer
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions and troubleshooting.

## Usage

### Word Splitter

1. **Launch the application** and select the "Word Splitter" tab
2. **Select input**:
   - Click "Browse File" to select a single Word document
   - Click "Browse Folder" for batch processing multiple files
   - Or paste the path directly in the input field
3. **Select output folder** where split files will be saved
4. **Configure delimiter** (default is ***)
5. **Enable batch mode** if processing multiple files
6. **Click Start** to begin splitting
7. **Monitor progress** with the progress bar
8. **Use Pause/Resume** or Stop as needed

#### Example: Splitting a Book into Chapters

Given a Word document with this structure:
```
Front Matter
Some introductory text...
***
Chapter 1: Introduction
This is chapter one...
***
Chapter 2: Methods
This is chapter two...
***
Chapter 3: Results
This is chapter three...
```

The splitter will create:
- `book_part_001.docx` - Front Matter
- `book_part_002.docx` - Chapter 1
- `book_part_003.docx` - Chapter 2
- `book_part_004.docx` - Chapter 3

### File Renamer

1. **Launch the application** and select the "File Renamer" tab
2. **Load files**:
   - Browse for input folder and click "Load Files"
   - Or click "Add Files" to select individual files
3. **Arrange files** in desired order:
   - Select files and use Move Up/Down buttons
   - Or Move to Top/Bottom
4. **Select output folder** where renamed files will be saved
5. **Choose prefix**:
   - Select from dropdown (Chapter, Section, Part, etc.)
   - Or enter custom prefix in the text box
6. **Select suffix type**:
   - Numeric (1, 2, 3, ...)
   - Alphabetic (a/A, b/B, c/C, ...)
   - Roman (i/I, ii/II, iii/III, ...)
7. **Set start number** (default is 1)
8. **Click Start** to begin renaming

#### Example: Renaming Chapter Files

Given files:
- `draft_chapter_1.docx`
- `draft_chapter_2.docx`
- `draft_chapter_3.docx`

With settings:
- Prefix: "Chapter"
- Suffix: Roman Upper (I, II, III)
- Start from: 1

Results:
- `Chapter I.docx`
- `Chapter II.docx`
- `Chapter III.docx`

## Use Cases

### Academic Publishing
- Split thesis/dissertation into chapters
- Rename figures, tables, and equations consistently
- Process multiple documents with batch mode

### Technical Documentation
- Split large technical manuals into sections
- Rename documentation files with consistent naming
- Organize document parts for easier management

### Book Publishing
- Split manuscript into chapters for editing
- Rename book sections (Part I, Part II, etc.)
- Batch process multiple books

### Corporate Documents
- Split comprehensive reports into sections
- Standardize file naming across departments
- Organize document libraries

## Architecture

### Project Structure
```
word-file-splitter-gui/
├── main_gui.py              # Main GUI application
├── word_splitter.py         # Word splitting logic
├── file_renamer.py          # File renaming logic
├── test_word_splitter.py    # Splitter tests
├── test_file_renamer.py     # Renamer tests
├── create_fixtures.py       # Generate sample files
├── requirements.txt         # Python dependencies
├── build_exe.spec          # PyInstaller configuration
├── INSTALL.md              # Installation guide
├── README.md               # This file
└── fixtures/               # Sample test files
    ├── sample_book.docx
    ├── short_sample.docx
    └── batch_samples/
```

### Core Components

#### WordSplitter (`word_splitter.py`)
- Handles Word document splitting based on delimiters
- Supports single file and batch processing
- Preserves document formatting and notes
- Implements pause/resume/stop functionality

#### FileRenamer (`file_renamer.py`)
- Manages file renaming with various suffix types
- Supports multiple numbering systems
- Implements pause/resume/stop functionality
- Handles file ordering and batch operations

#### Main GUI (`main_gui.py`)
- Tabbed interface using tkinter
- Separate tabs for splitter and renamer
- Background threading for responsive UI
- Progress tracking and status updates

## Testing

The project includes comprehensive test suites:

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_word_splitter.py
python -m pytest test_file_renamer.py

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html
```

### Test Coverage
- **44 total tests** covering all major functionality
- **Word Splitter**: 19 tests
  - Single file splitting
  - Batch processing
  - Custom delimiters
  - Error handling
  - Progress callbacks
  - Integration tests
- **File Renamer**: 25 tests
  - All suffix types
  - Prefix handling
  - File operations
  - Error handling
  - Integration tests

### Sample Fixtures

Create sample test files:
```bash
python create_fixtures.py
```

This creates:
- `fixtures/sample_book.docx` - Full book with chapters
- `fixtures/short_sample.docx` - Short document
- `fixtures/custom_delimiter_sample.docx` - Custom delimiter
- `fixtures/batch_samples/` - Multiple documents
- `fixtures/files_to_rename/` - Files for renaming

## Technical Details

### Dependencies
- **python-docx**: Word document manipulation
- **tkinter**: GUI framework (included with Python)
- **pytest**: Testing framework

### Platform Compatibility
- **Windows**: Fully supported, can create .exe
- **macOS**: Fully supported
- **Linux**: Fully supported (requires python3-tk on some distros)

### Delimiter Placement Rules
When splitting Word documents:
- Delimiters should be placed between sections
- Do not place at the very beginning of the document
- Do not place at the very end of the document
- Each delimiter creates a new split point
- Delimiter paragraphs are excluded from output

### File Naming Convention
Split files are named: `{original_name}_part_{number:03d}.docx`
- Example: `book.docx` → `book_part_001.docx`, `book_part_002.docx`, etc.

Renamed files follow: `{prefix} {suffix}.{extension}`
- Example: `Chapter I.docx`, `Chapter II.docx`, etc.

## Known Limitations

1. **Roman numerals**: Limited to 1-3999 (standard Roman numeral range)
2. **Word format**: Only supports .docx and .doc files
3. **Delimiter detection**: Delimiters must be in paragraph text (not in tables or headers)
4. **File size**: Very large files (>100MB) may take longer to process

## Troubleshooting

### Application won't start
- Ensure Python 3.7+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- On Linux, install tkinter: `sudo apt-get install python3-tk`

### Tests failing
- Ensure python-docx is installed: `pip install python-docx`
- Check that pytest is installed: `pip install pytest`
- Run tests from the project directory

### Splitting doesn't work
- Verify the document contains the delimiter text
- Check that the delimiter is in paragraph text (not tables/headers)
- Ensure the file is a valid .docx or .doc file

### Renaming fails
- Verify all input files exist
- Check that output directory is writable
- Ensure prefix is not empty

## Future Enhancements

Potential features for future versions:
- [ ] Support for other document formats (PDF, ODT)
- [ ] Custom delimiter patterns (regex support)
- [ ] Preview mode before splitting/renaming
- [ ] Undo/redo functionality
- [ ] Save/load configuration presets
- [ ] Merge files back together
- [ ] Command-line interface
- [ ] Drag-and-drop file input
- [ ] Dark mode theme
- [ ] Internationalization (i18n)

## Contributing

Contributions are welcome! Areas for contribution:
- Bug fixes and testing
- Additional suffix types or naming patterns
- GUI improvements and themes
- Documentation improvements
- Platform-specific optimizations

## License

MIT License - feel free to use this tool in personal or commercial projects.

## Author

Created for cross-departmental use in document processing and file management workflows.

## Acknowledgments

- Built with [python-docx](https://python-docx.readthedocs.io/) for Word document manipulation
- GUI created with tkinter, Python's standard GUI framework
- Tested with pytest framework

---

**Version**: 1.0.0
**Last Updated**: 2024
