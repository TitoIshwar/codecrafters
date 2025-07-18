from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from Core_API_Routes import router as core_router
from analytics_routes import router as analytics_router
import os
import uvicorn

app = FastAPI(
    title="One Brave Thing API",
    description="API for the personalized life coaching platform.",
    version="1.0.0"
)

# CORS setup
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://your-frontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("static/badges.html")  # ✅ Ensure this file exists

# API routers
app.include_router(core_router, prefix="/api", tags=["Core"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])

@app.get("/api", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the One Brave Thing API!"}

# Start the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
