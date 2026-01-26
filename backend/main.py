from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import dashboard, vaccines, medicines, blood, ambulance, alerts, auth
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth router (no prefix for /token)
app.include_router(auth.router)

app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(vaccines.router, prefix=settings.API_V1_STR)
app.include_router(medicines.router, prefix=settings.API_V1_STR)
app.include_router(blood.router, prefix=settings.API_V1_STR)
app.include_router(ambulance.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Health System Decision Intelligence API is running", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
