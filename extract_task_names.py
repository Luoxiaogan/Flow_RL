import json

# 读取JSONL文件并提取所有task_name
valid_tasks = set()
with open('Test_FILE/verl_internbootcamp/test/bootcamp_analysis_20250723_190329.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line.strip())
            if 'task_name' in data:
                valid_tasks.add(data['task_name'])
        except json.JSONDecodeError:
            continue

# 打印所有有效的task_name
print("Valid task names:")
for task in sorted(valid_tasks):
    print(f'"{task}"')

print(f"\nTotal count: {len(valid_tasks)}")

# 保存到文件
with open('valid_task_names.txt', 'w', encoding='utf-8') as f:
    for task in sorted(valid_tasks):
        f.write(f'{task}\n')

print("\nTask names saved to valid_task_names.txt") 