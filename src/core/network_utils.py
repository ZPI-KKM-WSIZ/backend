import asyncio
import logging
import random


async def retry_with_delay_async(async_func, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0,
                                 *args, **kwargs):
    """
    Executes an async function with exponential backoff retry logic.
    
    Retries the given async function with progressively increasing delays
    between attempts using exponential backoff with jitter.
    
    Args:
        async_func: The async function to execute.
        max_retries: Maximum number of retry attempts (default: 3).
        base_delay: Initial delay in seconds between retries (default: 1.0).
        max_delay: Maximum delay in seconds between retries (default: 10.0).
        *args: Positional arguments to pass to async_func.
        **kwargs: Keyword arguments to pass to async_func.
        
    Returns:
        The return value of the successful async_func execution.
        
    Raises:
        RuntimeError: If all retry attempts fail, wrapping the last exception.
    """
    last_exception = None
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1} to complete {async_func.__name__}")
            return await async_func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                delay += random.uniform(0, base_delay)
                await asyncio.sleep(delay)
    raise RuntimeError(
        f"Failed to complete {async_func.__name__} after {max_retries} attempts"
    ) from last_exception
