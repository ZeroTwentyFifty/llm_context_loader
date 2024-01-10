import os
import json
import tomllib


def build_repository_structure(root_dir="."):
    """Builds a dictionary representing the repository structure.

    Args:
        root_dir: The root directory to scan (defaults to ".").

    Returns:
        dict: A dictionary containing the repository structure.
    """

    EXCLUDE_DIRS = [".git", "__pycache__", "pytest_cache"]  # Add directories to exclude

    repository_structure = {}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]  # Filter excluded directories
        dir_structure = root.replace(str(root_dir), "").split(os.sep)

        # Build structure recursively
        current_level = repository_structure
        for subdir in dir_structure:
            current_level = current_level.setdefault(subdir, {})

        current_level["files"] = files

    return repository_structure


def get_dependencies_from_pyproject(pyproject_path="pyproject.toml"):
    """Extracts production and development dependencies from pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file (defaults to "pyproject.toml").

    Returns:
        dict: A dictionary with "dependencies" and "dev_dependencies" keys.
    """

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    poetry_config = pyproject.get("tool", {}).get("poetry", {})
    dependencies = poetry_config.get("dependencies", {})
    dev_dependencies = poetry_config.get("group", {}).get("dev", {}).get("dependencies", {})

    return {
        "dependencies": list(dependencies.keys()),
        "dev_dependencies": list(dev_dependencies.keys())
    }


def scan_project_context():
    """Scans the current directory for context-providing files and information.

    Returns:
        dict: A dictionary containing the collected context data.
    """

    context = {}

    # Check for pyproject.toml
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        context["project_name"] = pyproject.get("tool", {}).get("poetry", {}).get("name") or os.path.basename(os.path.normpath(os.getcwd()))
        context["python_version"] = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python")
    else:
        context["project_name"] = os.path.basename(os.path.normpath(os.getcwd()))

    if os.path.exists("pyproject.toml"):
        context.update(get_dependencies_from_pyproject())

    # Check for testing framework
    if os.path.exists("tests"):
        for root, _, files in os.walk("tests"):
            if "pytest.ini" in files:
                context["testing_framework"] = "pytest"
                break
            elif "unittest" in root:
                context["testing_framework"] = "unittest"
                break

    # Repository structure (simplified example)
    context["repository_structure"] = build_repository_structure()

    return context

def main():
    """Collects project context and prints it as JSON."""

    context = scan_project_context()
    print(json.dumps(context, indent=4))

if __name__ == "__main__":
    main()