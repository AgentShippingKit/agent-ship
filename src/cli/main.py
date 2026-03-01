"""Main CLI entry point for AgentShip."""

import click
from .commands import mcp, config


@click.group()
@click.version_option(version="0.1.0", prog_name="agentship")
def cli():
    """AgentShip - Production-ready AI agents framework.

    Manage MCP server connections, configure agents, and run AI workflows.
    """
    pass


# Register command groups
cli.add_command(mcp.mcp)
cli.add_command(config.config)


if __name__ == '__main__':
    cli()
