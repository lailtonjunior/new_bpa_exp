import uvicorn

from .main import app


def run():
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        proxy_headers=True,
    )


if __name__ == "__main__":
    run()
