在Test_FILE\verl_support\evaluation写一个评测脚本系统
首先,对一个model ckpt,利用sglang部署该模型的server
随后,从Test_FILE\verl_support\data下面的数据集拿到测试用数据,一个典型例子是Test_FILE\verl_support\data\test_new\test.parquet
数据集格式形如:
{
    'data_source': f"workflow_{benchmark_name}",
    'prompt': messages,  # HuggingFace chat format
    'ability': 'workflow',
    'reward_model': {
        'ground_truth': 'default'  # Fixed as specified
    },
    'extra_info': {
        'answer': original_answer,
        'raw_data': idx,  # Original row number
        'test_cases': test_case_indices,  # Random test case indices
        'data_path': data_path,  # Original dataset location
    }
}

对其中所有例子,并发调用Test_FILE\verl_support\scoreflow_reward.py中的compute_score函数(compute_score(self, data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:),其中solution_str是sglang server对数据集中该条prompt的回复,其他来自数据集该行

最后生成测试报告:分各个benchmark_name生成测试结果jsonl,将prompt,response,提取的workflow(<code>中间的部分</code>)和score,再输出每个benchmark的平均分的报告,放在测试时间_ckpt名字文件夹

该任务很复杂,确保读完所有相关文件后再操作,先列计划待我审批`