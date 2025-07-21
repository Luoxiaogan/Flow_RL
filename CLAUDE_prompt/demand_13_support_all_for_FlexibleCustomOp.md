1. 现在在`ScoreFlow/scripts`已经适配了五个benchmark的相关代码了
2. 现在我记得 gsm8k里面 `ScoreFlow/scripts/gsm8k/operator_an.py`有一个叫 FlexibleCustom 的operator
3. 支持可以让生成的workflow可以较为自由
4. 所以让你给其他的四个benchmark都适配FlexibleCustom 的operator，需要根据特点修改prompt等，以及conditions, op_prompt, operator_an都要修改
5. 以及，我觉得对于gsm8k, 不应该用run_code这个operator需要去掉
   1. 类似这个，也就是说，对于非代码类等，gsm8k, hotpotqa, drop, 都不能写代码
   2. 因此要删掉相关的operator, 以及对应的conditions, op_prompt
