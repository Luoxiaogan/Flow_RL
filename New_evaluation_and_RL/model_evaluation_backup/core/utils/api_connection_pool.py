"""
API Connection Pool Manager for reusing HTTP connections
"""
import aiohttp
import asyncio
import logging
from typing import Dict, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class APIConnectionPool:
    """
    Singleton connection pool manager for API requests
    """
    _instance = None
    _sessions: Dict[str, aiohttp.ClientSession] = {}
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def get_session(cls, key: str = 'default', 
                          timeout: int = 60,
                          connector_limit: int = 100) -> aiohttp.ClientSession:
        """
        Get or create a session for the given key
        
        Args:
            key: Session identifier (e.g., 'openai', 'azure')
            timeout: Request timeout in seconds
            connector_limit: Maximum number of connections
            
        Returns:
            aiohttp.ClientSession instance
        """
        instance = cls()
        
        async with cls._lock:
            if key not in cls._sessions or cls._sessions[key].closed:
                logger.debug(f"Creating new session for key: {key}")
                
                # Create connector with connection limit
                connector = aiohttp.TCPConnector(
                    limit=connector_limit,
                    limit_per_host=30,
                    force_close=False,
                    enable_cleanup_closed=True
                )
                
                # Create timeout
                timeout_obj = aiohttp.ClientTimeout(
                    total=timeout,
                    connect=10,
                    sock_read=timeout
                )
                
                # Create session
                cls._sessions[key] = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout_obj,
                    trust_env=False  # Ignore system proxy
                )
                
                logger.info(f"Created new API session: {key}")
            
            return cls._sessions[key]
    
    @classmethod
    async def close_session(cls, key: str = None):
        """
        Close a specific session or all sessions
        
        Args:
            key: Session key to close, or None to close all
        """
        async with cls._lock:
            if key:
                if key in cls._sessions:
                    await cls._sessions[key].close()
                    del cls._sessions[key]
                    logger.info(f"Closed API session: {key}")
            else:
                # Close all sessions
                for session_key, session in cls._sessions.items():
                    if not session.closed:
                        await session.close()
                        logger.info(f"Closed API session: {session_key}")
                cls._sessions.clear()
    
    @classmethod
    async def cleanup(cls):
        """
        Clean up all sessions
        """
        await cls.close_session(key=None)
        logger.info("All API sessions cleaned up")
    
    @classmethod
    @asynccontextmanager
    async def session_context(cls, key: str = 'default', **kwargs):
        """
        Context manager for session usage
        
        Usage:
            async with APIConnectionPool.session_context('openai') as session:
                async with session.post(url, json=data) as response:
                    result = await response.json()
        """
        session = await cls.get_session(key, **kwargs)
        try:
            yield session
        finally:
            # Session remains open for reuse
            pass
    
    @classmethod
    def get_stats(cls) -> Dict:
        """
        Get connection pool statistics
        
        Returns:
            Dictionary with session statistics
        """
        stats = {
            'total_sessions': len(cls._sessions),
            'sessions': {}
        }
        
        for key, session in cls._sessions.items():
            stats['sessions'][key] = {
                'closed': session.closed,
                'connector_limit': session.connector.limit if hasattr(session, 'connector') else None
            }
        
        return stats