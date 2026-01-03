#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Merge LoRA weights with base model
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import argparse
from pathlib import Path

def merge_lora_weights(
    base_model_path: str,
    lora_adapter_path: str,
    output_path: str,
    device_map: str = "auto",
    torch_dtype = torch.bfloat16
):
    """
    Merge LoRA adapter weights with base model
    
    Args:
        base_model_path: Path to base model
        lora_adapter_path: Path to LoRA adapter
        output_path: Path to save merged model
        device_map: Device mapping strategy
        torch_dtype: Data type for model weights
    """
    
    print(f"Loading base model from: {base_model_path}")
    print(f"Loading LoRA adapter from: {lora_adapter_path}")
    print(f"Output path: {output_path}")
    
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        trust_remote_code=True
    )
    
    # Load base model
    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch_dtype,
        device_map=device_map,
        trust_remote_code=True
    )
    
    # Load LoRA adapter
    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(
        base_model,
        lora_adapter_path,
        torch_dtype=torch_dtype,
        device_map=device_map
    )
    
    # Merge weights
    print("Merging weights...")
    model = model.merge_and_unload()
    
    # Save merged model
    print("Saving merged model...")
    model.save_pretrained(
        output_path,
        safe_serialization=True,
        max_shard_size="10GB"
    )
    
    # Save tokenizer
    print("Saving tokenizer...")
    tokenizer.save_pretrained(output_path)
    
    print(f"✅ Successfully merged model saved to: {output_path}")
    
    # Verify saved files
    saved_files = os.listdir(output_path)
    print(f"\nSaved files: {saved_files}")
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Merge LoRA adapter with base model")
    parser.add_argument(
        "--base_model_path",
        type=str,
        default="/nas/models/Qwen3-8B",
        help="Path to base model"
    )
    parser.add_argument(
        "--lora_adapter_path",
        type=str,
        default="/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/sft_output/Qwen3-8B_lora_new_0910/rank=8_lr=1.0e-5_epochs=2.0_bs=4_gc=6_not_inference_20250910_052536",
        help="Path to LoRA adapter (can be checkpoint-140 subdirectory or parent directory)"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/Merged_weight/Qwen3-8B/new",
        help="Path to save merged model"
    )
    parser.add_argument(
        "--use_checkpoint",
        action="store_true",
        help="Use checkpoint-140 subdirectory instead of parent directory"
    )
    parser.add_argument(
        "--dtype",
        type=str,
        default="bfloat16",
        choices=["float32", "float16", "bfloat16"],
        help="Data type for model weights"
    )
    
    args = parser.parse_args()
    
    # Adjust adapter path if using checkpoint
    if args.use_checkpoint:
        args.lora_adapter_path = os.path.join(args.lora_adapter_path, "checkpoint-140")
    
    # Convert dtype string to torch dtype
    dtype_map = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16
    }
    torch_dtype = dtype_map[args.dtype]
    
    # Merge weights
    merge_lora_weights(
        base_model_path=args.base_model_path,
        lora_adapter_path=args.lora_adapter_path,
        output_path=args.output_path,
        torch_dtype=torch_dtype
    )

if __name__ == "__main__":
    main()