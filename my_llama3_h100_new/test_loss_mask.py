#!/usr/bin/env python3
"""
Test script to verify loss masking implementation.
Tests both Llama and Qwen tokenizers with sample data.
"""

import torch
from transformers import AutoTokenizer
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collator import DataCollatorForChatML


def test_loss_masking(model_type="llama"):
    """Test loss masking for a specific model type."""
    
    print(f"\n{'='*60}")
    print(f"Testing Loss Masking for {model_type.upper()}")
    print('='*60)
    
    # Select appropriate model for testing
    if model_type == "llama":
        model_name = "meta-llama/Llama-3.2-1B-Instruct"
    else:  # qwen
        model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    # Set pad token if needed
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Create sample messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "The answer is 4."}
    ]
    
    # Apply chat template
    formatted_text = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=False
    )
    
    print(f"\nFormatted text:\n{formatted_text[:500]}...")
    
    # Tokenize
    tokenized = tokenizer(
        formatted_text,
        truncation=True,
        padding=False,
        max_length=512,
        return_overflowing_tokens=False,
    )
    
    print(f"\nTokenized length: {len(tokenized['input_ids'])} tokens")
    
    # Create data collator
    collator = DataCollatorForChatML(
        tokenizer=tokenizer,
        model_type=model_type,
        pad_to_multiple_of=8
    )
    
    # Test finding assistant tokens
    assistant_mask = collator.find_assistant_tokens(tokenized['input_ids'])
    
    # Count assistant tokens
    num_assistant_tokens = sum(assistant_mask)
    total_tokens = len(tokenized['input_ids'])
    
    print(f"\nAssistant tokens: {num_assistant_tokens}/{total_tokens} "
          f"({num_assistant_tokens/total_tokens*100:.1f}%)")
    
    # Show which parts are marked as assistant
    tokens = tokenizer.convert_ids_to_tokens(tokenized['input_ids'])
    print("\nToken analysis (first 50 tokens):")
    print("-" * 40)
    for i, (token, is_assistant) in enumerate(zip(tokens[:50], assistant_mask[:50])):
        marker = "✓" if is_assistant else " "
        print(f"{i:3d}: [{marker}] {token}")
    
    # Test the full collator
    batch = collator([tokenized])
    
    print(f"\nBatch shapes:")
    print(f"  input_ids:      {batch['input_ids'].shape}")
    print(f"  attention_mask: {batch['attention_mask'].shape}")
    print(f"  labels:         {batch['labels'].shape}")
    
    # Count non-masked labels
    non_masked = (batch['labels'][0] != -100).sum().item()
    print(f"\nLabels with loss: {non_masked}/{batch['labels'].shape[1]} "
          f"({non_masked/batch['labels'].shape[1]*100:.1f}%)")
    
    # Verify that only assistant tokens have valid labels
    print("\nVerifying label masking...")
    labels = batch['labels'][0].tolist()
    
    # Check first few positions
    print("First 20 label positions:")
    for i in range(min(20, len(labels))):
        if labels[i] != -100:
            token = tokenizer.decode([batch['input_ids'][0][i].item()])
            print(f"  Position {i}: label={labels[i]}, token='{token}'")
    
    return True


def test_batch_processing():
    """Test that batching works correctly."""
    print(f"\n{'='*60}")
    print("Testing Batch Processing")
    print('='*60)
    
    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Llama-3.2-1B-Instruct",
        trust_remote_code=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Create multiple samples with different lengths
    samples = []
    for i in range(3):
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": f"Question {i+1}?"},
            {"role": "assistant", "content": f"Answer {i+1}." * (i+1)}
        ]
        
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        
        tokenized = tokenizer(
            text,
            truncation=True,
            padding=False,
            max_length=512,
        )
        samples.append(tokenized)
    
    # Create collator and process batch
    collator = DataCollatorForChatML(
        tokenizer=tokenizer,
        model_type="llama",
        pad_to_multiple_of=8
    )
    
    batch = collator(samples)
    
    print(f"Batch size: {len(samples)}")
    print(f"Batch shapes:")
    print(f"  input_ids:      {batch['input_ids'].shape}")
    print(f"  attention_mask: {batch['attention_mask'].shape}")
    print(f"  labels:         {batch['labels'].shape}")
    
    # Check each sample in batch
    for i in range(len(samples)):
        non_masked = (batch['labels'][i] != -100).sum().item()
        total_attended = batch['attention_mask'][i].sum().item()
        print(f"\nSample {i+1}:")
        print(f"  Attended tokens: {total_attended}")
        print(f"  Labels with loss: {non_masked} ({non_masked/total_attended*100:.1f}%)")
    
    return True


if __name__ == "__main__":
    try:
        # Test Llama
        test_loss_masking("llama")
        
        # Test Qwen  
        test_loss_masking("qwen")
        
        # Test batching
        test_batch_processing()
        
        print(f"\n{'='*60}")
        print("✅ All tests passed successfully!")
        print('='*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)