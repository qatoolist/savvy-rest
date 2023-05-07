"""CLI commands for managing savvy-rest projects."""
from pathlib import Path
from typing import Any
from typing import Callable
from typing import TypeVar

import typer
from typing_extensions import Annotated

from .cli_manager import CLIManager
from .cli_manager import ProjectExistsError

cwd = Path.cwd()
app = typer.Typer()
state = {"verbose": False}
FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def typed_command(func: FuncT) -> FuncT:
    """Add type hints to the decorators."""
    typed_func: FuncT = app.command()(func)
    return typed_func


def typed_callback(func: FuncT) -> FuncT:
    """Add type hints to the decorators."""
    typed_func: FuncT = app.callback()(func)
    return typed_func


@typed_command
def new_project(
    project_name: Annotated[str, typer.Argument(help="The name of the new project.")],
    project_dir: Annotated[
        Path, typer.Option(..., help="The project directory path. Default is the current directory.")
    ] = cwd,
) -> None:
    """Create a new savvy-rest project."""
    if project_dir is None:
        current_directory = Path.cwd()
        project_dir = typer.prompt(
            f"Please provide the project directory (press Enter to use the default [{current_directory}])",
            default=current_directory,
            type=Path,
        )

    try:
        result = CLIManager.new_project(project_dir, project_name)
        typer.echo(result)
        if state["verbose"]:
            CLIManager.generate_project_tree(project_dir, project_name)
    except ProjectExistsError as err:
        typer.echo(f"Error: {err}")


@typed_command
def new_route(name: Annotated[str, typer.Argument(help="The name of the new route.")]) -> None:
    """Create a new route in the project."""
    print(f"Creating a new route {name}")


@typed_command
def new_scenario(
    route_name: Annotated[str, typer.Argument(help="The name of the route.")],
    scenario_name: Annotated[str, typer.Argument(help="The name of the new scenario.")],
) -> None:
    """Create a new scenario for a route."""
    print(f"Creating a new scenario {scenario_name} for a route {route_name}")


@typed_command
def update_config(
    environment_name: Annotated[str, typer.Argument(help="The name of the environment for updating the config.")],
    update: Annotated[
        str,
        typer.Option(
            ...,
            help="The new values for target environment configuration in dictionary format string, ex. {'config_name': 'new_value'}.",  # noqa
        ),
    ] = "",
) -> None:
    """Update the configuration for a specific environment."""
    print(f"Updating config {update} for a environment {environment_name}")


@typed_command
def run(
    environment_name: Annotated[str, typer.Option(..., help="The environment name to run the tests in.")] = 'stage',
    parallel_count: Annotated[int, typer.Option(..., help="The number of scenarios to run in parallel mode.")] = 0,
    tags: Annotated[str, typer.Option(..., help="Execute scenarios with these comma-separated tags.")] = "",
    routes: Annotated[str, typer.Option(..., help="Execute scenarios belonging to these comma-separated routes.")] = "",
    filters_: Annotated[str, typer.Option(..., help="Execute scenarios matching the specified filter condition.")] = "",
) -> None:
    """Run tests in the specified environment."""
    print(
        f"Running scenarios with configuration:: environment_name:{environment_name}, parallel_count:{parallel_count}, tags:{tags}, routes:{routes}, filters:{filters_}"  # noqa
    )


@typed_callback
def verbose_callback(verbose: bool = False) -> None:
    """Enable verbose output."""
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


if __name__ == "__main__":
    app()
