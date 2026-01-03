# src/data_collator.py
"""
Custom Data Collators for SFT training with loss masking support.
"""

import torch
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from transformers import PreTrainedTokenizer
from transformers.data.data_collator import DataCollatorMixin


@dataclass
class DataCollatorForChatML(DataCollatorMixin):
    """
    Data collator that masks loss for non-assistant tokens in chat format.
    
    This collator:
    1. Pads sequences to the same length in a batch
    2. Creates labels where non-assistant tokens are masked with -100
    3. Preserves the original input_ids for model input
    
    Args:
        tokenizer: The tokenizer used for encoding
        model_type: "llama" or "qwen" to handle different chat templates
        pad_to_multiple_of: Pad to a multiple of this value for efficiency
        return_tensors: Type of tensors to return ("pt" for PyTorch)
    """
    
    tokenizer: PreTrainedTokenizer
    model_type: str = "llama"
    pad_to_multiple_of: Optional[int] = 8
    return_tensors: str = "pt"
    
    def __post_init__(self):
        # Set up response markers based on model type
        if self.model_type == "llama":
            # Llama uses "assistant<|end_header_id|>" pattern
            self.assistant_start_tokens = self.tokenizer.encode(
                "assistant<|end_header_id|>", add_special_tokens=False
            )
            # For Llama, we also need to handle the newline after the header
            self.assistant_prefix_tokens = self.tokenizer.encode(
                "\n\n", add_special_tokens=False
            )
        elif self.model_type == "qwen":
            # Qwen uses "<|im_start|>assistant\n" pattern
            self.assistant_start_tokens = self.tokenizer.encode(
                "<|im_start|>assistant\n", add_special_tokens=False
            )
            self.assistant_prefix_tokens = []
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        # Get end tokens
        self.eos_token_id = self.tokenizer.eos_token_id
        if self.model_type == "llama":
            # Llama uses <|eot_id|> to end assistant responses
            self.assistant_end_tokens = self.tokenizer.encode(
                "<|eot_id|>", add_special_tokens=False
            )
        else:
            # Qwen uses <|im_end|> to end responses
            self.assistant_end_tokens = self.tokenizer.encode(
                "<|im_end|>", add_special_tokens=False
            )
    
    def find_assistant_tokens(self, input_ids: List[int]) -> List[bool]:
        """
        Find which tokens belong to assistant responses.
        
        Returns a boolean mask where True indicates assistant tokens.
        """
        mask = [False] * len(input_ids)
        i = 0
        
        while i < len(input_ids):
            # Check if we're at the start of an assistant response
            if self._matches_pattern(input_ids, i, self.assistant_start_tokens):
                # Mark the start pattern
                i += len(self.assistant_start_tokens)
                
                # Skip the prefix tokens if any (like newlines after header)
                if self.assistant_prefix_tokens and i < len(input_ids):
                    if self._matches_pattern(input_ids, i, self.assistant_prefix_tokens):
                        i += len(self.assistant_prefix_tokens)
                
                # Mark all tokens as assistant tokens until we hit the end marker
                while i < len(input_ids):
                    # Check for end of assistant response
                    if self._matches_pattern(input_ids, i, self.assistant_end_tokens):
                        # Don't mark the end tokens themselves
                        break
                    
                    # Mark this token as part of assistant response
                    mask[i] = True
                    i += 1
            else:
                i += 1
        
        return mask
    
    def _matches_pattern(self, input_ids: List[int], start_idx: int, pattern: List[int]) -> bool:
        """Check if pattern matches at the given position."""
        if start_idx + len(pattern) > len(input_ids):
            return False
        return input_ids[start_idx:start_idx + len(pattern)] == pattern
    
    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """
        Collate features into a batch with loss masking.
        
        Args:
            features: List of features, each containing "input_ids" and "attention_mask"
        
        Returns:
            Batch dictionary with input_ids, attention_mask, and labels
        """
        # First, pad all sequences to the same length
        batch_size = len(features)
        max_length = max(len(f["input_ids"]) for f in features)
        
        # Pad to multiple of pad_to_multiple_of if specified
        if self.pad_to_multiple_of:
            max_length = (
                (max_length + self.pad_to_multiple_of - 1)
                // self.pad_to_multiple_of
                * self.pad_to_multiple_of
            )
        
        # Initialize tensors
        input_ids = torch.full(
            (batch_size, max_length),
            self.tokenizer.pad_token_id,
            dtype=torch.long
        )
        attention_mask = torch.zeros((batch_size, max_length), dtype=torch.long)
        labels = torch.full((batch_size, max_length), -100, dtype=torch.long)
        
        # Fill in the actual data
        for i, feature in enumerate(features):
            seq_len = len(feature["input_ids"])
            input_ids[i, :seq_len] = torch.tensor(feature["input_ids"], dtype=torch.long)
            attention_mask[i, :seq_len] = torch.tensor(feature["attention_mask"], dtype=torch.long)
            
            # Create labels with masking
            # Find assistant tokens
            assistant_mask = self.find_assistant_tokens(feature["input_ids"])
            
            # Create labels: copy input_ids but mask non-assistant tokens
            for j in range(seq_len):
                if assistant_mask[j]:
                    # For assistant tokens, use the actual token id
                    labels[i, j] = feature["input_ids"][j]
                # else: keep -100 (ignored in loss)
            
            # Shift labels for next-token prediction
            if seq_len > 1:
                labels[i, :seq_len-1] = labels[i, 1:seq_len].clone()
                labels[i, seq_len-1] = -100
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


@dataclass  
class DataCollatorForCausalLMWithMasking(DataCollatorMixin):
    """
    Alternative data collator that uses a simpler approach.
    
    This version expects the dataset to already have marked which tokens
    are from assistant responses, making it more flexible but requiring
    preprocessing.
    """
    
    tokenizer: PreTrainedTokenizer
    pad_to_multiple_of: Optional[int] = 8
    return_tensors: str = "pt"
    
    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """
        Collate features where each feature may contain:
        - input_ids: token ids
        - attention_mask: attention mask  
        - labels: labels with -100 for masked positions (optional)
        - loss_mask: boolean mask for which positions to compute loss (optional)
        """
        batch_size = len(features)
        max_length = max(len(f["input_ids"]) for f in features)
        
        # Pad to multiple if specified
        if self.pad_to_multiple_of:
            max_length = (
                (max_length + self.pad_to_multiple_of - 1)
                // self.pad_to_multiple_of
                * self.pad_to_multiple_of
            )
        
        # Initialize tensors
        input_ids = torch.full(
            (batch_size, max_length),
            self.tokenizer.pad_token_id,
            dtype=torch.long
        )
        attention_mask = torch.zeros((batch_size, max_length), dtype=torch.long)
        labels = torch.full((batch_size, max_length), -100, dtype=torch.long)
        
        for i, feature in enumerate(features):
            seq_len = len(feature["input_ids"])
            input_ids[i, :seq_len] = torch.tensor(feature["input_ids"], dtype=torch.long)
            attention_mask[i, :seq_len] = torch.tensor(feature["attention_mask"], dtype=torch.long)
            
            # Handle labels
            if "labels" in feature:
                # Use provided labels
                labels[i, :seq_len] = torch.tensor(feature["labels"], dtype=torch.long)
            elif "loss_mask" in feature:
                # Create labels from loss_mask
                loss_mask = feature["loss_mask"]
                for j in range(seq_len - 1):
                    if loss_mask[j]:
                        labels[i, j] = feature["input_ids"][j + 1]
            else:
                # No masking, standard causal LM
                labels[i, :seq_len-1] = torch.tensor(feature["input_ids"][1:], dtype=torch.long)
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }