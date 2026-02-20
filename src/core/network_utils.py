import asyncio
import logging


async def retry_with_delay(max_retries: int, base_delay: float, async_func):
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1} to complete {async_func.__name__}")
            result = await async_func()
            if result:
                return result
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to complete {async_func.__name__} after {max_retries} attempts") from e
            await asyncio.sleep(base_delay * (2 ** attempt))
    raise RuntimeError(f"Failed to complete {async_func.__name__} after {max_retries} attempts")
