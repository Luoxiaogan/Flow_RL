"""
Reward server checker - checks if reward server is running
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
        
        # Clear proxy settings for localhost communication
        self._clear_proxy_settings()
    
    def _clear_proxy_settings(self):
        """
        Clear proxy environment variables to ensure local service communication works
        """
        # Set NO_PROXY to exclude localhost
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
        os.environ['no_proxy'] = 'localhost,127.0.0.1,0.0.0.0,*.local'
        
        # Clear proxy environment variables
        proxy_vars = ['http_proxy', 'https_proxy', 'all_proxy', 
                      'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']
        
        for proxy_var in proxy_vars:
            if proxy_var in os.environ:
                del os.environ[proxy_var]
                logger.info(f"✓ 已清除环境变量: {proxy_var}")
        
        logger.info(f"✓ 已设置 NO_PROXY='{os.environ.get('NO_PROXY', '')}' (防止代理拦截)")
    
    async def check_server(self, timeout: int = 5) -> bool:
        """
        Check if reward server is running and accessible
        
        Args:
            timeout: Timeout in seconds for health check
            
        Returns:
            True if server is running, False otherwise
        """
        try:
            # Clear proxy settings again before making request
            self._clear_proxy_settings()
            
            logger.info(f"检查 Reward Server: {self.health_endpoint}")
            
            # Create session with no proxy
            connector = aiohttp.TCPConnector(force_close=True)
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_obj,
                trust_env=False  # Ignore system proxy settings
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
            logger.error("启动命令: cd New_evaluation_and_RL/reward_server && python scoreflow_reward_server.py")
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
    
    def get_server_info(self) -> dict:
        """
        Get server information
        
        Returns:
            Dictionary with server information
        """
        return {
            'url': self.server_url,
            'health_endpoint': self.health_endpoint,
            'no_proxy': os.environ.get('NO_PROXY', ''),
            'proxy_cleared': all(
                var not in os.environ 
                for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
            )
        }


# Standalone test function
async def test_server_checker():
    """
    Test the reward server checker
    """
    checker = RewardServerChecker()
    
    print("Server Info:", checker.get_server_info())
    
    # Check if server is running
    is_running = await checker.check_server()
    
    if is_running:
        print("✓ Reward Server is running")
    else:
        print("✗ Reward Server is not running")
        print("Waiting for server to start...")
        
        # Wait for server
        if await checker.wait_for_server(max_attempts=6, delay=5):
            print("✓ Server is now available")
        else:
            print("✗ Server did not start in time")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_server_checker())