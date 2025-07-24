set -x
export USE_SGLANG=0
export DATA_HOME=/home/lg/workflow_tooluse/Flow_RL/Test_FILE/verl_support/data
# export CUDA_DEVICE_MAX_CONNECTIONS=1 # For megatron communication/computation overlapping
export HYDRA_FULL_ERROR=1
# INFO for 小狼: 这里改数据集路径
gsm8k_train_path=$DATA_HOME/gsm8k_verl_train.parquet
gsm8k_test_path=$DATA_HOME/gsm8k_verl_test.parquet
mbpp_train_path=$DATA_HOME/mbpp_verl_train.parquet
mbpp_test_path=$DATA_HOME/mbpp_verl_test.parquet

train_files="['$gsm8k_train_path', '$mbpp_train_path']"
test_files="['$gsm8k_test_path', '$mbpp_test_path']"

# actor_rollout_ref.model.path设置模型路径
#其他参数跑起来再改
python3 -m verl.trainer.main_ppo --config-path=config \
    --config-name='ppo_trainer.yaml'\
    algorithm.adv_estimator=grpo \
    data.train_files="$train_files" \
    data.val_files="$test_files" \
    data.train_batch_size=2 \
    data.max_prompt_length=2048 \
    data.max_response_length=4096 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    actor_rollout_ref.model.path=/data/pretrained_models/mistral-7B-v0.1 \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=1 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
    actor_rollout_ref.rollout.n=5 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console","wandb"]' \
    trainer.project_name='verl_grpo_example_gsm8k_math' \
    trainer.experiment_name='deepseek_llm_7b_math_dp' \
    trainer.n_gpus_per_node=1 \
    trainer.nnodes=1 \
    trainer.save_freq=20 \
    trainer.test_freq=5 \
    trainer.total_epochs=15 $@
