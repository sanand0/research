# Codex FastAPI Streaming Wrapper

A FastAPI-based web interface for OpenAI's Codex CLI that provides real-time streaming of Codex responses.

## Overview

This project wraps the [OpenAI Codex CLI](https://github.com/openai/codex) in a FastAPI application, enabling web-based access to Codex with real-time event streaming. The implementation includes:

- **Python wrapper** for spawning and managing `codex exec` processes
- **FastAPI server** with streaming and non-streaming endpoints
- **Interactive web interface** for easy interaction with Codex

## Architecture

### Components

1. **codex_wrapper.py**: Core Python wrapper
   - Spawns `codex exec --json` subprocess
   - Parses JSONL events from stdout
   - Provides async generator for streaming events
   - Handles configuration options (model, sandbox, working directory, etc.)

2. **app.py**: FastAPI application
   - `/api/codex/stream` - Server-Sent Events (SSE) streaming endpoint
   - `/api/codex/run` - Standard REST endpoint (returns all events at once)
   - `/` - Serves the web interface
   - `/health` - Health check endpoint

3. **index.html**: Web interface
   - Real-time streaming display
   - Event type color coding
   - Model and sandbox configuration
   - Both streaming and non-streaming modes

### How It Works

```
┌─────────────┐      HTTP/SSE      ┌──────────────┐
│   Browser   │ ◄─────────────────► │   FastAPI    │
│   (index.   │                     │    Server    │
│    html)    │                     │   (app.py)   │
└─────────────┘                     └──────────────┘
                                           │
                                           │ subprocess
                                           ▼
                                    ┌──────────────┐
                                    │    Codex     │
                                    │   Wrapper    │
                                    │(codex_wrap   │
                                    │   per.py)    │
                                    └──────────────┘
                                           │
                                           │ spawn & parse
                                           ▼
                                    ┌──────────────┐
                                    │ codex exec   │
                                    │   --json     │
                                    │  (CLI tool)  │
                                    └──────────────┘
                                           │
                                           │ JSONL events
                                           ▼
                                    OpenAI Codex API
```

## Installation

### Prerequisites

1. **Node.js** (for Codex CLI installation)
2. **Python 3.8+**
3. **OpenAI Codex CLI** access (ChatGPT Plus/Pro/Team/Enterprise)

### Setup Steps

1. **Install Codex CLI**:
   ```bash
   npm install -g @openai/codex
   ```

2. **Login to Codex** (required for actual usage):
   ```bash
   codex login
   ```
   This will open a browser window for ChatGPT authentication.

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:8000`.

### Using the Web Interface

1. Open your browser to `http://localhost:8000`
2. Enter a prompt in the textarea
3. Configure options (model, sandbox mode, working directory)
4. Click "Stream Response" for real-time streaming or "Run" for all-at-once results

### API Endpoints

#### POST /api/codex/stream

Stream Codex events using Server-Sent Events (SSE).

**Request Body**:
```json
{
  "prompt": "Create a Python function to calculate fibonacci numbers",
  "model": "gpt-5-codex",
  "sandbox": "workspace-write",
  "working_directory": "/tmp",
  "skip_git_repo_check": true
}
```

**Response**: SSE stream with events formatted as:
```
data: {"type": "thread.started", "thread_id": "..."}

data: {"type": "turn.started"}

data: {"type": "item.completed", "item": {...}}
```

#### POST /api/codex/run

Execute Codex and return all events at once.

**Request Body**: Same as `/api/codex/stream`

**Response**:
```json
{
  "events": [...],
  "final_response": "..."
}
```

### Using the Python Wrapper Directly

```python
from codex_wrapper import CodexWrapper
import asyncio

async def main():
    codex = CodexWrapper()

    # Streaming mode
    async for event in codex.run_streamed(
        prompt="Write a hello world program",
        working_directory="/tmp",
        skip_git_repo_check=True,
        sandbox="workspace-write"
    ):
        print(event)

    # Non-streaming mode
    result = await codex.run(
        prompt="Write a hello world program",
        working_directory="/tmp"
    )
    print(result['final_response'])

asyncio.run(main())
```

## Event Types

The Codex CLI emits various JSONL event types:

### Thread Events
- `thread.started` - New thread initiated
- `turn.started` - Agent processing started
- `turn.completed` - Processing finished (includes token usage)
- `turn.failed` - Processing failed with error

### Item Events
- `item.started` - New item being processed
- `item.updated` - Item state updated
- `item.completed` - Item processing finished

### Item Types
- `agent_message` - Assistant's text response
- `reasoning` - Agent's reasoning summary
- `command_execution` - Shell command execution
- `file_change` - File modifications
- `mcp_tool_call` - MCP tool invocation
- `web_search` - Web search query
- `todo_list` - Task planning
- `error` - Error information

## Configuration Options

### Model Selection
- `gpt-5-codex` - GPT-5 Codex (optimized for coding)
- `gpt-5` - GPT-5 (general purpose)
- Default model from config

### Sandbox Modes
- `read-only` - No write access
- `workspace-write` - Write access to workspace (default)
- `danger-full-access` - Full system access (dangerous!)

### Working Directory
Specify the directory where Codex should operate. By default, it requires a Git repository unless `skip_git_repo_check` is true.

## Authentication

Codex requires authentication with a ChatGPT account (Plus, Pro, Team, Enterprise, or Edu plans).

To authenticate:
```bash
codex login
```

Without authentication, requests will fail with 503 Service Unavailable errors.

## Testing

Run the test script to verify the wrapper:

```bash
python test_wrapper.py
```

This will attempt to run a simple prompt and display all events (requires authentication).

## Limitations

1. **Authentication Required**: Codex CLI requires a valid ChatGPT subscription
2. **No Approval Policy in Exec Mode**: The `-a` (approval policy) flag is not available in `codex exec` - only in interactive mode
3. **Git Repository**: By default, Codex requires running in a Git repository (can be bypassed with `--skip-git-repo-check`)
4. **Subprocess Overhead**: Each request spawns a new `codex exec` process

## Future Enhancements

Potential improvements:

1. **Session Management**: Persist threads and allow resuming previous sessions
2. **WebSocket Support**: Alternative to SSE for bidirectional communication
3. **Multi-user Support**: Handle multiple concurrent users with proper isolation
4. **Image Upload**: Support for attaching images to prompts
5. **Structured Output**: Support for JSON schema output validation
6. **Approval Workflow**: Interactive approval for command execution
7. **Thread History**: Browse and replay previous threads

## Technical Details

### Why Python Wrapper Instead of TypeScript SDK?

While OpenAI provides a TypeScript SDK, this implementation uses a Python wrapper for several reasons:

1. **FastAPI Integration**: Native Python integration with FastAPI
2. **Simplicity**: Direct subprocess management without Node.js bridge
3. **Flexibility**: Easy to customize and extend in Python
4. **Performance**: Minimal overhead, direct JSONL parsing

The wrapper mimics the TypeScript SDK's approach by spawning `codex exec --json` and parsing stdout.

### Event Streaming with SSE

Server-Sent Events (SSE) was chosen over WebSockets because:
- Simpler unidirectional communication model
- Native browser support with EventSource API
- Automatic reconnection handling
- Works with standard HTTP/HTTPS

## Project Structure

```
codex-fastapi-streaming/
├── codex_wrapper.py      # Python wrapper for Codex CLI
├── app.py                # FastAPI application
├── index.html            # Web interface
├── requirements.txt      # Python dependencies
├── test_wrapper.py       # Test script
├── notes.md              # Investigation notes
└── README.md             # This file
```

## License

This is a research project. OpenAI Codex CLI is subject to OpenAI's terms of service.

## References

- [OpenAI Codex CLI Repository](https://github.com/openai/codex)
- [Codex CLI Documentation](https://developers.openai.com/codex/cli/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
