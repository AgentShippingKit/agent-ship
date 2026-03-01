"""MCP server management commands."""

import click
from rich.console import Console

from ..services.api_client import AgentShipAPI
from ..services.oauth_flow import OAuthFlow
from ..services.config_manager import ConfigManager
from ..ui.console import (
    print_server_list,
    print_connection_table,
    print_server_info,
    print_success,
    print_error,
    print_warning,
)

console = Console()


def get_user_id(user_id: str = None) -> str:
    """Get user ID from parameter or config.

    Args:
        user_id: Optional user ID

    Returns:
        User ID to use
    """
    if user_id:
        return user_id

    config = ConfigManager()
    default_user = config.get_default_user()

    if not default_user:
        print_error("No user ID provided and no default user configured.")
        print_warning("Set a default user with: agentship config set default-user <user_id>")
        raise click.Abort()

    return default_user


@click.group()
def mcp():
    """Manage MCP server connections."""
    pass


@mcp.command()
@click.option('--connected', is_flag=True, help='Show only connected servers')
@click.option('--user-id', help='User ID (uses default if not specified)')
def list(connected, user_id):
    """List available or connected MCP servers."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())

        if connected:
            # List user's connections
            uid = get_user_id(user_id)
            connections = api.get_connections(uid)

            if not connections:
                print_warning(f"No connected servers for user: {uid}")
                console.print("\nConnect a server with:")
                console.print("  agentship mcp connect <server_name>")
                return

            print_connection_table(connections)

        else:
            # List available servers from catalog
            servers = api.get_catalog()

            if not servers:
                print_warning("No servers available in catalog")
                return

            print_server_list(servers, "Available MCP Servers")

    except Exception as e:
        print_error(f"Failed to list servers: {e}")
        raise click.Abort()


@mcp.command()
@click.argument('server_name')
@click.option('--user-id', help='User ID (uses default if not specified)')
def info(server_name, user_id):
    """Show detailed information about an MCP server."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())

        server = api.get_server_info(server_name)
        print_server_info(server)

    except Exception as e:
        print_error(f"Failed to get server info: {e}")
        raise click.Abort()


@mcp.command()
@click.argument('server_name')
@click.option('--user-id', help='User ID (uses default if not specified)')
@click.option('--scopes', help='OAuth scopes (comma-separated)')
def connect(server_name, user_id, scopes):
    """Connect to an MCP server via OAuth."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url(), timeout=config.get_timeout())
        uid = get_user_id(user_id)

        # Get server info
        console.print(f"🔗 Connecting to [cyan]{server_name}[/cyan]...")
        server = api.get_server_info(server_name)

        # Check if auth required
        if not server.get('requires_auth'):
            print_warning(
                f"{server_name} is a STDIO server and doesn't require OAuth connection.\n"
                f"Use 'agentship mcp configure {server_name}' to set it up."
            )
            return

        # Start OAuth flow
        oauth = OAuthFlow(api, server, uid, scopes)

        try:
            result = oauth.execute(timeout=config.get_timeout())

            if result['success']:
                print_success(f"Successfully connected to {server_name}!")

                if result.get('tool_count', 0) > 0:
                    console.print(f"\nAvailable tools: {result['tool_count']} tools discovered")

                console.print(f"\nTest your connection:")
                console.print(f"  agentship mcp test {server_name}")

            else:
                print_error(f"Connection failed: {result.get('error', 'Unknown error')}")
                raise click.Abort()

        except KeyboardInterrupt:
            print_warning("\nConnection cancelled by user")
            raise click.Abort()

    except click.Abort:
        raise
    except Exception as e:
        print_error(f"Failed to connect: {e}")
        raise click.Abort()


@mcp.command()
@click.argument('server_name')
@click.option('--user-id', help='User ID (uses default if not specified)')
def disconnect(server_name, user_id):
    """Disconnect from an MCP server."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())
        uid = get_user_id(user_id)

        # Confirm
        if not click.confirm(
            f"⚠️  This will remove your {server_name} connection and delete stored tokens. Continue?"
        ):
            print_warning("Cancelled")
            return

        api.disconnect(uid, server_name)
        print_success(f"Disconnected from {server_name}")

    except Exception as e:
        print_error(f"Failed to disconnect: {e}")
        raise click.Abort()


@mcp.command()
@click.argument('server_name')
@click.option('--user-id', help='User ID (uses default if not specified)')
def reconnect(server_name, user_id):
    """Reconnect to an MCP server (refresh token)."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())
        uid = get_user_id(user_id)

        # First disconnect
        console.print(f"🔄 Refreshing connection to [cyan]{server_name}[/cyan]...")
        api.disconnect(uid, server_name)

        # Then reconnect (reuse connect logic)
        server = api.get_server_info(server_name)
        oauth = OAuthFlow(api, server, uid, scopes=None)

        result = oauth.execute(timeout=config.get_timeout())

        if result['success']:
            print_success(f"Successfully reconnected to {server_name}!")
        else:
            print_error(f"Reconnection failed: {result.get('error', 'Unknown error')}")
            raise click.Abort()

    except Exception as e:
        print_error(f"Failed to reconnect: {e}")
        raise click.Abort()


@mcp.command()
@click.argument('server_name')
@click.option('--user-id', help='User ID (uses default if not specified)')
@click.option('--tool', help='Test specific tool')
def test(server_name, user_id, tool):
    """Test MCP server connection and list available tools."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())
        uid = get_user_id(user_id)

        console.print(f"Testing [cyan]{server_name}[/cyan] MCP Server...\n")

        result = api.test_connection(uid, server_name)

        if result['status'] == 'success':
            print_success("Connection successful")
            print_success("Authentication valid")

            if result.get('token_expires_at'):
                console.print(f"[green]✅ Token expires: {result['token_expires_at']}[/green]")

            # List tools
            from ..ui.console import print_tool_list
            if result.get('tools'):
                print_tool_list(result['tools'])

        else:
            print_error(f"Connection failed: {result.get('error', 'Unknown error')}")
            raise click.Abort()

    except Exception as e:
        print_error(f"Failed to test connection: {e}")
        raise click.Abort()


@mcp.command()
@click.argument('server_name')
@click.option('--user-id', help='User ID (uses default if not specified)')
@click.option('--connection-string', help='PostgreSQL connection string (for postgres server)')
def configure(server_name, user_id, **kwargs):
    """Configure STDIO MCP server (e.g., connection strings)."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())
        uid = get_user_id(user_id)

        # Get server info
        server = api.get_server_info(server_name)

        if server.get('requires_auth'):
            print_warning(
                f"{server_name} is an OAuth-based server.\n"
                f"Use 'agentship mcp connect {server_name}' instead."
            )
            return

        console.print(f"Configuring [cyan]{server_name}[/cyan] STDIO server...")

        # TODO: Implement interactive configuration based on config_template
        # For now, just show a message
        print_warning("Interactive configuration not yet implemented")
        console.print(f"\nTo configure {server_name}, add it to your .mcp.settings.json file")

    except Exception as e:
        print_error(f"Failed to configure: {e}")
        raise click.Abort()


@mcp.group()
def catalog():
    """Manage MCP server catalog."""
    pass


@catalog.command(name='list')
def catalog_list():
    """List servers in catalog."""
    try:
        config = ConfigManager()
        api = AgentShipAPI(base_url=config.get_api_url())

        servers = api.get_catalog()
        print_server_list(servers, "MCP Server Catalog")

    except Exception as e:
        print_error(f"Failed to list catalog: {e}")
        raise click.Abort()


@catalog.command()
@click.option('--file', 'file_path', required=True, help='Path to server definition file')
def add(file_path):
    """Add custom MCP server to catalog."""
    print_warning("Adding custom servers not yet implemented")
    console.print(f"Will add server from: {file_path}")


@catalog.command()
@click.argument('server_name')
def remove(server_name):
    """Remove MCP server from catalog."""
    print_warning("Removing servers not yet implemented")
    console.print(f"Will remove: {server_name}")
