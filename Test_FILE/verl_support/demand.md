请你在Test_FILE\verl_support该目录下拟写一个生成训练数据集parquet的脚本,要求:
核心功能模仿Test_FILE\verl_support_backup\generate_verl_data.py,也即根据这些benchmark生成一个数据集
允许指定某一个benchmark,多个或全部(指定多个时候混在一起),指定生成条目数或生成比例(超过总数时候就全生成),将data_dir下方的train.jsonl对应到train.parquet,test也是
参考ScoreFlow\SCOREFLOW_ARCHITECTURE.md文档
benchmark_name和其他信息从ScoreFlow\benchmark_mapping.jsonl拿
Test_FILE\workflow_generator.py里面有可能有帮助的信息
在plan之前详细阅读这些脚本并列出计划
每个条目格式形如
{
    'data_source': benchmark_name,
    'prompt': messages, #huggingface-chat格式, 从conditions.py拿模板和对应条目的例子合成
    'ability': "workflow",
    'reward_model': {
        'ground_truth': "default"  # 存储用于生成的问题索引
    },
    'extra_info': {
        'answer': 原数据集的answers,
        'raw_data':原数据集的对应行号,
        'test_cases':[列表,里面包含从原数据集(同一个benchmark)中选取的随机n(默认5)个行号],
        'data_dir':原数据集位置(以便用行号拿数据),
    }
}

下面的任务非常复杂，请你首先确保详细阅读了所有相关脚本后，列出计划，待我审查后执行

总任务：请你模仿Test_FILE\verl_internbootcamp\internbootcamp_reward.py,使其在另一个数据格式与执行流程不太一样的任务上进行;但是需要同样调用metagpt执行;需要注意的是一些相关脚本可能不一样或不存在,在ScoreFlow\SCOREFLOW_ARCHITECTURE.md阅读有关内容

注意:核心实现的函数为 compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:

首先，进入的数据格式为
{
    'data_source': benchmark_name,
    'solution_str': 模型的回复,里面有workflow,
    'reward_model': {
        'ground_truth': "default"  # 存储用于生成的问题索引
    },
    'extra_info': {
        'answer': 原数据集的answers,
        'raw_data':原数据集的对应行号,
        'test_cases':[列表,里面包含从原数据集(同一个benchmark)中选取的随机n(默认5)个行号],
        'data_path':原数据集位置(以便用行号拿数据),
    }
}
可以在这看到测试数据Test_FILE\verl_support\data\test_gen\test.parquet

其中重要的是solution_str与extra_info，你应该首先从solution_str中extract_workflow_from_response,与ScoreFlow\scripts\xxx\conditions.py中的python_start和python_end拼接在一起,得到python文件,存入Test_FILE/workspace/{benchmark_name}/(带上时间戳和随机编号),随后以类似调用Test_FILE\workflow_executor.py的方式在extra_info的几个测试用例上执行,并根据执行结果,按照原脚本的方式计算reward

你可以参考另一个数据集的执行流程:阅读Test_FILE\master_runner.py Test_FILE\workflow_generator.py与Test_FILE\workflow_executor.py,它们根据ScoreFlow\benchmark\drop.py与ScoreFlow\scripts\drop,ScoreFlow\scripts\common执行; 

;Test_FILE\metagpt_local这里是metagpt的本地地址

这个任务非常复杂,请你确保阅读完所有脚本后,再输出你的详细的reward_function计划