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

    EXCLUDE_DIRS = [".git", "__pycache__", ".pytest_cache", ".idea"]

    repository_structure = {}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        dir_structure = root.replace(str(root_dir), "").split(os.sep)

        # Build structure recursively
        current_level = repository_structure
        for subdir in dir_structure:
            if subdir != "":
                current_level[subdir] = {}
                current_level = current_level[subdir]

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


def build_context_description():
    """Generates a description of the purpose of the collected context data.

    Possible Alternative context_description:     context["context_explanation"] = "This context data provides
    information about a Python project, including its dependencies, structure, and testing framework. It is designed
    to help conversational LLMs understand the project's context when responding to prompts or generating code
    related to it."

    Returns:
        str: A description of the context data, suitable for an LLM.
    """

    return """
    This context data describes the structure and metadata of a Python project. 
    It includes information about:

    * **Project Name:** The name of the project.
    * **Python Version:** The required Python version for the project.
    * **Dependencies:** Python packages required for the project to function.
    * **Dev Dependencies:** Python packages required for development and testing.
    * **Repository Structure:** The file and directory structure of the project.

    This data can be used to provide background information to an LLM when 
    asking questions or giving instructions related to the project.
    """


def scan_project_context():
    """Scans the current directory for context-providing files and information.

    Returns:
        dict: A dictionary containing the collected context data.
    """

    context = {}

    context["context_description"] = build_context_description()

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
