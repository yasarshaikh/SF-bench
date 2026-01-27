# Recommended MCP Servers for SF-Bench

## High Value MCPs

### 1. Sequential Thinking
**Purpose**: Structured problem-solving for complex tasks.

**Setup**:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

**Use Cases**:
- Planning complex refactoring
- Debugging multi-step issues
- Designing new features

### 2. GitHub MCP
**Purpose**: Access PRs, issues, and repository data.

**Setup**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

**Use Cases**:
- Reading PR comments and reviews
- Checking issue status
- Understanding codebase history

### 3. Fetch (Web Content)
**Purpose**: Fetch and convert web content to markdown.

**Setup**:
```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

**Use Cases**:
- Reading documentation
- Fetching API specs
- Checking external resources

### 4. Git MCP
**Purpose**: Advanced git operations.

**Setup**:
```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    }
  }
}
```

**Use Cases**:
- Searching commit history
- Analyzing code changes
- Understanding file evolution

## Already Configured

Based on your current setup, you have:
- **cursor-ide-browser**: Browser automation for testing
- **user-uui**: UI component integration

## Installation

Add to Cursor Settings > Features > MCP:

1. Click "+ Add New MCP Server"
2. Enter the command from configurations above
3. Refresh tool list

## Priority Order

1. **Sequential Thinking** — Helps with complex planning (high value)
2. **GitHub** — Integrates with your workflow (if using GitHub)
3. **Fetch** — Useful for documentation lookup
4. **Git** — Advanced repository analysis

## Notes

- MCPs run as local Node.js processes
- Some require API keys (GitHub)
- Test after installation to verify connectivity
