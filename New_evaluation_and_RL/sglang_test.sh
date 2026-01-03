curl http://0.0.0.0:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-8b",
    "messages": [
      {"role": "user", "content": "帮我算一下 (-3+4i)/(1+2i)。"}
    ],
    "temperature": 0.7,
    "max_tokens": 8192
  }'
