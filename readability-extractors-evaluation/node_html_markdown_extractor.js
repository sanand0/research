#!/usr/bin/env node
/**
 * node-html-markdown extractor wrapper
 */

const fs = require('fs');
const { NodeHtmlMarkdown } = require('node-html-markdown');

// Get HTML file path from command line
const htmlFile = process.argv[2];

if (!htmlFile) {
    console.error('Usage: node node_html_markdown_extractor.js <html_file>');
    process.exit(1);
}

try {
    // Read HTML file
    const html = fs.readFileSync(htmlFile, 'utf-8');

    // Convert to Markdown
    const nhm = new NodeHtmlMarkdown();
    const markdown = nhm.translate(html);

    // Output markdown
    console.log(markdown);

} catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
}
