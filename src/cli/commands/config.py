"""CLI configuration commands."""

import click
from rich.console import Console
from rich.table import Table

from ..services.config_manager import ConfigManager

console = Console()


@click.group()
def config():
    """Manage CLI configuration."""
    pass


@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value.

    Examples:
        agentship config set default-user user123
        agentship config set api-url http://localhost:8000
    """
    try:
        # Normalize key (replace hyphens with underscores)
        config_key = key.replace('-', '_')

        # Validate known keys
        valid_keys = ['api_url', 'default_user', 'timeout', 'log_level']
        if config_key not in valid_keys:
            console.print(f"[yellow]⚠️  Unknown config key: {key}[/yellow]")
            console.print(f"Valid keys: {', '.join(valid_keys)}")
            return

        # Set value
        config_manager = ConfigManager()
        config_manager.set(config_key, value)

        console.print(f"[green]✅ Set {key} = {value}[/green]")
        console.print(f"\nConfig saved to: {config_manager.config_path}")

    except Exception as e:
        console.print(f"[red]❌ Failed to set config: {e}[/red]")
        raise click.Abort()


@config.command()
@click.argument('key', required=False)
def get(key):
    """Get a configuration value."""
    try:
        config_manager = ConfigManager()

        if key:
            # Get specific key
            config_key = key.replace('-', '_')
            value = config_manager.get(config_key)

            if value is None:
                console.print(f"[yellow]⚠️  Config key not set: {key}[/yellow]")
            else:
                console.print(f"{key}: {value}")
        else:
            # Get all config
            all_config = config_manager.get_all()

            if not all_config:
                console.print("[yellow]No configuration values set[/yellow]")
                return

            table = Table(title="Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")

            for k, v in all_config.items():
                # Convert underscores to hyphens for display
                display_key = k.replace('_', '-')
                table.add_row(display_key, str(v))

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Failed to get config: {e}[/red]")
        raise click.Abort()


@config.command()
def show():
    """Show all configuration values."""
    try:
        config_manager = ConfigManager()
        all_config = config_manager.get_all()

        console.print("\n[bold]AgentShip Configuration:[/bold]\n")

        if not all_config:
            console.print("[yellow]No configuration values set[/yellow]")
            console.print("\nSet a value with:")
            console.print("  agentship config set <key> <value>")
            return

        # Display key config values
        console.print(f"[cyan]API URL:[/cyan] {all_config.get('api_url', 'Not set')}")
        console.print(f"[cyan]Default User:[/cyan] {all_config.get('default_user', 'Not set')}")
        console.print(f"[cyan]Timeout:[/cyan] {all_config.get('timeout', 'Not set')} seconds")
        console.print(f"[cyan]Log Level:[/cyan] {all_config.get('log_level', 'Not set')}")

        console.print(f"\n[dim]Config file: {config_manager.config_path}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Failed to show config: {e}[/red]")
        raise click.Abort()
