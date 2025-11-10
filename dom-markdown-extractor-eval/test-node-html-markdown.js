const fs = require('fs');
const path = require('path');
const { NodeHtmlMarkdown } = require('node-html-markdown');
const { JSDOM } = require('jsdom');

// Get test files
const testDir = path.join(__dirname, 'test-cases');
const outputDir = path.join(__dirname, 'outputs/node-html-markdown');
const testFiles = fs.readdirSync(testDir).filter(f => f.endsWith('.html')).sort();

console.log(`Testing node-html-markdown on ${testFiles.length} files...\n`);

testFiles.forEach(file => {
  const htmlPath = path.join(testDir, file);
  const html = fs.readFileSync(htmlPath, 'utf8');

  // Parse HTML with JSDOM to get body content
  const dom = new JSDOM(html);
  const bodyHtml = dom.window.document.body.innerHTML;

  // Convert to Markdown
  const markdown = NodeHtmlMarkdown.translate(bodyHtml);

  // Save output
  const outputFile = file.replace('.html', '.md');
  const outputPath = path.join(outputDir, outputFile);
  fs.writeFileSync(outputPath, markdown);

  console.log(`✓ ${file} -> ${outputFile}`);
});

console.log('\nnode-html-markdown conversion complete!');
