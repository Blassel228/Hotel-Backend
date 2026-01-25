import asyncio
import uvicorn
from app.core.config import settings
from app.init_app import app


async def main():
    config = uvicorn.Config(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        limit_concurrency=1000,
        timeout_keep_alive=5,
        limit_max_requests=None,
        backlog=2048,
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
