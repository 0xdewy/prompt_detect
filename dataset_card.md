---
language:
- en
task_categories:
- text-classification
task_ids:
- prompt-injection-detection
- ai-safety
size_categories:
- 1K<n<10K
license: mit
multilinguality:
- monolingual
source_datasets:
- original
pretty_name: Prompt Detective Dataset
dataset_info:
  features:
  - name: text
    dtype: string
  - name: is_injection
    dtype: bool
  splits:
  - name: train
    num_bytes: 18006103
    num_examples: 1044
  configs:
  - config_name: default
    data_files:
    - split: train
      path: prompts.json
tags:
- prompt-injection
- ai-safety
- security
- content-moderation
---

# Prompt Detective Dataset

## Dataset Description

A curated dataset of 1,044 text prompts labeled for prompt injection detection. The dataset contains examples of both safe prompts and various types of prompt injection attacks.

### Dataset Summary

- **Total Examples**: 1,044
- **Safe Prompts**: 937 (89.7%)
- **Injection Examples**: 107 (10.3%)
- **Average Text Length**: ~500 characters
- **Language**: English

### Supported Tasks

- **Prompt Injection Detection**: Binary classification task to identify whether a text prompt contains a prompt injection attack.

### Languages

The text in the dataset is in English.

## Dataset Structure

### Data Fields

- `text`: The text prompt (string)
- `is_injection`: Boolean label indicating whether the text is a prompt injection (True) or safe prompt (False)

### Data Splits

The dataset is provided as a single split suitable for training and evaluation.

## Dataset Creation

### Curation Rationale

The dataset was created to train models for detecting prompt injection attacks in AI systems. Prompt injection is a security vulnerability where malicious users craft inputs that cause AI systems to bypass safety guidelines.

### Source Data

The dataset was created through:
1. **Manual collection** of known prompt injection examples from security research
2. **Generation** of safe prompts covering various topics and styles
3. **Synthetic creation** of injection examples using pattern-based approaches

### Annotations

#### Annotation process
Each example was manually reviewed and labeled by AI safety researchers.

#### Who are the annotators?
The dataset was annotated by the Prompt Detective project team.

### Personal and Sensitive Information

The dataset contains synthetic and curated examples. No real user data or personally identifiable information is included.

## Considerations for Using the Data

### Social Impact of Dataset

This dataset supports the development of AI safety tools that can help prevent malicious use of language models.

### Discussion of Biases

The dataset may have biases including:
- **Class imbalance**: More safe examples than injections
- **Style bias**: Injection examples may follow certain patterns
- **Topic coverage**: Limited to certain types of injections

### Other Known Limitations

1. **Evolving threats**: New prompt injection techniques may not be represented
2. **Context limitations**: Examples are analyzed in isolation without conversation history
3. **False positive risk**: Some legitimate but unusual prompts may resemble injections

## Additional Information

### Dataset Curators

The Prompt Detective project team.

### Licensing Information

MIT License

### Citation Information

```bibtex
@dataset{prompt_detective_dataset_2024,
  title = {Prompt Detective Dataset},
  author = {Prompt Detective Contributors},
  year = {2024},
  url = {https://github.com/yourusername/prompt-detective}
}
```

### Contributions

Thanks to all contributors who helped create and curate this dataset.