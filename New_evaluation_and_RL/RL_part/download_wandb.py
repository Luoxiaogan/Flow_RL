import wandb
import pandas as pd
import json
import os
from pathlib import Path

def download_run_complete(entity, project, run_id, save_dir=None):
    """
    下载一个 WandB run 的所有数据
    
    Args:
        entity: WandB entity/username
        project: 项目名称
        run_id: Run ID
        save_dir: 保存目录，默认为 'wandb_run_{run_id}'
    """
    
    # 初始化 API
    api = wandb.Api()
    run = api.run(f"{entity}/{project}/{run_id}")
    
    # 创建保存目录
    if save_dir is None:
        save_dir = f"wandb_run_{run_id}"
    
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    print(f"正在下载 Run: {run.name} ({run_id})")
    print(f"保存到: {save_path.absolute()}")
    print("="*50)
    
    # 1. 下载所有文件（包括模型、日志等）
    print("\n1. 下载所有文件...")
    files_path = save_path / "files"
    files_path.mkdir(exist_ok=True)
    
    files = run.files()
    for f in files:
        print(f"  下载: {f.name}")
        f.download(root=files_path, replace=True)
    
    # 2. 保存配置
    print("\n2. 保存配置...")
    config_path = save_path / "config.json"
    with open(config_path, 'w') as f:
        json.dump(dict(run.config), f, indent=2)
    print(f"  配置已保存到: config.json")
    
    # 3. 保存历史数据（metrics）
    print("\n3. 保存历史指标数据...")
    history = run.history()
    
    # 保存为 CSV
    history_csv_path = save_path / "history.csv"
    history.to_csv(history_csv_path, index=False)
    print(f"  历史数据已保存到: history.csv ({len(history)} 行)")
    
    # 也保存为 JSON 格式
    history_json_path = save_path / "history.json"
    history.to_json(history_json_path, orient='records', indent=2)
    
    # 4. 保存系统指标（GPU、CPU等）
    print("\n4. 保存系统指标...")
    try:
        system_metrics = run.history(stream="events")
        if not system_metrics.empty:
            system_metrics_path = save_path / "system_metrics.csv"
            system_metrics.to_csv(system_metrics_path, index=False)
            print(f"  系统指标已保存到: system_metrics.csv")
    except:
        print("  没有系统指标数据")
    
    # 5. 保存 Summary（最终指标）
    print("\n5. 保存 Summary...")
    summary_path = save_path / "summary.json"
    with open(summary_path, 'w') as f:
        # 修改：将 SummarySubDict 转换为普通字典
        summary_dict = {k: v for k, v in run.summary.items()}
        json.dump(summary_dict, f, indent=2, default=str)  # 添加 default=str 处理特殊类型
    print(f"  Summary 已保存到: summary.json")
    
    # 6. 保存元数据
    print("\n6. 保存元数据...")
    metadata = {
        "run_id": run.id,
        "run_name": run.name,
        "project": run.project,
        "entity": run.entity,
        "state": run.state,
        "created_at": str(run.created_at),
        "heartbeat_at": str(run.heartbeat_at),
        "tags": run.tags,
        "notes": run.notes,
        "url": run.url,
        "path": run.path,
        "runtime": run.summary.get("_runtime", None),
        "total_steps": run.summary.get("_step", None),
    }
    
    metadata_path = save_path / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  元数据已保存到: metadata.json")
    
    # 7. 保存日志（如果有）
    print("\n7. 检查日志...")
    logs_path = save_path / "logs"
    logs_path.mkdir(exist_ok=True)
    
    try:
        # 下载输出日志
        log_file = run.file("output.log")
        log_file.download(root=logs_path, replace=True)
        print("  输出日志已下载")
    except:
        print("  没有输出日志")
    
    # # 8. 创建一个汇总的 Excel 文件
    # print("\n8. 创建汇总 Excel 文件...")
    # excel_path = save_path / f"run_{run_id}_summary.xlsx"
    
    # with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    #     # History sheet
    #     history.to_excel(writer, sheet_name='History', index=False)
        
    #     # Config sheet
    #     config_df = pd.DataFrame([run.config])
    #     config_df.to_excel(writer, sheet_name='Config', index=False)
        
    #     # Summary sheet
    #     summary_df = pd.DataFrame([dict(run.summary)])
    #     summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
    #     # Metadata sheet
    #     metadata_df = pd.DataFrame([metadata])
    #     metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
    
    # print(f"  Excel 汇总已保存到: run_{run_id}_summary.xlsx")
    
    # 9. 创建 README 文件
    print("\n9. 创建 README...")
    readme_content = f"""# WandB Run: {run.name}

## 基本信息
- **Run ID**: {run.id}
- **Project**: {run.project}
- **Entity**: {run.entity}
- **创建时间**: {run.created_at}
- **状态**: {run.state}
- **URL**: {run.url}

## 文件说明
- `config.json`: 训练配置参数
- `history.csv/json`: 训练过程中的所有指标
- `system_metrics.csv`: 系统资源使用情况（GPU、CPU等）
- `summary.json`: 最终的指标值
- `metadata.json`: Run 的元信息
- `files/`: WandB 保存的所有文件（模型、日志等）
- `run_{run_id}_summary.xlsx`: Excel 格式的汇总数据

## 快速加载数据
```python
import pandas as pd
import json

# 加载历史数据
history = pd.read_csv('history.csv')

# 加载配置
with open('config.json', 'r') as f:
    config = json.load(f)

# 加载 summary
with open('summary.json', 'r') as f:
    summary = json.load(f)
```
"""
    
    readme_path = save_path / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  README 已创建")
    
    print("\n" + "="*50)
    print(f"✅ 所有数据已下载到: {save_path.absolute()}")
    print(f"文件夹大小: {sum(f.stat().st_size for f in save_path.rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")
    
    return str(save_path.absolute())


# 使用示例
if __name__ == "__main__":
    # 根据你的 URL 提取的信息
    entity = "luogan_little_wolf-peking-university"
    project = "qwen3_rl_0917_old_ckpt"
    run_id = "7uqork2s"

    base_dir = "wandb_data_save/"
    add = "qwen3_rl_0917_old_ckpt"

    # wandb api: 6d73f146a264e1dd556fc16529a88c3871ec4af3
    # wandb api: 6d73f146a264e1dd556fc16529a88c3871ec4af3
    # wandb api: 6d73f146a264e1dd556fc16529a88c3871ec4af3
    # wandb api: 6d73f146a264e1dd556fc16529a88c3871ec4af3
    # wandb api: 6d73f146a264e1dd556fc16529a88c3871ec4af3
    
    # 下载所有数据
    saved_path = download_run_complete(
        entity=entity,
        project=project,
        run_id=run_id,
        save_dir=f"{base_dir}{add}"  # 可以自定义保存目录名
    )
    
    print(f"\n你可以在这个目录查看所有数据: {saved_path}")
