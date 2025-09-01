启动:
```
tmux kill-server
tmux new -d -s api_proxy
tmux new -d -s reward_server
```
进入之后:
```
tmux attach -t api_proxy
source ~/.bashrc 
conda activate workflow
```