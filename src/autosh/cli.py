"""AutoSH CLI — 一句中文，自动补命令。"""

import os
import shutil
import sys
from importlib import resources
from pathlib import Path

import click


@click.group()
def main():
    """AutoSH — 一句中文，自动补命令。"""
    pass


@main.command()
@click.argument("shell", type=click.Choice(["zsh", "bash"]))
def init(shell: str):
    """Install AutoSH shell integration.

    SHELL must be 'zsh' or 'bash'.
    """
    from autosh.config import Config

    config = Config()
    if not config.get("api_key"):
        click.echo("No API key configured. Set one first:")
        click.echo(f"  autosh config set api_key <your-deepseek-key>")
        click.echo("")

    autosh_dir = Path.home() / ".autosh"
    autosh_dir.mkdir(parents=True, exist_ok=True)

    # Create default config if missing
    if not (autosh_dir / "config.yaml").exists():
        config.save()
        click.echo(f"  Created {autosh_dir / 'config.yaml'}")

    # Copy shell template
    tmpl_name = f"autosh.{shell}"
    dest = autosh_dir / tmpl_name
    template = resources.files("autosh.templates") / tmpl_name
    shutil.copy(str(template), str(dest))
    click.echo(f"  Installed {dest}")

    rc_file = ".bashrc" if shell == "bash" else ".zshrc"
    rc_path = Path.home() / rc_file

    source_line = f"source ~/.autosh/autosh.{shell}  # AutoSH"
    if rc_path.exists():
        if source_line not in rc_path.read_text():
            click.echo(f"\n  Add this line to {rc_file}:")
            click.echo(f"  {source_line}")
        else:
            click.echo(f"\n  Already sourced in {rc_file}")
    else:
        click.echo(f"\n  Add this line to your shell rc file:")
        click.echo(f"  {source_line}")

    click.echo(f"\n  Reload your shell or run: source ~/{dest.relative_to(Path.home())}")
    click.echo(f"\n  Ctrl+G       → 极速出命令")
    click.echo(f"  Ctrl+/       → 三选一 + 中文解释")
    click.echo(f"  Ctrl+_       → 三选一（Ctrl+/ 的终端等价按键）")


@main.group(invoke_without_command=True)
@click.pass_context
def config(ctx):
    """Manage AutoSH configuration."""
    if ctx.invoked_subcommand is None:
        from autosh.config import Config

        c = Config()
        click.echo(c.display())


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a config value."""
    from autosh.config import PROVIDERS, Config

    valid = {"provider", "model", "base_url", "api_key"}
    if key not in valid:
        click.echo(f"Unknown config key: {key}")
        click.echo(f"Valid keys: {', '.join(sorted(valid))}")
        sys.exit(1)
    c = Config()
    if key == "provider" and value not in PROVIDERS:
        click.echo(f"Unknown provider: {value}")
        click.echo(f"Available: {', '.join(PROVIDERS.keys())}")
        sys.exit(1)
    c.set(key, value)
    if key == "provider":
        preset = PROVIDERS[value]
        click.echo(f"  provider = {value}")
        click.echo(f"  model    = {preset['model']} (auto)")
        click.echo(f"  base_url = {preset['base_url']} (auto)")
    else:
        display_val = value
        if key == "api_key":
            display_val = "****"
        click.echo(f"  {key} = {display_val}")


@main.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--multi", is_flag=True, help="Return multiple suggestions (JSON array)")
def suggest_cmd(query: tuple[str, ...], multi: bool = False):
    """Generate a shell command suggestion from Chinese text."""
    text = " ".join(query)
    if not os.environ.get("AUTOSH_NO_DAEMON"):
        try:
            from autosh.daemon import DaemonResponseError, suggest as daemon_suggest

            results = daemon_suggest(text, multi)
            if multi:
                for r in results:
                    click.echo(f"{r['cmd']} | {r['desc']}")
            elif results:
                click.echo(results[0]["cmd"])
            else:
                sys.exit(1)
            return
        except DaemonResponseError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        except Exception:
            pass

    from autosh.config import Config
    from autosh.suggest import suggest, suggest_multi

    config = Config()
    api_key = config.get("api_key")
    if not api_key:
        click.echo("Error: no API key configured.", err=True)
        click.echo("Run: autosh config set api_key <your-key>", err=True)
        sys.exit(1)
    try:
        if multi:
            results = suggest_multi(text, config)
            for r in results:
                click.echo(f"{r['cmd']} | {r['desc']}")
        else:
            result = suggest(text, config)
            if result:
                click.echo(result)
            else:
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--keys", is_flag=True, help="Interactively test shortcut key sequences.")
def doctor(keys: bool = False):
    """Check AutoSH setup and diagnose issues."""
    from autosh.doctor import run as run_doctor

    run_doctor(keys=keys)


@main.group("daemon")
def daemon_group():
    """Manage the local AutoSH daemon."""
    pass


@daemon_group.command("start")
def daemon_start():
    """Start the local daemon."""
    from autosh.daemon import ensure_running, socket_path

    ensure_running()
    click.echo(f"daemon running: {socket_path()}")


@daemon_group.command("stop")
def daemon_stop():
    """Stop the local daemon."""
    from autosh.daemon import stop

    if stop():
        click.echo("daemon stopped")
    else:
        click.echo("daemon not running")


@daemon_group.command("status")
def daemon_status():
    """Show daemon status."""
    from autosh.daemon import is_running, socket_path

    if is_running():
        click.echo(f"daemon running: {socket_path()}")
    else:
        click.echo("daemon not running")
