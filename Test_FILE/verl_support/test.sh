set -x
export USE_SGLANG=1
# export DATA_HOME=/home/lg/workflow_tooluse/Flow_RL/Test_FILE/verl_support/data
export DATA_HOME=/nas/ganluo/Flow_RL/Test_FILE/verl_support/data
# export CUDA_DEVICE_MAX_CONNECTIONS=1 # For megatron communication/computation overlapping
export HYDRA_FULL_ERROR=1

# 添加调试和修复 NCCL 通信问题的环境变量
export NCCL_DEBUG=INFO
export NCCL_P2P_DISABLE=1
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export TORCH_CUDA_ARCH_LIST="8.0"
export CUDA_LAUNCH_BLOCKING=1
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
    data.train_batch_size=16 \
    data.max_prompt_length=2048 \
    data.max_response_length=4096 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    actor_rollout_ref.model.path=/nas/models/qwen2.5-math-7B_instruct \
    actor_rollout_ref.actor.optim.lr=5e-7 \
    actor_rollout_ref.actor.ppo_mini_batch_size=4 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.001 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=sglang \
    actor_rollout_ref.hybrid_engine=False \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.3 \
    actor_rollout_ref.rollout.n=2 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.actor.use_torch_compile=False \
    actor_rollout_ref.ref.use_torch_compile=False \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console","wandb"]' \
    trainer.project_name='verl_grpo_h100_test' \
    trainer.experiment_name='qwen2.5_7b_math_h100_8gpu_test' \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=1 \
    trainer.save_freq=10 \
    trainer.test_freq=2 \
    trainer.total_epochs=3 $@
