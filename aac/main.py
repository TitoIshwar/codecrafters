from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from Core_API_Routes import router as core_router
from analytics_routes import router as analytics_router
import uvicorn
import os

# Create the FastAPI app instance
app = FastAPI(
    title="One Brave Thing API",
    description="API for the personalized life coaching platform.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://your-frontend.onrender.com"  # ✅ Add your deployed frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend folder to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main HTML page (badges.html or another)
@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("static/badges.html")  # ✅ Update to your homepage filename

# Include API routers
app.include_router(core_router, prefix="/api", tags=["Core"])
app.include_router(analytics_router, prefix="/api", tags=["Analytics"])


#✅ This is fine as a separate path
@app.get("/api", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the One Brave Thing API!"}

port = int(os.environ.get("PORT", 8000))

# Local run
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
