#!/bin/bash

# 文件清理脚本 - 清理Workflow Orchestrator V5项目中的过时文件
# 运行前请确保已备份重要数据

echo "=== Workflow Orchestrator V5 文件清理脚本 ==="
echo "此脚本将删除过时的文件，保留V5单文件架构所需的核心文件"
echo

# 确认操作
read -p "确认要删除旧版本文件吗？[y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

echo "开始清理..."

# 切换到脚本目录
cd "$(dirname "$0")"

# 删除旧版本Python文件
echo "删除旧版本程序文件..."
rm -f workflow_orchestrator_v2.py
rm -f workflow_orchestrator_v3.py
rm -f workflow_orchestrator_v4.py
rm -f "workflow_orchestrator_v5 _backup.py"

# 删除外部配置系统
echo "删除外部配置系统..."
rm -f config.py
rm -rf config/

# 删除旧版shell脚本
echo "删除旧版shell脚本..."
rm -f run_workflow.sh
rm -f run_workflow_direct.sh
rm -f run_workflow_multi_api_example.sh
rm -f setup_workflow_config.sh

# 删除旧版文档
echo "删除旧版文档..."
rm -f QUICK_START.md
rm -f README_CONFIG.md

# 删除测试文件
echo "删除测试文件..."
rm -f new_test.py
rm -f test_form_metagpt.py

# 删除缓存目录
echo "删除缓存目录..."
rm -rf __pycache__/

# 删除旧工作目录（如果为空）
if [ -d "workspace" ]; then
    if [ -z "$(ls -A workspace 2>/dev/null)" ]; then
        echo "删除空的旧工作目录..."
        rm -rf workspace/
    else
        echo "⚠️  workspace/目录不为空，请手动检查后删除"
    fi
fi

# 删除日志目录（如果只包含测试日志）
if [ -d "logs" ]; then
    echo "⚠️  发现logs/目录，请手动检查后决定是否删除"
fi

# 删除metagpt目录（如果是临时复制）
if [ -d "metagpt" ]; then
    echo "⚠️  发现metagpt/目录，请确认是否为临时复制，可手动删除"
fi

echo
echo "=== 清理完成 ==="
echo "保留的核心文件："
echo "  ✓ workflow_orchestrator_v5.py"
echo "  ✓ run_workflow_argparse.sh"
echo "  ✓ workflow_orchestrator_v5_使用文档.md"
echo "  ✓ 文件清理指南.md"
echo "  ✓ ScoreFlow/ (框架依赖)"
echo "  ✓ workspace_v5/ (工作目录)"
echo

echo "现在可以使用以下命令运行程序："
echo "  bash run_workflow_argparse.sh"
echo

echo "如需自定义配置，请编辑 run_workflow_argparse.sh 中的配置区域"
