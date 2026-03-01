"""OAuth flow handler for CLI."""

import time
import webbrowser
from typing import Dict, Optional, Any
from rich.console import Console

from .api_client import AgentShipAPI

console = Console()


class OAuthFlow:
    """Handle OAuth flow for CLI commands."""

    def __init__(
        self,
        api_client: AgentShipAPI,
        server: Dict[str, Any],
        user_id: str,
        scopes: Optional[str] = None
    ):
        """Initialize OAuth flow handler.

        Args:
            api_client: AgentShip API client
            server: Server definition from catalog
            user_id: User identifier
            scopes: Optional comma-separated OAuth scopes
        """
        self.api = api_client
        self.server = server
        self.user_id = user_id
        self.scopes = scopes

    def execute(self, timeout: int = 300) -> Dict[str, Any]:
        """Execute OAuth flow and return result.

        Args:
            timeout: Maximum time to wait for authorization (seconds)

        Returns:
            Dict with success status and details
        """
        try:
            # 1. Initiate OAuth
            console.print(f"🔗 Initiating {self.server['name']} connection...")

            init_response = self.api.initiate_oauth(
                server_id=self.server['id'],
                user_id=self.user_id,
                scopes=self.scopes
            )

            auth_url = init_response['auth_url']
            session_id = init_response['session_id']

            # 2. Open browser
            console.print(f"\n🌐 Opening browser for authentication...")
            console.print(f"   Visit: [link]{auth_url}[/link]\n")

            try:
                webbrowser.open(auth_url)
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not open browser automatically: {e}[/yellow]")
                console.print(f"[yellow]Please open the URL manually in your browser[/yellow]\n")

            # 3. Poll for completion
            console.print(f"⏳ Waiting for authorization... (timeout in {timeout//60}m)")

            start_time = time.time()

            with console.status("[bold cyan]Waiting for authorization..."):
                while time.time() - start_time < timeout:
                    status_response = self.api.check_auth_status(session_id)
                    status = status_response['status']

                    if status == 'completed':
                        # Success! Fetch tool count
                        try:
                            tools = self.api.list_tools(self.user_id, self.server['id'])
                            tool_count = len(tools)
                        except Exception:
                            tool_count = 0

                        return {
                            'success': True,
                            'server_id': self.server['id'],
                            'tool_count': tool_count,
                            'connected_at': status_response.get('connected_at')
                        }

                    elif status == 'expired':
                        return {
                            'success': False,
                            'error': 'Authorization session expired. Please try again.'
                        }

                    elif status == 'error':
                        return {
                            'success': False,
                            'error': status_response.get('error_message', 'Unknown error')
                        }

                    # Still pending, continue polling
                    time.sleep(2)  # Poll every 2 seconds

            # Timeout
            return {
                'success': False,
                'error': f'Timeout waiting for authorization ({timeout}s)'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'OAuth flow error: {str(e)}'
            }
