下面的任务非常复杂，请你首先确保详细阅读了所有相关脚本后，列出计划，待我审查后执行

总任务：请你改造Test_FILE\verl_internbootcamp\internbootcamp_reward.py,使其实际调用metagpt框架进行执行

目前的Test_FILE\verl_internbootcamp\internbootcamp_reward.py并没有实际调用metagpt框架进行执行，我希望你进行如下修改：
首先，进入的数据格式为
        verl_entry = {
            "data_source": f"internbootcamp",
            "solution_str": 模型输出的回复，其中包含workflow code，
            "reward_model": {
                "ground_truth": "default"
            },
            "extra_info": {
                "score": 1.0,  # 默认分数
                "task_name": task_name,
                "test_cases": [str(ex.get("identity", f"example_{i}")) for i, ex in enumerate(examples)] if examples else [],
                "entry_id": entry_id,
                "task_type": get_task_type(task_name),
                "num_examples": len(examples),
                "timestamp": datetime.now().isoformat(),
                "generation_time": time.time() - start_time
            }
        }
其中重要的是solution_str与extra_info，你应该首先从solution_str中调用原reward脚本的extract_workflow_from_response,与ScoreFlow\scripts\internbootcamp\conditions.py中的python_start和python_end拼接在一起,得到python文件,存入Test_FILE/workspace/internbootcamp/(带上时间戳和随机编号),随后调用Test_FILE\workflow_executor.py在extra_info的三个测试用例上执行,并根据执行结果,按照原脚本的方式计算reward

你可以参考另一个数据集的执行流程:阅读Test_FILE\master_runner.py Test_FILE\workflow_generator.py与Test_FILE\workflow_executor.py,它们根据ScoreFlow\benchmark\drop.py与ScoreFlow\scripts\drop,ScoreFlow\scripts\common执行; 在我的数据集上,ScoreFlow上对应的脚本变为ScoreFlow\scripts\internbootcamp与ScoreFlow\scripts\common,但是执行流程变得极其复杂

同时,你也要改造Test_FILE\verl_internbootcamp\test\test_internbootcamp_reward.py,全流程真实llm调用真实执行

这个任务非常复杂,请你确保阅读完所有脚本后,再输出你的详细的reward_function计划