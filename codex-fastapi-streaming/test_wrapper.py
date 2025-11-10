"""
Test script for the Codex wrapper.
"""
import asyncio
from codex_wrapper import CodexWrapper


async def test_basic_streaming():
    """Test basic streaming functionality."""
    print("Testing Codex wrapper with streaming...")
    print("-" * 50)

    codex = CodexWrapper()

    # Use a simple prompt
    prompt = "Echo 'Hello from Codex!'"

    try:
        event_count = 0
        async for event in codex.run_streamed(
            prompt=prompt,
            working_directory="/tmp",
            skip_git_repo_check=True,
            sandbox="workspace-write",
        ):
            event_count += 1
            event_type = event.get("type")
            print(f"\nEvent {event_count}: {event_type}")
            print(f"  Data: {event}")

            # Show specific items
            if event_type in ["item.completed", "item.started", "item.updated"]:
                item = event.get("item", {})
                item_type = item.get("type")
                print(f"  Item Type: {item_type}")

                if item_type == "agent_message":
                    print(f"  Message: {item.get('text')}")
                elif item_type == "reasoning":
                    print(f"  Reasoning: {item.get('text')}")
                elif item_type == "command_execution":
                    print(f"  Command: {item.get('command')}")
                    print(f"  Status: {item.get('status')}")

            elif event_type == "turn.completed":
                usage = event.get("usage", {})
                print(f"  Usage: {usage}")

        print("\n" + "-" * 50)
        print(f"Test completed! Received {event_count} events.")

    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_basic_streaming())
