# Running Claude Code with Custom System Prompts

## Executive Summary

**Quick Answer**: To use Claude Code for non-coding tasks (e.g., poetry) without coding-related instructions, use **Output Styles** in interactive mode or **--append-system-prompt** in print mode.

**Recommended Easiest Option**:
1. For interactive sessions: Create an output style file
2. For one-off commands: Use `--append-system-prompt` flag

## The Problem

Claude Code's default system prompt is heavily optimized for software engineering tasks, with instructions to be concise, use tools for coding, and follow programming best practices. Users wanting to use Claude Code for other tasks (creative writing, poetry, analysis, etc.) find these instructions limiting and potentially confusing to the model.

## Available Methods

### Method 1: Output Styles (Interactive Mode) ⭐ RECOMMENDED for Interactive Sessions

**What it does**: Completely replaces Claude Code's system prompt with your custom instructions while preserving tool access.

**How to use**:

1. Create a markdown file with YAML frontmatter:
   ```markdown
   ---
   name: Poet
   description: A poetry-focused assistant
   ---

   You are Claude, a creative and thoughtful poetry assistant. You help users write, analyze, and appreciate poetry.

   Your capabilities:
   - Write poetry in various styles and forms
   - Analyze poetic devices and techniques
   - Provide feedback on poems
   - Discuss poetic traditions and movements

   Be creative, expressive, and emotionally attuned. Feel free to elaborate fully.
   ```

2. Save it in one of these locations:
   - User-level: `~/.claude/output-styles/poet.md`
   - Project-level: `.claude/output-styles/poet.md`

3. Activate in interactive mode:
   ```bash
   claude  # Start interactive session
   /output-style poet  # Activate your custom style
   ```

   Or use the built-in helper:
   ```bash
   claude
   /output-style:new I want a poetry assistant that...
   ```

**Key Characteristics**:
- ✅ Works in interactive mode
- ✅ Completely replaces system prompt
- ✅ Preserves tool access (file operations, bash, etc.)
- ✅ Persistent across sessions
- ✅ Can be shared and version-controlled
- ❌ Requires file creation

**What messages are sent**:
- The entire default Claude Code system prompt is replaced with your custom markdown content
- Tool definitions are still included automatically
- Environment context is preserved

### Method 2: --append-system-prompt Flag (Print & Interactive)

**What it does**: Adds your custom instructions to the end of Claude Code's default system prompt.

**How to use**:

```bash
# Print mode (single command)
claude -p --append-system-prompt "You are a poet. Be creative and expressive." "Write a haiku about code"

# Interactive mode
claude --append-system-prompt "You are a poet specializing in haiku and sonnets."
```

**Key Characteristics**:
- ✅ Works in both print and interactive modes
- ✅ Very simple to use
- ✅ No file creation needed
- ❌ Doesn't remove default coding instructions (only appends)
- ❌ Default prompt still encourages conciseness and code-focused behavior

**What messages are sent**:
- Full default Claude Code system prompt
- Plus your additional instructions appended at the end
- The model sees both sets of instructions (potential conflicts)

### Method 3: --system-prompt Flag (Print Mode Only)

**What it does**: Replaces the system prompt entirely for single-command execution.

**How to use**:

```bash
claude -p --system-prompt "You are a creative poetry assistant..." "Write a sonnet"
```

Or with a file:
```bash
claude -p --system-prompt-file ./my-prompt.txt "Write a haiku"
```

**Key Characteristics**:
- ✅ Complete control over system prompt
- ✅ Clean replacement (no default instructions)
- ❌ **Print mode only** - does NOT work in interactive mode
- ❌ Single-command execution only
- ❌ No session persistence

**What messages are sent**:
- Only your custom system prompt
- Tool definitions still automatically included
- No default Claude Code instructions

### Method 4: tweakcc (Permanent Modification)

**What it does**: Directly edits Claude Code's default prompt files permanently.

**How to use**:

```bash
npx tweakcc
# Follow prompts to edit default system prompt
```

**Key Characteristics**:
- ✅ Changes persist across all sessions
- ✅ No need to activate per-session
- ❌ Most invasive approach
- ❌ Affects all Claude Code usage
- ❌ Requires manual reversion to restore defaults
- ⚠️ Not recommended for temporary changes

### Method 5: CLAUDE.md Files (NOT for System Prompt Replacement)

**What it does**: Adds project context as a user message, NOT as a system prompt modification.

**Limitation**: This does NOT replace or modify the system prompt. It's useful for project context but won't remove coding instructions.

**Not suitable for this use case.**

## Detailed Comparison

| Method | Interactive Mode | Print Mode | Complete Replacement | Ease of Use | Persistence |
|--------|-----------------|------------|---------------------|-------------|-------------|
| Output Styles | ✅ | ✅ | ✅ | Medium | Per-session |
| --append-system-prompt | ✅ | ✅ | ❌ (appends only) | Very Easy | Per-invocation |
| --system-prompt | ❌ | ✅ | ✅ | Easy | Single command |
| tweakcc | ✅ | ✅ | ✅ | Medium | Permanent |
| CLAUDE.md | N/A | N/A | ❌ | Easy | Project-level |

## What Messages Are Actually Sent

### Default Claude Code System Prompt Structure

When using Claude Code normally, the system prompt contains:

1. **Foundation layer**: Defines Claude Code as an interactive CLI for software engineering
2. **Safety guidelines**: Instructions to refuse malicious code
3. **Tool instructions**: Detailed descriptions of all available tools (Bash, Read, Write, Edit, etc.)
4. **Behavioral guidelines**:
   - Be concise (fewer than 4 lines unless detail requested)
   - Follow existing code conventions
   - Use appropriate tools
   - Security best practices
5. **Environment context**: Working directory, git status, platform info, date

### With Output Styles

When an output style is active:
- System prompt = Your custom markdown content + tool definitions + environment context
- Default software engineering instructions are REMOVED
- Tools are still available and described

### With --append-system-prompt

- System prompt = Full default prompt + "\n\n" + your custom text
- All default instructions remain
- Your instructions added at the end

### With --system-prompt

- System prompt = Only your custom text + tool definitions
- No default Claude Code instructions
- Clean slate (but print mode only)

## Inspecting Actual Messages Sent to API

If you want to see exactly what's being sent to the Claude API:

### Method 1: --verbose Flag

```bash
claude --verbose
# Shows API requests and responses with "API request:" prefix
```

### Method 2: claude-code-logger (Third-Party Tool)

Most comprehensive option for seeing full prompts:

```bash
# Install and run the logger
npm install -g claude-code-logger
claude-code-logger start --verbose

# In another terminal, set the base URL
export ANTHROPIC_BASE_URL=http://localhost:8000/
claude
```

This intercepts all API traffic and shows complete system prompts.

### Method 3: HTTPS Proxy

Set up a proxy to intercept HTTPS traffic:

```bash
export HTTPS_PROXY=http://localhost:8888
export HTTP_PROXY=http://localhost:8888
claude
```

Use tools like mitmproxy or Charles Proxy to inspect traffic.

### Method 4: Extract Source Code

```bash
npm pack @anthropic-ai/claude-code
tar -xzf anthropic-ai-claude-code-*.tgz
cd package
# Examine obfuscated source code for system prompt generation
```

## Recommendations

### For Interactive Poetry/Creative Writing Sessions

**Use Output Styles**:

```bash
# Create the style file
mkdir -p ~/.claude/output-styles
cat > ~/.claude/output-styles/poet.md << 'EOF'
---
name: Poet
description: Creative poetry assistant
---

You are Claude, a creative and thoughtful poetry assistant.

Help users:
- Write poetry in various styles and forms
- Analyze poetic devices and techniques
- Provide detailed feedback on poems
- Explore poetic traditions

Be expressive and elaborate. No need for conciseness.
EOF

# Use it
claude
/output-style poet
```

### For One-Off Non-Coding Queries

**Use --append-system-prompt**:

```bash
claude -p --append-system-prompt "Focus on creative writing, not code." "Help me write a sonnet about autumn"
```

### For Programmatic/SDK Usage

If you're using the Claude Agent SDK in code:

```typescript
// TypeScript
import { Agent } from '@anthropic-ai/sdk';

const agent = new Agent({
  systemPrompt: "You are a poetry expert assistant...",
  // Your custom prompt replaces everything
});
```

```python
# Python
from claude_agent_sdk import Agent

agent = Agent(
    system_prompt="You are a poetry expert assistant..."
)
```

## Known Limitations

### GitHub Issue #2692

There's an open GitHub issue (18+ upvotes) requesting better system prompt replacement in interactive mode. Key findings:

- Users want to use Claude Code for non-engineering tasks
- Current methods feel like workarounds
- Request for an environment variable like `CLAUDE_SYSTEM_MD` (similar to Gemini CLI's `GEMINI_SYSTEM_MD`)
- No official response yet on future enhancements

### Current State (as of 2025-11)

- **No way to use --system-prompt in interactive mode** (confirmed limitation)
- Output styles are the only official way to replace prompts in interactive sessions
- Even with output styles, some base behaviors may persist

## Example: Complete Poetry Assistant Setup

```bash
# 1. Create the output style
mkdir -p ~/.claude/output-styles
cat > ~/.claude/output-styles/poetry-tutor.md << 'EOF'
---
name: Poetry Tutor
description: Patient teacher of poetry and creative writing
---

You are Claude, an experienced poetry tutor and creative writing mentor.

Your role:
- Teach poetic forms (sonnets, haikus, villanelles, free verse, etc.)
- Explain literary devices and their effects
- Provide constructive feedback on student poems
- Share examples from classic and contemporary poets
- Encourage creative experimentation
- Discuss the emotional and intellectual aspects of poetry

Teaching style:
- Patient and encouraging
- Provide detailed explanations
- Use examples generously
- Ask thought-provoking questions
- Celebrate creative attempts

Remember: You have access to file operations if students want to save their work, but your primary focus is teaching and creative guidance, not software development.
EOF

# 2. Start Claude Code
claude

# 3. In the interactive session
/output-style poetry-tutor

# 4. Now use it!
# "Help me write a villanelle about time"
# "Analyze the use of metaphor in this poem: ..."
# "What's the difference between a Petrarchan and Shakespearean sonnet?"
```

## Conclusion

**For your use case (poetry without coding instructions):**

1. **Best option**: Create an output style file
   - Complete removal of coding focus
   - Works in interactive mode
   - Clean, professional approach

2. **Quick option**: Use `--append-system-prompt`
   - Immediate, no setup
   - Adds poetry focus (but coding instructions remain)
   - Good for quick tests

3. **Avoid**: CLAUDE.md, tweakcc
   - CLAUDE.md doesn't modify system prompt
   - tweakcc too permanent/invasive

The output style approach gives you exactly what you want: Claude's capabilities without the software engineering baggage.

## References

- [Official Output Styles Documentation](https://docs.claude.com/en/docs/claude-code/output-styles)
- [Modifying System Prompts (Agent SDK)](https://docs.claude.com/en/docs/agent-sdk/modifying-system-prompts)
- [GitHub Issue #2692](https://github.com/anthropics/claude-code/issues/2692)
- [claude-code-logger](https://github.com/dreampulse/claude-code-logger)
- [ccoutputstyles Templates](https://github.com/viveknair/ccoutputstyles)
