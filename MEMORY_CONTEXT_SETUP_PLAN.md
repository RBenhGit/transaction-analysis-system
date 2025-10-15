# Claude Code Memory & Context Setup - Implementation Plan

**Project**: Transaction Analysis System
**Date**: 2025-10-03
**Purpose**: Comprehensive memory and context management setup for Claude Code

---

## 🎯 What We'll Set Up

### 1. **Memory Hierarchy** (3 Levels)
Claude Code supports hierarchical memory:
- **Enterprise Memory**: Organization-wide (if applicable)
- **Project Memory**: `CLAUDE.md` ✓ *Already exists!*
- **User Memory**: `~/.claude/CLAUDE.md` (personal preferences across all projects)

### 2. **Project Configuration** (`.claude/` directory)
- **`settings.json`**: Shared team settings (committed to git)
  - Tool permissions (allow/deny specific commands)
  - Model configuration
  - Hooks for automation

- **`settings.local.json`**: Personal settings (git-ignored)
  - Local environment variables
  - Personal tool preferences
  - Output style preferences

### 3. **Session Management with Hooks**
Configure automated behaviors:
- **SessionStart**: Auto-load project context
- **UserPromptSubmit**: Validate commands before execution
- **PreToolUse**: Safety checks for file operations
- **PostToolUse**: Track changes and log activities

### 4. **Custom Output Style** (Optional)
Create a specialized output style for:
- Financial data analysis workflows
- Python development best practices
- Banking domain-specific instructions

---

## 📋 Detailed Implementation Plan

### **Step 1: Create `.claude/` Directory Structure**
```
.claude/
├── settings.json          # Shared project settings (git tracked)
├── settings.local.json    # Personal settings (git ignored)
└── hooks/                 # Optional: Custom hook scripts
    ├── session_start.sh
    └── pre_tool_use.sh
```

### **Step 2: Configure `settings.json` (Shared)**
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Read(*)",
      "Glob(*)",
      "Grep(*)",
      "Bash(python *)",
      "Bash(pip *)",
      "Bash(pytest *)",
      "Bash(git *)",
      "Edit(*)",
      "Write(*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Write(.env)",
      "Read(*.key)"
    ]
  },
  "hooks": {
    "sessionStart": {
      "command": "echo 'Transaction Analysis Project - Session Started'"
    }
  }
}
```

### **Step 3: Configure `settings.local.json` (Personal)**
```json
{
  "env": {
    "PYTHONPATH": "./src:./adapters:./modules",
    "PROJECT_ROOT": "."
  },
  "outputStyle": "default"
}
```

### **Step 4: Create User-Level Memory** (Optional)
`~/.claude/CLAUDE.md`:
```markdown
# Personal Development Preferences

## Code Style
- Prefer type hints in all Python functions
- Use docstrings with Google style format
- Favor composition over inheritance

## Workflow
- Always run tests before committing
- Use descriptive commit messages
- Prefer small, focused pull requests
```

### **Step 5: Update `.gitignore`**
```
.claude/settings.local.json
.claude/hooks/*.local.*
*.pyc
__pycache__/
.env
.venv/
output/
```

### **Step 6: Set Up Session Hooks** (Advanced)
Example `SessionStart` hook to load context:
```json
{
  "hooks": {
    "sessionStart": {
      "command": "python -c \"print('\\n=== Transaction Analysis System ===\\nProject: Banking Data Analysis\\nMain Components: Excel Import, JSON Adapter, Visualization\\n')\"",
      "timeout": 5000
    },
    "userPromptSubmit": {
      "command": "echo '{\"allow\": true}'",
      "outputFormat": "json"
    }
  }
}
```

### **Step 7: Custom Output Style** (Optional)
Create financial analysis-specific output style via `/output-style:new`

---

## 🎁 Benefits You'll Get

1. **Persistent Context**: Project knowledge automatically loaded every session
2. **Safety Controls**: Prevent accidental destructive operations
3. **Personalization**: Separate team vs. personal preferences
4. **Automation**: Hooks run checks and load context automatically
5. **Consistency**: Team members share same tool permissions
6. **Flexibility**: Local overrides for individual workflows

---

## 🚀 Quick Start Commands

Once set up, you can use:
- `/memory` - Edit project memory (CLAUDE.md)
- `/output-style` - Switch output styles
- `#` - Quick add to memory
- `/settings` - View current configuration

---

## ⚙️ Recommended Configuration for Your Project

Given your Transaction Analysis project, I recommend:

1. **Essential**: `.claude/settings.json` with tool permissions
2. **Essential**: Updated `.gitignore`
3. **Recommended**: `settings.local.json` for PYTHONPATH
4. **Optional**: User-level `CLAUDE.md` for coding preferences
5. **Optional**: Custom output style for financial analysis

---

## 📚 Additional Resources

### Memory System Documentation
- **Hierarchy**: Enterprise → Project (CLAUDE.md) → User (~/.claude/CLAUDE.md)
- **File Imports**: Use `@path/to/import` syntax in memory files
- **Maximum Import Depth**: 5 hops
- **Quick Add**: Use `#` shortcut during conversation
- **Edit Command**: `/memory` to directly edit memories

### Settings Precedence
1. Enterprise managed policies (highest priority)
2. Command line arguments
3. Local project settings (`.claude/settings.local.json`)
4. Shared project settings (`.claude/settings.json`)
5. User settings (`~/.claude/settings.json`) (lowest priority)

### Hook Events Available
- **PreToolUse**: Runs before tool execution
- **PostToolUse**: Runs after tool completion
- **UserPromptSubmit**: Runs when a user submits a prompt
- **SessionStart**: Runs when session begins
- **SessionEnd**: Runs when session ends
- **Stop**: Runs when agent stops
- **SubagentStop**: Runs when subagent stops

### Hook Output Methods
1. **Exit Codes**:
   - `0`: Success/Allow
   - `2`: Block operation
   - Other: Error

2. **JSON Output** (advanced):
   ```json
   {
     "allow": true,
     "context": "Additional context to add",
     "feedback": "Message to display"
   }
   ```

### Security Considerations
⚠️ **WARNING**: Hooks execute shell commands automatically
- Validate all inputs
- Use absolute paths
- Quote shell variables properly
- Avoid accessing sensitive files
- Test hooks thoroughly before deployment

### Debugging
- Use `claude --debug` flag to see detailed hook execution
- Check hook output in debug logs
- Test hooks individually before combining

---

## 🔄 Implementation Checklist

- [ ] Create `.claude/` directory
- [ ] Create `settings.json` with tool permissions
- [ ] Create `settings.local.json` for personal config
- [ ] Update `.gitignore` to exclude local settings
- [ ] Test basic session start
- [ ] (Optional) Create user-level `CLAUDE.md`
- [ ] (Optional) Set up session hooks
- [ ] (Optional) Create custom output style
- [ ] Commit shared settings to git
- [ ] Document setup process for team members

---

## 📝 Notes

- Keep `CLAUDE.md` at project root (already exists - comprehensive!)
- Use `.claude/settings.local.json` for personal API keys and paths
- Never commit sensitive data or credentials
- Test hook commands manually before adding to config
- Review and update memories periodically
- Consider creating output style for domain-specific tasks

---

**Next Steps**: When ready to implement, start with Step 1 and work through systematically. Test each component before moving to the next.
