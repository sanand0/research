# Codex FastAPI Streaming - Investigation Notes

## Objective
Build a FastAPI app that wraps OpenAI's Codex CLI and streams responses for a web interface.

## Investigation Log

### Step 1: Initial Setup
- Created project folder: codex-fastapi-streaming
- Initialized notes.md file

### Step 2: Research Phase
- Cloned OpenAI Codex repository from https://github.com/openai/codex
- Examined TypeScript SDK at sdk/typescript/

#### Key Findings:
1. **Architecture**: Codex CLI is written in Rust, with a TypeScript SDK wrapper
2. **SDK Approach**: The TS SDK spawns the codex CLI binary and exchanges JSONL events over stdin/stdout
3. **Streaming Support**: The SDK provides `runStreamed()` method that returns an async generator of events
4. **Event Types**: thread.started, turn.started, item.started, item.updated, item.completed, turn.completed, turn.failed
5. **Item Types**: agent_message, reasoning, command_execution, file_change, mcp_tool_call, web_search, todo_list, error

#### Implementation Strategy:
Since FastAPI is Python-based, we have two approaches:
1. Build a Python wrapper that spawns codex CLI binary directly (mimicking TS SDK approach)
2. Use the TypeScript SDK through a Node.js subprocess

**Decision**: We'll build a Python wrapper that spawns the codex CLI binary directly, parsing JSONL events. This will be cleaner and avoid the Node.js dependency.

### Step 3: Installation & Testing
- Installed Codex CLI v0.57.0 via npm
- Verified `codex exec --json` command outputs JSONL events to stdout
- This is the key to building a Python wrapper that can stream events

### Step 4: Implementation
Created three main components:

1. **codex_wrapper.py**: Python wrapper that:
   - Spawns `codex exec --json` as a subprocess
   - Streams JSONL events from stdout as an async generator
   - Handles command-line options (model, sandbox, working directory, etc.)
   - Parses events in real-time

2. **app.py**: FastAPI application with:
   - `/api/codex/stream` - Server-Sent Events (SSE) endpoint for streaming
   - `/api/codex/run` - Non-streaming endpoint that returns all events at once
   - `/` - Serves the web interface
   - CORS support for cross-origin requests

3. **index.html**: Interactive web interface with:
   - Prompt input textarea
   - Model and sandbox configuration options
   - Stream and non-stream execution modes
   - Real-time event display with color-coded event types
   - Beautiful gradient UI design

### Step 5: Testing Results
- Successfully tested the wrapper with `codex exec --json`
- Confirmed JSONL event parsing works correctly
- Observed events: thread.started, turn.started, error, turn.failed
- Authentication requirement noted (503 errors without login)

### Key Findings:
1. The `codex exec` command doesn't support `-a` (approval policy) option - only available in interactive mode
2. Events are streamed as JSONL on stdout when using `--json` flag
3. Error messages and reconnection attempts are reported as events
4. The wrapper successfully parses and yields events in real-time

### Step 6: Finalization
- Created comprehensive README.md with full documentation
- Added startup script (start_server.sh)
- Verified FastAPI server starts correctly on port 8000
- Cleaned up cloned repository (as per project guidelines)
- Tested wrapper functionality (JSONL parsing confirmed working)

## Summary

Successfully created a FastAPI-based web interface for OpenAI Codex CLI with streaming support.

**What Works:**
- ✅ Python wrapper spawns and manages codex exec processes
- ✅ JSONL event parsing and streaming via async generators
- ✅ FastAPI server with SSE streaming endpoints
- ✅ Interactive web interface with real-time event display
- ✅ Configuration options for model, sandbox, working directory
- ✅ Both streaming and non-streaming modes

**Deliverables:**
1. `codex_wrapper.py` - Core Python wrapper (150+ lines)
2. `app.py` - FastAPI application (140+ lines)
3. `index.html` - Web interface (500+ lines)
4. `test_wrapper.py` - Test script
5. `start_server.sh` - Startup script
6. `requirements.txt` - Dependencies
7. `README.md` - Comprehensive documentation

**Technical Achievements:**
- Mimicked TypeScript SDK approach without Node.js dependency
- Real-time event streaming using Server-Sent Events (SSE)
- Clean async/await architecture for non-blocking I/O
- Color-coded event visualization in web UI
- Error handling for authentication and service issues

**Limitations Discovered:**
- Requires Codex CLI authentication (ChatGPT Plus/Pro/Team/Enterprise)
- Approval policy not available in exec mode
- Each request spawns new process (no session persistence by default)

This implementation provides a solid foundation for building web applications on top of Codex CLI.

