"""Rich console utilities for CLI output."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Dict, Any


def create_console() -> Console:
    """Create a Rich console instance.

    Returns:
        Configured Console instance
    """
    return Console()


def print_server_list(servers: List[Dict[str, Any]], title: str = "MCP Servers"):
    """Print formatted list of MCP servers.

    Args:
        servers: List of server dictionaries
        title: Table title
    """
    console = create_console()

    # Group by transport type
    oauth_servers = [s for s in servers if s.get('transport') in ('sse', 'http') and s.get('requires_auth')]
    stdio_servers = [s for s in servers if s.get('transport') == 'stdio']

    console.print(f"\n[bold]{title}:[/bold]\n")

    if oauth_servers:
        console.print("[cyan]OAuth-based (SSE/HTTP):[/cyan]")
        for server in oauth_servers:
            transport = server.get('transport', '').upper()
            console.print(f"  [bold]{server['id']:15}[/bold] - {server.get('description', '')} [{transport}]")

    if stdio_servers:
        console.print()
        console.print("[cyan]Auto-available (STDIO):[/cyan]")
        for server in stdio_servers:
            console.print(f"  [bold]{server['id']:15}[/bold] - {server.get('description', '')}")

    console.print()


def print_connection_table(connections: List[Dict[str, Any]]):
    """Print formatted table of user connections.

    Args:
        connections: List of connection dictionaries
    """
    console = create_console()

    table = Table(title="Connected MCP Servers")
    table.add_column("Server", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Connected", style="dim")
    table.add_column("Last Used", style="dim")

    for conn in connections:
        status = conn.get('status', 'unknown')
        status_icon = "✅" if status == 'active' else "⚠️" if status == 'expired' else "❌"

        table.add_row(
            conn['server_id'],
            f"{status_icon} {status}",
            conn.get('connected_at', 'N/A'),
            conn.get('last_used_at', 'Never')
        )

    console.print()
    console.print(table)
    console.print()


def print_server_info(server: Dict[str, Any]):
    """Print detailed information about an MCP server.

    Args:
        server: Server dictionary
    """
    console = create_console()

    info_text = f"""[bold]Server:[/bold] {server['name']}
[bold]ID:[/bold] {server['id']}
[bold]Transport:[/bold] {server['transport'].upper()}
[bold]Description:[/bold] {server.get('description', 'N/A')}
"""

    if server.get('url'):
        info_text += f"[bold]URL:[/bold] {server['url']}\n"

    if server.get('requires_auth'):
        info_text += f"[bold]Authentication:[/bold] OAuth ({server.get('oauth', {}).get('provider', 'Unknown')})\n"
        if server.get('oauth', {}).get('scopes'):
            scopes = ', '.join(server['oauth']['scopes'])
            info_text += f"[bold]Scopes:[/bold] {scopes}\n"
    else:
        info_text += "[bold]Authentication:[/bold] None required\n"

    panel = Panel(info_text, title=f"[bold cyan]{server['name']}[/bold cyan]", border_style="cyan")
    console.print()
    console.print(panel)
    console.print()


def print_tool_list(tools: List[Dict[str, Any]], limit: int = 10):
    """Print formatted list of MCP tools.

    Args:
        tools: List of tool dictionaries
        limit: Maximum number of tools to display
    """
    console = create_console()

    console.print(f"\n[bold]Available Tools ({len(tools)}):[/bold]")

    for i, tool in enumerate(tools[:limit], 1):
        console.print(f"  {i}. [cyan]{tool.get('name', 'Unknown')}[/cyan]")
        if tool.get('description'):
            console.print(f"     {tool['description']}")

    if len(tools) > limit:
        console.print(f"  ... and {len(tools) - limit} more")

    console.print()


def print_success(message: str):
    """Print success message.

    Args:
        message: Success message
    """
    console = create_console()
    console.print(f"[green]✅ {message}[/green]")


def print_error(message: str):
    """Print error message.

    Args:
        message: Error message
    """
    console = create_console()
    console.print(f"[red]❌ {message}[/red]")


def print_warning(message: str):
    """Print warning message.

    Args:
        message: Warning message
    """
    console = create_console()
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_info(message: str):
    """Print info message.

    Args:
        message: Info message
    """
    console = create_console()
    console.print(f"[cyan]ℹ️  {message}[/cyan]")
