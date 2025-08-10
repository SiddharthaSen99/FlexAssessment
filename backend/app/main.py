from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.reviews import router as reviews_router
from .models.db import create_db_and_tables


app = FastAPI(title="Flex Living Reviews API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(reviews_router, prefix="/api")
