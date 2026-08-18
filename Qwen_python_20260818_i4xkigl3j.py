from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from agent import analyze_watch_history
import os

app = FastAPI(title="Reel Interest Inference Agent")

# Serve static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

class HistoryRequest(BaseModel):
    history: str

@app.post("/api/analyze")
async def analyze(req: HistoryRequest):
    if not req.history.strip():
        return JSONResponse(status_code=400, content={"error": "History cannot be empty"})
    
    result = analyze_watch_history(req.history)
    return result

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

# Render requires the app to listen on the PORT environment variable
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)