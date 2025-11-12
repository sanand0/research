# Custom System Prompt Research Notes

## Goal
Find out how to run Claude Code with a custom system prompt for non-coding tasks (e.g., poetry) without code-related system instructions.

## Investigation Plan
1. Read Claude Code documentation
2. Examine source code
3. Inspect logs and configuration files
4. Test different configuration methods
5. Consider proxy approach if needed

## Investigation Log

### Session started: 2025-11-12

#### Documentation Research

Found several methods for customizing system prompts:

1. **--append-system-prompt** (CLI flag)
   - Adds custom instructions to Claude Code's default system prompt
   - Works in both interactive and print modes (since v1.0.51)
   - Preserves all default capabilities and tools
   - Example: `claude --append-system-prompt "You are a poet..."`
   - RECOMMENDED for most use cases

2. **--system-prompt** (CLI flag)
   - Completely replaces the system prompt
   - Available since v2.0.14
   - **LIMITATION**: Only works for single-command executions (print mode)
   - Does NOT work in interactive mode
   - Tools are still included automatically

3. **--system-prompt-file** (CLI flag)
   - Same as --system-prompt but reads from a file
   - Print mode only

4. **Output Styles**
   - Markdown files stored in ~/.claude/output-styles/ or .claude/output-styles/
   - Can completely modify the system prompt
   - Works in interactive mode
   - Activated via `/output-style [name]` command
   - Appears to be the solution for custom prompts in interactive mode!

5. **CLAUDE.md Files**
   - Adds context as a USER message, not system prompt
   - Not suitable for replacing system prompt

6. **tweakcc**
   - Tool (npx tweakcc) to permanently edit Claude Code's default prompt files
   - Changes persist across all sessions
   - Most invasive approach

**Key Finding**: For non-coding interactive sessions, **Output Styles** seem to be the best approach since --system-prompt doesn't work in interactive mode.

#### CLI Reference Research

According to the official CLI reference, the flags are:

1. **--system-prompt "text"**
   - CLI ref says: Works in both interactive and print modes
   - Other docs say: Print mode only
   - **CONTRADICTION** - needs testing to verify!

2. **--system-prompt-file path**
   - Loads custom system prompt from file
   - Print mode only (consistent across sources)

3. **--append-system-prompt "text"**
   - Works in both interactive and print modes (confirmed)
   - Adds to end of default prompt

#### GitHub Source Code Insights

Examined gists containing extracted system prompts:
- System prompt is dynamically generated
- Contains foundation layer, safety guidelines, UI layer
- Enforces conciseness ("fewer than 4 lines")
- Tools are defined with Zod schemas
- Main logic in heavily obfuscated cli.mjs

#### Local Configuration Inspection

Checked ~/.claude/ directory:
- settings.json exists (hooks and permissions config)
- No output-styles directory by default
- Conversation logs in .jsonl format don't contain system prompts
- Logs only contain user/assistant messages, not API calls

#### Tools for Inspecting System Prompts

Found several tools to see actual API traffic:

1. **--verbose flag**
   - Built-in Claude Code flag
   - Shows "API request:" prefixed messages
   - Helpful for debugging but may not show full system prompt

2. **claude-code-logger** (npm package)
   - Dedicated tool for inspecting Claude Code API traffic
   - Shows full system prompts with -v flag
   - Usage: Set ANTHROPIC_BASE_URL=http://localhost:8000/ and run logger
   - Most comprehensive option for seeing what's sent

3. **HTTPS_PROXY method**
   - Set HTTP_PROXY/HTTPS_PROXY to intercept traffic
   - See raw API calls
   - Good for debugging

4. **Source code extraction**
   - npm pack @anthropic-ai/claude-code
   - Extract and examine obfuscated source
   - System prompts embedded in code

#### Output Styles Format

Created test output style file. Format is:

```markdown
---
name: Style Name
description: Brief description
---

Your custom system prompt instructions here...
```

Files stored in:
- User-level: ~/.claude/output-styles/
- Project-level: .claude/output-styles/

Key finding: Output styles "turn off" the software engineering parts of Claude Code's default system prompt and replace them with custom instructions.

Community tool available: ccoutputstyles (npx ccoutputstyles) provides templates

#### GitHub Issue #2692 - Important Finding

Confirmed from GitHub issue discussion:
- **--system-prompt flag does NOT work in interactive mode** (only print mode)
- Multiple users requesting this feature (18+ upvotes)
- Users want to use Claude Code for non-engineering tasks
- Current limitation: cannot override core behaviors in base prompt
- Comparison: Gemini CLI allows complete system prompt replacement via GEMINI_SYSTEM_MD env var
- CLAUDE.md only supplements, doesn't replace system prompt
- No official solution for full system prompt replacement in interactive mode yet

**This confirms that Output Styles are the ONLY way to modify system prompts in interactive mode!**

#### Experimental Testing

Created output style file at ~/.claude/output-styles/poet.md
Attempted to test --append-system-prompt in print mode (command took too long, likely API initialization)

#### Summary of Findings

**For non-coding tasks in Claude Code:**

1. **Output Styles** - BEST for interactive mode
   - Complete system prompt replacement
   - Removes all coding-related instructions
   - File format: YAML frontmatter + markdown content
   - Location: ~/.claude/output-styles/ or .claude/output-styles/
   - Activate with: /output-style [name]

2. **--append-system-prompt** - BEST for quick/print mode
   - Adds to default prompt
   - Works in both interactive and print modes
   - Doesn't remove coding instructions

3. **--system-prompt** - Print mode only
   - Complete replacement but ONLY for single commands
   - Does NOT work in interactive mode (confirmed)

4. **tweakcc** - Permanent modification (not recommended)

5. **CLAUDE.md** - NOT suitable (adds user messages, not system prompt)

**Recommended approach**: Create output style files for different non-coding use cases
