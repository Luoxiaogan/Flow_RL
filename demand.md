接下来, 需要做的事情是:

首先着眼于`./ScoreFlow/scripts/gsm8k`, `./ScoreFlow/scripts/mbpp`, `./Test_FILE/workflow_executor.py`, `./Test_FILE/workflow_generator.py`, `./Test_FILE/master_runner.py`, `./Test_FILE/run_workflow_system.sh`.
1. 检查里面的大小写适配问题, 我之前测试的时候会有出现`import GSM8K`的报错.
2. 路径依赖修改为相对路径
3. 进行小规模测试, using `./Test_FILE/run_workflow_system.sh`, 例如就执行一个datapoint.