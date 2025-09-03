"""
Reward server health checker
"""
import os
import aiohttp
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RewardServerChecker:
    """
    Checks if reward server is running and accessible
    """
    
    def __init__(self, server_url: str = 'http://localhost:8899'):
        """
        Initialize server checker
        
        Args:
            server_url: URL of the reward server
        """
        self.server_url = server_url
        self.health_endpoint = f"{server_url}/health"
        self._clear_proxy_settings()
    
    def _clear_proxy_settings(self):
        """
        Clear proxy environment variables to ensure local service communication works
        """
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
        os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
        
        proxy_vars = ['http_proxy', 'https_proxy', 'all_proxy', 
                      'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']
        
        for proxy_var in proxy_vars:
            if proxy_var in os.environ:
                del os.environ[proxy_var]
                logger.debug(f"已清除环境变量: {proxy_var}")
    
    async def check_server(self, timeout: int = 5) -> bool:
        """
        Check if reward server is running
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            True if server is running, False otherwise
        """
        try:
            self._clear_proxy_settings()
            logger.info(f"检查 Reward Server: {self.health_endpoint}")
            
            connector = aiohttp.TCPConnector(force_close=True)
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_obj,
                trust_env=False
            ) as session:
                async with session.get(self.health_endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✓ Reward Server 正常运行: {data}")
                        return True
                    else:
                        logger.warning(f"Reward Server 返回状态码: {response.status}")
                        return False
                        
        except aiohttp.ClientError as e:
            logger.error(f"无法连接到 Reward Server: {e}")
            logger.error(f"请确保 Reward Server 在 {self.server_url} 上运行")
            logger.error("启动命令: bash New_evaluation_and_RL/servers_and_proxy/start_scoreflow_reward.sh")
            return False
        except Exception as e:
            logger.error(f"检查 Reward Server 时出错: {e}")
            return False
    
    async def wait_for_server(self, max_attempts: int = 12, delay: int = 5) -> bool:
        """
        Wait for reward server to become available
        
        Args:
            max_attempts: Maximum number of attempts
            delay: Delay between attempts in seconds
            
        Returns:
            True if server becomes available, False if timeout
        """
        logger.info(f"等待 Reward Server 启动 (最多 {max_attempts * delay} 秒)...")
        
        for attempt in range(1, max_attempts + 1):
            if await self.check_server():
                logger.info(f"✓ Reward Server 已就绪 (尝试 {attempt}/{max_attempts})")
                return True
            
            if attempt < max_attempts:
                logger.info(f"Reward Server 未就绪，{delay} 秒后重试... (尝试 {attempt}/{max_attempts})")
                await asyncio.sleep(delay)
        
        logger.error(f"✗ Reward Server 在 {max_attempts * delay} 秒后仍未就绪")
        return False