#!/usr/bin/env python3
"""
VERL Training Parameters Generator
生成VERL训练所需的所有参数
"""

import yaml
import sys
from pathlib import Path


def generate_training_params(config_file):
    """生成VERL训练参数"""
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # 获取project_root
    project_root = Path(config.get('project_root', str(Path(config_file).parent.parent)))

    # 获取RL训练配置
    rl_config = config.get('rl_training', {})

    # 构建参数列表
    params = []

    # 数据配置
    data_config = rl_config.get('data', {})
    train_files = data_config.get('train_files')
    test_files = data_config.get('test_files')

    # 构建数据文件的完整路径 - Hydra列表语法，需要整体加单引号
    if train_files:
        train_path = project_root / train_files
        params.append(f'$$LIST$$data.train_files=["{train_path}"]$$LIST$$')

    if test_files:
        test_path = project_root / test_files
        params.append(f'$$LIST$$data.val_files=["{test_path}"]$$LIST$$')

    # 添加其他数据参数
    params.append(f'data.train_batch_size={data_config.get("train_batch_size", 16)}')
    params.append(f'data.max_prompt_length={data_config.get("max_prompt_length", 8192)}')
    params.append(f'data.max_response_length={data_config.get("max_response_length", 8192)}')
    params.append(f'data.filter_overlong_prompts={str(data_config.get("filter_overlong_prompts", True)).lower()}')
    
    truncation = data_config.get("truncation", "error")
    params.append(f'data.truncation={truncation}')

    # 模型配置
    model_config = rl_config.get('model', {})
    model_path = model_config.get('base_model_path', '/nas/models/Qwen2.5-7B-Instruct')
    params.append(f'actor_rollout_ref.model.path={model_path}')
    params.append(f'actor_rollout_ref.model.enable_gradient_checkpointing={str(model_config.get("enable_gradient_checkpointing", True)).lower()}')
    params.append(f'actor_rollout_ref.model.trust_remote_code={str(model_config.get("trust_remote_code", False)).lower()}')

    # Actor配置
    actor_config = rl_config.get('actor', {})
    learning_rate = actor_config.get("learning_rate", "5e-7")
    params.append(f'actor_rollout_ref.actor.optim.lr={learning_rate}')
    params.append(f'actor_rollout_ref.actor.ppo_mini_batch_size={actor_config.get("ppo_mini_batch_size", 8)}')
    params.append(f'actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu={actor_config.get("ppo_micro_batch_size_per_gpu", 2)}')
    params.append(f'actor_rollout_ref.actor.use_kl_loss={str(actor_config.get("use_kl_loss", True)).lower()}')
    params.append(f'actor_rollout_ref.actor.kl_loss_coef={actor_config.get("kl_loss_coef", 0.001)}')
    
    kl_loss_type = actor_config.get("kl_loss_type", "low_var_kl")
    params.append(f'actor_rollout_ref.actor.kl_loss_type={kl_loss_type}')
    params.append(f'actor_rollout_ref.actor.entropy_coeff={actor_config.get("entropy_coeff", 0)}')
    params.append(f'actor_rollout_ref.actor.use_torch_compile={str(actor_config.get("use_torch_compile", False)).lower()}')

    # Actor Checkpoint配置
    checkpoint_config = actor_config.get('checkpoint', {})
    if checkpoint_config:
        save_contents = checkpoint_config.get('save_contents', ['model', 'optimizer', 'extra'])
        load_contents = checkpoint_config.get('load_contents', save_contents)
        
        # Hydra列表格式：["item1","item2","item3"] - 需要整体加单引号
        save_contents_str = '[' + ','.join([f'"{item}"' for item in save_contents]) + ']'
        load_contents_str = '[' + ','.join([f'"{item}"' for item in load_contents]) + ']'
        params.append(f"$$LIST$$actor_rollout_ref.actor.checkpoint.save_contents={save_contents_str}$$LIST$$")
        params.append(f"$$LIST$$actor_rollout_ref.actor.checkpoint.load_contents={load_contents_str}$$LIST$$")

    # Rollout配置
    rollout_config = rl_config.get('rollout', {})
    params.append(f'actor_rollout_ref.rollout.tensor_model_parallel_size={rollout_config.get("tensor_model_parallel_size", 2)}')
    params.append(f'actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu={rollout_config.get("log_prob_micro_batch_size_per_gpu", 2)}')
    params.append(f'actor_rollout_ref.rollout.n={rollout_config.get("n", 2)}')
    
    rollout_name = rollout_config.get("name", "sglang")
    params.append(f'actor_rollout_ref.rollout.name={rollout_name}')
    params.append(f'actor_rollout_ref.rollout.gpu_memory_utilization={model_config.get("gpu_memory_utilization", 0.5)}')
    params.append(f'actor_rollout_ref.hybrid_engine={str(rollout_config.get("hybrid_engine", True)).lower()}')
    
    # 标准Generation参数 - 如果配置中提供了这些参数
    if 'temperature' in rollout_config:
        params.append(f'actor_rollout_ref.rollout.temperature={rollout_config["temperature"]}')
    if 'top_p' in rollout_config:
        params.append(f'actor_rollout_ref.rollout.top_p={rollout_config["top_p"]}')
    if 'top_k' in rollout_config:
        params.append(f'actor_rollout_ref.rollout.top_k={rollout_config["top_k"]}')
    
    # 注意：以下参数已被移除，因为它们不是VERL标准参数
    # - min_p: 不在VERL标准rollout配置中
    # - custom_chat_template: 可能导致配置错误
    # - reasoning_parser: SGLang不识别此参数
    # - enable_thinking: SGLang不识别此参数

    # Reference模型配置
    ref_config = rl_config.get('ref', {})
    params.append(f'actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu={ref_config.get("log_prob_micro_batch_size_per_gpu", 2)}')
    params.append(f'actor_rollout_ref.ref.use_torch_compile={str(ref_config.get("use_torch_compile", False)).lower()}')

    # Critic配置（如果存在）
    critic_config = rl_config.get('critic', {})
    if critic_config:
        critic_checkpoint = critic_config.get('checkpoint', {})
        if critic_checkpoint:
            save_contents = critic_checkpoint.get('save_contents', ['model', 'optimizer', 'extra'])
            load_contents = critic_checkpoint.get('load_contents', save_contents)
            save_contents_str = '[' + ','.join([f'"{item}"' for item in save_contents]) + ']'
            load_contents_str = '[' + ','.join([f'"{item}"' for item in load_contents]) + ']'
            params.append(f"$$LIST$$critic.checkpoint.save_contents={save_contents_str}$$LIST$$")
            params.append(f"$$LIST$$critic.checkpoint.load_contents={load_contents_str}$$LIST$$")

    # 算法配置
    algorithm_config = rl_config.get('algorithm', {})
    adv_estimator = algorithm_config.get("adv_estimator", "grpo")
    params.append(f'algorithm.adv_estimator={adv_estimator}')
    params.append(f'algorithm.use_kl_in_reward={str(algorithm_config.get("use_kl_in_reward", False)).lower()}')

    # 训练器配置
    trainer_config = rl_config.get('trainer', {})
    params.append(f'trainer.total_epochs={trainer_config.get("total_epochs", 3)}')
    params.append(f'trainer.n_gpus_per_node={trainer_config.get("n_gpus_per_node", 8)}')
    params.append(f'trainer.nnodes={trainer_config.get("nnodes", 1)}')
    params.append(f'trainer.save_freq={trainer_config.get("save_freq", 10)}')
    params.append(f'trainer.test_freq={trainer_config.get("test_freq", 2)}')
    params.append(f'trainer.critic_warmup={trainer_config.get("critic_warmup", 0)}')
    
    project_name = trainer_config.get("project_name", "verl_grpo_h100_test")
    params.append(f'trainer.project_name={project_name}')
    
    experiment_name = trainer_config.get("experiment_name", "qwen2.5_7b_h100_8gpu_test")
    params.append(f'trainer.experiment_name={experiment_name}')

    # Checkpoint管理配置 - 使用++前缀添加新配置
    max_ckpt_num = trainer_config.get('max_ckpt_num', 3)
    if max_ckpt_num is not None:
        params.append(f'++trainer.max_ckpt_num={max_ckpt_num}')
    params.append(f'++trainer.save_on_each_node={str(trainer_config.get("save_on_each_node", False)).lower()}')

    # 日志配置 - logger需要++前缀和特殊引号处理
    logger_config = trainer_config.get('logger', ['console'])
    if isinstance(logger_config, list):
        logger_str = '[' + ','.join([f'"{item}"' for item in logger_config]) + ']'
    else:
        logger_str = '["console"]'
    params.append(f"$$LIST$$++trainer.logger={logger_str}$$LIST$$")

    # 日志频率配置 - 使用++前缀
    log_freq = trainer_config.get('log_freq', 1)
    params.append(f'++trainer.log_freq={log_freq}')

    log_to_wandb_every_n_steps = trainer_config.get('log_to_wandb_every_n_steps', 1)
    params.append(f'++trainer.log_to_wandb_every_n_steps={log_to_wandb_every_n_steps}')

    # WandB配置
    wandb_config = trainer_config.get('wandb_config', {})
    if wandb_config and 'wandb' in logger_config:
        if wandb_config.get('entity'):
            entity = wandb_config["entity"]
            params.append(f'trainer.wandb_entity={entity}')
        if wandb_config.get('tags'):
            tags_str = '[' + ','.join([f'"{tag}"' for tag in wandb_config['tags']]) + ']'
            params.append(f"$$LIST$$++trainer.wandb_tags={tags_str}$$LIST$$")
        if wandb_config.get('notes'):
            # 处理包含空格的notes，保持原始格式但用双引号包围
            notes = wandb_config["notes"]
            params.append(f'++trainer.wandb_notes="{notes}"')
        params.append(f'++trainer.wandb_save_code={str(wandb_config.get("save_code", True)).lower()}')
        params.append(f'++trainer.wandb_log_model={str(wandb_config.get("log_model", False)).lower()}')

    # 检查点目录
    checkpoint_dir = trainer_config.get('default_local_dir', 'rl_out/checkpoints')
    if not Path(checkpoint_dir).is_absolute():
        checkpoint_dir = project_root / checkpoint_dir
    params.append(f'++trainer.default_local_dir={checkpoint_dir}')

    # 奖励配置
    reward_config = rl_config.get('reward', {})
    reward_manager = reward_config.get("reward_manager", "prime")
    params.append(f'++reward_model.reward_manager={reward_manager}')

    # 自定义奖励函数
    custom_reward = reward_config.get('custom_reward_function', {})
    if custom_reward.get('enabled', False):
        reward_path = custom_reward.get('path')
        if reward_path:
            reward_path = project_root / reward_path
            params.append(f'++custom_reward_function.path={reward_path}')
            name = custom_reward.get("name", "compute_score")
            params.append(f'++custom_reward_function.name={name}')

    # 输出参数 - 每行一个参数，便于bash处理
    for param in params:
        print(param)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python generate_training_params.py <config_file>", file=sys.stderr)
        sys.exit(1)
    
    config_file = sys.argv[1]
    if not Path(config_file).exists():
        print(f"配置文件不存在: {config_file}", file=sys.stderr)
        sys.exit(1)
    
    generate_training_params(config_file)