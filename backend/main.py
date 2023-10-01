from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import router


app = FastAPI(title="FIREWALL DEBUGGER API")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="debug",
        reload=True,
    )
