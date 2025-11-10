#!/bin/bash
# Test Pandoc converter

TEST_DIR="test-cases"
OUTPUT_DIR="outputs/pandoc"

mkdir -p "$OUTPUT_DIR"

echo "Testing Pandoc on HTML files..."
echo ""

count=0
for html_file in "$TEST_DIR"/*.html; do
    filename=$(basename "$html_file")
    output_file="$OUTPUT_DIR/${filename%.html}.md"

    pandoc -f html -t markdown "$html_file" -o "$output_file"

    if [ $? -eq 0 ]; then
        echo "✓ $filename -> ${filename%.html}.md"
        count=$((count + 1))
    else
        echo "✗ Failed: $filename"
    fi
done

echo ""
echo "Pandoc conversion complete! ($count files)"
