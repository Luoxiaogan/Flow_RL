export CUDA_VISIBLE_DEVICES=0

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
# OUTPUT_DIR="saves/Qwen3-8B-Thinking/lora/train_simple_2_${TIMESTAMP}"
OUTPUT_DIR="saves/Qwen3-8B-Thinking/lora/train_simple_2_20250901_200042"

llamafactory-cli train \
    --stage sft \
    --do_train True \
    --model_name_or_path Qwen/Qwen3-8B \
    --preprocessing_num_workers 16 \
    --finetuning_type lora \
    --template qwen3 \
    --flash_attn auto \
    --dataset_dir data \
    --dataset sft_data_simple \
    --cutoff_len 6500 \
    --learning_rate 5e-5 \
    --num_train_epochs 1.0 \
    --max_samples 100000 \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --lr_scheduler_type cosine \
    --max_grad_norm 1.0 \
    --logging_steps 5 \
    --save_steps 10 \
    --warmup_steps 20 \
    --packing False \
    --enable_thinking True \
    --report_to none \
    --output_dir "$OUTPUT_DIR" \
    --bf16 True \
    --plot_loss True \
    --trust_remote_code True \
    --ddp_timeout 180000000 \
    --include_num_input_tokens_seen True \
    --optim adamw_torch \
    --lora_rank 8 \
    --lora_alpha 16 \
    --lora_dropout 0 \
    --lora_target all \
    --sample_generation_steps 2 \
    --sample_generation_num 2 \
    --sample_generation_max_tokens 4096 \
    --sample_generation_temperature 1.0 \
    --save_generation_samples true