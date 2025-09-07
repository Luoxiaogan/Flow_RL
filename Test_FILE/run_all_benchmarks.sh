#!/bin/bash

# ==============================================================================
#                   主控脚本 - 批量执行所有Benchmark工作流
# ==============================================================================
#
# 该脚本按顺序执行所有5个benchmark的工作流生成与执行系统。
# 它会调用各个独立的 run_workflow_system_*.sh 脚本，并记录执行状态。
#
# --- 使用方法 ---
# 1. 确保所有子脚本都有执行权限: chmod +x run_workflow_system_*.sh
# 2. 运行脚本: bash run_all_benchmarks.sh
# 3. 可选参数:
#    --continue-on-error : 即使某个benchmark失败也继续执行
#    --start-from <benchmark> : 从指定的benchmark开始执行
#
# ==============================================================================

# 导航到脚本所在的目录
cd "$(dirname "$0")" || exit

# ============================ 配置部分 =======================================

# 定义所有要执行的benchmark，按照执行顺序
BENCHMARKS=("gsm8k" "mbpp" "humaneval" "hotpotqa" "drop")

# 对应的脚本文件名
declare -A SCRIPT_FILES=(
    ["gsm8k"]="run_workflow_system_gsm8k.sh"
    ["mbpp"]="run_workflow_system_mbpp.sh"
    ["humaneval"]="run_workflow_system_humaneval.sh"
    ["hotpotqa"]="run_workflow_system_hotpotqa.sh"
    ["drop"]="run_workflow_system_drop.sh"
)

# 结果记录
declare -A RESULTS
declare -A START_TIMES
declare -A END_TIMES

# 默认配置
CONTINUE_ON_ERROR=false
START_FROM=""
LOG_DIR="./logs/batch_run_$(date +%Y%m%d_%H%M%S)"

# ============================ 参数解析 =======================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --continue-on-error)
            CONTINUE_ON_ERROR=true
            shift
            ;;
        --start-from)
            START_FROM="$2"
            shift 2
            ;;
        --help|-h)
            echo "使用方法: $0 [选项]"
            echo "选项:"
            echo "  --continue-on-error    即使某个benchmark失败也继续执行"
            echo "  --start-from <name>    从指定的benchmark开始执行"
            echo "  --help, -h            显示此帮助信息"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# ============================ 函数定义 =======================================

# 记录日志
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/main.log"
}

# 检查脚本文件是否存在
check_scripts() {
    local all_exist=true
    for benchmark in "${BENCHMARKS[@]}"; do
        if [[ ! -f "${SCRIPT_FILES[$benchmark]}" ]]; then
            log "ERROR" "脚本文件不存在: ${SCRIPT_FILES[$benchmark]}"
            all_exist=false
        fi
    done
    
    if [[ "$all_exist" == false ]]; then
        log "ERROR" "请确保所有脚本文件都存在"
        return 1
    fi
    
    # 检查执行权限
    for benchmark in "${BENCHMARKS[@]}"; do
        if [[ ! -x "${SCRIPT_FILES[$benchmark]}" ]]; then
            log "WARN" "添加执行权限: ${SCRIPT_FILES[$benchmark]}"
            chmod +x "${SCRIPT_FILES[$benchmark]}"
        fi
    done
    
    return 0
}

# 运行单个benchmark
run_benchmark() {
    local benchmark=$1
    local script="${SCRIPT_FILES[$benchmark]}"
    local log_file="$LOG_DIR/${benchmark}.log"
    
    log "INFO" "开始执行: $benchmark"
    START_TIMES[$benchmark]=$(date +%s)
    
    # 执行脚本并记录输出
    bash "$script" > "$log_file" 2>&1
    local exit_code=$?
    
    END_TIMES[$benchmark]=$(date +%s)
    
    if [[ $exit_code -eq 0 ]]; then
        RESULTS[$benchmark]="SUCCESS"
        log "INFO" "$benchmark 执行成功"
    else
        RESULTS[$benchmark]="FAILED (exit code: $exit_code)"
        log "ERROR" "$benchmark 执行失败，退出码: $exit_code"
        
        # 显示最后几行错误日志
        log "ERROR" "错误日志末尾:"
        tail -n 10 "$log_file" | while IFS= read -r line; do
            log "ERROR" "  $line"
        done
        
        if [[ "$CONTINUE_ON_ERROR" == false ]]; then
            return $exit_code
        fi
    fi
    
    return 0
}

# 计算执行时间
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    local hours=$((duration / 3600))
    local minutes=$(((duration % 3600) / 60))
    local seconds=$((duration % 60))
    printf "%02d:%02d:%02d" $hours $minutes $seconds
}

# 显示执行总结
show_summary() {
    log "INFO" "=================================================="
    log "INFO" "                 执行总结"
    log "INFO" "=================================================="
    
    local total_start=$(date +%s)
    local total_end=0
    local success_count=0
    local failed_count=0
    
    # 找出最早的开始时间和最晚的结束时间
    for benchmark in "${BENCHMARKS[@]}"; do
        if [[ -n "${START_TIMES[$benchmark]}" ]]; then
            if [[ ${START_TIMES[$benchmark]} -lt $total_start ]]; then
                total_start=${START_TIMES[$benchmark]}
            fi
            if [[ ${END_TIMES[$benchmark]} -gt $total_end ]]; then
                total_end=${END_TIMES[$benchmark]}
            fi
        fi
    done
    
    # 显示每个benchmark的结果
    for benchmark in "${BENCHMARKS[@]}"; do
        if [[ -n "${RESULTS[$benchmark]}" ]]; then
            local status="${RESULTS[$benchmark]}"
            local duration=""
            
            if [[ -n "${START_TIMES[$benchmark]}" ]] && [[ -n "${END_TIMES[$benchmark]}" ]]; then
                duration=$(calculate_duration "${START_TIMES[$benchmark]}" "${END_TIMES[$benchmark]}")
            fi
            
            if [[ "$status" == "SUCCESS" ]]; then
                ((success_count++))
                log "INFO" "  $benchmark: ✓ 成功 (耗时: $duration)"
            else
                ((failed_count++))
                log "INFO" "  $benchmark: ✗ $status (耗时: $duration)"
            fi
        else
            log "INFO" "  $benchmark: - 未执行"
        fi
    done
    
    # 显示总体统计
    local total_duration=$(calculate_duration $total_start $total_end)
    log "INFO" "--------------------------------------------------"
    log "INFO" "总计: 成功 $success_count 个，失败 $failed_count 个"
    log "INFO" "总耗时: $total_duration"
    log "INFO" "日志目录: $LOG_DIR"
    log "INFO" "=================================================="
}

# ============================ 主程序 =======================================

# 创建日志目录
mkdir -p "$LOG_DIR"

log "INFO" "=================================================="
log "INFO" "           批量执行Benchmark工作流"
log "INFO" "=================================================="
log "INFO" "开始时间: $(date)"
log "INFO" "工作目录: $(pwd)"
log "INFO" "日志目录: $LOG_DIR"
log "INFO" "继续执行选项: $CONTINUE_ON_ERROR"
if [[ -n "$START_FROM" ]]; then
    log "INFO" "从 $START_FROM 开始执行"
fi
log "INFO" "=================================================="

# 检查所有脚本文件
if ! check_scripts; then
    exit 1
fi

# 确定开始位置
start_index=0
if [[ -n "$START_FROM" ]]; then
    found=false
    for i in "${!BENCHMARKS[@]}"; do
        if [[ "${BENCHMARKS[$i]}" == "$START_FROM" ]]; then
            start_index=$i
            found=true
            break
        fi
    done
    
    if [[ "$found" == false ]]; then
        log "ERROR" "未找到指定的benchmark: $START_FROM"
        log "ERROR" "可用的benchmark: ${BENCHMARKS[*]}"
        exit 1
    fi
fi

# 执行各个benchmark
overall_success=true
for ((i=$start_index; i<${#BENCHMARKS[@]}; i++)); do
    benchmark="${BENCHMARKS[$i]}"
    
    log "INFO" ""
    log "INFO" "------------- 执行第 $((i+1))/${#BENCHMARKS[@]} 个任务: $benchmark -------------"
    
    if ! run_benchmark "$benchmark"; then
        overall_success=false
        if [[ "$CONTINUE_ON_ERROR" == false ]]; then
            log "ERROR" "执行中断，停止后续任务"
            break
        fi
    fi
    
    # 任务间短暂休息，避免资源争抢
    if [[ $((i+1)) -lt ${#BENCHMARKS[@]} ]]; then
        log "INFO" "等待5秒后继续下一个任务..."
        sleep 5
    fi
done

# 显示总结
show_summary

# 设置退出码
if [[ "$overall_success" == true ]]; then
    exit 0
else
    exit 1
fi