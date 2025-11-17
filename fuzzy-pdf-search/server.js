const express = require('express');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

// In-memory storage for PDF metadata (in production, use a database)
const pdfStore = new Map();

// Configure multer for PDF uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadsDir),
  filename: (req, file, cb) => {
    const id = uuidv4().slice(0, 8); // Short unique ID
    cb(null, `${id}.pdf`);
  }
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  },
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
});

// Serve static files
app.use(express.static('public'));
app.use('/uploads', express.static(uploadsDir));

// Upload endpoint
app.post('/api/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const pdfId = path.basename(req.file.filename, '.pdf');
    const pdfPath = req.file.path;

    // Extract text from PDF
    const dataBuffer = fs.readFileSync(pdfPath);
    const pdfData = await pdfParse(dataBuffer);

    // Store metadata and extracted text
    pdfStore.set(pdfId, {
      id: pdfId,
      filename: req.file.originalname,
      path: pdfPath,
      text: pdfData.text,
      numPages: pdfData.numpages,
      uploadedAt: new Date()
    });

    res.json({
      id: pdfId,
      filename: req.file.originalname,
      numPages: pdfData.numpages
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Failed to process PDF' });
  }
});

// Get PDF metadata and text
app.get('/api/pdf/:id', (req, res) => {
  const pdfId = req.params.id;
  const pdfData = pdfStore.get(pdfId);

  if (!pdfData) {
    return res.status(404).json({ error: 'PDF not found' });
  }

  res.json({
    id: pdfData.id,
    filename: pdfData.filename,
    text: pdfData.text,
    numPages: pdfData.numPages
  });
});

// Serve the PDF file
app.get('/api/pdf/:id/file', (req, res) => {
  const pdfId = req.params.id;
  const pdfData = pdfStore.get(pdfId);

  if (!pdfData) {
    return res.status(404).json({ error: 'PDF not found' });
  }

  res.sendFile(pdfData.path);
});

// Serve viewer page for any PDF ID
app.get('/view/:id', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'viewer.html'));
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
