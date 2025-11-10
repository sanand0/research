"""
FastAPI application for streaming Codex responses.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
from pathlib import Path

from codex_wrapper import CodexWrapper

app = FastAPI(
    title="Codex Streaming API",
    description="FastAPI wrapper for OpenAI Codex CLI with streaming support",
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

# Initialize Codex wrapper
codex = CodexWrapper()


class CodexRequest(BaseModel):
    """Request model for Codex execution."""
    prompt: str = Field(..., description="The prompt/instructions for Codex")
    working_directory: Optional[str] = Field(None, description="Directory to run Codex in")
    skip_git_repo_check: bool = Field(True, description="Skip Git repository requirement")
    images: Optional[List[str]] = Field(None, description="List of image paths to attach")
    model: Optional[str] = Field(None, description="Model to use (e.g., gpt-5-codex)")
    sandbox: Optional[str] = Field("workspace-write", description="Sandbox mode")
    approval_policy: Optional[str] = Field("on-failure", description="Approval policy")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for structured output")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface."""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        return html_file.read_text()
    return """
    <html>
        <head><title>Codex Streaming API</title></head>
        <body>
            <h1>Codex Streaming API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """


@app.post("/api/codex/stream")
async def stream_codex(request: CodexRequest):
    """
    Stream Codex events as Server-Sent Events (SSE).

    This endpoint runs Codex with the provided prompt and streams back
    JSONL events in real-time using Server-Sent Events format.
    """
    async def event_generator():
        try:
            async for event in codex.run_streamed(
                prompt=request.prompt,
                working_directory=request.working_directory,
                skip_git_repo_check=request.skip_git_repo_check,
                images=request.images,
                model=request.model,
                sandbox=request.sandbox,
                approval_policy=request.approval_policy,
                output_schema=request.output_schema,
            ):
                # Format as Server-Sent Event
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/api/codex/run")
async def run_codex(request: CodexRequest):
    """
    Run Codex and return all events at once (non-streaming).

    This endpoint runs Codex with the provided prompt and returns
    all events and the final response after completion.
    """
    try:
        result = await codex.run(
            prompt=request.prompt,
            working_directory=request.working_directory,
            skip_git_repo_check=request.skip_git_repo_check,
            images=request.images,
            model=request.model,
            sandbox=request.sandbox,
            approval_policy=request.approval_policy,
            output_schema=request.output_schema,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "codex-streaming-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
