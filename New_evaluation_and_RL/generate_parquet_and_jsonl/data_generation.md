数据生成脚本New_evaluation_and_RL\generate_parquet_and_jsonl\generate_verl_training_data.py


生成逻辑:
cd New_evaluation_and_RL\generate_parquet_and_jsonl
测试数据集组
generate_verl_training_data.py --num-train-entries 0 --num-test-entries 20 --output-dir test_scoreflow_data --benchmarks all --benchmark-mapping ScoreFlow/benchmark_mapping_all.jsonl(记得改绝对路径) --test-cases-per-entry 50(建议改低! 到20差不多了)

New_evaluation_and_RL\generate_parquet_and_jsonl\truncate_test_cases.py 可用于删减测试用例数量,删减到0后,复制到各个RL数据集的测试集部分下用于临时测试

RL训练数据集组
python generate_verl_training_data.py --benchmarks all --benchmark-mapping ScoreFlow/benchmark_mapping_rl.jsonl(记得改绝对路径)--num-train-entries 100 -num-test-entries 0 --test-cases-per-entry 5

less_env和less_op组: 
python generate_verl_training_data.py --benchmarks all --benchmark-mapping ScoreFlow/benchmark_mapping_less_env.jsonl(记得改绝对路径)--num-train-entries 100 -num-test-entries 0 --test-cases-per-entry 5
python generate_verl_training_data.py --benchmarks all --benchmark-mapping ScoreFlow/benchmark_mapping_less_op.jsonl(记得改绝对路径)--num-train-entries 100 -num-test-entries 0 --test-cases-per-entry 5