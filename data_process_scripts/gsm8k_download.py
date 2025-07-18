from datasets import load_dataset

# 指定数据集名称
dataset_name = "openai/gsm8k"

# 指定您想要保存的本地路径
local_path = "/Users/luogan/Code/workflow_generation/Flow_RL/Datasets/gsm8k"

# 下载并保存数据集到指定路径
# `cache_dir` 参数会将原始数据和缓存文件保存在指定目录下
dataset = load_dataset(dataset_name, 'main', cache_dir=local_path)

# 打印数据集信息，确认下载成功
print(dataset)

# 您可以查看训练集和测试集的样本
print("训练集样本:")
print(dataset['train'][0])

print("\n测试集样本:")
print(dataset['test'][0])