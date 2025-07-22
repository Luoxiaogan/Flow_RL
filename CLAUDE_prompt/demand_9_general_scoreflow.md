1. `test_checkpoint/ScoreFlow`和`Test_FILE/ScoreFlow`都使用了scoreflow
2. 理论上他们都是一样的调用.
   1. 这一点你需要阅读一下`test_checkpoint/ckpt_test.md` and `/Test_FILE/V2版本.md` and `Test_FILE/run_workflow_zh.md`.
3. 那么是否可以在`/Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow`这里, 那么以后只需要修改这个了.
4. 我已经复制了一份到`/Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow`.
   1. 你先不动`test_checkpoint/ScoreFlow`和`Test_FILE/ScoreFlow`
   2. 而是修改`test_checkpoint`和`Test_FILE`里面import `ScoreFlow`的逻辑
   3. 使得都import `./ScoreFlow`
