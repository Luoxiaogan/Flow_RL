# Qwen-Max-Latest Thinking Feature Configuration

## Overview

This document describes how to configure the workflow system to use `qwen-max-latest` with the thinking feature enabled.

## Configuration Changes

### 1. config2.yaml
Already configured correctly with:
- `model: "qwen-max-latest"`
- Correct API key and base URL

### 2. run_workflow_system_drop.sh

Updated API configurations to include thinking parameters:

```json
API_POOL='[
    {
        "provider": "openai",
        "model": "qwen-max-latest",
        "api_key": "956c41bd0f31beaf68b871d4987af4bb",
        "base_url": "https://idealab.alibaba-inc.com/api/openai/v1",
        "stream": false,
        "stream_options": {"include_usage": true},
        "enable_thinking": true,
        "thinking_budget": 1000
    }
]'
```

### 3. workflow_generator.py

Modified `call_openai_compatible_api` function to support extra parameters:
- Passes `stream` and `stream_options` directly to the API
- Passes `enable_thinking` and `thinking_budget` via `extra_body` parameter

## Testing

Run the test script to verify the configuration:
```bash
python test_qwen_thinking.py
```

## CURL Reference

The configuration is based on this working CURL command:
```bash
curl -X POST https://idealab.alibaba-inc.com/api/openai/v1/chat/completions \
-H "Authorization: Bearer 956c41bd0f31beaf68b871d4987af4bb" \
-H "Content-Type: application/json" \
-d '{
    "model": "qwen-max-latest",
    "messages": [...],
    "stream": false,
    "stream_options": {"include_usage": true},
    "enable_thinking": true,
    "thinking_budget": 1000
}'
```

## Parameters Explained

- **enable_thinking**: Enables the model's internal thinking process
- **thinking_budget**: Maximum tokens allocated for thinking (1000 tokens)
- **stream**: Set to false for non-streaming responses
- **stream_options**: Includes usage statistics in the response

## Notes

- The thinking feature is only available for `qwen-max-latest` model
- The `extra_body` parameter in OpenAI client is used to pass non-standard parameters
- MetaGPT execution (workflow_executor.py) doesn't need these parameters as they're only for workflow generation