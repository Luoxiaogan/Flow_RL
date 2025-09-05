#!/bin/bash
# merge_lora.sh
set -e

LORA_DIR="/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/sft_output/Qwen3-8B_lora/train_with_generation_20250903_062349/checkpoint-164"
OUT_DIR="/nas/ganluo/Flow_RL/llama_factory_qwen3_thinking_lora/Merged_weight/Qwen3-8B/rank_8_epoch_2"
BASE_MODEL="/nas/models/Qwen3-8B"

echo "Merging LoRA weights..."
python -c "
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained('$BASE_MODEL', torch_dtype='auto', device_map='auto')
model = PeftModel.from_pretrained(model, '$LORA_DIR')
model = model.merge_and_unload()
model.save_pretrained('$OUT_DIR')

tok = AutoTokenizer.from_pretrained('$BASE_MODEL')
tok.save_pretrained('$OUT_DIR')

print('✅ merged checkpoint saved to', '$OUT_DIR')
"

echo ""
echo "合并完成，可直接在 RL 代码里使用:"
echo "  base_model_path = \"$OUT_DIR\""
