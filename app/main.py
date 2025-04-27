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
    )
    server = uvicorn.Server(config)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
