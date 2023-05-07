"""CLIManager, a class for managing RestEZ projects."""
import os
import threading
from pathlib import Path
from typing import Any
from typing import Dict

import typer
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader
from rich import print as rprint
from rich.filesize import decimal
from rich.text import Text
from rich.tree import Tree

Node = Tree


class ProjectExistsError(Exception):
    """ProjectExistsError class."""


class CLIManager:
    """CLIManager class."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> 'CLIManager':
        """Create a singleton object."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def _create_folders(cls, structure: Dict[str, Any], project_dir: Path, project_name: str) -> int:
        count = 0
        for folder in structure["folders"]:
            (project_dir / project_name / folder["path"]).mkdir(parents=True, exist_ok=True)
            for file in folder["files"]:
                (project_dir / project_name / folder["path"] / file).touch()
                count += 1
        return count

    @classmethod
    def _create_templates(
        cls, structure: Dict[str, Any], project_dir: Path, project_name: str, env: Environment
    ) -> int:
        count = 0
        for template_info in structure["templates"]:
            template = env.get_template(template_info["name"])
            with open(project_dir / project_name / template_info["path"], "w") as file:
                content = template.render(project_name=project_name)
                file.write(content)
            count += 1
        return count

    @classmethod
    def generate_project_tree(cls, project_dir: Path, project_name: str) -> None:
        """Generate a tree representation of the project structure."""
        tree = Tree(
            f":open_file_folder: [bold blue][link file://{project_dir / project_name}]{project_name}/",
            guide_style="bold bright_blue",
        )
        project_path = project_dir / project_name

        nodes: Dict[str, Node] = {}

        for root, dirs, files in os.walk(project_path):
            level = root.replace(str(project_path), "").count(os.sep)
            current_path = os.sep.join(root.split(os.sep)[-level:])
            parent_node = tree if level == 0 else nodes[current_path]

            for directory in dirs:
                node = parent_node.add(
                    f"[bold magenta]:open_file_folder: [link file://{Path(root) / directory}]{directory}",
                    guide_style="bold bright_blue",
                )
                nodes[os.path.join(current_path, directory)] = node

            for file in files:
                file_path = Path(root) / file
                text_filename = Text(file, "green")
                text_filename.stylize(f"link file://{file_path}")
                file_size = file_path.stat().st_size
                text_filename.append(f" ({decimal(file_size)})", "blue")
                icon = "🐍 " if file_path.suffix == ".py" else "📄 "
                parent_node.add(Text(icon) + text_filename, guide_style="bold bright_blue")

        rprint(tree)

    @classmethod
    def new_project(cls, project_dir: Path, project_name: str) -> str:
        """Core logic for creating a new project."""
        project_dir = Path(project_dir)
        if not project_dir:
            project_dir = Path.cwd()

        if (project_dir / project_name).exists():
            raise ProjectExistsError(f"The project '{project_name}' already exists in '{project_dir}'.")

        with open("your_yaml_file.yaml", "r") as yaml_file:
            structure = yaml.safe_load(yaml_file)

        env = Environment(loader=FileSystemLoader(str(Path(__file__).parent / 'templates')), autoescape=True)

        total_items = len(structure["folders"]) + len(structure["templates"])
        with typer.progressbar(length=total_items, label="Creating files...") as progress:
            created_folders = cls._create_folders(structure, project_dir, project_name)
            progress.update(created_folders)
            created_templates = cls._create_templates(structure, project_dir, project_name, env)
            progress.update(created_templates)

        return f"New project '{project_name}' created successfully in '{project_dir}'."
