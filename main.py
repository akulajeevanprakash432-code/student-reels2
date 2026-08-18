import os
import json
import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from openai import OpenAI

# Initialize OpenAI client (uses environment variable, falls back to mock if missing)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

app = FastAPI(title="Reel Interest Inference Agent")

# ==============================================================================
# AI AGENT LOGIC
# ==============================================================================
SYSTEM_PROMPT = """You are an expert content-recommendation strategist for engineering students. 
Analyze the watch history and find the underlying latent interest, not just surface keywords.
Rules:
- Reject lazy keyword matches. Find the broader career/learning goal.
- Reject hype-bait. Recommend genuinely educational, skill-building content.
- If history has < 2 items, set confidence to "Low".
- Output STRICTLY valid JSON with these exact keys: 
  "current_reel", "interest_detected", "why", "recommended_tech_reel", "category", "why_this_recommendation", "difficulty", "confidence".
- Do not include markdown formatting like ```json. Just raw JSON."""

class HistoryRequest(BaseModel):
    history: str

@app.post("/api/analyze")
async def analyze(req: HistoryRequest):
    if not req.history.strip():
        return JSONResponse(status_code=400, content={"error": "History cannot be empty"})
    
    # Mock fallback if no API key is provided (so the UI still works for testing)
    if os.getenv("OPENAI_API_KEY") in [None, "", "mock-key"]:
        return {
            "current_reel": req.history.split("->")[-1].strip("[] \n"),
            "interest_detected": "Software Engineering Career Prep (Mock Mode)",
            "why": "Add your OPENAI_API_KEY to Render Environment Variables to get real AI analysis. The sequence shows a transition from basic concepts to career-focused content.",
            "recommended_tech_reel": "System Design Basics: How to Think About Scalability",
            "category": "HLD",
            "why_this_recommendation": "Bridges the gap between basic coding interviews and actual software engineering responsibilities.",
            "difficulty": "Beginner",
            "confidence": "Low"
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Watch History: {req.history}"}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"AI inference failed: {str(e)}"})

# ==============================================================================
# FRONTEND DASHBOARD (HTML + CSS + JS IN ONE STRING)
# ==============================================================================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reel Interest Inference Dashboard</title>
    <style>
        :root {
            --bg-primary: #0f172a; --bg-secondary: #1e293b; --bg-tertiary: #334155;
            --text-primary: #f8fafc; --text-secondary: #94a3b8;
            --accent: #38bdf8; --accent-hover: #0ea5e9;
            --success: #22c55e; --warning: #eab308; --danger: #ef4444;
            --border: #475569;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-primary); color: var(--text-primary);
            line-height: 1.6; min-height: 100vh; padding: 2rem 1rem;
        }
        header { text-align: center; margin-bottom: 2rem; }
        h1 { font-size: 2rem; color: var(--accent); margin-bottom: 0.5rem; }
        header p { color: var(--text-secondary); }
        
        .dashboard {
            max-width: 1200px; margin: 0 auto;
            display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
        }
        @media (max-width: 900px) { .dashboard { grid-template-columns: 1fr; } }
        
        .card {
            background-color: var(--bg-secondary); border: 1px solid var(--border);
            border-radius: 12px; padding: 1.5rem; height: 100%;
        }
        .card h2 { font-size: 1.25rem; margin-bottom: 1rem; color: var(--accent); display: flex; align-items: center; gap: 0.5rem; }
        
        .video-container {
            position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;
            background: #000; border-radius: 8px; margin-bottom: 1rem;
        }
        .video-container iframe {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;
        }
        .video-placeholder {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; align-items: center; justify-content: center;
            color: var(--text-secondary); font-size: 1.1rem;
        }

        .input-group { margin-bottom: 1rem; }
        label { display: block; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.9rem; }
        
        .url-input-row { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
        input[type="text"] {
            flex: 1; background: var(--bg-primary); border: 1px solid var(--border);
            border-radius: 6px; color: var(--text-primary); padding: 0.75rem; font-size: 0.95rem;
        }
        input[type="text"]:focus, textarea:focus { outline: none; border-color: var(--accent); }
        
        textarea {
            width: 100%; min-height: 150px; background: var(--bg-primary);
            border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);
            padding: 1rem; font-family: monospace; font-size: 0.9rem; resize: vertical;
        }
        
        .btn {
            width: 100%; padding: 0.85rem; background: var(--accent); color: var(--bg-primary);
            border: none; border-radius: 8px; font-size: 1rem; font-weight: 700;
            cursor: pointer; transition: all 0.2s;
        }
        .btn:hover { background: var(--accent-hover); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-small { width: auto; padding: 0.75rem 1.25rem; white-space: nowrap; }

        .results-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }
        .result-item {
            background: var(--bg-tertiary); padding: 1rem; border-radius: 8px;
            border-left: 4px solid var(--accent);
        }
        .result-item.full-width { grid-column: 1 / -1; }
        .result-label {
            font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;
            color: var(--text-secondary); margin-bottom: 0.25rem; font-weight: 600;
        }
        .result-value { font-size: 1rem; font-weight: 500; }
        
        .conf-high { border-left-color: var(--success); }
        .conf-med { border-left-color: var(--warning); }
        .conf-low { border-left-color: var(--danger); }
        
        .hidden { display: none; }
        .fade-in { animation: fadeIn 0.4s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <header>
        <h1>🎯 Reel Interest Inference Agent</h1>
        <p>Paste YouTube links or video titles to infer latent career signals & get tailored recommendations.</p>
 a   </header>

    <main class="dashboard">
        <!-- LEFT COLUMN: Input & Video Player -->
        <section class="card">
            <h2>📺 Watch History & Player</h2>
            
            <div class="video-container">
                <div id="videoPlaceholder" class="video-placeholder">Paste a YouTube URL below to preview</div>
                <iframe id="youtubePlayer" class="hidden" src="" allowfullscreen></iframe>
            </div>

            <div class="url-input-row">
                <input type="text" id="ytUrl" placeholder="Paste YouTube URL (e.g., https://youtu.be/...)">
                <button class="btn btn-small" onclick="addVideo()">+ Add</button>
            </div>

            <div class="input-group">
                <label>Full Watch History Sequence</label>
                <textarea id="historyInput" placeholder="[Java NullPointerException meme] -> [Day in the life of a startup SWE] -> [MacBook Air vs Dell XPS for CS students]"></textarea>
            </div>
            
            <button id="analyzeBtn" class="btn" onclick="analyzeHistory()">🔍 Analyze & Recommend</button>
        </section>

        <!-- RIGHT COLUMN: Analysis Dashboard -->
        <section class="card">
            <h2>🧠 Inference Dashboard</h2>
            <div id="resultsContainer" class="hidden fade-in">
                <div class="results-grid" id="resultsGrid"></div>
            </div>
            <div id="emptyState" style="text-align: center; color: var(--text-secondary); padding: 3rem 1rem;">
                <p>Waiting for analysis...</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">Add videos to the history and click "Analyze"</p>
            </div>
        </section>
    </main>

    <script>
        function extractVideoId(url) {
            const match = url.match(/(?:v=|\\/|youtu\\.be\\/)([0-9A-Za-z_-]{11})/);
            return match ? match[1] : null;
        }

        function addVideo() {
            const urlInput = document.getElementById('ytUrl');
            const url = urlInput.value.trim();
            const videoId = extractVideoId(url);
            
            if (videoId) {
                // Update player
                document.getElementById('videoPlaceholder').classList.add('hidden');
                const player = document.getElementById('youtubePlayer');
                player.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
                player.classList.remove('hidden');
                
                // Add to history textarea
                const historyArea = document.getElementById('historyInput');
                const title = `YouTube Video (${videoId})`;
                if (historyArea.value.trim()) {
                    historyArea.value += ` -> [${title}]`;
                } else {
                    historyArea.value = `[${title}]`;
                }
                urlInput.value = ''; // Clear input
            } else {
                alert('Invalid YouTube URL. Please try again.');
            }
        }

        async function analyzeHistory() {
            const history = document.getElementById('historyInput').value.trim();
            const btn = document.getElementById('analyzeBtn');
            const resultsContainer = document.getElementById('resultsContainer');
            const emptyState = document.getElementById('emptyState');
            const resultsGrid = document.getElementById('resultsGrid');

            if (!history) return alert('Please add at least one video or text to the history.');

            btn.disabled = true;
            btn.textContent = '🤖 Analyzing latent signals...';
            resultsContainer.classList.add('hidden');
            emptyState.classList.remove('hidden');

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ history })
                });
                const data = await response.json();

                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    renderResults(data);
                    emptyState.classList.add('hidden');
                    resultsContainer.classList.remove('hidden');
                }
            } catch (error) {
                alert("Failed to connect to backend. Check console.");
                console.error(error);
            } finally {
                btn.disabled = false;
                btn.textContent = '🔍 Analyze & Recommend';
            }
        }

        function renderResults(data) {
            const grid = document.getElementById('resultsGrid');
            grid.innerHTML = '';

            const fields = [
                { label: 'Current Reel / Video', value: data.current_reel, fullWidth: true },
                { label: 'Interest Detected', value: data.interest_detected, fullWidth: true },
                { label: 'Why (Latent Signal)', value: data.why, fullWidth: true },
                { label: 'Recommended Tech Reel', value: data.recommended_tech_reel, fullWidth: true },
                { label: 'Category', value: data.category },
                { label: 'Difficulty', value: data.difficulty },
                { label: 'Confidence', value: data.confidence, isConfidence: true },
                { label: 'Why This Recommendation', value: data.why_this_recommendation, fullWidth: true }
            ];

            fields.forEach(field => {
                const item = document.createElement('div');
                item.className = `result-item ${field.fullWidth ? 'full-width' : ''}`;
                
                if (field.isConfidence) {
                    const conf = field.value.toLowerCase();
                    if (conf.includes('high')) item.classList.add('conf-high');
                    else if (conf.includes('medium')) item.classList.add('conf-med');
                    else item.classList.add('conf-low');
                }

                item.innerHTML = `<div class="result-label">${field.label}</div><div class="result-value">${field.value}</div>`;
                grid.appendChild(item);
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return HTML_CONTENT

# Render requires the app to listen on the PORT environment variable
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
