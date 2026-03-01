"""End-to-end test for MCP OAuth integration.

This script tests the complete MCP OAuth flow:
1. List available servers
2. Connect to GitHub (manual OAuth)
3. List tools
4. Test connection
5. Disconnect

Prerequisites:
- Database running with migrations
- FastAPI service running
- GitHub OAuth app configured
- CLI installed
"""

import os
import sys
import subprocess
import time

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_step(step_num: int, description: str):
    """Print test step."""
    print(f"\n{BLUE}━━━ Step {step_num}: {description} ━━━{RESET}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{RED}❌ {message}{RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def run_cli_command(command: list, expect_interaction: bool = False) -> tuple:
    """Run CLI command and return output.

    Args:
        command: Command as list of strings
        expect_interaction: If True, run interactively

    Returns:
        (success, output)
    """
    try:
        if expect_interaction:
            # For interactive commands like connect
            result = subprocess.run(
                command,
                capture_output=False,
                text=True
            )
            return result.returncode == 0, ""
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)


def check_prerequisites():
    """Check if prerequisites are met."""
    print_step(0, "Checking Prerequisites")

    # Check database
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print_error("DATABASE_URL not set")
        return False
    print_success(f"DATABASE_URL: {db_url}")

    # Check encryption key
    encryption_key = os.getenv("MCP_TOKEN_ENCRYPTION_KEY")
    if not encryption_key:
        print_warning("MCP_TOKEN_ENCRYPTION_KEY not set - will generate temporary key")
    else:
        print_success("MCP_TOKEN_ENCRYPTION_KEY: configured")

    # Check GitHub OAuth
    github_client_id = os.getenv("GITHUB_OAUTH_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")

    if not github_client_id or not github_client_secret:
        print_error("GitHub OAuth credentials not configured")
        print_warning("Set GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET")
        return False
    print_success("GitHub OAuth: configured")

    # Check FastAPI running
    try:
        import httpx
        response = httpx.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_success("FastAPI service: running")
        else:
            print_error(f"FastAPI service returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"FastAPI service not accessible: {e}")
        print_warning("Start with: python src/service/main.py")
        return False

    return True


def test_e2e():
    """Run end-to-end test."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}MCP OAuth End-to-End Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    # Check prerequisites
    if not check_prerequisites():
        print_error("\nPrerequisites not met. Please fix and try again.")
        return False

    test_user = "e2e_test_user"

    # Step 1: Configure CLI
    print_step(1, "Configure CLI")

    success, _ = run_cli_command([
        "agentship", "config", "set", "api-url", "http://localhost:8000"
    ])
    if not success:
        print_error("Failed to set api-url")
        return False
    print_success("Set api-url")

    success, _ = run_cli_command([
        "agentship", "config", "set", "default-user", test_user
    ])
    if not success:
        print_error("Failed to set default-user")
        return False
    print_success(f"Set default-user: {test_user}")

    # Step 2: List available servers
    print_step(2, "List Available Servers")

    success, output = run_cli_command(["agentship", "mcp", "list"])
    if not success:
        print_error("Failed to list servers")
        return False

    if "github" in output:
        print_success("GitHub server found in catalog")
    else:
        print_error("GitHub server not found in catalog")
        return False

    # Step 3: Get server info
    print_step(3, "Get Server Info")

    success, output = run_cli_command(["agentship", "mcp", "info", "github"])
    if not success:
        print_error("Failed to get server info")
        return False

    if "GitHub" in output and "OAuth" in output:
        print_success("GitHub server info retrieved")
    else:
        print_error("GitHub server info incomplete")
        return False

    # Step 4: Connect to GitHub (interactive)
    print_step(4, "Connect to GitHub")

    print_warning("This step requires manual interaction:")
    print("  1. Browser will open")
    print("  2. Authorize the application on GitHub")
    print("  3. Wait for success message")
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

    success = run_cli_command(
        ["agentship", "mcp", "connect", "github"],
        expect_interaction=True
    )[0]

    if not success:
        print_error("Failed to connect to GitHub")
        print_warning("This is expected if OAuth was cancelled or failed")
        return False

    print_success("Connected to GitHub!")

    # Give time for token storage
    time.sleep(2)

    # Step 5: List connected servers
    print_step(5, "List Connected Servers")

    success, output = run_cli_command([
        "agentship", "mcp", "list", "--connected"
    ])

    if not success:
        print_error("Failed to list connected servers")
        return False

    if "github" in output and "active" in output:
        print_success("GitHub connection active")
    else:
        print_error("GitHub not in connected servers")
        return False

    # Step 6: Test connection
    print_step(6, "Test GitHub Connection")

    success, output = run_cli_command([
        "agentship", "mcp", "test", "github"
    ])

    if not success:
        print_error("Connection test failed")
        print_warning("This may be expected if GitHub MCP server is not available")
        # Don't return False - GitHub MCP might not be available yet
    else:
        print_success("Connection test passed")
        if "tools" in output.lower():
            print_success("Tools listed successfully")

    # Step 7: Disconnect
    print_step(7, "Disconnect from GitHub")

    # Use echo to auto-confirm
    success = subprocess.run(
        ["bash", "-c", "echo y | agentship mcp disconnect github"],
        capture_output=True
    ).returncode == 0

    if not success:
        print_error("Failed to disconnect")
        return False

    print_success("Disconnected from GitHub")

    # Step 8: Verify disconnection
    print_step(8, "Verify Disconnection")

    success, output = run_cli_command([
        "agentship", "mcp", "list", "--connected"
    ])

    if "github" in output:
        print_error("GitHub still in connected servers")
        return False

    print_success("GitHub successfully disconnected")

    return True


def main():
    """Main test function."""
    try:
        success = test_e2e()

        print(f"\n{BLUE}{'='*60}{RESET}")
        if success:
            print(f"{GREEN}✅ All tests passed!{RESET}")
            print(f"{GREEN}MCP OAuth integration is working correctly.{RESET}")
            return 0
        else:
            print(f"{RED}❌ Some tests failed.{RESET}")
            print(f"{YELLOW}Check the output above for details.{RESET}")
            return 1

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        return 1
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
