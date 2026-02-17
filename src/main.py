import uvicorn

from src.fast_api.fastapi_factory import create_fastapi_app

app = create_fastapi_app()

if __name__ == '__main__':
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, log_config=None)
