接下来, 需要做的事情是:

着眼于`./Test_FILE/ScoreFlow/scripts/humaneval`中的文件
1. 首先你可以查看测试中得到的: `./Test_FILE/workspace_human_eval/generated_workflows/humaneval`文件夹下的workflow, 我觉得太相似了
2. 对于condition里面的meta prompt, 是不是需要各种设计，来使得生成多样化的workflow呢?

对于3，你需要首先分析一下必要性，如果不必要，那么就不用改了.

3. 除了修改prompt. 你还可以考虑的是, 增加一个并行度: 一个选定的数据组合, 先按照前面的逻辑生成了一个workflow, 之后, 可以把这个workflow的代码打包加上给api，在原来的prompt后面再加一步，即生成一个和这个逻辑上不一样的. 并行度可以设置，默认为2. 命名就是0号变成了0_0;0_1.
   1. 这个主要需要修改`workflow_generator.py`, 因为是作为单个数据点的生成逻辑
   2. 然后由于根据并行度, 单个数据点生成的多个workflow都需要保存+测试, 因此可能需要修改其他的程序
   3. 接口上需要修改`master_runner.py` and `run_workflow_system_human_eval.sh`.