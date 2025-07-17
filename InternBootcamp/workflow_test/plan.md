请你写一个脚本,做如下事情
1. 处理数据集:
   在internbootcamp中挑几个任务,根据其在bootcamp中的源代码的开头,取出来作为任务描述,截取到Here is a reference code to solve this task.之前的片段;然后再用接口生成几个测试用例;将这个任务的名称,测试用例(参数和prompt),任务描述,和顺序id为键生成一个jsonl

2. workflow测试
   要求一个模型LLM_CONFIG = {
        "provider": "aliyun_dashscope", 
        "model": "qwen-plus",
        "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",

    }首先根据任务描述,要求上游生成一个指导性system_prompt去"指挥"下游模型该怎么解决这个问题;随后生成的system_prompt被输入给下游模型,连带测试用例一起给,要求模型解决,随后验证其准确性;将这个任务数据,system_prompt,下游模型生成的解答以及是否正确都存入json
代码尽量简洁,只要最小实现