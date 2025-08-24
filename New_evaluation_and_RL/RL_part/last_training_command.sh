#!/bin/bash
# VERL RL训练命令 - 生成时间: 2025-08-23 21:00:24

# 设置环境变量
export USE_SGLANG=1
export NCCL_DEBUG=INFO
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

# 执行训练命令
python /nas/ganluo/Flow_RL/verl/verl/trainer/main_ppo.py \
  --config-path=config \
  --config-name=ppo_trainer.yaml \
  'data.train_files=["/nas/ganluo/Flow_RL/New_evaluation_and_RL/parquet_and_jsonl_data/RL/train.parquet"]' \
  'data.val_files=["/nas/ganluo/Flow_RL/New_evaluation_and_RL/parquet_and_jsonl_data/RL/test.parquet"]' \
  data.train_batch_size=16 \
  data.max_prompt_length=8192 \
  data.max_response_length=8192 \
  data.filter_overlong_prompts=true \
  data.truncation=error \
  actor_rollout_ref.model.path=/nas/models/Qwen3-8B \
  actor_rollout_ref.model.enable_gradient_checkpointing=true \
  actor_rollout_ref.model.trust_remote_code=false \
  actor_rollout_ref.actor.optim.lr=5e-7 \
  actor_rollout_ref.actor.ppo_mini_batch_size=8 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2 \
  actor_rollout_ref.actor.use_kl_loss=true \
  actor_rollout_ref.actor.kl_loss_coef=0.001 \
  actor_rollout_ref.actor.kl_loss_type=low_var_kl \
  actor_rollout_ref.actor.entropy_coeff=0 \
  actor_rollout_ref.actor.use_torch_compile=false \
  'actor_rollout_ref.actor.checkpoint.save_contents=["model","extra"]' \
  'actor_rollout_ref.actor.checkpoint.load_contents=["model","extra"]' \
  actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=2 \
  actor_rollout_ref.rollout.n=2 \
  actor_rollout_ref.rollout.name=sglang \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
  actor_rollout_ref.hybrid_engine=true \
  actor_rollout_ref.rollout.temperature=0.6 \
  actor_rollout_ref.rollout.top_p=0.95 \
  actor_rollout_ref.rollout.top_k=20 \
  actor_rollout_ref.rollout.min_p=0.0 \
  actor_rollout_ref.model.custom_chat_template=auto \
  ++actor_rollout_ref.rollout.engine_kwargs.sglang.reasoning_parser=qwen3 \
  ++actor_rollout_ref.rollout.engine_kwargs.sglang.enable_thinking=true \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=2 \
  actor_rollout_ref.ref.use_torch_compile=false \
  'critic.checkpoint.save_contents=["model","extra"]' \
  'critic.checkpoint.load_contents=["model","extra"]' \
  algorithm.adv_estimator=grpo \
  algorithm.use_kl_in_reward=false \
  trainer.total_epochs=3 \
  trainer.n_gpus_per_node=8 \
  trainer.nnodes=1 \
  trainer.save_freq=10 \
  trainer.test_freq=2 \
  trainer.critic_warmup=0 \
  trainer.project_name=verl_grpo_h100_test \
  trainer.experiment_name=qwen2.5_7b_h100_8gpu_test \
  ++trainer.max_ckpt_num=3 \
  ++trainer.save_on_each_node=false \
  '++trainer.logger=["console","wandb"]' \
  ++trainer.log_freq=1 \
  ++trainer.log_to_wandb_every_n_steps=1 \
  '++trainer.wandb_tags=["rl","ppo","qwen2.5"]' \
  ++trainer.wandb_notes="PPO training with ScoreFlow rewards" \
  ++trainer.wandb_save_code=true \
  ++trainer.wandb_log_model=false \
  ++trainer.default_local_dir=/nas/ganluo/Flow_RL/rl_out/checkpoints \
  ++reward_model.reward_manager=prime \
  ++custom_reward_function.path=/nas/ganluo/Flow_RL/New_evaluation_and_RL/RL_part/scoreflow_reward_client.py \
  ++custom_reward_function.name=compute_score \

