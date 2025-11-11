"""
Test script for the Codex token wrapper.
"""
import asyncio
from codex_token_wrapper import CodexTokenWrapper


async def test_token_streaming():
    """Test token-by-token streaming functionality."""
    print("Testing Codex token wrapper...")
    print("=" * 60)

    # Test with word-level tokens
    codex = CodexTokenWrapper(token_size="word")

    prompt = "Explain what is Python in one sentence."

    try:
        token_count = 0
        event_count = 0
        current_message = ""

        print(f"\n📝 Prompt: {prompt}")
        print("\n🚀 Streaming tokens:\n")

        async for event in codex.run_token_streamed(
            prompt=prompt,
            working_directory="/tmp",
            skip_git_repo_check=True,
            sandbox="workspace-write",
        ):
            event_type = event.get("type")

            if event_type == "token":
                token_count += 1
                token = event.get("token")
                item_type = event.get("item_type")

                # Print token inline for typewriter effect
                print(token, end='', flush=True)
                current_message += token

            elif event_type == "item.completed.complete":
                # Message completed - add newline
                print("\n")

            else:
                # Other events
                event_count += 1
                if event_type in ["thread.started", "turn.started", "turn.completed"]:
                    print(f"\n[{event_type}]", end='')
                    if event_type == "turn.completed":
                        usage = event.get("usage", {})
                        print(f" - Tokens: {usage.get('output_tokens', 0)} output")
                elif event_type == "error":
                    print(f"\n❌ Error: {event.get('message')}")

        print("\n" + "=" * 60)
        print(f"✅ Test completed!")
        print(f"   Tokens received: {token_count}")
        print(f"   Events received: {event_count}")
        print(f"   Final message length: {len(current_message)} chars")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()


async def test_token_sizes():
    """Test different token sizes."""
    print("\n\n" + "=" * 60)
    print("Testing different token sizes...")
    print("=" * 60)

    test_text = "Hello world, this is a test!"

    for token_size in ["word", "char", "chunk"]:
        codex = CodexTokenWrapper(token_size=token_size)
        tokens = codex._tokenize(test_text)

        print(f"\n{token_size.upper()} mode:")
        print(f"  Input: '{test_text}'")
        print(f"  Tokens ({len(tokens)}): {tokens[:10]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("Codex Token Streaming Test Suite")
    print("=" * 60)

    # Test tokenization
    asyncio.run(test_token_sizes())

    # Test streaming (requires authentication)
    print("\n\nNote: The following test requires Codex CLI authentication")
    print("Run 'codex login' if you haven't already\n")

    try:
        asyncio.run(test_token_streaming())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
