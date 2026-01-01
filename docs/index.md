# AgentShip Documentation

**Build and deploy AI agents in minutes, not weeks.**

## 🚀 Start Here

1. **[Quick Start](getting-started/quickstart.md)** - Get running in 5 minutes ⭐
2. **[Docker Setup](docker-setup.md)** - One-command setup (recommended)
3. **[Create Your First Agent](getting-started/quickstart.md#step-3-create-your-first-agent)** - Build an agent

## 📖 Guides

### Getting Started
- [Quick Start](getting-started/quickstart.md) - Fastest way to get started
- [Installation](getting-started/installation.md) - Local development setup
- [Configuration](getting-started/configuration.md) - Environment variables

### Building Agents
- [Overview](building-agents/overview.md) - Introduction to agents
- [Agent Patterns](building-agents/patterns/) - Orchestrator, single-agent, tool-based
- [Tools](building-agents/tools.md) - Adding tools to agents
- [Agent Configuration](building-agents/agent-configuration.md) - YAML configuration

### API Reference
- [BaseAgent](api/base-agent.md) - Core agent class
- [AgentConfig](api/agent-config.md) - Configuration reference
- [Models](api/models.md) - Data models

### Deployment
- [Overview](deployment/overview.md) - Deployment guide
- [Heroku](deployment/heroku.md) - Deploy to Heroku

### Testing
- [Overview](testing/overview.md) - Testing guide
- [Writing Tests](testing/writing-tests.md) - How to write tests

## 🎯 Quick Reference

**Setup:**
```bash
make docker-setup  # One command!
```

**Create Agent:**
1. Create directory: `src/agents/all_agents/my_agent/`
2. Add `main_agent.yaml` and `main_agent.py`
3. Done! Agent is auto-discovered.

**Common Commands:**
```bash
make docker-up      # Start
make docker-down    # Stop
make dev            # Local dev server
make test           # Run tests
```

## 💡 Need Help?

- [Quick Start Guide](getting-started/quickstart.md) - Start here
- [GitHub Issues](https://github.com/harshuljain13/ship-ai-agents/issues) - Report bugs
- [Contributing](contributing.md) - Contribute to the project

---

**Everything you need to build and deploy AI agents.** 🚀
