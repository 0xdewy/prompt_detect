#!/bin/bash

# Setup script for HuggingFace deployment

echo "🚀 Setting up Prompt Detective for HuggingFace..."

# Create necessary directories
mkdir -p .huggingface

# Check if git-lfs is installed
if ! command -v git-lfs &> /dev/null; then
    echo "❌ git-lfs is not installed. Please install it first:"
    echo "  Ubuntu/Debian: sudo apt-get install git-lfs"
    echo "  macOS: brew install git-lfs"
    echo "  Windows: Download from https://git-lfs.github.com/"
    exit 1
fi

# Initialize git-lfs if not already initialized
if [ ! -f .gitattributes ]; then
    echo "📁 Initializing git-lfs..."
    git lfs install
    git lfs track "*.parquet" "*.pt" "*.pth" "*.bin" "*.safetensors" "prompts.json"
fi

# Create HuggingFace model card
echo "📄 Creating HuggingFace model card..."
cat > README.md << 'EOF'
---
license: mit
tags:
- prompt-injection
- ai-safety
- security
- pytorch
- text-classification
---

# Prompt Detective

Prompt injection detection model for AI safety.

## Usage

```python
from prompt_detective import SimplePromptDetector

detector = SimplePromptDetector()
result = detector.predict("Your prompt here")
print(f"Is injection: {result['is_injection']}")
```

See [GitHub repository](https://github.com/yourusername/prompt-detective) for full documentation.
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Upload to HuggingFace: huggingface-cli upload your-username/prompt-detective ."
echo "2. For dataset: huggingface-cli upload your-username/prompt-detective-dataset prompts.json"
echo "3. For Spaces: Create new Space with Gradio and upload app.py + requirements_hf.txt"