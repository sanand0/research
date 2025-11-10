"""
Python wrapper for OpenAI Codex CLI that provides streaming event support.
"""
import asyncio
import json
import subprocess
from typing import AsyncGenerator, Dict, Any, Optional, List
from pathlib import Path


class CodexWrapper:
    """Wrapper for Codex CLI that spawns the exec command and streams JSONL events."""

    def __init__(self, codex_binary: str = "codex"):
        """
        Initialize the Codex wrapper.

        Args:
            codex_binary: Path to the codex binary (defaults to 'codex' in PATH)
        """
        self.codex_binary = codex_binary

    async def run_streamed(
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
        Run Codex with a prompt and stream back JSONL events.

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
            Dict[str, Any]: JSONL events from Codex
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

        # Note: approval_policy (-a) is not available in 'codex exec'
        # It's only available in the interactive CLI
        # if approval_policy:
        #     cmd.extend(["-a", approval_policy])

        # Handle output schema if provided
        schema_file = None
        if output_schema:
            # Create temporary schema file
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

        finally:
            # Clean up schema file
            if schema_file and schema_file.exists():
                schema_file.unlink()

    async def run(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run Codex and collect all events into a single response.

        Args:
            prompt: The prompt/instructions for Codex
            **kwargs: Additional arguments passed to run_streamed

        Returns:
            Dict containing all events and the final response
        """
        events = []
        final_response = None

        async for event in self.run_streamed(prompt, **kwargs):
            events.append(event)

            # Extract final agent message
            if event.get("type") == "item.completed":
                item = event.get("item", {})
                if item.get("type") == "agent_message":
                    final_response = item.get("text")

        return {
            "events": events,
            "final_response": final_response
        }
