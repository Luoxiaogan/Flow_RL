#!/bin/bash
# 快速测试健康检查修复是否生效

echo "=========================================="
echo "测试健康检查修复"
echo "=========================================="
echo

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试端口（默认API代理端口）
API_PROXY_PORT=5019

echo "1. 测试健康检查端点 (不会触发阿里云API调用)"
echo "   URL: http://localhost:$API_PROXY_PORT/health"
echo

# 使用curl测试健康检查端点
echo "使用curl测试："
if curl -s http://localhost:$API_PROXY_PORT/health 2>/dev/null | python3 -m json.tool; then
    echo -e "\n${GREEN}✅ 健康检查端点返回JSON数据成功${NC}"
else
    echo -e "\n${RED}❌ 无法访问健康检查端点${NC}"
    echo -e "${YELLOW}请先启动API代理：bash servers_and_proxy/start_api_proxy.sh${NC}"
    exit 1
fi

echo
echo "2. 测试启动脚本的健康检查逻辑"
echo

# 模拟启动脚本的健康检查
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$API_PROXY_PORT/health | grep -q "200"; then
    echo -e "${GREEN}✅ 启动脚本健康检查逻辑测试通过${NC}"
    echo "   返回状态码: 200"
else
    echo -e "${RED}❌ 启动脚本健康检查逻辑失败${NC}"
fi

echo
echo "=========================================="
echo -e "${GREEN}修复验证完成！${NC}"
echo
echo "说明："
echo "1. /health 端点只返回服务状态，不会转发到阿里云"
echo "2. 启动脚本现在使用 /health 端点进行健康检查"
echo "3. 不会再出现 'GET method not supported' 错误"
echo
echo "下一步："
echo "1. 重启API代理服务以应用修改"
echo "2. 运行 start_scoreflow_reward.sh 验证完整流程"
echo "=========================================="