import re

with open('Fulllist_InternBootcamp.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
# Find all lines with task types
task_types = set()
for line in lines:
    if '|' in line and 'bootcamp' in line and line.count('|') >= 3:
        parts = line.split('|')
        if len(parts) >= 3:
            # The type is usually in the third column
            task_type = parts[2].strip()
            if task_type and task_type != 'Type' and not task_type.startswith('---'):
                task_types.add(task_type)

print('All unique task types:')
for i, task_type in enumerate(sorted(task_types), 1):
    print(f'{i}. {task_type}')
print(f'\nTotal: {len(task_types)} unique task types')