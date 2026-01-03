请你为my_llama3_h100_with_eval增加一个功能,允许训练过程中,自动在保存ckpt后对ckpt的性能进行评估;请你仔细阅读New_evaluation_and_RL\reward_server,这个脚本将会在性能评估前启动(你可以在脚本中检查这个端口是否已经开启)
测试用数据集位于New_evaluation_and_RL\generate_parquet_and_jsonl\test_scoreflow_data\train.jsonl,其数据结构形如

```json
                        'data_source': f"workflow_{benchmark_name}",
                        'prompt': messages,  # HuggingFace chat format
                        'ability': 'workflow',
                        'reward_model': {
                            'ground_truth': 'default'  # Fixed as specified
                        },
                        'extra_info': {
                            # 'answer': original_answer,  # Removed as requested
                            'raw_data': idx,  # Original row number
                            'test_cases': list(test_case_indices) if hasattr(test_case_indices, '__iter__') else [test_case_indices],  # Ensure list format (not numpy array)
                            'data_path': data_path,  # Original dataset location
                        }
                    }
```
你需要部署该ckpt,针对数据集中每一个prompt生成对应的solution_str,将其发送至reward_server端口(发送数据示例形如New_evaluation_and_RL\servers_and_proxy\test_request.json),并拿到reward相关信息;最后分各个data_source里的benchmark_name显示平均成绩,与总和成绩等信息,写入报告

这个任务非常非常复杂,think hard,首先为我在my_llama3_h100_with_eval\plan.md列出你的详细计划,等我审批