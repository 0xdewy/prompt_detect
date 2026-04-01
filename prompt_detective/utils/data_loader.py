"""
Data loading utilities for prompt injection detection.
"""

from typing import Dict, List

import torch
from torch.utils.data import Dataset


class PromptDataset(Dataset):
    """Simple dataset for prompt injection data."""

    def __init__(self, data: List[Dict], processor):
        self.data = data
        self.processor = processor

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item["text"]
        label = item["label"]

        token_ids = self.processor.encode(text)

        return {
            "input_ids": torch.tensor(token_ids, dtype=torch.long),
            "label": torch.tensor(label, dtype=torch.long),
        }
