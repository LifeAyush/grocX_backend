import asyncio
import logging
from typing import List, Tuple, Callable, Any, Coroutine
from app.core.config import settings

logger = logging.getLogger(__name__)

async def run_concurrently_with_limit(
    tasks: List[Tuple[Callable, Tuple]], 
    limit: int = settings.MAX_CONCURRENT_REQUESTS
) -> List[Any]:
    """
    Run a list of tasks concurrently with a limit on the number of
    simultaneous tasks.
    
    Args:
        tasks: List of tuples (function, args) to run concurrently
        limit: Maximum number of tasks to run simultaneously
        
    Returns:
        List of results from all tasks
    """
    semaphore = asyncio.Semaphore(limit)
    results = []
    
    async def run_with_semaphore(func, args):
        async with semaphore:
            try:
                return await func(*args)
            except Exception as e:
                logger.error(f"Error in concurrent task: {str(e)}")
                raise
    
    # Create tasks with semaphore
    concurrent_tasks = [
        asyncio.create_task(run_with_semaphore(func, args))
        for func, args in tasks
    ]
    
    # Wait for all tasks to complete
    if concurrent_tasks:
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
    
    # Check for exceptions
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Task {i} failed with error: {str(result)}")
    
    # Filter out exceptions
    return [r for r in results if not isinstance(r, Exception)]

async def with_timeout(coro: Coroutine, timeout: float = settings.SCRAPER_TIMEOUT) -> Any:
    """
    Run a coroutine with a timeout.
    
    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        
    Returns:
        Result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If the coroutine takes longer than the timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {timeout} seconds")
        raise