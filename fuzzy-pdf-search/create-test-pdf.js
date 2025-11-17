const PDFDocument = require('pdfkit');
const fs = require('fs');

const doc = new PDFDocument();
const stream = fs.createWriteStream('test.pdf');
doc.pipe(stream);

doc.fontSize(24).text('Fuzzy PDF Search Test Document', { align: 'center' });
doc.moveDown();

doc.fontSize(12).text(`
This is a test document for the Fuzzy PDF Search application.

The application allows users to search for text in PDF documents using fuzzy matching.
Even if you make a small typo or spelling mistake, it will find the best matching text.

Features include:
- PDF upload and text extraction
- Fuzzy text matching with configurable thresholds
- Shareable URLs with search queries
- Visual highlighting of matched text

For example, if you search for "fuzzi matcing" (misspelled),
it should still find "fuzzy matching" in this document.

The search algorithm uses Levenshtein distance and other similarity metrics
to find the best matches even with errors in the search query.

This document was created on ${new Date().toLocaleDateString()} for testing purposes.
`);

doc.addPage();
doc.fontSize(18).text('Page 2: Additional Content');
doc.moveDown();
doc.fontSize(12).text(`
Here is some more content on the second page.

This demonstrates multi-page PDF support.
The search functionality works across all pages of the document.

Key terms for testing:
- Implementation details
- Algorithmic complexity
- User interface design
- Performance optimization
- Error handling mechanisms
`);

doc.end();

stream.on('finish', () => {
  console.log('Test PDF created successfully');
});

stream.on('error', (err) => {
  console.error('Error creating PDF:', err);
});
