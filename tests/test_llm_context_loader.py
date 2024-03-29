import os

import pytest

from llm_context_loader import scan_project_context, build_repository_structure


@pytest.fixture(scope="function")
def test_project_dir(tmp_path):
    """Creates a temporary test project directory with basic structure."""

    test_dir = tmp_path / "test_project"
    os.mkdir(test_dir)
    with open(test_dir / "pyproject.toml", "w") as f:
        f.write("[tool.poetry]\nname = 'my-project'\n")
    return test_dir


def test_project_name_from_pyproject(test_project_dir):
    """Uses the fixture to create a temporary directory for isolation."""

    os.chdir(test_project_dir)
    context = scan_project_context()
    assert context["project_name"] == "my-project"


def test_project_name_fallback(test_project_dir):
    """Asserts the fallback behavior when pyproject.toml is missing."""

    # Remove the pyproject.toml file for this test
    os.remove(test_project_dir / "pyproject.toml")

    os.chdir(test_project_dir)
    context = scan_project_context()

    assert context["project_name"] == os.path.basename(os.getcwd())  # Now correctly asserts against "test_project"


def test_build_repository_structure(tmp_path):
    """Tests the build_repository_structure function."""

    # Create a test directory structure
    test_dir = tmp_path / "test_project"
    os.mkdir(test_dir)
    os.mkdir(test_dir / "src")
    os.mkdir(test_dir / "tests")
    os.mkdir(test_dir / "__pycache__")  # Create __pycache__ to test exclusion
    with open(test_dir / "README.md", "w") as f:
        f.write("Test Project")
    with open(test_dir / "src" / "main.py", "w") as f:
        f.write("print('Hello from main.py')")
    with open(test_dir / "tests" / "test_something.py", "w") as f:
        f.write("def test_function():\n    assert True")

    # Build the repository structure
    repo_structure = build_repository_structure(test_dir)

    # Assert the expected structure (excluding __pycache__)
    assert repo_structure == {
        "files": ["README.md"],
        "src": {"files": ["main.py"]},
        "tests": {"files": ["test_something.py"]}
    }


def test_pyproject_dependencies(test_project_dir):
    """Tests extracting dependencies from pyproject.toml."""

    with open(test_project_dir / "pyproject.toml", "w") as f:
        f.write("""
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.12"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"

        """)

    os.chdir(test_project_dir)
    context = scan_project_context()

    assert context["dependencies"] == ["python"]
    assert context["dev_dependencies"] == ["pytest"]


def test_context_explanation(test_project_dir):  # Test function renamed
    """Tests the generated context explanation."""

    os.chdir(test_project_dir)
    context = scan_project_context()

    assert "context data describes" in context["context_explanation"]
    assert "Python project" in context["context_explanation"]
    assert "dependencies" in context["context_explanation"]
    assert "structure" in context["context_explanation"]
    # ... (potentially more specific asserts for the new description)
