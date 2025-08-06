我现在重新设计了计划：
1. operator的设计中有三种prompt: 第一是内部的basic的prompt，这个硬编码在operator的函数中，例如review算子的函数中，有"please review"这样的字样；第二个是硬编码在workflow里面对于算子的instruction, 这个可以是对于这个benchmark特异的，例如对于DROP，review算子的instruction就要求仔细检查数数和计算的正确性；第三个是传递的上下文，这个是在workflow被执行的时候，随着输入的问题在变化的。
   1. 因此，我们所有的workflow（可能除了最后的提取答案），都是（除了自带的比如有self.problem），本质上还是需要有self.instruction的输入（workflow函数硬编码），以及self.message的输入（上下文）

2. 对于是否使用program，这是一个对比试验，所以我们先不使用任何任务特异的TOOL。仅仅考虑上下文，那么差不多只有：ScEnsemble；Review；Custom；revise; 而对于flex_custom。我不使用，因为我需要的是，把node的链接拓扑暴露出来，只是在生成SFT数据的时候，鼓励几个例子，例如循环，并行，轮询等逻辑。以及他们的组合。请你仔细思考和分析，以及对于目前的operator的还有什么选项？ScEnsemble；Review；Custom；revise; ，可能还要有一个，归纳总结？
