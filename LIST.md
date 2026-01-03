绝对路径
/home/lg/workflow_tooluse/Flow_RL_luogan
建议全部在本路径下工作,里面藏了各种隐藏config没法动

流程:
首先需要启动4个tmux,全部在workflow环境下启动,目前的环境名分别是
api_proxy(直接连接就行),在负责api代理
reward: 在挂reward_server
sglang: 在挂sglang server
rl:(起名叫rl但是没干rl的活): 在挂evaluation,也可以用来挂generation

下面是各部分概述
## api相关:
New_evaluation_and_RL/metagpt_api_key_proxy/api_pool_config.yaml 疑似这个是真正起效的,我也把api key换成自己的了
此处疑似可以配置api,不知道是否起效,New_evaluation_and_RL/config.yaml(这里我已经换成我自己的了)
New_evaluation_and_RL/servers_and_proxy/start_api_proxy_pool.sh于此处启动代理,已在api_proxy tmux启动

## reward server相关:
New_evaluation_and_RL/metagpt_api_key_proxy/api_pool_config.yaml 此处改相关配置
New_evaluation_and_RL/servers_and_proxy/start_scoreflow_reward.sh 此处启动server,已经在tmux reward启动

## 新operator注册与数据生成相关:
于ScoreFlow/scripts/common处改好,增加新operator与对应的condition; operator_an.py似乎没用上
随后写入一个benchmark_mapping.jsonl ScoreFlow/benchmark_mapping_vdb.jsonl此处注册了vectorsearch相关信息(必须按照此格式,有些benchmark_mapping.jsonl的格式是无法用的!!必须带比例信息)

随后在New_evaluation_and_RL/generate_parquet_and_jsonl/generate_verl_training_data_with_proportion.py处注册新operator(注意!!!,必须用with_proportion版本,另一个版本实现是错的);文件内搜索"VectorSearch"即可发现如何注册新op,注意大小写

随后在New_evaluation_and_RL/generate_parquet_and_jsonl python generate_verl_training_data_with_proportion.py --benchmark-mapping /home/lg/workflow_tooluse/Flow_RL_luogan/ScoreFlow/benchmark_mapping_vdb.jsonl --output-dir testvdb --train-num 0 --test-num 50 生成数据

你需要知道以下参数:    parser.add_argument('--num-examples', type=int, default=1,
                       help='Number of problem examples per prompt (default: 1)')
    parser.add_argument('--num-train-test-cases', type=int, default=5,
                       help='Number of test cases for train entries (default: 5)')
    parser.add_argument('--num-test-test-cases', type=int, default=5,
                       help='Number of test cases for test entries (default: 5)')

## sglang生成相关
在上述指定的output_dir下提取jsonl,
在tmux sglang下启动bash New_evaluation_and_RL/sglang_inference.sh(已经启动)
然后New_evaluation_and_RL/batch_inference_sglang_rollout.py(略)

## evaluation相关
相关文件在workflow_evaluator
运行前在workflow_evaluator/config.yaml内指定参数
重点:
  data_sources:(如果要加东西)
io:
  input_dir: '/home/lg/workflow_tooluse/Flow_RL_luogan/New_evaluation_and_RL'
  default_input_file: 'test_vdb_with_responses_rollout=2.jsonl'

  output_dir: './results_vdb_rollout=2'
  其他不用管

随后python workflow_executor.py
注意有断点续传机制,因此开新实验要建新文件夹

输出文件夹内:
例如workflow_evaluator/results_vdb_rollout=2
raw文件夹内保存了原始结果便于核查
其余文件懒得写了...

# 总结: 
api代理 reward_server sglang已经开好不用管

加上新operator后,直接生成jsonl,rollout然后evaluation就完事了