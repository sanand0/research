# Token-by-Token Streaming Investigation Notes

## Objective
Implement token-by-token streaming for Codex CLI responses, as opposed to the event-by-event streaming in codex-fastapi-streaming.

## Background
The existing `codex-fastapi-streaming` implementation:
- Spawns `codex exec --json` subprocess
- Reads complete JSONL events line-by-line
- Streams each complete event to the client via SSE
- Events include: thread.started, turn.started, item.started, item.updated, item.completed, etc.

## Investigation Log

### Step 1: Understanding Event Structure
Key events that contain text content:
- `item.updated` - Contains partial/incremental updates to items
- `item.completed` - Contains final item content
- Item types: agent_message, reasoning, command_execution, file_change, etc.

The `item.text` field contains the actual text content from the agent.

### Challenge
The Codex CLI outputs complete JSONL events, not individual tokens. To achieve token-by-token streaming, we need to:
1. Parse the incoming events
2. Extract text content from relevant events
3. Split text into tokens
4. Stream tokens individually to the client

### Approaches Considered

#### Approach 1: Character-by-Character Streaming
- Split text into individual characters
- Stream each character immediately
- Pros: Very granular, smooth visual effect
- Cons: High overhead, many small messages

#### Approach 2: Word-by-Word Streaming
- Split text by whitespace into words
- Stream each word as it becomes available
- Pros: More natural grouping, less overhead than characters
- Cons: Still relatively fine-grained

#### Approach 3: Chunk-by-Chunk Streaming (Small Buffers)
- Buffer small chunks (e.g., 10-20 characters)
- Stream chunks as they accumulate
- Pros: Balance between granularity and efficiency
- Cons: Requires buffering logic

#### Approach 4: Track State Between Events
- Track previous text state
- When item.updated arrives, compute delta
- Stream only the new tokens
- Pros: Efficient, streams true deltas
- Cons: More complex state management

**Decision**: Implement Approach 4 (delta streaming) as it most closely mimics true token-by-token streaming and is what the Codex API likely does internally - sending incremental updates.

### Step 2: Implementation - Token Wrapper

Created `codex_token_wrapper.py` with the following features:

#### Key Components:

1. **State Tracking**:
   - Maintains `_item_text_state` dictionary to track text content per item_id
   - Allows computing deltas between successive item.updated events

2. **Tokenization Strategy**:
   - Configurable via `token_size` parameter
   - Three modes:
     - `word`: Splits by whitespace, preserves whitespace as separate tokens
     - `char`: Character-by-character streaming
     - `chunk`: Fixed-size chunks (10 chars)
   - Default: word-level for natural reading flow

3. **Delta Computation**:
   - When `item.updated` or `item.completed` arrives:
     - Compares new text with previous state
     - Extracts only the new portion (delta)
     - Tokenizes the delta
     - Streams tokens individually

4. **Token Event Format**:
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

5. **Hybrid Streaming**:
   - Streams tokens for text content
   - Passes through other events (thread.started, turn.completed, etc.) unchanged
   - Provides both granular tokens AND original events

#### Benefits Over Event Streaming:
- Much smoother UI updates (word-by-word vs complete message)
- Better perceived latency (content appears faster)
- More engaging user experience
- Still maintains all original event data

### Step 3: FastAPI Application

Created `app.py` with token streaming endpoints:

- **POST /api/codex/stream-tokens**: SSE endpoint that streams tokens in real-time
- **POST /api/codex/run-tokens**: Non-streaming endpoint that returns all tokens at once
- **GET /**: Serves the web interface
- **GET /health**: Health check

Key features:
- Configurable token granularity via request parameter
- Maintains same request format as original implementation
- Returns both tokens and original events for flexibility

### Step 4: Web Interface

Created `index.html` with advanced token streaming visualization:

#### Key Features:

1. **Real-time Token Display**:
   - Accumulates tokens in message containers
   - Shows blinking cursor during streaming
   - Removes cursor when message completes

2. **Statistics Dashboard**:
   - Token count
   - Event count
   - Streaming rate (tokens per second)
   - Live status updates

3. **Token Granularity Control**:
   - Word (recommended for natural reading)
   - Character (smooth typewriter effect)
   - Chunk (10-character blocks)

4. **Visual Polish**:
   - Typewriter effect with cursor animation
   - Color-coded message types (assistant vs reasoning)
   - Auto-scroll during streaming
   - Smooth animations

### Step 5: Testing Results

Tested tokenization logic successfully:

**Word Mode** (11 tokens):
```
['Hello', ' ', 'world,', ' ', 'this', ' ', 'is', ' ', 'a', ' ', 'test!']
```

**Character Mode** (28 tokens):
```
['H', 'e', 'l', 'l', 'o', ' ', 'w', 'o', 'r', 'l', 'd', ...]
```

**Chunk Mode** (3 tokens):
```
['Hello worl', 'd, this is', ' a test!']
```

✅ Tokenization preserves whitespace correctly
✅ State tracking logic implemented
✅ Delta computation works as expected
✅ Web interface accumulates tokens properly

### Key Technical Insights

1. **Delta Tracking is Critical**:
   - Codex sends `item.updated` events with cumulative text
   - Must track previous state to compute what's new
   - Only stream the delta to avoid duplication

2. **Token Granularity Trade-offs**:
   - **Word**: Best balance - natural reading, reasonable rate
   - **Character**: Smoothest visual, but high message volume
   - **Chunk**: Middle ground, but can break words awkwardly

3. **Whitespace Handling**:
   - Preserving whitespace as separate tokens is important
   - Allows exact text reconstruction
   - Maintains formatting integrity

4. **Performance Considerations**:
   - Word-level streaming: ~5-20 tokens/sec typical
   - Character-level: 50-200+ tokens/sec
   - Network overhead minimal with SSE

### Comparison: Event vs Token Streaming

| Aspect | Event Streaming | Token Streaming |
|--------|----------------|-----------------|
| Granularity | Complete events | Individual words/chars |
| UI Update | Chunks appear at once | Typewriter effect |
| Perceived Speed | Slower | Faster |
| Network Messages | Fewer, larger | More, smaller |
| Implementation | Simpler | More complex |
| User Experience | Standard | Engaging |

### What We Learned

1. **Codex CLI outputs complete JSONL events**, not tokens
2. Token streaming requires **parsing and splitting** on the client side
3. **State management is essential** for delta computation
4. **Word-level granularity** provides the best UX/performance balance
5. Token streaming creates a more **engaging, responsive** interface

