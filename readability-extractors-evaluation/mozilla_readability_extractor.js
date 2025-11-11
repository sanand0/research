#!/usr/bin/env node
/**
 * Mozilla Readability extractor with Turndown for Markdown conversion
 */

const fs = require('fs');
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const TurndownService = require('turndown');

// Get HTML file path from command line
const htmlFile = process.argv[2];

if (!htmlFile) {
    console.error('Usage: node mozilla_readability_extractor.js <html_file>');
    process.exit(1);
}

try {
    // Read HTML file
    const html = fs.readFileSync(htmlFile, 'utf-8');

    // Parse with JSDOM
    const dom = new JSDOM(html, {
        url: 'https://example.com' // Readability needs a base URL
    });

    // Run Readability
    const reader = new Readability(dom.window.document);
    const article = reader.parse();

    if (!article) {
        console.error('Failed to parse article');
        process.exit(1);
    }

    // Convert to Markdown with Turndown
    const turndownService = new TurndownService({
        headingStyle: 'atx',
        codeBlockStyle: 'fenced'
    });

    const markdown = turndownService.turndown(article.content);

    // Output markdown
    console.log(markdown);

} catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
}
