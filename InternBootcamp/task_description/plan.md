请你在该文件夹InternBootcamp\task_description写一个简易项目,负责调用模型LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}对InternBootcamp\internbootcamp\bootcamp里面的每一个任务进行描述评价(并行)
要求:分三次输出以下三种描述 1.英文详细描述,这个描述会被提供给其他模型,要求包含完整而简洁的任务描述,输入输出格式或示范,格式尽可能统一 2.中文简要描述:这个描述会提供给人看,尽可能简洁 3.任务实现评价:审查完整代码,检查任务是否有质量问题,代码实现是否清晰正确,输出一个json,包含评价(1-5),正确性(有误,正确,不清楚)[1和2只需要提供代码前面的注释给模型] 最后输出一个jsonl返回给我,展示统计信息