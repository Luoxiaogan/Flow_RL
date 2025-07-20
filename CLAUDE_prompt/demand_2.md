接下来, 需要做的事情是:

着眼于`./ScoreFlow/scripts/gsm8k`, `./Test_FILE/workflow_executor.py`, `./Test_FILE/workflow_generator.py`, `./Test_FILE/master_runner.py`, `./Test_FILE/run_workflow_system.sh`.
1. 学习`./ScoreFlow/scripts/gsm8k`和`./ScoreFlow/scripts/mbpp`
2. 需要为`./ScoreFlow/scripts/humaneval`进行修改.
   1. 里面的`judger.py`和`extraction.py`没有用，我已经删掉了
   2. 除了修改`conditions.py`, `op_prompt.py`, `operator_an.py`, `operator.py`
   3. 还需要修改`handler.py`
   4. 你可以阅读`./Processed_dataset/human_eval`里面的`test.jsonl`的前三行来了解数据的结构, 注意这里human_eval只有test的数据
   5. 不需要完全阅读jsonl文件，因为太大了.