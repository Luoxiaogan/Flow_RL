本次我们的目的是，对于`Test_FILE/ScoreFlow/scripts/gsm8k`and`Test_FILE/ScoreFlow/scripts/humaneval` 里面的operator/prompt/code进行修改和增加
1. 目的是, 目前的operator, 虽然是api自己输出的prompt, 加上operator里面提前设置好的prompt. 
2. 但是可能对于生成workflow的过程来说, 在给定的operator里面其实很难修改逻辑
3. 并且由于我们要求, workflow在给llm的api的prompt里面不能够包含题目的信息
   1. 因为我们是要对一个benchmark生成能够解决这benchmark里面所有问题的一个workflow
4. 因此可能需要定义一个叫custom的operator?
   1. 仍然要求workflow在给llm的api的prompt里面不能够包含题目的信息
   2. 但是llm生成workflow的时候, 可以对custom进行一些个性化的测试
   3. 从而能够丰富workflow的多样性.
5. 除了custom的operator, 你也可以思考其他办法