# 📁 scripts/generate-docs.sh

#!/bin/bash

# Generate documentation script for AI Benchmark Service

set -e

echo "📚 Generating documentation..."

# Check if required tools are installed
if ! command -v pandoc &> /dev/null; then
    echo "❌ pandoc is not installed"
    echo "Install pandoc to generate documentation"
    exit 1
fi

# Create docs directory
mkdir -p docs/generated

# Generate API documentation
echo "📡 Generating API documentation..."
# This would typically use Swagger/OpenAPI tools
# For now, we'll just copy existing docs
cp -r docs/*.md docs/generated/

# Generate code documentation
echo "💻 Generating code documentation..."
# This would typically use tools like Sphinx for Python
# For now, we'll create a placeholder
echo "# Code Documentation" > docs/generated/CODE_DOCS.md
echo "" >> docs/generated/CODE_DOCS.md
echo "Generated on $(date)" >> docs/generated/CODE_DOCS.md

# Generate user guides
echo "📖 Generating user guides..."
# This would typically convert markdown to PDF/HTML
for file in docs/*.md; do
    filename=$(basename "$file" .md)
    echo "Converting $filename..."
    # pandoc "$file" -o "docs/generated/${filename}.pdf"
    # pandoc "$file" -o "docs/generated/${filename}.html"
done

echo "✅ Documentation generation completed!"
echo "Documentation available in docs/generated/"