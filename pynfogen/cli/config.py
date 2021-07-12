import logging

import click
import yaml


@click.command()
@click.argument("key", type=str, required=False)
@click.argument("value", type=str, required=False)
@click.option("--unset", is_flag=True, default=False, help="Unset/remove the configuration value.")
@click.option("--list", "list_", is_flag=True, default=False, help="List all set configuration values.")
@click.pass_context
def config(ctx, key: str, value: str, unset: bool, list_: bool):
    """Manage configuration."""
    if not key and not value and not list_:
        return click.echo(config.get_help(ctx))

    log = logging.getLogger("config")

    config_path = ctx.obj["config_path"]
    if config_path.exists():
        with config_path.open() as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    else:
        data = None
    if not data:
        data = {}

    if list_:
        print(yaml.dump(data).rstrip())
        return

    tree = key.split(".")
    temp = data
    for t in tree[:-1]:
        if temp.get(t) is None:
            temp[t] = {}
        temp = temp[t]

    if unset:
        if tree[-1] in temp:
            del temp[tree[-1]]
        log.info(f"Unset {key}")
    else:
        if value is None:
            if tree[-1] not in temp:
                raise click.ClickException(f"Key {key} does not exist in the config.")
            print(f"{key}: {temp[tree[-1]]}")
        else:
            temp[tree[-1]] = value
            log.info(f"Set {key} to {repr(value)}")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with config_path.open("wt") as f:
                yaml.dump(data, f)
