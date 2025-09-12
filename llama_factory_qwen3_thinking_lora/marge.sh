#!/bin/bash

# Merge LoRA weights with base model
# Usage: bash merge_lora.sh

# Set paths
BASE_MODEL_PATH="/nas/models/Qwen3-8B"
LORA_ADAPTER_PATH="/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/sft_output/Qwen3-8B_lora_new_0910/rank=8_lr=1.0e-5_epochs=2.0_bs=4_gc=6_not_inference_20250910_052536"
OUTPUT_PATH="/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/Merged_weight/Qwen3-8B/new_0910"

# Choose which adapter to use (parent directory or checkpoint-140)
# Option 1: Use the final adapter in parent directory
# ADAPTER_PATH="$LORA_ADAPTER_PATH"

# Option 2: Use checkpoint-140 (uncomment if needed)
ADAPTER_PATH="$LORA_ADAPTER_PATH/checkpoint-140"

echo "========================================="
echo "Merging LoRA weights with base model"
echo "========================================="
echo "Base model: $BASE_MODEL_PATH"
echo "LoRA adapter: $ADAPTER_PATH"
echo "Output path: $OUTPUT_PATH"
echo "========================================="

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_PATH

# Run merge script
python merge_lora.py \
    --base_model_path "$BASE_MODEL_PATH" \
    --lora_adapter_path "$ADAPTER_PATH" \
    --output_path "$OUTPUT_PATH" \
    --dtype bfloat16

echo "========================================="
echo "Merge completed!"
echo "Merged model saved to: $OUTPUT_PATH"
echo "========================================="

# List output files
echo "Output files:"
ls -lh $OUTPUT_PATH/