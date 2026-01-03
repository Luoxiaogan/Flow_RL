启动:
```
tmux kill-server
tmux new -d -s api_proxy
tmux new -d -s reward_server
tmux new -d -s rl
```
进入之后:
可能需要改一下conda:
```
export PATH="/root/miniforge3/envs/wf_rl/bin:$PATH"
export PATH="/root/miniforge3/envs/lg_workflow/bin:$PATH"
which python
```
最后
```
tmux attach -t api_proxy
source ~/.bashrc 
conda activate workflow
```
