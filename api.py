"""
FastAPI backend for the Claims Processing Agent.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import tempfile
import os
import json
from pathlib import Path

from src.agent import ClaimsProcessingAgent

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Claims Processing Agent",
    description="AI-powered autonomous FNOL document processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (web interface)
web_dir = Path(__file__).parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# Configuration file for storing settings
CONFIG_FILE = Path(__file__).parent / ".config.json"

# Initialize the agent
agent = None


class APIKeyConfig(BaseModel):
    """Model for API key configuration."""
    api_key: str



def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")


def get_api_key() -> Optional[str]:
    """Get API key from config file or environment."""
    # First check config file
    config = load_config()
    if 'gemini_api_key' in config and config['gemini_api_key']:
        return config['gemini_api_key']
    
    # Fall back to environment variable
    return os.getenv('GEMINI_API_KEY')


def get_agent(force_reload: bool = False) -> ClaimsProcessingAgent:
    """Get or create the claims processing agent."""
    global agent
    
    # Reload agent if requested or not initialized
    if force_reload or agent is None:
        api_key = get_api_key()
        try:
            agent = ClaimsProcessingAgent(api_key=api_key)
        except Exception as e:
            # If agent creation fails, create without API key (will use fallback)
            agent = ClaimsProcessingAgent(api_key=None)
    
    return agent


class ProcessingResult(BaseModel):
    """Response model for claim processing."""
    extractedFields: Dict[str, Any]
    missingFields: list
    recommendedRoute: str
    reasoning: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the web interface."""
    web_file = Path(__file__).parent / "web" / "index.html"
    if web_file.exists():
        return web_file.read_text()
    return """
    <html>
        <body>
            <h1>Insurance Claims Processing Agent API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """


@app.post("/process", response_model=ProcessingResult)
async def process_claim(file: UploadFile = File(...)):
    """
    Process an uploaded FNOL document.
    
    Args:
        file: FNOL document (PDF or TXT)
        
    Returns:
        Processing result with extracted fields, missing fields, route, and reasoning
    """
    # Validate file format
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.txt']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Please upload PDF or TXT files."
        )
    
    # Save uploaded file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process the claim
        claims_agent = get_agent()
        result = claims_agent.process_claim(tmp_path)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing claim: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if agent can be initialized
        get_agent()
        return {"status": "healthy", "message": "Agent is ready"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )




@app.get("/routing-rules")
async def get_routing_rules():
    """Get the routing rules summary."""
    claims_agent = get_agent()
    return {
        "rules": claims_agent.router.get_routing_summary(),
        "fast_track_threshold": claims_agent.router.FAST_TRACK_THRESHOLD
    }


@app.get("/config")
async def get_config():
    """Get current configuration status."""
    api_key = get_api_key()
    config = load_config()
    
    return {
        "has_api_key": bool(api_key),
        "api_key_source": "config_file" if config.get('gemini_api_key') else ("env" if api_key else "none"),
        "using_gemini": bool(api_key),
        "using_fallback": not bool(api_key)
    }


@app.post("/config/api-key")
async def set_api_key(config: APIKeyConfig):
    """
    Set or update the Gemini API key.
    
    Args:
        config: API key configuration
        
    Returns:
        Success message and new configuration status
    """
    try:
        # Get current config
        current_config = load_config()
        
        # Update API key
        current_config['gemini_api_key'] = config.api_key.strip()
        
        # Save configuration
        save_config(current_config)
        
        # Reload agent with new API key
        get_agent(force_reload=True)
        
        return {
            "success": True,
            "message": "API key configured successfully. Agent reloaded with Gemini AI.",
            "using_gemini": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure API key: {str(e)}"
        )


@app.delete("/config/api-key")
async def remove_api_key():
    """
    Remove the configured API key and use fallback extraction.
    
    Returns:
        Success message
    """
    try:
        # Get current config
        current_config = load_config()
        
        # Remove API key
        if 'gemini_api_key' in current_config:
            del current_config['gemini_api_key']
        
        # Save configuration
        save_config(current_config)
        
        # Reload agent without API key
        get_agent(force_reload=True)
        
        return {
            "success": True,
            "message": "API key removed. Using pattern-based extraction.",
            "using_gemini": False
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove API key: {str(e)}"
        )



if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Insurance Claims Processing Agent API                   ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Server starting...
    
    📍 API URL: http://localhost:{port}
    📚 API Docs: http://localhost:{port}/docs
    🌐 Web Interface: http://localhost:{port}
    
    Press Ctrl+C to stop the server.
    """)
    
    uvicorn.run(app, host=host, port=port)
