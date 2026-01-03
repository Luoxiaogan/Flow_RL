# API Proxy 测试指南

## 1. 本地测试

**启动服务：**
```bash
cd /Users/luogan/Code/workflow_generation/New_Flow_RL
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxx"
python -m services.api_proxy.server
```

**测试（另开终端）：**
```bash
curl http://localhost:5059/health

curl http://localhost:5059/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen-turbo", "messages": [{"role": "user", "content": "1+1等于几"}]}'
```

---

## 2. Docker 测试

### 2.1 配置

```bash
cd /Users/luogan/Code/workflow_generation/New_Flow_RL/docker
cp .env.example .env
# 编辑 .env，填入 DASHSCOPE_API_KEY
```

### 2.2 构建和运行

```bash
# 构建（需要代理下载镜像）
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
docker-compose build proxy

# 运行（不需要代理）
unset http_proxy https_proxy all_proxy
docker-compose up -d proxy
```

### 2.3 测试

```bash
curl http://localhost:5059/health

curl http://localhost:5059/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen-turbo", "messages": [{"role": "user", "content": "1+1等于几"}]}'
```

### 2.4 常用命令

```bash
docker system df

docker-compose -f docker/docker-compose.yml start # 重新启动所有当前的容器

docker-compose -f docker/docker-compose.yml stop # 停止所有的容器
```


```bash
# 构建
docker-compose build proxy          # 构建 proxy 镜像
docker-compose build                # 构建所有服务镜像

# 启动
docker-compose up -d proxy          # 后台启动 proxy
docker-compose up -d                # 后台启动所有服务
docker-compose up proxy             # 前台启动（看实时日志）

# 查看状态
docker-compose ps                   # 查看服务状态
docker ps                           # 查看运行中的容器
docker ps -a                        # 查看所有容器（含已停止）
docker images                       # 查看所有镜像

# 查看日志
docker-compose logs proxy           # 查看 proxy 日志
docker-compose logs -f proxy        # 实时跟踪日志（Ctrl+C 退出）
docker-compose logs --tail=50 proxy # 只看最后50行

# 停止
docker-compose stop proxy           # 停止容器（保留）
docker-compose down                 # 停止并删除容器

# 清理
docker-compose down --rmi all       # 停止并删除容器+镜像
docker system prune                 # 清理无用的容器/镜像/网络
```
