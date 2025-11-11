"""
Python wrapper for OpenAI Codex CLI with token-by-token streaming support.

This wrapper extends the basic event streaming to provide token-level granularity
by tracking text deltas between events and streaming them as individual tokens.
"""
import asyncio
import json
import subprocess
import re
from typing import AsyncGenerator, Dict, Any, Optional, List
from pathlib import Path


class CodexTokenWrapper:
    """
    Wrapper for Codex CLI that provides token-by-token streaming.

    Unlike event-by-event streaming, this wrapper:
    1. Tracks text state across item.updated events
    2. Computes deltas when new text arrives
    3. Splits deltas into tokens (words/chunks)
    4. Streams tokens individually for smooth UI updates
    """

    def __init__(self, codex_binary: str = "codex", token_size: str = "word"):
        """
        Initialize the Codex token wrapper.

        Args:
            codex_binary: Path to the codex binary (defaults to 'codex' in PATH)
            token_size: Token granularity - "word", "char", or "chunk" (default: "word")
        """
        self.codex_binary = codex_binary
        self.token_size = token_size
        # Track text state for each item_id
        self._item_text_state: Dict[str, str] = {}

    def _tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens based on token_size setting.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        if not text:
            return []

        if self.token_size == "char":
            # Character-by-character
            return list(text)
        elif self.token_size == "chunk":
            # Small chunks (10 characters)
            chunk_size = 10
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        else:  # "word" (default)
            # Split by whitespace but preserve the whitespace
            # This ensures we can reconstruct the original text
            tokens = []
            current_token = ""

            for char in text:
                if char in ' \t\n':
                    if current_token:
                        tokens.append(current_token)
                        current_token = ""
                    tokens.append(char)
                else:
                    current_token += char

            if current_token:
                tokens.append(current_token)

            return tokens

    async def run_token_streamed(
        self,
        prompt: str,
        working_directory: Optional[str] = None,
        skip_git_repo_check: bool = True,
        images: Optional[List[str]] = None,
        model: Optional[str] = None,
        sandbox: Optional[str] = "workspace-write",
        approval_policy: Optional[str] = "on-failure",
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run Codex with a prompt and stream back tokens as they arrive.

        Args:
            prompt: The prompt/instructions for Codex
            working_directory: Directory to run Codex in
            skip_git_repo_check: Skip Git repository requirement
            images: List of image paths to attach
            model: Model to use (e.g., "gpt-4", "gpt-5-codex")
            sandbox: Sandbox mode (read-only, workspace-write, danger-full-access)
            approval_policy: Approval policy (untrusted, on-failure, on-request, never)
            output_schema: JSON schema for structured output

        Yields:
            Dict[str, Any]: Token events and other JSONL events from Codex

        Token events have the structure:
        {
            "type": "token",
            "item_id": "...",
            "item_type": "agent_message",
            "token": "text chunk",
            "token_index": 0
        }
        """
        # Build command
        cmd = [self.codex_binary, "exec", "--json"]

        if working_directory:
            cmd.extend(["-C", working_directory])

        if skip_git_repo_check:
            cmd.append("--skip-git-repo-check")

        if images:
            for image in images:
                cmd.extend(["-i", image])

        if model:
            cmd.extend(["-m", model])

        if sandbox:
            cmd.extend(["-s", sandbox])

        # Handle output schema if provided
        schema_file = None
        if output_schema:
            schema_file = Path("/tmp/codex_schema.json")
            schema_file.write_text(json.dumps(output_schema))
            cmd.extend(["--output-schema", str(schema_file)])

        # Add prompt as final argument
        cmd.append(prompt)

        try:
            # Start the process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
            )

            # Stream stdout line by line
            if process.stdout:
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break

                    # Parse JSONL event
                    try:
                        event = json.loads(line.decode().strip())

                        # Process events that contain text content
                        if event.get("type") in ["item.updated", "item.completed"]:
                            async for token_event in self._process_text_event(event):
                                yield token_event
                        else:
                            # Pass through non-text events as-is
                            yield event

                    except json.JSONDecodeError as e:
                        # Yield error event if we can't parse
                        yield {
                            "type": "error",
                            "message": f"Failed to parse JSONL: {e}",
                            "raw_line": line.decode().strip()
                        }

            # Wait for process to complete
            await process.wait()

            # Check for errors
            if process.returncode != 0 and process.stderr:
                stderr = await process.stderr.read()
                if stderr:
                    yield {
                        "type": "error",
                        "message": f"Codex process failed: {stderr.decode()}"
                    }

            # Clear state after completion
            self._item_text_state.clear()

        finally:
            # Clean up schema file
            if schema_file and schema_file.exists():
                schema_file.unlink()

    async def _process_text_event(self, event: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process an event that may contain text and yield token events.

        Args:
            event: The original event from Codex

        Yields:
            Token events for text deltas, plus the original event
        """
        item = event.get("item", {})
        item_id = item.get("id", "unknown")
        item_type = item.get("type", "unknown")
        text = item.get("text", "")

        # Only process events with text content
        if not text or item_type not in ["agent_message", "reasoning"]:
            # For non-text items, just pass through
            yield event
            return

        # Get previous text state
        previous_text = self._item_text_state.get(item_id, "")

        # Compute delta (new text that wasn't there before)
        if text.startswith(previous_text):
            delta = text[len(previous_text):]
        else:
            # Text was completely replaced - stream all of it
            delta = text
            previous_text = ""

        # Update state
        self._item_text_state[item_id] = text

        # If there's new text, tokenize and stream it
        if delta:
            tokens = self._tokenize(delta)
            token_index = len(self._tokenize(previous_text))

            for token in tokens:
                yield {
                    "type": "token",
                    "item_id": item_id,
                    "item_type": item_type,
                    "token": token,
                    "token_index": token_index,
                    "event_type": event.get("type")  # item.updated or item.completed
                }
                token_index += 1

        # Also yield the original event for clients that want it
        yield {
            "type": f"{event.get('type')}.complete",
            "original_event": event
        }

    async def run(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run Codex and collect all tokens and events into a single response.

        Args:
            prompt: The prompt/instructions for Codex
            **kwargs: Additional arguments passed to run_token_streamed

        Returns:
            Dict containing all events, tokens, and the final response
        """
        events = []
        tokens = []
        final_response = None

        async for event in self.run_token_streamed(prompt, **kwargs):
            if event.get("type") == "token":
                tokens.append(event)
            else:
                events.append(event)

            # Extract final agent message
            if event.get("type") == "item.completed.complete":
                original = event.get("original_event", {})
                item = original.get("item", {})
                if item.get("type") == "agent_message":
                    final_response = item.get("text")

        return {
            "events": events,
            "tokens": tokens,
            "token_count": len(tokens),
            "final_response": final_response
        }
