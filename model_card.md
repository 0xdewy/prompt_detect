---
language:
- en
license: mit
library_name: pytorch
tags:
- prompt-injection
- ai-safety
- security
- content-moderation
datasets:
- prompt-detective-dataset
metrics:
- accuracy
- f1
- precision
- recall
---

# Prompt Detective: Prompt Injection Detection Model

## Model Description

Prompt Detective is a convolutional neural network (CNN) model designed to detect prompt injection attacks in AI systems. The model analyzes text input and classifies it as either a safe prompt or a potential prompt injection attempt.

**Model Architecture**: CNN-based text classifier with embedding layer, convolutional layers, and fully connected layers.

**Intended Use**: This model is intended for use in AI safety pipelines to filter out malicious prompt injection attempts before they reach language models.

## Training Data

The model was trained on an aggregated dataset of:
- **6,362 safe prompts** (37.0%)
- **10,833 injection examples** (63.0%)
- **Total: 17,195 examples** (English and Spanish)

The dataset includes various types of prompt injection attacks:
- Direct instruction overrides
- Context manipulation
- Social engineering attempts
- Encoded/obfuscated injections
- Role-playing jailbreaks
- Multi-language injection attempts

## Usage

### Installation
```bash
pip install prompt-detective
```

### Basic Usage
```python
from prompt_detective import SimplePromptDetector

# Load the detector with pre-trained model
detector = SimplePromptDetector()

# Analyze text for prompt injection
result = detector.predict("Ignore all previous instructions")
print(f"Is injection: {result['is_injection']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Command Line Interface
```bash
# Analyze text
prompt-detective predict "Ignore all previous instructions"

# Analyze file
prompt-detective predict --file input.txt

# Train a new model
prompt-detective train
```

## Performance

The model achieves the following performance metrics on the test set:
- **Accuracy**: ~95%
- **F1 Score**: ~0.92
- **Precision**: ~0.89
- **Recall**: ~0.95

## Limitations

1. **Class Distribution**: The dataset has more injection examples than safe prompts (63% vs 37%)
2. **Evolving Threats**: New prompt injection techniques may not be covered
3. **False Positives**: Some legitimate but unusual prompts may be flagged
4. **Context Limitations**: The model analyzes text in isolation without broader conversation context
5. **Language Coverage**: Better performance on English than Spanish prompts

## Ethical Considerations

This model is designed to enhance AI safety by detecting malicious prompt injections. However, users should:

1. **Not rely solely on automated detection** - Human review is recommended for critical applications
2. **Consider false positives** - Legitimate but unusual prompts may be incorrectly flagged
3. **Regularly update the model** - As new injection techniques emerge, the model should be retrained
4. **Respect user privacy** - Only analyze text where appropriate consent has been obtained

## Training Details

- **Framework**: PyTorch
- **Training Time**: ~30 minutes on GPU
- **Batch Size**: 32
- **Learning Rate**: 0.001
- **Optimizer**: Adam
- **Loss Function**: Binary Cross-Entropy

## Citation

If you use this model in your research, please cite:

```bibtex
@software{prompt_detective_2024,
  title = {Prompt Detective: Prompt Injection Detection Model},
  author = {Prompt Detective Contributors},
  year = {2024},
  url = {https://github.com/yourusername/prompt-detective}
}
```

## License

MIT License

## Contact

For questions, issues, or contributions, please open an issue on the [GitHub repository](https://github.com/yourusername/prompt-detective).