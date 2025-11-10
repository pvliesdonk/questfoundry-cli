"""Provider and role registry utilities for questfoundry-py integration"""

from pathlib import Path
from typing import Optional

from rich.console import Console

try:
    from questfoundry.providers import ProviderConfig, ProviderRegistry
    from questfoundry.roles import RoleRegistry
    QUESTFOUNDRY_AVAILABLE = True
except ImportError:
    QUESTFOUNDRY_AVAILABLE = False
    ProviderConfig = None  # type: ignore
    ProviderRegistry = None  # type: ignore
    RoleRegistry = None  # type: ignore

from qf.utils.workspace import get_spec_path

console = Console()


def get_provider_config(config_path: Optional[Path] = None) -> "ProviderConfig":
    """
    Get or create ProviderConfig.

    Args:
        config_path: Optional path to config file (defaults to .questfoundry/config.yml)

    Returns:
        ProviderConfig instance

    Raises:
        RuntimeError: If questfoundry-py is not installed
    """
    if not QUESTFOUNDRY_AVAILABLE:
        raise RuntimeError(
            "questfoundry-py library is not installed. "
            "Install with: pip install questfoundry-py[openai]"
        )

    if config_path:
        return ProviderConfig(config_path=config_path)
    return ProviderConfig()


def get_provider_registry(
    config: Optional["ProviderConfig"] = None,
) -> "ProviderRegistry":
    """
    Get or create ProviderRegistry.

    Args:
        config: Optional ProviderConfig (will be created if not provided)

    Returns:
        ProviderRegistry instance

    Raises:
        RuntimeError: If questfoundry-py is not installed
    """
    if not QUESTFOUNDRY_AVAILABLE:
        raise RuntimeError(
            "questfoundry-py library is not installed. "
            "Install with: pip install questfoundry-py[openai]"
        )

    if config is None:
        config = get_provider_config()

    return ProviderRegistry(config)


def get_role_registry(
    provider_registry: Optional["ProviderRegistry"] = None,
    spec_path: Optional[Path] = None,
) -> "RoleRegistry":
    """
    Get or create RoleRegistry.

    Args:
        provider_registry: Optional ProviderRegistry (will be created if not provided)
        spec_path: Optional path to questfoundry-spec (will be auto-detected if not provided)

    Returns:
        RoleRegistry instance

    Raises:
        RuntimeError: If questfoundry-py is not installed
        RuntimeError: If spec directory cannot be found
    """
    if not QUESTFOUNDRY_AVAILABLE:
        raise RuntimeError(
            "questfoundry-py library is not installed. "
            "Install with: pip install questfoundry-py[openai]"
        )

    if provider_registry is None:
        provider_registry = get_provider_registry()

    if spec_path is None:
        spec_path = get_spec_path()

    return RoleRegistry(
        provider_registry=provider_registry,
        spec_path=spec_path,
    )


def require_provider_registry() -> "ProviderRegistry":
    """
    Get ProviderRegistry or exit with error message.

    This is a convenience function for CLI commands that require
    providers. It provides user-friendly error messages and exits
    with code 1 on error.

    Returns:
        ProviderRegistry instance

    Note:
        This function calls sys.exit(1) on error, so it should only
        be used in CLI command contexts, not in library code.
    """
    import sys

    try:
        return get_provider_registry()
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        if "not installed" in str(e):
            console.print(
                "\n[yellow]Hint:[/yellow] Install questfoundry-py with providers:\n"
                "  pip install questfoundry-py[openai]"
            )
        sys.exit(1)


def require_role_registry(
    spec_path: Optional[Path] = None,
) -> "RoleRegistry":
    """
    Get RoleRegistry or exit with error message.

    This is a convenience function for CLI commands that require
    roles. It provides user-friendly error messages and exits
    with code 1 on error.

    Args:
        spec_path: Optional path to questfoundry-spec directory

    Returns:
        RoleRegistry instance

    Note:
        This function calls sys.exit(1) on error, so it should only
        be used in CLI command contexts, not in library code.
    """
    import sys

    try:
        provider_registry = get_provider_registry()
        return get_role_registry(provider_registry, spec_path)
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        if "not installed" in str(e):
            console.print(
                "\n[yellow]Hint:[/yellow] Install questfoundry-py with providers:\n"
                "  pip install questfoundry-py[openai]"
            )
        elif "spec" in str(e).lower():
            console.print(
                "\n[yellow]Hint:[/yellow] Initialize the spec submodule:\n"
                "  git submodule update --init --recursive\n"
                "Or set QUESTFOUNDRY_SPEC_PATH environment variable."
            )
        sys.exit(1)
