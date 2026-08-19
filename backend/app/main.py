from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.platforms import router as platforms_router
from app.routers.clients import router as clients_router
from app.routers.resource import router as resource_router
from app.routers.imports import router as imports_router
from app.routers.analysis import router as analysis_router
from app.routers.accounts import router as accounts_router
from app.routers.users import router as users_router
from app.routers.gorgias_credentials import router as gorgias_credentials_router


app = FastAPI(title="IS Resource File Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(platforms_router)
app.include_router(clients_router)
app.include_router(resource_router)
app.include_router(imports_router)
app.include_router(analysis_router)
app.include_router(accounts_router)
app.include_router(users_router)
app.include_router(gorgias_credentials_router)

@app.get("/")
def root():
    return {"message": "API is running"}