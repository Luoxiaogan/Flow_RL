我正在进行代码的重构，我在进行强化学习任务，原先我配置了两个任务的数据集生成与reward——function_server脚本，现在我已经完成了其中一个任务的迁移，请你仿照这个任务的迁移操作，迁移另一个任务

任务分两类，scoreflow与internbootcamp
scoreflow原脚本地址：
Test_FILE\verl_support\generate_verl_training_data.py
Test_FILE\verl_support\scoreflow_reward_utils.py Test_FILE\verl_support\scoreflow_reward_server.py
scoreflow现脚本地址：
New_evaluation_and_RL\generate_parquet_and_jsonl\generate_verl_training_data.py
New_evaluation_and_RL\reward_server

internbootcamp原脚本地址：
Test_FILE\verl_internbootcamp\filter_and_generate_verl.py(调用了Test_FILE\verl_internbootcamp\generate_verl_data.py)
Test_FILE\verl_internbootcamp\generate_verl_data.py
Test_FILE\verl_internbootcamp\internbootcamp_reward_utils.py
Test_FILE\verl_internbootcamp\internbootcamp_reward_server.py
internbootcamp现脚本地址：
New_evaluation_and_RL\internbootcamp_reward_server下面,我把原脚本粘贴过来了r
New_evaluation_and_RL\generate_parquet_and_jsonl\internbootcamp_generate_verl_training_data.py这个是数据集生成脚本
New_evaluation_and_RL\generate_parquet_and_jsonl\internbootcamp_data_test\test.parquet这个是用于测试的数据集

请你首先详细阅读这里面的所有文件（以及重要的被引用文件），按以下操作执行
1. 根据New_evaluation_and_RL\docs\scoreflow_v2.md,修改internbootcamp_reward_server,注意:两个任务的处理逻辑不相同,你只需要加上如下几个功能TeeOutput SafeTeeOutput WorkflowExecutionLogger IndividualTestCaseLogger SimpleTeeOutput,但是核心类不动或者少动,测试用例是New_evaluation_and_RL\servers_and_proxy\test_request_internbootcamp.json
2. 一定注意,以类似# 加载配置文件
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# 读取配置
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        paths_config = config.get('paths', {})
        # 获取project_root，用于构建默认路径
        project_root = config.get('project_root', '/Users/luogan/Code/workflow_generation/Flow_RL')
else:
    print(f"Warning: Config file not found at {CONFIG_FILE}")
    paths_config = {}
    project_root = '/Users/luogan/Code/workflow_generation/Flow_RL'

# 转换为Path对象
project_root_path = Path(project_root)

# 从config.yaml获取路径（相对路径），然后基于project_root构建完整路径
# scoreflow_handlers - 如果是"."则使用project_root本身
scoreflow_handlers = paths_config.get('scoreflow_handlers', '.')
if scoreflow_handlers == '.':
    SCOREFLOW_HANDLERS_PATH = project_root_path
else:
    SCOREFLOW_HANDLERS_PATH = project_root_path / scoreflow_handlers
# benchmark_mapping - 相对路径拼接
benchmark_mapping = paths_config.get('benchmark_mapping', 'ScoreFlow/benchmark_mapping.jsonl')
BENCHMARK_MAPPING_PATH = project_root_path / benchmark_mapping

# processed_dataset - 相对路径拼接
processed_dataset = paths_config.get('processed_dataset', 'Processed_dataset')
PROCESSED_DATASET_PATH = project_root_path / processed_dataset的方式,以config加载路径,所有文件都要改

注意,你需要在另一个环境下执行,这个环境依赖不全,因此不要自己跑测试