#!/bin/bash
# Run script for InternBootcamp workflow generation using ScoreFlow

# Configuration
BASE_DIR=$(dirname "$0")
CONFIG_FILE="${BASE_DIR}/config.json"
OUTPUT_BASE="${BASE_DIR}/output"

# LLM Configuration (adjust as needed)
export OPENAI_BASE_URL="https://api.deepseek.com"
export OPENAI_API_KEY="sk-your-api-key"
export OPENAI_MODEL="deepseek-chat"

# Create output directory
mkdir -p "${OUTPUT_BASE}"

echo "=== InternBootcamp Workflow Generation with ScoreFlow ==="
echo

# Function to run workflow generation
run_workflow_generation() {
    local workflow_type=$1
    local tasks=$2
    
    echo ">>> Generating ${workflow_type} workflows for tasks: ${tasks}"
    
    python "${BASE_DIR}/workflow_generator_scoreflow.py" \
        --workflow-type "${workflow_type}" \
        --tasks ${tasks} \
        --workflows-per-task 3 \
        --config "${CONFIG_FILE}" \
        --output-dir "${OUTPUT_BASE}/workflows_${workflow_type}" \
        --temperature 0.7 \
        --max-workers 5
}

# Function to run workflow execution
run_workflow_execution() {
    local workflow_type=$1
    
    echo ">>> Executing ${workflow_type} workflows"
    
    python "${BASE_DIR}/workflow_executor_scoreflow.py" \
        --workflow-dir "${OUTPUT_BASE}/workflows_${workflow_type}/individual_workflows" \
        --config "../config2.yaml" \
        --output-dir "${OUTPUT_BASE}/execution_results_${workflow_type}" \
        --max-workers 3 \
        --timeout 180
}

# Function to generate VERL data with workflows
run_verl_generation() {
    local workflow_type=$1
    local tasks=$2
    
    echo ">>> Generating VERL data with ${workflow_type} workflows"
    
    python "${BASE_DIR}/generate_verl_with_workflows.py" \
        --workflow-type "${workflow_type}" \
        --tasks ${tasks} \
        --entries-per-task 5 \
        --examples-per-entry 3 \
        --config "${CONFIG_FILE}" \
        --output-dir "${OUTPUT_BASE}/verl_data" \
        --temperature 0.7 \
        --max-workers 3 \
        --execution-timeout 180
}

# Main execution flow
main() {
    # Example tasks (adjust based on available tasks)
    EXAMPLE_TASKS="sudoku_4x4_easy minesweeper_5x5 kakuro_5x5"
    
    # Option 1: Generate and execute workflows separately
    echo "=== Option 1: Separate Generation and Execution ==="
    echo
    
    # Generate predefined operator workflows
    run_workflow_generation "predefined" "${EXAMPLE_TASKS}"
    
    # Generate flexible custom operator workflows
    run_workflow_generation "flexible" "${EXAMPLE_TASKS}"
    
    # Execute workflows and calculate rewards
    run_workflow_execution "predefined"
    run_workflow_execution "flexible"
    
    echo
    echo "=== Option 2: Integrated VERL Data Generation ==="
    echo
    
    # Generate VERL data with predefined operator workflows
    run_verl_generation "predefined" "${EXAMPLE_TASKS}"
    
    # Generate VERL data with flexible custom operator workflows
    run_verl_generation "flexible" "${EXAMPLE_TASKS}"
    
    echo
    echo "=== Generation Complete ==="
    echo "Results saved to: ${OUTPUT_BASE}"
    echo
    echo "Summary:"
    echo "- Predefined workflows: ${OUTPUT_BASE}/workflows_predefined/"
    echo "- Flexible workflows: ${OUTPUT_BASE}/workflows_flexible/"
    echo "- Execution results: ${OUTPUT_BASE}/execution_results_*/"
    echo "- VERL training data: ${OUTPUT_BASE}/verl_data/"
}

# Parse command line arguments
case "${1:-all}" in
    "generate")
        # Only generate workflows
        run_workflow_generation "${2:-predefined}" "${3:-sudoku_4x4_easy minesweeper_5x5}"
        ;;
    "execute")
        # Only execute workflows
        run_workflow_execution "${2:-predefined}"
        ;;
    "verl")
        # Generate VERL data with workflows
        run_verl_generation "${2:-predefined}" "${3:-sudoku_4x4_easy minesweeper_5x5}"
        ;;
    "all")
        # Run complete pipeline
        main
        ;;
    *)
        echo "Usage: $0 {generate|execute|verl|all} [workflow_type] [tasks]"
        echo "  workflow_type: predefined or flexible"
        echo "  tasks: space-separated list of task names"
        exit 1
        ;;
esac