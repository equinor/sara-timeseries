import uvicorn

from sara_timeseries.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "sara_timeseries.app:app",
        host=settings.FAST_API_HOST,
        port=settings.FAST_API_PORT,
        reload=settings.RELOAD,
    )
