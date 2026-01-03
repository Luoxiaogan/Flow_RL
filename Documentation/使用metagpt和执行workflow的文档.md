1. 请使用`workflow`环境:
```bash
conda activate workflow
```

2. 由于是本地安装在`/home/lg/workflow_tooluse/ScoreFlow/metagpt_local`的旧版本，所以在打开python文件的时候可以忽略`metagpt`相关的`import error`.

3. 如果要运行一个`workflow`, 需要termial在有`config2.yaml`的一级目录下运行，这个写了`api-key`. 目前在

`/home/lg/workflow_tooluse/Flow_RL/Test_FILE/config`

所以需要在`/home/lg/workflow_tooluse/Flow_RL/Test_FILE`下启动
```bash
cd /home/lg/workflow_tooluse/Flow_RL/Test_FILE
python /home/lg/workflow_tooluse/Flow_RL/Test_FILE/new_test.py
```