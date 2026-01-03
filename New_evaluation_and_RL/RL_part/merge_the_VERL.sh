python -m verl.model_merger merge \
      --backend fsdp \
      --local_dir /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor \
      --target_dir /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor_hf_official