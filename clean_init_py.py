import re

# 读取有效的task_name列表
valid_tasks = set()
with open('valid_task_names.txt', 'r', encoding='utf-8') as f:
    for line in f:
        valid_tasks.add(line.strip())

print(f"Loaded {len(valid_tasks)} valid task names")

# 读取__init__.py文件
init_file_path = 'InternBootcamp/internbootcamp/bootcamp/__init__.py'
with open(init_file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取BOOTCAMP_REGISTRY字典部分
registry_start = content.find('BOOTCAMP_REGISTRY = {')
registry_end = content.find('}', registry_start) + 1

if registry_start == -1 or registry_end == -1:
    print("Could not find BOOTCAMP_REGISTRY in the file")
    exit(1)

# 提取字典内容
registry_content = content[registry_start:registry_end]

# 解析每个条目
entries = []
lines = registry_content.split('\n')
current_entry = ""

for line in lines:
    line = line.strip()
    if line.startswith('"') and line.endswith(','):
        # 完整的条目行
        entries.append(line)
    elif line.startswith('"') and not line.endswith(','):
        # 开始的行，需要继续
        current_entry = line
    elif current_entry and line.endswith(','):
        # 结束的行
        current_entry += line
        entries.append(current_entry)
        current_entry = ""
    elif current_entry:
        # 中间的行
        current_entry += line

# 过滤有效的条目
valid_entries = []
removed_count = 0

for entry in entries:
    # 提取bootcamp名称（去掉"bootcamp"后缀）
    match = re.match(r'"([^"]+)"', entry)
    if match:
        bootcamp_name = match.group(1)
        # 移除"bootcamp"后缀并转换为小写
        task_name = bootcamp_name.lower().replace('bootcamp', '')
        
        if task_name in valid_tasks:
            valid_entries.append(entry)
        else:
            removed_count += 1
            print(f"Removing: {bootcamp_name} (task_name: {task_name})")

print(f"\nRemoved {removed_count} entries")
print(f"Kept {len(valid_entries)} entries")

# 重建BOOTCAMP_REGISTRY字典
new_registry = 'BOOTCAMP_REGISTRY = {\n'
for entry in valid_entries:
    new_registry += '    ' + entry + '\n'
new_registry += '}'

# 替换原内容
new_content = content[:registry_start] + new_registry + content[registry_end:]

# 写回文件
with open(init_file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nUpdated {init_file_path} successfully!")

# 更新__all__列表
all_start = new_content.find('__all__ = [\'Basebootcamp\'] + list(BOOTCAMP_REGISTRY.keys())')
if all_start != -1:
    print("__all__ list will be automatically updated when the file is imported")
else:
    print("Warning: Could not find __all__ line to update") 