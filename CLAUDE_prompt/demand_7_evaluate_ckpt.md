本次我们的目的是，对于SFT之后的模型进行测试.
1. 代码应该在`test_checkpoint`里面进行书写
2. 我已经在`test_checkpoint`复制粘贴了需要的`Test_FILE/ScoreFlow`, `Test_FILE/config`. 
   1. As  `test_checkpoint/config`, `test_checkpoint/ScoreFlow`.
3. 我的思路是, 对于一个给定的ckpt的root, 应该用vllm把这个模型在一个server上启动(一个bash文件, 需要设定端口)
   1. 这个server首先默认选择cuda:7
4. 然后, 和`Test_FILE/master_runner.py`, `Test_FILE/workflow_executor.py`, `Test_FILE/workflow_generator.py`的逻辑相似
   1. 首先按照同样的方法组合prompt, 但是这次是输入给server，而不是api
   2. 之后, 得到server上模型返回的workflow.
   3. 之后, 可以对这个workflow做测试
   4. 这里的测试应该是可以调用`handelr.py`这样的模块来使用的
5. 最后整合成一个大的，可以硬编码参数的.sh文件, 应该是首先启动server, 然后组合prompt给server, 得到返回的workflow, 然后测试(这里调用api)
6. server使用vllm, 因此可以并行(batching), 可以设置一个并行度.
7. 测试的并行度可以学习`Test_FILE/master_runner.py`
8. 希望能够分离出对于server传递组合的prompt的模块，以及对于生成的workflow进行测试的模块。
   1. 因为后续训练RL，这两个模块可以直接复用
9. 最后写一个ckpt_test.md说明文档, in english
   1.  然后翻译一个ckpt_test_zh.md说明文档, in simplified chineses