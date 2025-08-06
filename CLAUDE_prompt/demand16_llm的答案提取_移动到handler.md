1. 我目前想要把第一步用LLM做答案提取移动到handler部分
2. 例如，我们首先解决 /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop
3. 目前的设计是：
   1. 对于生成的workflow
   2. 拼接 /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop/conditions.py 里面的python_start , python_end
   3. python_end use the FormatAnswer operator in /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop/operator.py
   4. and the prompt is in the FORMAT_ANSWER_PROMPT in /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop/op_prompt.py
4. 现在我要修改到，删除掉这个 FormatAnswer 的设计，然后python_end就是正常的结尾
   1. 然后，我可以在handler里面, 同等地使用这个功能, in /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop/handler.py
   2. 也就是在 /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop/handler.py, 找个地方定义一个operator，然后不 import pydantic and prompt, 直接硬编码
   3. 然后先调用LLM，再rule based
   4. 把这个拆出来作为一个函数，in /Users/luogan/Code/workflow_generation/Flow_RL/ScoreFlow/scripts/drop/handler.py
   5. 这样的好处是，我可以直接在硬编码prompt里面修改答案的格式，（例如，适配DROP）