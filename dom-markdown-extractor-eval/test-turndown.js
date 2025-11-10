const fs = require('fs');
const path = require('path');
const TurndownService = require('turndown');
const { JSDOM } = require('jsdom');

// Configure Turndown
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced'
});

// Get test files
const testDir = path.join(__dirname, 'test-cases');
const outputDir = path.join(__dirname, 'outputs/turndown');
const testFiles = fs.readdirSync(testDir).filter(f => f.endsWith('.html')).sort();

console.log(`Testing Turndown on ${testFiles.length} files...\n`);

testFiles.forEach(file => {
  const htmlPath = path.join(testDir, file);
  const html = fs.readFileSync(htmlPath, 'utf8');

  // Parse HTML with JSDOM to get a proper DOM
  const dom = new JSDOM(html);
  const bodyHtml = dom.window.document.body.innerHTML;

  // Convert to Markdown
  const markdown = turndownService.turndown(bodyHtml);

  // Save output
  const outputFile = file.replace('.html', '.md');
  const outputPath = path.join(outputDir, outputFile);
  fs.writeFileSync(outputPath, markdown);

  console.log(`✓ ${file} -> ${outputFile}`);
});

console.log('\nTurndown conversion complete!');
