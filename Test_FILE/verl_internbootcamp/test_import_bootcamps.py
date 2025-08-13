import sys
import os
import json
import re
import traceback
from pathlib import Path
import importlib
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime


def find_project_root(current_file: Path) -> Path:
	current_dir = current_file.resolve().parent
	return current_dir.parents[1]


def setup_sys_path(project_root: Path) -> None:
	# Ensure project root and InternBootcamp package are importable
	root_str = str(project_root)
	ib_str = str(project_root / "InternBootcamp")
	if root_str not in sys.path:
		sys.path.insert(0, root_str)
	if ib_str not in sys.path:
		sys.path.insert(0, ib_str)


def parse_task_names(jsonl_path: Path) -> List[str]:
	"""Parse unique task_name values from a JSONL file, with robust fallbacks."""
	task_names: Set[str] = set()
	if not jsonl_path.exists():
		raise FileNotFoundError(f"JSONL not found: {jsonl_path}")
	with jsonl_path.open('r', encoding='utf-8', errors='ignore') as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			# Try strict JSON first
			obj = None
			try:
				obj = json.loads(line)
			except Exception:
				# Fallback: relax with a regex search
				match = re.search(r'"task_name"\s*:\s*"([^"]+)"', line)
				if match:
					task = match.group(1)
					if task:
						task_names.add(task.strip())
				continue
			if isinstance(obj, dict):
				# Direct key
				task = obj.get('task_name')
				if isinstance(task, str) and task:
					task_names.add(task.strip())
					continue
				# Nested common shapes
				task_from_nested = None
				if isinstance(obj.get('task'), dict):
					task_from_nested = obj['task'].get('task_name') or obj['task'].get('name')
				if not task_from_nested and isinstance(obj.get('extra_info'), dict):
					task_from_nested = obj['extra_info'].get('task_name')
				if isinstance(task_from_nested, str) and task_from_nested:
					task_names.add(task_from_nested.strip())
	return sorted({t.strip().lower() for t in task_names if t and isinstance(t, str)})


def extract_task_name_from_line(line: str) -> Optional[str]:
	"""Extract task_name from a single JSONL line using JSON first, then regex."""
	line = line.strip()
	if not line:
		return None
	try:
		obj = json.loads(line)
		if isinstance(obj, dict):
			if isinstance(obj.get('task_name'), str) and obj['task_name']:
				return obj['task_name'].strip().lower()
			# Nested shapes
			task_from_nested = None
			if isinstance(obj.get('task'), dict):
				task_from_nested = obj['task'].get('task_name') or obj['task'].get('name')
			if not task_from_nested and isinstance(obj.get('extra_info'), dict):
				task_from_nested = obj['extra_info'].get('task_name')
			if isinstance(task_from_nested, str) and task_from_nested:
				return task_from_nested.strip().lower()
	except Exception:
		pass
	m = re.search(r'"task_name"\s*:\s*"([^"]+)"', line)
	if m:
		return m.group(1).strip().lower()
	return None


def delete_error_lines(jsonl_path: Path, failing_tasks: Set[str]) -> Tuple[int, int]:
	"""Delete lines whose task_name is in failing_tasks. Returns (removed_count, remaining_lines)."""
	if not failing_tasks:
		return 0, sum(1 for _ in jsonl_path.open('r', encoding='utf-8', errors='ignore'))
	# Backup
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	backup_path = jsonl_path.with_suffix('.jsonl.bak_' + timestamp)
	# Read all lines
	with jsonl_path.open('r', encoding='utf-8', errors='ignore') as f:
		lines = f.readlines()
	# Compute keep/remove
	kept_lines: List[str] = []
	removed = 0
	for raw in lines:
		task = extract_task_name_from_line(raw)
		if task and task.strip().lower() in failing_tasks:
			removed += 1
			continue
		kept_lines.append(raw)
	# Write backup then overwrite original
	with backup_path.open('w', encoding='utf-8') as bf:
		bf.writelines(lines)
	with jsonl_path.open('w', encoding='utf-8') as outf:
		outf.writelines(kept_lines)
	return removed, len(kept_lines)


def try_import_task(task_name: str) -> Tuple[bool, str]:
	"""Attempt to import module and class for a given task_name. Return (ok, message)."""
	module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
	class_name = f"{task_name.capitalize()}bootcamp"
	try:
		module = importlib.import_module(module_path)
		# Also verify the expected class exists (if present)
		if hasattr(module, class_name):
			getattr(module, class_name)
			return True, f"Imported {module_path} and found class {class_name}"
		return True, f"Imported {module_path} (class {class_name} not found)"
	except Exception as e:
		return False, f"Failed to import {module_path}: {e}\n{traceback.format_exc()}"


def main() -> None:
	current_file = Path(__file__)
	project_root = find_project_root(current_file)
	setup_sys_path(project_root)
	jsonl_path = current_file.parent / 'bootcamp_analysis_filtered.jsonl'

	print(f"Project root: {project_root}")
	print(f"Reading tasks from: {jsonl_path}")

	tasks = parse_task_names(jsonl_path)
	print(f"Discovered {len(tasks)} unique task_name(s)")
	if not tasks:
		print("No task names found. Exiting.")
		return

	successes: List[str] = []
	errors: Dict[str, str] = {}
	for idx, task in enumerate(tasks, start=1):
		ok, msg = try_import_task(task)
		prefix = f"[{idx}/{len(tasks)}] {task}"
		if ok:
			print(prefix + " -> OK")
			successes.append(task)
		else:
			print(prefix + " -> ERROR")
			errors[task] = msg

	print("\n=== Summary ===")
	print(f"OK: {len(successes)} | ERROR: {len(errors)} | TOTAL: {len(tasks)}")

	# Delete error lines and report counts
	if errors:
		failing_set = {t.strip().lower() for t in errors.keys()}
		removed, remaining = delete_error_lines(jsonl_path, failing_set)
		print(f"\nRemoved {removed} line(s) from JSONL that matched failing tasks.")
		print(f"Remaining lines in JSONL: {remaining}")
		print("\nDetailed errors:")
		for task, detail in errors.items():
			print(f"\n--- {task} ---\n{detail}")


if __name__ == '__main__':
	main() 