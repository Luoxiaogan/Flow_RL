"""
API Connection Pool Manager for reusing HTTP connections
"""
import threading
import logging
from typing import Dict, Optional
from contextlib import contextmanager
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class APIConnectionPool:
    """
    Singleton connection pool manager for API requests
    """
    _instance = None
    _sessions: Dict[str, requests.Session] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_session(cls, key: str = 'default',
                    timeout: int = 60,
                    max_retries: int = 3,
                    pool_connections: int = 10,
                    pool_maxsize: int = 100) -> requests.Session:
        """
        Get or create a session for the given key

        Args:
            key: Session identifier (e.g., 'openai', 'azure')
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to save in the pool

        Returns:
            requests.Session instance
        """
        instance = cls()

        with cls._lock:
            if key not in cls._sessions:
                logger.debug(f"Creating new session for key: {key}")

                # Create session
                session = requests.Session()

                # Configure retry strategy
                retry_strategy = Retry(
                    total=max_retries,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )

                # Create adapter with connection pooling
                adapter = HTTPAdapter(
                    max_retries=retry_strategy,
                    pool_connections=pool_connections,
                    pool_maxsize=pool_maxsize
                )

                # Mount adapter for both HTTP and HTTPS
                session.mount("http://", adapter)
                session.mount("https://", adapter)

                # Set default timeout (can be overridden per request)
                session.timeout = timeout

                cls._sessions[key] = session
                logger.info(f"Created new API session: {key}")

            return cls._sessions[key]
    
    @classmethod
    def close_session(cls, key: str = None):
        """
        Close a specific session or all sessions

        Args:
            key: Session key to close, or None to close all
        """
        with cls._lock:
            if key:
                if key in cls._sessions:
                    cls._sessions[key].close()
                    del cls._sessions[key]
                    logger.info(f"Closed API session: {key}")
            else:
                # Close all sessions
                for session_key, session in cls._sessions.items():
                    session.close()
                    logger.info(f"Closed API session: {session_key}")
                cls._sessions.clear()
    
    @classmethod
    def cleanup(cls):
        """
        Clean up all sessions
        """
        cls.close_session(key=None)
        logger.info("All API sessions cleaned up")
    
    @classmethod
    @contextmanager
    def session_context(cls, key: str = 'default', **kwargs):
        """
        Context manager for session usage

        Usage:
            with APIConnectionPool.session_context('openai') as session:
                response = session.post(url, json=data)
                result = response.json()
        """
        session = cls.get_session(key, **kwargs)
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
                'active': True,  # requests.Session doesn't have a 'closed' state
                'adapters': len(session.adapters)
            }
        
        return stats