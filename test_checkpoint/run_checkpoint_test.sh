#!/bin/bash

# Checkpoint Testing Pipeline Script
# This script orchestrates the complete checkpoint testing process

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# ===== Configuration (Can be hardcoded or passed as arguments) =====

# Model checkpoint path
CHECKPOINT_PATH="${1:-/path/to/model/checkpoint}"

# Benchmark settings
BENCHMARK="${2:-gsm8k}"
DATASET_PATH="${3:-../Processed_dataset/gsm8k.jsonl}"

# Server settings
SERVER_PORT="${4:-8000}"
GPU_ID="${5:-7}"
TENSOR_PARALLEL_SIZE="${6:-1}"
MAX_MODEL_LEN="${7:-4096}"

# Execution LLM configuration (for workflow testing)
# This should match the format in Test_FILE/config2.yaml
EXEC_LLM='{"provider": "openai", "model": "qwen2-72b-instruct", "api_key": "YOUR_API_KEY", "base_url": "https://api.siliconflow.cn/v1"}'

# Test parameters
NUM_BATCHES=10
WORKFLOWS_PER_BATCH=15
PROBLEMS_PER_WORKFLOW=3
PARALLELISM=2

# Output directory
OUTPUT_BASE_DIR="checkpoint_test_results"

# ===== Functions =====

print_banner() {
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

check_server_ready() {
    local max_attempts=30
    local attempt=0
    
    echo "Waiting for vLLM server to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$SERVER_PORT/health > /dev/null 2>&1; then
            echo "Server is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo "Server failed to start within timeout!"
    return 1
}

cleanup() {
    echo "Cleaning up..."
    
    # Kill vLLM server if running
    if [ ! -z "$SERVER_PID" ]; then
        echo "Stopping vLLM server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
    fi
    
    # Kill any remaining python processes on the port
    lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null
}

# Set up cleanup on exit
trap cleanup EXIT

# ===== Main Execution =====

print_banner "Checkpoint Testing Pipeline"

echo "Configuration:"
echo "  Checkpoint: $CHECKPOINT_PATH"
echo "  Benchmark: $BENCHMARK"
echo "  Dataset: $DATASET_PATH"
echo "  GPU: cuda:$GPU_ID"
echo "  Port: $SERVER_PORT"
echo ""

# Check if checkpoint exists
if [ ! -d "$CHECKPOINT_PATH" ] && [ ! -f "$CHECKPOINT_PATH" ]; then
    echo "Error: Checkpoint path does not exist: $CHECKPOINT_PATH"
    exit 1
fi

# Check if dataset exists
if [ ! -f "$DATASET_PATH" ]; then
    echo "Error: Dataset file does not exist: $DATASET_PATH"
    exit 1
fi

# Step 1: Start vLLM server
print_banner "Starting vLLM Server"

python start_vllm_server.py \
    --model-path "$CHECKPOINT_PATH" \
    --port $SERVER_PORT \
    --gpu-id $GPU_ID \
    --tensor-parallel-size $TENSOR_PARALLEL_SIZE \
    --max-model-len $MAX_MODEL_LEN \
    --served-model-name "checkpoint-model" &

SERVER_PID=$!
echo "vLLM server started with PID: $SERVER_PID"

# Wait for server to be ready
if ! check_server_ready; then
    echo "Failed to start vLLM server!"
    exit 1
fi

# Step 2: Run checkpoint testing
print_banner "Running Checkpoint Test"

python test_checkpoint.py \
    --checkpoint-path "$CHECKPOINT_PATH" \
    --benchmark "$BENCHMARK" \
    --dataset-path "$DATASET_PATH" \
    --server-url "http://localhost:$SERVER_PORT" \
    --exec-llm "$EXEC_LLM" \
    --num-batches $NUM_BATCHES \
    --workflows-per-batch $WORKFLOWS_PER_BATCH \
    --problems-per-workflow $PROBLEMS_PER_WORKFLOW \
    --parallelism $PARALLELISM \
    --output-base-dir "$OUTPUT_BASE_DIR"

TEST_EXIT_CODE=$?

# Step 3: Generate summary report
print_banner "Test Complete"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "Checkpoint testing completed successfully!"
    
    # Find the latest test directory
    LATEST_TEST_DIR=$(ls -t "$OUTPUT_BASE_DIR" | head -1)
    if [ ! -z "$LATEST_TEST_DIR" ]; then
        echo "Results saved to: $OUTPUT_BASE_DIR/$LATEST_TEST_DIR"
        
        # Display summary if available
        SUMMARY_FILE="$OUTPUT_BASE_DIR/$LATEST_TEST_DIR/test_summary.json"
        if [ -f "$SUMMARY_FILE" ]; then
            echo ""
            echo "Test Summary:"
            python -c "
import json
with open('$SUMMARY_FILE', 'r') as f:
    summary = json.load(f)
    print(f\"  Total workflows: {summary['total_generated']}\")
    print(f\"  Successfully generated: {summary['total_successful']}\")
    print(f\"  Verified correct: {summary['total_correct']}\")
    print(f\"  Success rate: {summary['success_rate']*100:.1f}%\")
    print(f\"  Total time: {summary['elapsed_time']:.1f}s\")
"
        fi
    fi
else
    echo "Checkpoint testing failed with exit code: $TEST_EXIT_CODE"
fi

echo ""
echo "Pipeline complete!"