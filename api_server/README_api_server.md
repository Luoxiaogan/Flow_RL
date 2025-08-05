# API 中转队列服务器

这是一个 API 请求中转服务器，它会：
1. 接收所有发送到 localhost 的请求
2. 将请求加入队列
3. 每隔 0.1 秒将请求原封不动转发到目标服务器

## 功能特点

- **请求队列化**：所有请求先进入队列，按顺序处理
- **固定间隔转发**：每隔 0.1 秒转发一个请求
- **完整转发**：保留所有请求头、请求体和参数
- **重试机制**：失败请求自动重试（最多 3 次）
- **状态追踪**：可查询请求状态和队列信息
- **配置管理**：支持动态更新配置

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements_api_server.txt
```

### 2. 配置目标服务器
编辑 `api_server_config.json`：
```json
{
    "forward_url": "http://your-target-server.com/api",
    "local_port": 5000,
    "queue_interval": 0.1,
    "timeout": 30,
    "max_retries": 3
}
```

### 3. 启动服务器

**Windows:**
```bash
run_api_server.bat
```

**Linux/Mac:**
```bash
python api_server_advanced.py
```

### 4. 发送请求
将原本发送到目标服务器的请求改为发送到：
```
http://localhost:5000/your/api/path
```

## API 端点

### 主要功能
- `http://localhost:5000/*` - 所有请求都会被队列化并转发

### 管理端点
- `GET /api/queue/status` - 查看队列状态
- `GET /api/request/<request_id>` - 查询特定请求状态
- `GET/POST /api/config` - 查看或更新配置
- `GET /health` - 健康检查

## 示例

### 发送请求
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "age": 30}'
```

响应：
```json
{
    "status": "queued",
    "request_id": "1234567890.0_127.0.0.1",
    "queue_position": 1,
    "timestamp": "2024-01-01T12:00:00",
    "estimated_wait": 0.1
}
```

### 查询队列状态
```bash
curl http://localhost:5000/api/queue/status
```

### 更新配置
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "forward_url": "http://new-server.com/api",
    "queue_interval": 0.2
  }'
```

## 注意事项

1. 服务器会保存最近 1000 个请求的响应状态
2. 请求按照先进先出（FIFO）顺序处理
3. 如果目标服务器无响应，会自动重试
4. 所有请求都会返回 202 状态码（已接受）