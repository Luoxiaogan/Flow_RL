# Token Tracking and Cost Management System

## Overview

This directory contains an enhanced version of the ScoreFlow Reward Server with integrated token tracking and cost management capabilities. The system tracks API token usage, calculates costs, and can apply score penalties based on resource consumption.

## Features

### 1. Token Tracking
- **Per-workflow tracking**: Each workflow execution has isolated token counting
- **Model-aware pricing**: Supports multiple model pricing configurations
- **Real-time statistics**: Track prompt/completion tokens and costs
- **MetaGPT integration**: Uses native MetaGPT Context and CostManager

### 2. Cost Management
- **Multi-model support**: Configure prices for different AI models
- **Flexible penalty modes**: Linear, square, exponential, logarithmic, threshold
- **Cost alerts**: Configurable thresholds for workflow/hourly/daily costs
- **Detailed reporting**: Generate comprehensive cost reports

### 3. Enhanced API
- **Token stats in responses**: Automatic inclusion in compute_score responses
- **Dedicated endpoints**: `/token_stats`, `/cost_report`, `/reset_stats`
- **Batch processing support**: Handle multiple workflows with aggregated stats

## Architecture

```
reward_server_cost/
├── token_tracker.py           # Token tracking module using MetaGPT
├── cost_calculator.py         # Cost calculation and penalty logic
├── scoreflow_reward_utils_with_cost.py  # Main utility with tracking
├── scoreflow_reward_server_with_cost.py # Enhanced server
├── config_cost.yaml          # Configuration file
├── test_token_tracking.py    # Test script
└── start_server_with_cost.sh # Startup script
```

## Configuration

Edit `config_cost.yaml` to configure:

### Token Tracking
```yaml
token_tracking:
  enabled: true
  pricing:
    models:
      qwen-turbo:
        input_price: 0.5   # per million tokens
        output_price: 1.5
```

### Penalty Settings
```yaml
penalty:
  enabled: true
  mode: "linear"       # linear|square|exponential|logarithmic|threshold
  rate: 0.1           # penalty rate
  max_penalty: 0.3    # maximum penalty cap
```

### Alerts
```yaml
alerts:
  enabled: true
  thresholds:
    workflow_cost: 2.0
    hourly_cost: 10.0
    daily_cost: 100.0
```

## Installation

1. **Install dependencies**:
```bash
pip install flask flask-cors pyyaml
```

2. **Install MetaGPT** (for token tracking):
```bash
pip install metagpt
```

3. **Configure paths**: Update paths in config files if needed

## Usage

### Starting the Server

```bash
# Using the startup script
bash start_server_with_cost.sh

# Or directly
python scoreflow_reward_server_with_cost.py --host 0.0.0.0 --port 8899
```

### API Endpoints

#### 1. Compute Score with Token Stats
```bash
curl -X POST http://localhost:8899/compute_score \
  -H "Content-Type: application/json" \
  -d '{
    "data_source": "gsm8k",
    "solution_str": "<workflow_code>",
    "ground_truth": "default",
    "extra_info": {"test_cases": [0, 1, 2]}
  }'
```

Response includes token statistics:
```json
{
  "success": true,
  "score": 0.85,
  "token_stats": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801,
    "total_cost": 0.0018
  }
}
```

#### 2. Get Token Statistics
```bash
curl http://localhost:8899/token_stats
```

#### 3. Get Cost Report
```bash
curl http://localhost:8899/cost_report
```

#### 4. Reset Statistics
```bash
curl -X POST http://localhost:8899/reset_stats
```

## Testing

Run the test script to verify functionality:

```bash
python test_token_tracking.py
```

This will test:
- Token tracker initialization
- Cost calculator functions
- Penalty calculations
- Server API endpoints

## How It Works

### Token Tracking Flow

1. **Workflow starts**: Create isolated Context with CostManager
2. **LLM execution**: MetaGPT tracks tokens via CostManager
3. **Workflow ends**: Extract statistics from CostManager
4. **Apply penalties**: Calculate cost-based score adjustments
5. **Return results**: Include token stats in response

### Cost Calculation

```python
# Per million tokens pricing
input_cost = (prompt_tokens / 1_000_000) * input_price
output_cost = (completion_tokens / 1_000_000) * output_price
total_cost = input_cost + output_cost

# Apply penalty (if enabled)
penalty = total_cost * penalty_rate  # for linear mode
final_score = base_score * (1 - min(penalty, max_penalty))
```

## Penalty Modes

1. **Linear**: `penalty = cost * rate`
2. **Square**: `penalty = cost² * rate`
3. **Exponential**: `penalty = (e^cost - 1) * rate`
4. **Logarithmic**: `penalty = log(1 + cost) * rate`
5. **Threshold**: Progressive penalties based on cost thresholds

## Performance Considerations

- **Memory**: Each workflow maintains separate Context (cleanup after TTL)
- **Concurrency**: Thread-safe token tracking with locks
- **Caching**: Configurable cache for statistics (default 1 hour)
- **Cleanup**: Automatic cleanup of old contexts to prevent memory leaks

## Troubleshooting

### Token tracking not working
- Check MetaGPT is installed: `pip install metagpt`
- Verify config_cost.yaml has `token_tracking.enabled: true`
- Check server logs for initialization messages

### Costs showing as zero
- Ensure workflow actually calls LLM
- Verify CostManager is properly linked to LLM instance
- Check model pricing configuration

### Penalties not applied
- Verify `penalty.enabled: true` in config
- Check penalty mode and rate settings
- Ensure token stats are being collected

## Integration with Existing System

This enhanced version maintains full compatibility with the original ScoreFlow Reward Server while adding:
- Optional token tracking (can be disabled)
- Backward-compatible API (original endpoints unchanged)
- Configurable features (all enhancements are optional)

## Future Enhancements

- [ ] Database storage for historical data
- [ ] Visualization dashboard
- [ ] Budget limits and automatic throttling
- [ ] Multi-user token accounting
- [ ] Export reports in multiple formats
- [ ] Webhook notifications for alerts

## Support

For issues or questions:
1. Check the test script output
2. Review server logs for errors
3. Verify configuration settings
4. Ensure all dependencies are installed

## License

This is part of the Flow_RL project. See main project documentation for license details.