# Codex FastAPI Token-by-Token Streaming

A FastAPI-based web interface for OpenAI's Codex CLI that provides **token-by-token streaming** for a smooth, typewriter-like user experience.

## Overview

This project extends the [codex-fastapi-streaming](../codex-fastapi-streaming) implementation by adding token-level streaming granularity. Instead of displaying complete events at once, text responses are broken down into individual tokens (words, characters, or chunks) and streamed in real-time, creating an engaging typewriter effect.

### Key Difference: Event vs Token Streaming

| Feature | Event Streaming | Token Streaming (This Project) |
|---------|----------------|--------------------------------|
| **Granularity** | Complete JSONL events | Individual words/characters |
| **UI Update** | Chunks appear all at once | Smooth typewriter effect |
| **Perceived Speed** | Standard | Feels faster and more responsive |
| **User Experience** | Functional | Engaging and modern |
| **Implementation** | Simpler | State tracking + delta computation |

## Architecture

```
┌─────────────┐      SSE         ┌──────────────────┐
│   Browser   │ ◄───────────────► │   FastAPI        │
│   (index.   │   Token Stream   │   Server         │
│    html)    │                  │   (app.py)       │
└─────────────┘                  └──────────────────┘
                                          │
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │ CodexToken       │
                                 │ Wrapper          │
                                 │ (codex_token_    │
                                 │  wrapper.py)     │
                                 └──────────────────┘
                                          │
                                          │ 1. Parse events
                                          │ 2. Track state
                                          │ 3. Compute deltas
                                          │ 4. Tokenize
                                          ▼
                                 ┌──────────────────┐
                                 │ codex exec       │
                                 │ --json           │
                                 └──────────────────┘
                                          │
                                          ▼
                                 OpenAI Codex API
```

## How It Works

### The Challenge

The Codex CLI (`codex exec --json`) outputs complete JSONL events, not individual tokens:

```json
{"type": "item.updated", "item": {"id": "123", "type": "agent_message", "text": "Hello world"}}
{"type": "item.updated", "item": {"id": "123", "type": "agent_message", "text": "Hello world, this is"}}
{"type": "item.updated", "item": {"id": "123", "type": "agent_message", "text": "Hello world, this is Codex"}}
```

Each event contains the **full cumulative text**, not just the delta.

### The Solution

Our token wrapper:

1. **Tracks State**: Maintains previous text for each item_id
2. **Computes Deltas**: Extracts only the new text portion
3. **Tokenizes**: Splits deltas into words/characters/chunks
4. **Streams**: Emits individual token events

**Example Flow**:

```
Event 1: text = "Hello world"
  → Delta = "Hello world"
  → Tokens: ["Hello", " ", "world"]

Event 2: text = "Hello world, this is"
  → Delta = ", this is"  (removed "Hello world" prefix)
  → Tokens: [",", " ", "this", " ", "is"]

Event 3: text = "Hello world, this is Codex"
  → Delta = " Codex"
  → Tokens: [" ", "Codex"]
```

### Token Event Format

```json
{
  "type": "token",
  "item_id": "item_123",
  "item_type": "agent_message",
  "token": "Hello",
  "token_index": 0,
  "event_type": "item.updated"
}
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Node.js** (for Codex CLI)
3. **OpenAI Codex CLI** access (ChatGPT Plus/Pro/Team/Enterprise)

### Setup

1. **Install Codex CLI**:
   ```bash
   npm install -g @openai/codex
   ```

2. **Login to Codex**:
   ```bash
   codex login
   ```

3. **Install Python dependencies**:
   ```bash
   cd codex-fastapi-streaming-token
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

```bash
python app.py
```

Or use the startup script:
```bash
./start_server.sh
```

The server will start on `http://localhost:8000`.

### Using the Web Interface

1. Open `http://localhost:8000` in your browser
2. Enter a prompt (e.g., "Explain how binary search works")
3. Select token granularity:
   - **Word** (recommended): Natural word-by-word streaming
   - **Character**: Ultra-smooth character-by-character
   - **Chunk**: 10-character blocks
4. Click "Stream Tokens" and watch the typewriter effect!

### API Endpoints

#### POST /api/codex/stream-tokens

Stream tokens in real-time using Server-Sent Events.

**Request**:
```json
{
  "prompt": "Explain what is Python",
  "token_size": "word",
  "model": "gpt-5-codex",
  "sandbox": "workspace-write",
  "working_directory": "/tmp",
  "skip_git_repo_check": true
}
```

**Response**: SSE stream
```
data: {"type": "thread.started", "thread_id": "..."}

data: {"type": "token", "item_id": "123", "token": "Python", "token_index": 0}

data: {"type": "token", "item_id": "123", "token": " ", "token_index": 1}

data: {"type": "token", "item_id": "123", "token": "is", "token_index": 2}
```

#### POST /api/codex/run-tokens

Execute Codex and return all tokens at once (non-streaming).

**Response**:
```json
{
  "events": [...],
  "tokens": [
    {"type": "token", "token": "Python", ...},
    {"type": "token", "token": " ", ...},
    ...
  ],
  "token_count": 42,
  "final_response": "Python is a high-level programming language..."
}
```

## Token Granularity Options

### Word Mode (Recommended)

**Characteristics**:
- Splits by whitespace
- Preserves whitespace as separate tokens
- Natural reading flow
- Typical rate: 5-20 tokens/second

**Example**: `"Hello world!"` → `["Hello", " ", "world", "!"]`

**Best for**: General use, balanced UX

### Character Mode

**Characteristics**:
- Character-by-character streaming
- Ultra-smooth typewriter effect
- High message volume
- Typical rate: 50-200 tokens/second

**Example**: `"Hi!"` → `["H", "i", "!"]`

**Best for**: Maximum visual smoothness, demos

### Chunk Mode

**Characteristics**:
- Fixed 10-character chunks
- Middle ground between word and char
- Can break words awkwardly
- Moderate message volume

**Example**: `"Hello world!"` → `["Hello worl", "d!"]`

**Best for**: Experimentation, specific UX requirements

## Features

### Token Streaming
- ✅ Real-time token-by-token delivery
- ✅ Configurable granularity (word/char/chunk)
- ✅ Delta computation for efficiency
- ✅ State tracking across events
- ✅ Smooth typewriter effect

### Web Interface
- ✅ Live streaming visualization
- ✅ Blinking cursor during typing
- ✅ Statistics dashboard (token count, rate, etc.)
- ✅ Color-coded message types
- ✅ Auto-scroll during streaming
- ✅ Smooth animations

### API
- ✅ FastAPI with async/await
- ✅ Server-Sent Events (SSE) streaming
- ✅ CORS support
- ✅ Health check endpoint
- ✅ Interactive API docs at `/docs`

## Implementation Details

### State Management

The wrapper maintains a state dictionary to track text across events:

```python
self._item_text_state: Dict[str, str] = {}
```

For each `item.updated` event:
1. Retrieve previous text: `previous = self._item_text_state.get(item_id, "")`
2. Compute delta: `delta = new_text[len(previous):]`
3. Update state: `self._item_text_state[item_id] = new_text`
4. Tokenize and stream delta

### Tokenization Algorithm

**Word Mode** preserves whitespace:

```python
tokens = []
current_token = ""

for char in text:
    if char in ' \t\n':
        if current_token:
            tokens.append(current_token)
            current_token = ""
        tokens.append(char)  # Preserve whitespace
    else:
        current_token += char

if current_token:
    tokens.append(current_token)
```

This ensures exact text reconstruction: `''.join(tokens) == original_text`

### Frontend Token Accumulation

The web interface:
1. Creates message containers for each item_id
2. Appends tokens as they arrive
3. Shows blinking cursor during streaming
4. Removes cursor when item completes

## Testing

Run the test suite:

```bash
python test_wrapper.py
```

This will:
1. Test tokenization logic for all three modes
2. Attempt a live streaming test (requires authentication)

**Sample Output**:
```
WORD mode:
  Input: 'Hello world, this is a test!'
  Tokens (11): ['Hello', ' ', 'world,', ' ', 'this', ' ', 'is', ' ', 'a', ' ']...

CHAR mode:
  Input: 'Hello world, this is a test!'
  Tokens (28): ['H', 'e', 'l', 'l', 'o', ' ', 'w', 'o', 'r', 'l']...

CHUNK mode:
  Input: 'Hello world, this is a test!'
  Tokens (3): ['Hello worl', 'd, this is', ' a test!']...
```

## Performance Considerations

### Network Overhead

- **Word mode**: Minimal overhead, ~10-20 messages/sec
- **Character mode**: Higher overhead, 50-200+ messages/sec
- **SSE**: Efficient for unidirectional streaming
- **Compression**: SSE supports gzip compression

### Memory Usage

- State dictionary: O(n) where n = number of active items
- Cleared after each request completes
- Minimal impact for typical usage

### Perceived Performance

Token streaming **feels faster** to users because:
1. Content appears immediately (first tokens arrive quickly)
2. Progressive disclosure keeps users engaged
3. Typewriter effect suggests active processing

## Comparison with Original Implementation

This project is based on [codex-fastapi-streaming](../codex-fastapi-streaming) with these enhancements:

| Aspect | Original | This Project |
|--------|----------|--------------|
| Streaming Unit | JSONL Events | Tokens (words/chars) |
| State Tracking | None | Per-item text state |
| Delta Computation | None | Automatic |
| Tokenization | None | Configurable (word/char/chunk) |
| UI Effect | Event-by-event | Typewriter |
| Perceived Latency | Standard | Improved |

**Files**:
- `codex_wrapper.py` → `codex_token_wrapper.py` (added state tracking, tokenization)
- `app.py` (updated endpoints for token streaming)
- `index.html` (enhanced UI with token accumulation)

## Technical Insights

### Why Delta Tracking?

Codex CLI sends cumulative text in `item.updated` events. Without delta tracking:
- Duplicate tokens would be streamed
- UI would show repeated text
- Performance would degrade

Delta tracking ensures we only stream **new** content.

### Why Preserve Whitespace?

Treating whitespace as separate tokens:
- Allows exact text reconstruction
- Maintains formatting integrity
- Enables word-boundary detection
- Simplifies token accumulation logic

### Why Three Token Sizes?

Different use cases benefit from different granularities:
- **Word**: Best for general use, natural reading
- **Character**: Best for demos, maximum smoothness
- **Chunk**: Experimental, balance between the two

## Limitations

1. **Requires Codex CLI**: Needs `codex` binary in PATH
2. **Authentication Required**: Must run `codex login` first
3. **State Memory**: Tracks state per request (cleared on completion)
4. **No Multi-session**: Each request is independent
5. **Subprocess Overhead**: Spawns new process per request

## Future Enhancements

- [ ] **WebSocket Support**: Alternative to SSE for bidirectional communication
- [ ] **Session Persistence**: Resume interrupted streams
- [ ] **Token Batching**: Configurable batch size for efficiency
- [ ] **Compression**: Reduce bandwidth for character mode
- [ ] **Multi-user Support**: Handle concurrent requests with isolation
- [ ] **Token Metrics**: Detailed analytics (latency, throughput, etc.)
- [ ] **Custom Tokenizers**: Support for different tokenization strategies

## Project Structure

```
codex-fastapi-streaming-token/
├── codex_token_wrapper.py   # Token streaming wrapper
├── app.py                    # FastAPI application
├── index.html                # Web interface with token UI
├── requirements.txt          # Python dependencies
├── test_wrapper.py           # Test suite
├── start_server.sh           # Startup script
├── notes.md                  # Investigation notes
└── README.md                 # This file
```

## Key Takeaways

1. **Codex CLI outputs complete events** - token streaming requires client-side processing
2. **Delta tracking is essential** - avoids duplicate content
3. **Word-level is optimal** - best balance of UX and performance
4. **State management matters** - must track text across events
5. **Token streaming improves UX** - creates engaging, responsive interfaces

## References

- [Parent Project: codex-fastapi-streaming](../codex-fastapi-streaming)
- [OpenAI Codex CLI](https://github.com/openai/codex)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Server-Sent Events (SSE)](https://html.spec.whatwg.org/multipage/server-sent-events.html)

## License

This is a research project. OpenAI Codex CLI is subject to OpenAI's terms of service.
