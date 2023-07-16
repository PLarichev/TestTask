import uvicorn
from fastapi import FastAPI
from app.core.api import api_router, api_router_with_token
from app.db.session import engine
from app.db.models import Base
from app.config import config


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api",
    debug=config.DEBUG,
)

app.include_router(api_router)
app.include_router(api_router_with_token)


@app.on_event('startup')
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.on_event('shutdown')
def shutdown_event():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
